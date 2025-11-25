import copy
import math
import random

def initialize_board(n):
    board = [[' ' for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for col in range(n):
            if (row + col) % 2 == 0:
                if row < (n // 2 - 1):
                    board[row][col] = 'W'
                elif row >= (n - (n // 2 - 1)):
                    board[row][col] = 'B'
    return board

def print_board(board):
    n = len(board)
    print("  " + " ".join(str(i) for i in range(n)))
    for r in range(n):
        print(r, end=" ")
        for c in range(n):
            print(board[r][c] if board[r][c] != ' ' else '.', end=" ")
        print()

def check_for_captures(board, player, r=None, c=None):
    n = len(board)
    if r is not None and c is not None:
        piece = board[r][c]
        if player == 'W' and piece not in ['W', 'WK']:
            return False
        if player == 'B' and piece not in ['B', 'BK']:
            return False
        is_king = piece in ['WK', 'BK']
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_king else \
                    [(1, -1), (1, 1)] if player == 'W' else [(-1, -1), (-1, 1)]
        
        if is_king:
            # For kings, check long range captures in all directions
            opponent = 'B' if player == 'W' else 'W'
            for dr, dc in directions:
                enemy_found = False
                enemy_r, enemy_c = -1, -1
                
                # Look for an enemy piece and empty space beyond it
                for distance in range(1, n):
                    check_r = r + dr * distance
                    check_c = c + dc * distance
                    
                    if not (0 <= check_r < n and 0 <= check_c < n):
                        break
                        
                    if not enemy_found:
                        if board[check_r][check_c] in [opponent, opponent + 'K']:
                            enemy_found = True
                            enemy_r, enemy_c = check_r, check_c
                        elif board[check_r][check_c] != ' ':
                            break
                    else:
                        # After finding enemy, look for empty space
                        if board[check_r][check_c] == ' ':
                            return True
                        else:
                            break
        else:
            # Regular piece logic (unchanged)
            for dr, dc in directions:
                adj_r = r + dr
                adj_c = c + dc
                jump_r = r + 2*dr
                jump_c = c + 2*dc
                if 0 <= adj_r < n and 0 <= adj_c < n and 0 <= jump_r < n and 0 <= jump_c < n:
                    adj_piece = board[adj_r][adj_c]
                    opponent = 'B' if player == 'W' else 'W'
                    if adj_piece in [opponent, opponent + 'K'] and board[jump_r][jump_c] == ' ':
                        return True
        return False
    
    # Check entire board for captures
    for r in range(n):
        for c in range(n):
            piece = board[r][c]
            if player == 'W' and piece not in ['W', 'WK']:
                continue
            if player == 'B' and piece not in ['B', 'BK']:
                continue
            is_king = piece in ['WK', 'BK']
            
            if is_king:
                # Check king's capturing possibilities in all directions
                opponent = 'B' if player == 'W' else 'W'
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                
                for dr, dc in directions:
                    enemy_found = False
                    
                    # Look along the diagonal for an enemy piece and empty space beyond it
                    for distance in range(1, n):
                        check_r = r + dr * distance
                        check_c = c + dc * distance
                        
                        if not (0 <= check_r < n and 0 <= check_c < n):
                            break
                            
                        if not enemy_found:
                            if board[check_r][check_c] in [opponent, opponent + 'K']:
                                enemy_found = True
                            elif board[check_r][check_c] != ' ':
                                break
                        else:
                            # After finding enemy, look for empty space
                            if board[check_r][check_c] == ' ':
                                return True
                            else:
                                break
            else:
                # Regular piece logic (unchanged)
                directions = [(1, -1), (1, 1)] if player == 'W' else [(-1, -1), (-1, 1)]
                for dr, dc in directions:
                    adj_r = r + dr
                    adj_c = c + dc
                    jump_r = r + 2*dr
                    jump_c = c + 2*dc
                    if 0 <= adj_r < n and 0 <= adj_c < n and 0 <= jump_r < n and 0 <= jump_c < n:
                        adj_piece = board[adj_r][adj_c]
                        opponent = 'B' if player == 'W' else 'W'
                        if adj_piece in [opponent, opponent + 'K'] and board[jump_r][jump_c] == ' ':
                            return True
    return False

def is_valid_move(board, player, sr, sc, er, ec, mandatory_captures):
    n = len(board)
    if not (0 <= sr < n and 0 <= sc < n and 0 <= er < n and 0 <= ec < n):
        return False, False
    piece = board[sr][sc]
    if player == 'W' and piece not in ['W', 'WK']:
        return False, False
    if player == 'B' and piece not in ['B', 'BK']:
        return False, False
    if board[er][ec] != ' ':
        return False, False
    dr = er - sr
    dc = ec - sc
    if abs(dr) != abs(dc):
        return False, False
    distance = abs(dr)
    if distance == 0:
        return False, False
    is_king = piece in ['WK', 'BK']
    opponent = 'B' if player == 'W' else 'W'
    dir_r = dr // distance
    dir_c = dc // distance

    if is_king:
        # Check path between start and end positions
        enemy_count = 0
        enemy_position = None
        
        for step in range(1, distance):
            current_r = sr + dir_r * step
            current_c = sc + dir_c * step
            if current_r < 0 or current_r >= n or current_c < 0 or current_c >= n:
                continue
                
            current_piece = board[current_r][current_c]
            if current_piece in [opponent, opponent + 'K']:
                enemy_count += 1
                enemy_position = (current_r, current_c)
            elif current_piece != ' ':
                return False, False
                
        if mandatory_captures:
            # For mandatory captures, king must capture exactly one piece
            if enemy_count == 1:
                return True, True
            return False, False
        else:
            # Without mandatory captures, king can move any distance without enemies in path
            if enemy_count == 0:
                return True, False
            elif enemy_count == 1:
                return True, True
            else:
                return False, False
    else:
        # Regular piece logic (unchanged)
        if distance not in [1, 2]:
            return False, False
        if (player == 'W' and dr < 0) or (player == 'B' and dr > 0):
            return False, False
        if distance == 2:
            mr = (sr + er) // 2
            mc = (sc + ec) // 2
            mid_piece = board[mr][mc]
            if mid_piece not in [opponent, opponent + 'K']:
                return False, False
            return True, True
        else:
            if mandatory_captures:
                return False, False
            return True, False

def get_all_valid_moves(board, player, must_capture=None):
    n = len(board)
    moves = []
    if must_capture is None:
        mandatory_captures = check_for_captures(board, player)
    else:
        mandatory_captures = must_capture
    
    for r in range(n):
        for c in range(n):
            piece = board[r][c]
            if player == 'W' and piece not in ['W', 'WK']:
                continue
            if player == 'B' and piece not in ['B', 'BK']:
                continue
            
            directions = []
            if piece in ['WK', 'BK']:
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                for dr, dc in directions:
                    if mandatory_captures:
                        # For mandatory captures, check all possible capture distances
                        opponent = 'B' if player == 'W' else 'W'
                        enemy_found = False
                        
                        for distance in range(1, n):
                            check_r = r + dr * distance
                            check_c = c + dc * distance
                            
                            if not (0 <= check_r < n and 0 <= check_c < n):
                                break
                                
                            if not enemy_found:
                                if board[check_r][check_c] in [opponent, opponent + 'K']:
                                    enemy_found = True
                                elif board[check_r][check_c] != ' ':
                                    break
                            else:
                                # After finding enemy, add all valid landing spots
                                if board[check_r][check_c] == ' ':
                                    er = check_r
                                    ec = check_c
                                    valid, is_capture = is_valid_move(board, player, r, c, er, ec, mandatory_captures)
                                    if valid and is_capture:
                                        moves.append((r, c, er, ec))
                                else:
                                    break
                    else:
                        # For normal moves, check all possible distances
                        max_steps = 0
                        while True:
                            new_r = r + dr * (max_steps + 1)
                            new_c = c + dc * (max_steps + 1)
                            if 0 <= new_r < n and 0 <= new_c < n:
                                max_steps += 1
                            else:
                                break
                        for step in range(1, max_steps + 1):
                            er = r + dr * step
                            ec = c + dc * step
                            valid, is_capture = is_valid_move(board, player, r, c, er, ec, mandatory_captures)
                            if valid:
                                moves.append((r, c, er, ec))
            else:
                # Regular piece logic (unchanged)
                if player == 'W':
                    directions = [(1, -1), (1, 1)]
                else:
                    directions = [(-1, -1), (-1, 1)]
                for dr, dc in directions:
                    for step in [1, 2]:
                        er = r + dr * step
                        ec = c + dc * step
                        valid, is_capture = is_valid_move(board, player, r, c, er, ec, mandatory_captures)
                        if valid and ((mandatory_captures and is_capture) or not mandatory_captures):
                            moves.append((r, c, er, ec))
    return moves

def apply_move(board, move, player):
    sr, sc, er, ec = move
    piece = board[sr][sc]
    is_king = piece in ['WK', 'BK']
    board[sr][sc] = ' '
    board[er][ec] = piece

    dr = er - sr
    dc = ec - sc
    distance = abs(dr)
    dir_r = dr // distance
    dir_c = dc // distance
    is_capture = False
    
    if distance > 1:
        opponent = 'B' if player == 'W' else 'W'
        
        if is_king:
            # For kings, find and remove the captured piece
            for step in range(1, distance):
                check_r = sr + dir_r * step
                check_c = sc + dir_c * step
                if 0 <= check_r < len(board) and 0 <= check_c < len(board):
                    check_piece = board[check_r][check_c]
                    if check_piece in [opponent, opponent + 'K']:
                        board[check_r][check_c] = ' '
                        is_capture = True
                        break
        else:
            # For regular pieces (unchanged)
            mid_r = sr + dir_r
            mid_c = sc + dir_c
            if 0 <= mid_r < len(board) and 0 <= mid_c < len(board):
                mid_piece = board[mid_r][mid_c]
                if mid_piece in [opponent, opponent + 'K']:
                    board[mid_r][mid_c] = ' '
                    is_capture = True
    
    n = len(board)
    if (player == 'W' and er == n - 1 and piece == 'W') or (player == 'B' and er == 0 and piece == 'B'):
        board[er][ec] = player + 'K'
    
    return is_capture

def can_capture_again(board, player, row, col):
    return check_for_captures(board, player, row, col)

def make_move_with_multiple_captures(board, start_move, player):
    sr, sc, er, ec = start_move
    moves_made = [start_move]
    
    # Wykonaj pierwszy ruch
    is_capture = apply_move(board, start_move, player)
    
    # Tylko jeśli był to ruch z biciem, sprawdź możliwość kolejnych bić
    if is_capture:
        current_row, current_col = er, ec
        
        # Sprawdź, czy można wykonać kolejne bicia tym samym pionkiem
        while can_capture_again(board, player, current_row, current_col):
            capture_moves = []
            for move in get_all_valid_moves(board, player, True):
                if move[0] == current_row and move[1] == current_col:
                    capture_moves.append(move)
            
            if not capture_moves:
                break
                
            next_move = capture_moves[0]
            sr, sc, er, ec = next_move
            apply_move(board, next_move, player)
            moves_made.append(next_move)
            current_row, current_col = er, ec
    
    return moves_made

def evaluate_board(board, player):
    score = 0
    opponent = 'B' if player == 'W' else 'W'
    for row in board:
        for piece in row:
            if piece == player:
                score += 2
            elif piece == player + 'K':
                score += 5
            elif piece == opponent:
                score -= 2
            elif piece == opponent + 'K':
                score -= 5
    return score

def minmax(board, depth, alpha, beta, maximizing_player, player):
    if depth == 0:
        return evaluate_board(board, player)
    
    valid_moves = get_all_valid_moves(board, player)
    opponent = 'B' if player == 'W' else 'W'
    
    if maximizing_player:
        max_eval = -math.inf
        for move in valid_moves:
            new_board = copy.deepcopy(board)
            make_move_with_multiple_captures(new_board, move, player)
            evaluation = minmax(new_board, depth-1, alpha, beta, False, opponent)
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in valid_moves:
            new_board = copy.deepcopy(board)
            make_move_with_multiple_captures(new_board, move, player)
            evaluation = minmax(new_board, depth-1, alpha, beta, True, opponent)
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval

class MCTSNode:
    def __init__(self, board, player, parent=None, move=None):
        self.board = copy.deepcopy(board)
        self.player = player
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = get_all_valid_moves(board, player)
        self.move = move

    def ucb1(self, exploration=1.4):
        if self.visits == 0:
            return math.inf
        return (self.wins / self.visits) + exploration * math.sqrt(math.log(self.parent.visits) / self.visits)

def mcts(root, iterations):
    for _ in range(iterations):
        node = root
        while node.untried_moves == [] and node.children:
            node = max(node.children, key=lambda n: n.ucb1())
        
        if node.untried_moves:
            move = random.choice(node.untried_moves)
            new_board = copy.deepcopy(node.board)
            make_move_with_multiple_captures(new_board, move, node.player)
            opponent = 'B' if node.player == 'W' else 'W'
            child = MCTSNode(new_board, opponent, node, move)
            node.children.append(child)
            node.untried_moves.remove(move)
            node = child
        
        current_board = copy.deepcopy(node.board)
        current_player = node.player
        while True:
            moves = get_all_valid_moves(current_board, current_player)
            if not moves:
                break
            move = random.choice(moves)
            make_move_with_multiple_captures(current_board, move, current_player)
            current_player = 'B' if current_player == 'W' else 'W'
        
        result = evaluate_game(current_board, root.player)
        while node:
            node.visits += 1
            node.wins += result
            node = node.parent
    
    if not root.children:
        return None
    return max(root.children, key=lambda c: c.visits).move

def evaluate_game(board, original_player):
    w_count = sum(row.count('W') + row.count('WK') for row in board)
    b_count = sum(row.count('B') + row.count('BK') for row in board)
    
    if original_player == 'W':
        return 1 if w_count > b_count else -1 if b_count > w_count else 0
    else:
        return 1 if b_count > w_count else -1 if w_count > b_count else 0

def ai_move(board, player, ai_type, depth=3, iterations=1000):
    if ai_type == 'minmax':
        best_move = None
        best_value = -math.inf
        valid_moves = get_all_valid_moves(board, player)
        opponent = 'B' if player == 'W' else 'W'
        
        for move in valid_moves:
            new_board = copy.deepcopy(board)
            make_move_with_multiple_captures(new_board, move, player)
            value = minmax(new_board, depth-1, -math.inf, math.inf, False, opponent)
            if value > best_value:
                best_value = value
                best_move = move
        return best_move
    
    elif ai_type == 'mcts':
        root = MCTSNode(board, player)
        best_move = mcts(root, iterations)
        return best_move

def main():
    n = int(input("Enter board size (even number >=4): "))
    while n % 2 != 0 or n < 4:
        n = int(input("Please enter an even number >=4: "))
    
    ai_choice = input("Choose opponent type (human/minmax/mcts): ").lower()
    while ai_choice not in ['human', 'minmax', 'mcts']:
        ai_choice = input("Invalid choice. Enter human/minmax/mcts: ")

    board = initialize_board(n)
    current_player = 'W'
    
    while True:
        print_board(board)
        valid_moves = get_all_valid_moves(board, current_player)
        if not valid_moves:
            print(f"Player {current_player} has no valid moves. Player {'B' if current_player == 'W' else 'W'} wins!")
            break
        
        opponent = 'B' if current_player == 'W' else 'W'
        opponent_count = sum(row.count(opponent) + row.count(opponent + 'K') for row in board)
        if opponent_count == 0:
            print(f"Player {current_player} wins!")
            break
        
        if current_player == 'B' and ai_choice != 'human':
            print("AI is thinking...")
            move = ai_move(board, current_player, ai_choice)
            if move:
                moves_sequence = make_move_with_multiple_captures(board, move, current_player)
                print(f"AI moves: {moves_sequence}")
            else:
                print("AI couldn't find a valid move. Game ends.")
                break
        else:
            move_sequence = []
            current_r, current_c = None, None
            
            mandatory_captures = check_for_captures(board, current_player)
            while True:
                try:
                    start = input(f"Player {current_player}, enter piece to move (row col): ").split()
                    sr, sc = map(int, start)
                    piece = board[sr][sc]
                    if current_player == 'W' and piece not in ['W', 'WK']:
                        print("Not your piece.")
                        continue
                    if current_player == 'B' and piece not in ['B', 'BK']:
                        print("Not your piece.")
                        continue
                    end = input("Enter destination (row col): ").split()
                    er, ec = map(int, end)
                    valid, is_capture = is_valid_move(board, current_player, sr, sc, er, ec, mandatory_captures)
                    if mandatory_captures and not is_capture:
                        print("You must make a capture move.")
                        continue
                    if not valid:
                        print("Invalid move.")
                        continue
                    break
                except:
                    print("Invalid input. Try again.")
            
            move = (sr, sc, er, ec)
            moves_sequence = make_move_with_multiple_captures(board, move, current_player)
            if len(moves_sequence) > 1:
                print(f"Multiple captures made: {moves_sequence}")
        
        current_player = 'B' if current_player == 'W' else 'W'

if __name__ == "__main__":
    main()

    