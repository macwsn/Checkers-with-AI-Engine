import pygame
from pygame.locals import *
from heckers import *
import time

# Colors
COLORS = {
    'background': (30, 30, 30),
    'board_light': (232, 235, 239),
    'board_dark': (125, 135, 150),
    'white_piece': (255, 255, 255),
    'black_piece': (0, 0, 0),
    'highlight': (0, 255, 0),
    'button': (100, 100, 100),
    'button_text': (255, 255, 255),
    'text': (255, 255, 255),
}

# Constants
CELL_SIZE = 60
MARGIN = 5
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
FPS = 60
ANIMATION_SPEED = 0.3  # seconds for one animation
PAUSE_AFTER_MOVE = 1.0  # seconds

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = COLORS['button']
        self.text_color = COLORS['button_text']
        self.font = pygame.font.Font(None, 24)
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class TextInput:
    def __init__(self, x, y, width, height, initial_text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = initial_text
        self.active = False
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.font = pygame.font.Font(None, 32)
        self.render_text()
    
    def render_text(self):
        self.text_surf = self.font.render(self.text, True, COLORS['text'])
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.render_text()
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.text_surf, (self.rect.x + 5, self.rect.y + 5))

class AnimatedPiece:
    def __init__(self, piece_type, start_pos, end_pos, duration=ANIMATION_SPEED):
        self.piece_type = piece_type
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.start_time = time.time()
        self.is_finished = False
        
    def get_current_position(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            self.is_finished = True
            return self.end_pos
        
        # Linear interpolation
        progress = elapsed / self.duration
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        return (x, y)

def draw_board(screen, game):
    n = game.n
    # Draw board squares
    for row in range(n):
        for col in range(n):
            x = MARGIN + col * CELL_SIZE
            y = MARGIN + row * CELL_SIZE
            color = COLORS['board_light'] if (row + col) % 2 == 0 else COLORS['board_dark']
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            
    # Draw highlights
    if game.selected_piece:
        row, col = game.selected_piece
        x = MARGIN + col * CELL_SIZE
        y = MARGIN + row * CELL_SIZE
        pygame.draw.rect(screen, COLORS['highlight'], (x, y, CELL_SIZE, CELL_SIZE), 3)
        
        for (er, ec) in game.valid_moves:
            x = MARGIN + ec * CELL_SIZE
            y = MARGIN + er * CELL_SIZE
            pygame.draw.circle(screen, COLORS['highlight'], 
                              (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//4)
    
    # Create a mapping of what pieces to draw where
    pieces_to_draw = {}
    
    # Add all static pieces from the board (excluding pieces that are being animated)
    animated_positions = []
    for anim in game.animations:
        if hasattr(game, 'pending_move'):
            sr, sc, er, ec = game.pending_move[0]
            animated_positions.append((sr, sc))
            # For captures, exclude the captured piece
            if abs(er - sr) == 2 and abs(ec - sc) == 2:
                captured_row = (sr + er) // 2
                captured_col = (sc + ec) // 2
                animated_positions.append((captured_row, captured_col))
    
    # Draw static pieces
    for row in range(n):
        for col in range(n):
            if (row, col) not in animated_positions:
                piece = game.board[row][col]
                if piece != ' ':
                    pieces_to_draw[(game.piece_centers[(row, col)])] = piece
    
    # Add animated pieces
    for anim in game.animations:
        if not anim.is_finished:
            current_pos = anim.get_current_position()
            pieces_to_draw[current_pos] = anim.piece_type
    
    # Draw all pieces
    for pos, piece_type in pieces_to_draw.items():
        # Draw piece
        color = COLORS['white_piece'] if piece_type in ['W', 'WK'] else COLORS['black_piece']
        pygame.draw.circle(screen, color, pos, CELL_SIZE//3)
        
        # Draw crown for kings
        if 'K' in piece_type:
            crown_color = (255, 215, 0)
            pygame.draw.circle(screen, crown_color, pos, 8)
            pygame.draw.line(screen, crown_color, 
                           (pos[0] - 10, pos[1]),
                           (pos[0] + 10, pos[1]), 3)
            pygame.draw.line(screen, crown_color, 
                           (pos[0] - 5, pos[1] - 5),
                           (pos[0] + 5, pos[1] - 5), 3)