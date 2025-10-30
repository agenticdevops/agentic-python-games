import pygame
import random
import os

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 20  # Number of cells in width/height (e.g., 600/20 = 30px per cell)
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255) # For food (note: current food color is RED)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game Speed
INITIAL_SNAKE_SPEED = 10 # Frames per second

# --- Snake Class ---
class Snake:
    def __init__(self):
        self.reset()
        self.color = GREEN

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        # Prevent turning 180 degrees (e.g., if moving right, cannot immediately turn left)
        # Check if the new direction is directly opposite the current direction
        if (self.direction[0] * -1, self.direction[1] * -1) == point:
            pass # Ignore the input if it's a direct opposite
        else:
            self.direction = point

    def move(self):
        cur = self.get_head_position()
        x_dir, y_dir = self.direction

        # Calculate new head position based on current direction and cell size
        new_head_x = cur[0] + (x_dir * CELL_SIZE)
        new_head_y = cur[1] + (y_dir * CELL_SIZE)
        new_head_pos = (new_head_x, new_head_y)

        # Wall collision check
        if not (0 <= new_head_pos[0] < SCREEN_WIDTH and 0 <= new_head_pos[1] < SCREEN_HEIGHT):
            return True # Collision with wall occurred

        # Self-collision check
        # Determine the body segments that will persist after the move.
        # If the snake is growing, all current segments remain.
        # If not growing, the last segment will be removed, so it's not a collision target.
        segments_to_check = self.positions[:] # Check against all current segments
        if not self.grow_pending:
            # If not growing, the tail is about to move, so it's not a collision point
            segments_to_check = self.positions[:-1]

        if new_head_pos in segments_to_check:
            return True # Collision with self occurred

        # If no collision, update positions
        self.positions.insert(0, new_head_pos) # Add new head at the beginning
        if not self.grow_pending:
            self.positions.pop() # Remove tail if not growing
        else:
            self.length += 1 # Increase snake length
            self.grow_pending = False # Reset flag after growing

        return False # No collision occurred

    def eat(self):
        self.score += 10 # Increase score
        self.grow_pending = True # Set flag to grow next move

    def draw(self, surface):
        # Draw each segment of the snake
        for p in self.positions:
            pygame.draw.rect(surface, self.color, (p[0], p[1], CELL_SIZE, CELL_SIZE))

    def reset(self):
        self.length = 3 # Snake starts with 3 segments

        # Calculate initial head position to be grid-aligned and roughly centered
        initial_head_x = (SCREEN_WIDTH // 2 // CELL_SIZE) * CELL_SIZE
        initial_head_y = (SCREEN_HEIGHT // 2 // CELL_SIZE) * CELL_SIZE

        self.direction = RIGHT # Default initial direction for the snake

        # Initialize positions for a 3-segment snake moving right
        self.positions = [
            (initial_head_x, initial_head_y),
            (initial_head_x - CELL_SIZE, initial_head_y),
            (initial_head_x - (2 * CELL_SIZE), initial_head_y)
        ]
        self.score = 0 # Reset score
        self.grow_pending = False # Reset growth flag


# --- Food Class ---
class Food:
    def __init__(self, snake_positions):
        self.position = (0,0) # Initialize with a dummy position
        self.color = RED # Food color
        self.spawn(snake_positions) # Spawn initial food

    def spawn(self, snake_positions):
        while True:
            # Generate random grid coordinates for food
            x = random.randrange(0, GRID_SIZE) * CELL_SIZE
            y = random.randrange(0, GRID_SIZE) * CELL_SIZE
            self.position = (x, y)
            # Ensure food does not spawn on the snake's body
            if self.position not in snake_positions:
                break # Found a valid position

    def draw(self, surface):
        # Draw the food item
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], CELL_SIZE, CELL_SIZE))

# --- High Score System ---
HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    """Loads the high score from a file."""
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                return int(f.read()) # Convert stored string to int
            except ValueError: # Handle corrupted file (non-integer content)
                return 0 # Return 0 if file content is invalid
    return 0 # Return 0 if file does not exist

def save_high_score(score):
    """Saves the high score to a file."""
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score)) # Write score as string

# --- Main Game Function ---
def main():
    pygame.init() # Initialize all imported pygame modules
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Set up the display surface
    pygame.display.set_caption("Snake Game") # Set window title
    clock = pygame.time.Clock() # Create a clock object to control frame rate

    # Fonts for text display
    font = pygame.font.Font(None, 36) # Default font, size 36 for score/instructions
    game_over_font = pygame.font.Font(None, 48) # Larger font for game over message

    high_score = load_high_score() # Load the initial high score

    snake = Snake() # Create snake object
    food = Food(snake.positions) # Create food object, ensuring it doesn't spawn on the snake

    running = True # Main loop control flag
    game_over = False # Game state flag
    current_speed = INITIAL_SNAKE_SPEED # Initialize game speed

    while running:
        for event in pygame.event.get(): # Process all events in the event queue
            if event.type == pygame.QUIT: # If the user clicks the close button
                running = False # Exit the main loop
            elif event.type == pygame.KEYDOWN: # If a key is pressed
                if game_over:
                    if event.key == pygame.K_r: # 'R' to Restart
                        snake.reset() # Reset snake state
                        food.spawn(snake.positions) # Spawn new food
                        game_over = False # Reset game over flag
                        current_speed = INITIAL_SNAKE_SPEED # Reset speed
                    elif event.key == pygame.K_q: # 'Q' to Quit
                        running = False # Exit the main loop
                else:
                    # Player controls for snake direction, ignoring 180-degree turns
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        snake.turn(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        snake.turn(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        snake.turn(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        snake.turn(RIGHT)

        if not game_over:
            # Move snake and check for collisions
            if snake.move(): # move() returns True if a collision occurred (wall or self)
                game_over = True # Set game over flag
                if snake.score > high_score: # Check for new high score
                    high_score = snake.score
                    save_high_score(high_score) # Save new high score

            # Check for food consumption
            if snake.get_head_position() == food.position:
                snake.eat() # Snake eats food
                food.spawn(snake.positions) # Spawn new food
                # Optional: Increase game speed as the snake grows
                # This adds difficulty over time. Speed increases by 1 for every 5 segments grown.
                current_speed = INITIAL_SNAKE_SPEED + (snake.length // 5) * 1

        # --- Drawing ---
        screen.fill(BLACK) # Clear screen with black background

        snake.draw(screen) # Draw the snake
        food.draw(screen) # Draw the food

        # Draw current score
        score_text = font.render(f"Score: {snake.score}", True, WHITE)
        screen.blit(score_text, (5, 5)) # Position at top-left

        # Draw high score
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        # Position high score in the top-right corner
        screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 5, 5))

        # Display "Game Over!" message if game has ended
        if game_over:
            game_over_message = game_over_font.render("Game Over!", True, RED)
            restart_message = font.render("Press 'R' to Restart or 'Q' to Quit", True, WHITE)

            # Center the messages on the screen
            game_over_rect = game_over_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            restart_rect = restart_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

            screen.blit(game_over_message, game_over_rect)
            screen.blit(restart_message, restart_rect)

        pygame.display.flip() # Update the full display Surface to the screen

        clock.tick(current_speed) # Control game speed (frames per second)

    pygame.quit() # Uninitialize pygame modules when the loop ends

if __name__ == "__main__":
    main() # Run the main game function when the script is executed
