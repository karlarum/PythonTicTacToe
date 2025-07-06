import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Tic-Tac-Toe"

# Grid
GRID_SIZE = 3
CELL_SIZE = 150
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2 - 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Animation
ANIMATION_SPEED = 8

# X and O game pieces
class GamePiece:
    
    def __init__(self, piece_type, row, col):
        self.piece_type = piece_type
        self.row = row
        self.col = col
        
        # Animation properties
        self.current_x = -100  # Off screen
        self.current_y = -100
        self.target_x = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        self.target_y = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        self.moving = True
        self.scale = 0.1
        self.target_scale = 1.0
    
    def update(self):
        if self.moving:
            # Move pieces to their target position
            dx = self.target_x - self.current_x
            dy = self.target_y - self.current_y
            
            if abs(dx) < ANIMATION_SPEED and abs(dy) < ANIMATION_SPEED:
                self.current_x = self.target_x
                self.current_y = self.target_y
                self.moving = False
            else:
                if dx != 0:
                    self.current_x += ANIMATION_SPEED if dx > 0 else -ANIMATION_SPEED
                if dy != 0:
                    self.current_y += ANIMATION_SPEED if dy > 0 else -ANIMATION_SPEED
        
        # Growing effect
        if self.scale < self.target_scale:
            self.scale += 0.05
            if self.scale > self.target_scale:
                self.scale = self.target_scale
    
    def draw(self, screen):
        size = int(40 * self.scale)
        
        if self.piece_type == 'X':
            # Create X using two lines
            start1 = (self.current_x - size, self.current_y - size)
            end1 = (self.current_x + size, self.current_y + size)
            start2 = (self.current_x - size, self.current_y + size)
            end2 = (self.current_x + size, self.current_y - size)
            
            pygame.draw.line(screen, RED, start1, end1, int(8 * self.scale))
            pygame.draw.line(screen, RED, start2, end2, int(8 * self.scale))
        else:  # O
            # Create O using a circle
            pygame.draw.circle(screen, BLUE, 
                             (int(self.current_x), int(self.current_y)), 
                             size, int(8 * self.scale))


class TicTacToeGame:
    
    def __init__(self):
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()
        
        # Game state
        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.winning_line = None
        
        # Animated pieces list
        self.pieces = []
        
        # UI
        self.restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 50, 200, 40)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        
        # Sound
        self.setup_sounds()
        
        self.running = True
    
    def setup_sounds(self):
        # Sound effects using Pygame
        try:
            # Initialize Pygame mixer for sound
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # Soft pop sounds
            self.click_sound = self.create_pop_sound(800, 0.1, 0.3)  # Soft click
            self.win_sound = self.create_chord_sound()  # Musical chord for win
            self.tie_sound = self.create_pop_sound(400, 0.2, 0.2)   # Neutral sound for tie
            
            self.sound_enabled = True
            
        except Exception as e:
            print(f"Sound not available: {e}")
            self.sound_enabled = False
    
    def create_pop_sound(self, frequency, duration, volume):
        # Soft pop sound
        import numpy as np
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        gentle_freq = frequency * 0.3
        
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            wave = np.sin(2 * np.pi * gentle_freq * i / sample_rate)
            
            if i < frames * 0.05:
                envelope = i / (frames * 0.05)
            else:
                decay_progress = (i - frames * 0.05) / (frames * 0.95)
                envelope = np.exp(-decay_progress * 3)
            
            # Low volume so it's not too loud
            final_volume = volume * 0.25
            arr[i][0] = wave * envelope * final_volume * 32767
            arr[i][1] = wave * envelope * final_volume * 32767
        
        # Convert to pygame sound
        sound_array = arr.astype(np.int16)
        return pygame.sndarray.make_sound(sound_array)
    
    def create_chord_sound(self):
# Musical chord for win
        import numpy as np
        
        sample_rate = 22050
        duration = 0.6
        frames = int(duration * sample_rate)
        
        frequencies = [261, 329, 392] 
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            wave = 0
            for freq in frequencies:
                wave += np.sin(2 * np.pi * freq * i / sample_rate) / len(frequencies)

            if i < frames * 0.1:
                envelope = i / (frames * 0.1)
            elif i > frames * 0.5:
                envelope = (frames - i) / (frames * 0.5)
            else:
                envelope = 1.0
            
            # Low volume so it's not too loud
            final_volume = 0.2
            arr[i][0] = wave * envelope * final_volume * 32767
            arr[i][1] = wave * envelope * final_volume * 32767
        
        sound_array = arr.astype(np.int16)
        return pygame.sndarray.make_sound(sound_array)
    
    def play_sound(self, sound_type):
        # Play soft pop sound effects
        if not self.sound_enabled:
            return
            
        try:
            if sound_type == 'click' and hasattr(self, 'click_sound'):
                self.click_sound.play()
            elif sound_type == 'win' and hasattr(self, 'win_sound'):
                self.win_sound.play()
            elif sound_type == 'tie' and hasattr(self, 'tie_sound'):
                self.tie_sound.play()
        except Exception as e:
            print(f"Sound error: {e}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_click(event.pos)
    
    def handle_mouse_click(self, pos):
        mouse_x, mouse_y = pos
        
        # Check if restart button was clicked
        if self.restart_button.collidepoint(mouse_x, mouse_y):
            self.restart_game()
            return
        
        # Only process game moves if game is not over
        if self.game_over:
            return
        
        # Check if click is within the game board
        if (GRID_OFFSET_X <= mouse_x <= GRID_OFFSET_X + GRID_SIZE * CELL_SIZE and
            GRID_OFFSET_Y <= mouse_y <= GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE):
            
            # Calculate which cell was clicked
            col = int((mouse_x - GRID_OFFSET_X) // CELL_SIZE)
            row = int((mouse_y - GRID_OFFSET_Y) // CELL_SIZE)
            
            # Make sure the click is within bounds and cell is empty
            if (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and 
                self.board[row][col] == ''):
                self.make_move(row, col)
    
    def make_move(self, row, col):
        self.play_sound('click')
        
        self.board[row][col] = self.current_player
        
        piece = GamePiece(self.current_player, row, col)
        self.pieces.append(piece)
        
        # Check for win or tie
        if self.check_winner():
            self.game_over = True
            self.winner = self.current_player
            self.play_sound('win')
        elif self.is_board_full():
            self.game_over = True
            self.winner = None
            self.play_sound('tie')
        else:
            # Switch players
            self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def check_winner(self):
        # Check rows
        for row in range(GRID_SIZE):
            if (self.board[row][0] == self.board[row][1] == self.board[row][2] != ''):
                self.winning_line = ('row', row)
                return True
        
        # Check columns
        for col in range(GRID_SIZE):
            if (self.board[0][col] == self.board[1][col] == self.board[2][col] != ''):
                self.winning_line = ('col', col)
                return True
        
        # Check diagonals
        if (self.board[0][0] == self.board[1][1] == self.board[2][2] != ''):
            self.winning_line = ('diag1', None)
            return True
        
        if (self.board[0][2] == self.board[1][1] == self.board[2][0] != ''):
            self.winning_line = ('diag2', None)
            return True
        
        return False
    
    def is_board_full(self):
        # Check if the board is full
        for row in self.board:
            for cell in row:
                if cell == '':
                    return False
        return True
    
    def restart_game(self):
        # Restart the game
        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.winning_line = None
        self.pieces = []
    
    def update(self):
        for piece in self.pieces:
            piece.update()
    
    def draw_grid(self):
        # Draw vertical lines
        for i in range(1, GRID_SIZE):
            x = GRID_OFFSET_X + i * CELL_SIZE
            pygame.draw.line(self.screen, BLACK, 
                           (x, GRID_OFFSET_Y), 
                           (x, GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE), 3)
        
        # Draw horizontal lines
        for i in range(1, GRID_SIZE):
            y = GRID_OFFSET_Y + i * CELL_SIZE
            pygame.draw.line(self.screen, BLACK,
                           (GRID_OFFSET_X, y),
                           (GRID_OFFSET_X + GRID_SIZE * CELL_SIZE, y), 3)
        
        # Draw border
        pygame.draw.rect(self.screen, BLACK,
                        (GRID_OFFSET_X, GRID_OFFSET_Y, 
                         GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE), 3)
    
    def draw_pieces(self):
        for piece in self.pieces:
            piece.draw(self.screen)
    
    def draw_winning_line(self):
        # Line through the winning combination
        if not self.winning_line:
            return
        
        line_type, index = self.winning_line
        
        if line_type == 'row':
            start_x = GRID_OFFSET_X + 10
            start_y = GRID_OFFSET_Y + index * CELL_SIZE + CELL_SIZE // 2
            end_x = GRID_OFFSET_X + GRID_SIZE * CELL_SIZE - 10
            end_y = start_y
        elif line_type == 'col':
            start_x = GRID_OFFSET_X + index * CELL_SIZE + CELL_SIZE // 2
            start_y = GRID_OFFSET_Y + 10
            end_x = start_x
            end_y = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE - 10
        elif line_type == 'diag1':
            start_x = GRID_OFFSET_X + 10
            start_y = GRID_OFFSET_Y + 10
            end_x = GRID_OFFSET_X + GRID_SIZE * CELL_SIZE - 10
            end_y = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE - 10
        else:
            start_x = GRID_OFFSET_X + GRID_SIZE * CELL_SIZE - 10
            start_y = GRID_OFFSET_Y + 10
            end_x = GRID_OFFSET_X + 10
            end_y = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE - 10
        
        pygame.draw.line(self.screen, GREEN, (start_x, start_y), (end_x, end_y), 5)
    
    def draw_ui(self):
        # Game status
        if self.game_over:
            if self.winner:
                text = f"Player {self.winner} Wins!"
                color = GREEN
            else:
                text = "It's a Tie!"
                color = BLACK
        else:
            text = f"Player {self.current_player}'s Turn"
            color = BLACK
        
        text_surface = self.font_large.render(text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.screen.blit(text_surface, text_rect)
        
        # Restart button
        pygame.draw.rect(self.screen, GRAY, self.restart_button)
        pygame.draw.rect(self.screen, BLACK, self.restart_button, 2)
        
        button_text = self.font_medium.render("Restart Game", True, WHITE)
        button_text_rect = button_text.get_rect(center=self.restart_button.center)
        self.screen.blit(button_text, button_text_rect)
    
    def draw(self):
        # Clear screen
        self.screen.fill(WHITE)
        
        # Game elements
        self.draw_grid()
        self.draw_pieces()
        
        # Winning line if game is over
        if self.game_over and self.winning_line:
            self.draw_winning_line()
        
        # UI
        self.draw_ui()
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    game = TicTacToeGame()
    game.run()


if __name__ == "__main__":
    main()