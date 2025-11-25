import time
import copy
from checkers import *
from gui import *

class Game:
    def __init__(self, n, opponent_type):
        self.n = n
        self.board = initialize_board(n)
        self.current_player = 'W'
        self.opponent_type = opponent_type
        self.selected_piece = None
        self.valid_moves = []
        self.mandatory_captures = False
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        self.animations = []
        self.pause_until = 0  # Time until the pause ends
        
        # Pre-calculate piece positions
        self.piece_centers = {}
        for row in range(n):
            for col in range(n):
                x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
                y = MARGIN + row * CELL_SIZE + CELL_SIZE // 2
                self.piece_centers[(row, col)] = (x, y)
    
    def update_mandatory_captures(self):
        self.mandatory_captures = check_for_captures(self.board, self.current_player)
    
    def get_valid_moves_for_piece(self, row, col):
        all_moves = get_all_valid_moves(self.board, self.current_player, self.mandatory_captures)
        return [(er, ec) for (sr, sc, er, ec) in all_moves if sr == row and sc == col]
    
    def handle_click(self, row, col):
        if self.game_over or (self.current_player == 'B' and self.opponent_type != 'human') or self.ai_thinking or self.animations or time.time() < self.pause_until:
            return
        
        self.update_mandatory_captures()
        
        # If a piece is already selected and we're clicking on a destination
        if self.selected_piece:
            sr, sc = self.selected_piece
            if (row, col) in self.valid_moves:
                move = (sr, sc, row, col)
                # Start animation before modifying the board
                piece_type = self.board[sr][sc]
                start_pos = self.piece_centers[(sr, sc)]
                end_pos = self.piece_centers[(row, col)]
                
                # Add animation
                self.animations.append(AnimatedPiece(piece_type, start_pos, end_pos))
                
                # Check for captures (for animation)
                if abs(row - sr) == 2 and abs(col - sc) == 2:
                    # This is a capture move, animate captured piece disappearing
                    captured_row = (sr + row) // 2
                    captured_col = (sc + col) // 2
                    captured_pos = self.piece_centers[(captured_row, captured_col)]
                    # Add fade-out animation for captured piece
                    # For simplicity, we just move it off screen
                    off_screen = (-50, -50)
                    self.animations.append(AnimatedPiece(self.board[captured_row][captured_col], 
                                                     captured_pos, off_screen))
                
                # Store move to be executed after animation
                self.pending_move = (move, self.current_player)
                self.selected_piece = None
                self.valid_moves = []
            else:
                # Reset selection if clicked elsewhere
                self.selected_piece = None
                self.valid_moves = []
        else:
            # Check if clicked on a valid piece
            piece = self.board[row][col]
            if piece == ' ':
                return
                
            if (self.current_player == 'W' and piece not in ['W', 'WK']) or \
               (self.current_player == 'B' and piece not in ['B', 'BK']):
                return
            
            self.selected_piece = (row, col)
            self.valid_moves = self.get_valid_moves_for_piece(row, col)
    
    def update_animations(self):
        if self.animations and all(anim.is_finished for anim in self.animations):
            # Apply move after animation ends
            if hasattr(self, 'pending_moves'):
                move = self.pending_moves[self.move_index]
                apply_move(self.board, move, self.current_player)
                self.move_index += 1
                
                # If we have more moves in sequence, animate next one
                if self.move_index < len(self.pending_moves):
                    next_move = self.pending_moves[self.move_index]
                    sr, sc, er, ec = next_move
                    piece_type = self.board[sr][sc]
                    start_pos = self.piece_centers[(sr, sc)]
                    end_pos = self.piece_centers[(er, ec)]
                    
                    # Add animation for next move
                    self.animations.append(AnimatedPiece(piece_type, start_pos, end_pos))
                    
                    # Add animation for captured piece if it's a capture
                    if abs(er - sr) == 2 and abs(ec - sc) == 2:
                        captured_row = (sr + er) // 2
                        captured_col = (sc + ec) // 2
                        captured_pos = self.piece_centers[(captured_row, captured_col)]
                        off_screen = (-50, -50)
                        self.animations.append(AnimatedPiece(self.board[captured_row][captured_col], 
                                                        captured_pos, off_screen))
                    return
                
                # Finished entire move sequence
                self.pause_until = time.time() + PAUSE_AFTER_MOVE
                self.current_player = 'B' if self.current_player == 'W' else 'W'
                self.check_game_over()
                delattr(self, 'pending_moves')
                delattr(self, 'move_index')
            
            # Apply single move for player (not AI)
            elif hasattr(self, 'pending_move'):
                move, player = self.pending_move
                make_move_with_multiple_captures(self.board, move, player)
                self.pause_until = time.time() + PAUSE_AFTER_MOVE
                self.current_player = 'B' if player == 'W' else 'W'
                self.check_game_over()
                delattr(self, 'pending_move')
                
            self.animations = []
    
    def check_game_over(self):
        valid_moves = get_all_valid_moves(self.board, self.current_player)
        if not valid_moves:
            self.game_over = True
            self.winner = 'B' if self.current_player == 'W' else 'W'
        
        # Also check if no pieces left
        w_count = sum(row.count('W') + row.count('WK') for row in self.board)
        b_count = sum(row.count('B') + row.count('BK') for row in self.board)
        
        if w_count == 0:
            self.game_over = True
            self.winner = 'B'
        elif b_count == 0:
            self.game_over = True
            self.winner = 'W'
        
    def ai_move(self):
        if self.current_player == 'B' and self.opponent_type != 'human' and not self.game_over and not self.animations and time.time() >= self.pause_until:
            self.ai_thinking = True
            move = ai_move(self.board, self.current_player, self.opponent_type, depth=4, iterations=500)
            self.ai_thinking = False
            
            if move:
                # Find move sequence (for multiple captures)
                moves_sequence = [(move[0], move[1], move[2], move[3])]
                
                # Create temporary board copy to determine move sequence
                temp_board = copy.deepcopy(self.board)
                moves_sequence = make_move_with_multiple_captures(temp_board, move, self.current_player)
                
                # Animate only first move - rest will be handled after it ends
                first_move = moves_sequence[0]
                sr, sc, er, ec = first_move
                piece_type = self.board[sr][sc]
                start_pos = self.piece_centers[(sr, sc)]
                end_pos = self.piece_centers[(er, ec)]
                
                # Add animation for first move
                self.animations.append(AnimatedPiece(piece_type, start_pos, end_pos))
                
                # Add animation for captured piece if it's a capture
                if abs(er - sr) == 2 and abs(ec - sc) == 2:
                    captured_row = (sr + er) // 2
                    captured_col = (sc + ec) // 2
                    captured_pos = self.piece_centers[(captured_row, captured_col)]
                    off_screen = (-50, -50)
                    self.animations.append(AnimatedPiece(self.board[captured_row][captured_col], 
                                                    captured_pos, off_screen))
                
                # Save entire move sequence to execute after animation ends
                self.pending_moves = moves_sequence
                self.move_index = 0