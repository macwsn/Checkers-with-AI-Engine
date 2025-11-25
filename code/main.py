import pygame
import sys
from game import *
from gui import *

def setup_screen():
    pygame.init()
    screen = pygame.display.set_mode((400, 450))
    pygame.display.set_caption("Checkers Setup")
    
    board_size_input = TextInput(100, 100, 200, 40, '8')
    opponent_buttons = [
        Button(100, 200, 200, 40, 'Human', 'human'),
        Button(100, 250, 200, 40, 'AI (Minimax)', 'minmax'),
        Button(100, 300, 200, 40, 'AI (MCTS)', 'mcts')
    ]
    start_button = Button(100, 350, 200, 40, 'Start Game', 'start')
    
    title_font = pygame.font.Font(None, 36)
    title_text = title_font.render("Checkers Setup", True, COLORS['text'])
    size_label = pygame.font.Font(None, 28).render("Board Size:", True, COLORS['text'])
    opponent_label = pygame.font.Font(None, 28).render("Select Opponent:", True, COLORS['text'])
    
    selected_opponent = None
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(COLORS['background'])
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                for btn in opponent_buttons:
                    if btn.is_clicked(event.pos):
                        selected_opponent = btn.action
                if start_button.is_clicked(event.pos) and selected_opponent:
                    try:
                        n = int(board_size_input.text)
                        if n >= 4 and n % 2 == 0:
                            pygame.quit()
                            return n, selected_opponent
                    except:
                        pass
                board_size_input.handle_event(event)
            if event.type == KEYDOWN:
                board_size_input.handle_event(event)
        
        # Draw elements
        screen.blit(title_text, (100, 30))
        screen.blit(size_label, (100, 70))
        screen.blit(opponent_label, (100, 170))
        
        board_size_input.draw(screen)
        for btn in opponent_buttons:
            btn.draw(screen)
            if selected_opponent == btn.action:
                pygame.draw.rect(screen, COLORS['highlight'], btn.rect, 3)
        start_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop(n, opponent_type):
    pygame.init()
    WINDOW_WIDTH = CELL_SIZE * n + 2 * MARGIN + 200
    WINDOW_HEIGHT = CELL_SIZE * n + 2 * MARGIN
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Checkers")
    
    game = Game(n, opponent_type)
    buttons = [
        Button(WINDOW_WIDTH - 150, 50, BUTTON_WIDTH, BUTTON_HEIGHT, "New Game", 'new'),
        Button(WINDOW_WIDTH - 150, 120, BUTTON_WIDTH, BUTTON_HEIGHT, "Quit", 'quit')
    ]
    
    # Pre-render text
    font = pygame.font.Font(None, 36)
    player_turn_text_w = font.render("White's Turn", True, COLORS['text'])
    player_turn_text_b = font.render("Black's Turn", True, COLORS['text'])
    ai_thinking_text = font.render("AI thinking...", True, COLORS['text'])
    paused_text = font.render("Waiting...", True, COLORS['text'])
    game_over_font = pygame.font.Font(None, 74)
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        screen.fill(COLORS['background'])
        
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in buttons:
                    if btn.is_clicked(pos):
                        if btn.action == 'quit':
                            pygame.quit()
                            return 'quit'
                        elif btn.action == 'new':
                            pygame.quit()
                            return 'new'
                
                # Handle board clicks
                if not game.game_over and (game.current_player == 'W' or game.opponent_type == 'human'):
                    x, y = pos
                    col = (x - MARGIN) // CELL_SIZE
                    row = (y - MARGIN) // CELL_SIZE
                    if 0 <= row < n and 0 <= col < n:
                        game.handle_click(row, col)
        
        # Update animations
        game.update_animations()
        
        # AI move
        if not game.game_over and not game.animations:
            game.ai_move()
        
        # Drawing
        draw_board(screen, game)
        for btn in buttons:
            btn.draw(screen)
        
        # Draw turn indicator
        if game.ai_thinking:
            screen.blit(ai_thinking_text, (WINDOW_WIDTH - 150, 180))
        elif time.time() < game.pause_until:
            screen.blit(paused_text, (WINDOW_WIDTH - 150, 180))
        else:
            turn_text = player_turn_text_w if game.current_player == 'W' else player_turn_text_b
            screen.blit(turn_text, (WINDOW_WIDTH - 150, 180))
        
        # Game over message
        if game.game_over:
            text = game_over_font.render(f"Player {'White' if game.winner == 'W' else 'Black'} wins!", 
                                        True, COLORS['text'])
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            # Draw semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(FPS)

def start_game():
    while True:
        n, opponent = setup_screen()
        result = game_loop(n, opponent)
        if result == 'quit':
            break

if __name__ == "__main__":
    start_game()