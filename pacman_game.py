import pygame
import random
import sys
import math

# --- Constants ---
# Initial screen dimensions (will be adjusted based on maze)
INITIAL_SCREEN_WIDTH = 800 # Not used for actual screen setup
INITIAL_SCREEN_HEIGHT = 600 # Not used for actual screen setup
TILE_SIZE = 30 # Size of each grid cell (e.g., 30x30 pixels)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0) # For additional ghost color if needed

# Game Parameters
PACMAN_INITIAL_SPEED = 3
GHOST_INITIAL_SPEED = 2
FOOD_SCORE = 10
INITIAL_LIVES = 3
GHOST_CHANGE_DIR_PROB = 0.02 # Probability for ghost to change direction each frame (per update)
DEATH_PAUSE_MS = 1000 # Milliseconds to pause after Pacman loses a life

# Maze Layouts for different levels
# W: Wall, F: Food, P: Pacman Start, G: Ghost Start, S: Empty Space
LEVEL_MAPS = [
    [ # Level 1
        "WWWWWWWWWWWWWWWWWWWWWWWWW",
        "WFFFFFFFFFFFFF W W W FFFW",
        "WF W W W F W W W W W F WFW",
        "W F W F F F F F W F F W F W",
        "W W W W W W W W W W W W W W",
        "W F F F F F F F F F F F F W",
        "W W W W W W W W W W W W W W",
        "W F W F W W W W W W W F W F W",
        "WPW W F W G W W W G W F W WFW",
        "W F W F W W W W W W W F W F W",
        "W W W W W W W W W W W W W W",
        "W F F F F F F F F F F F F W",
        "WWWWWWWWWWWWWWWWWWWWWWWWW"
    ],
    [ # Level 2
        "WWWWWWWWWWWWWWWWWWWWWWWWW",
        "WFFFFFFFFFFFFFFFFFFFFFFFFW",
        "WF W F W F W F W F W F WFW",
        "W F F F F F F F F F F F F W",
        "W W W W W W W W W W W W W W",
        "W F W F W F W F W F W F W F W",
        "W W W W W W W W W W W W W W",
        "W F W F W F W F W F W F W F W",
        "WPW G W G W G W G W G W G WFW",
        "W F W F W F W F W F W F W F W",
        "W W W W W W W W W W W W W W",
        "WFFFFFFFFFFFFFFFFFFFFFFFFW",
        "WWWWWWWWWWWWWWWWWWWWWWWWW"
    ],
    [ # Level 3 (More complex walls, fewer open paths)
        "WWWWWWWWWWWWWWWWWWWWWWWWW",
        "WFFFFFFFFF W F W FFFFFFFF W",
        "WF W W W F W F W F W W W F W",
        "W F W F W F W F W F W F W F W",
        "W W W W W W W W W W W W W W",
        "W F W F F F W F F F W F F F W",
        "W W W W W W W W W W W W W W",
        "W F W F W F W F W F W F W F W",
        "WPW G W G W G W G W G W G WFW",
        "W F W F W F W F W F W F W F W",
        "W W W W W W W W W W W W W W",
        "W FFFFFFFFF W F W FFFFFFFFF W",
        "WWWWWWWWWWWWWWWWWWWWWWWWW"
    ]
]

# Calculate actual screen width/height based on maze and tile size
# Note: This assumes all levels have the same dimensions as LEVEL_MAPS[0].
# If levels could vary in size, SCREEN_WIDTH/HEIGHT would need to be recalculated in load_level.
MAP_WIDTH = len(LEVEL_MAPS[0][0])
MAP_HEIGHT = len(LEVEL_MAPS[0])
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# --- Game Classes ---

class Entity(pygame.sprite.Sprite):
    """Base class for Pacman and Ghosts."""
    def __init__(self, game, x, y, color, speed, size_factor=0.8):
        super().__init__()
        self.game = game
        self.grid_x = x
        self.grid_y = y
        self.speed = speed
        self.direction = STOP
        self.color = color

        # Pixel position (center of the entity)
        self.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2

        self.size = int(TILE_SIZE * size_factor)
        # Create a transparent surface for drawing, allows custom shapes
        self.image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def get_grid_pos(self):
        """Returns the current grid cell (column, row) the entity is in."""
        return (int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))

    def can_move_in_direction(self, direction):
        """Checks if the entity can move one step in the given direction without hitting a wall."""
        if direction == STOP:
            return True # Can always "move" (stay still)

        # Predict the next center position
        predicted_x = self.x + direction[0] * self.speed
        predicted_y = self.y + direction[1] * self.speed

        # Create a temporary rectangle for the predicted position
        # This is more robust than just checking the center point
        temp_rect = pygame.Rect(0, 0, self.size, self.size)
        temp_rect.center = (int(predicted_x), int(predicted_y))

        # Check if any corner of the predicted rectangle would collide with a wall
        for wall_rect in self.game.walls:
            if temp_rect.colliderect(wall_rect):
                return False
        return True

    def update(self):
        """Placeholder for update logic, to be overridden by subclasses."""
        pass

    def draw(self, screen):
        """Placeholder for draw logic, to be overridden by subclasses."""
        screen.blit(self.image, self.rect)


class Pacman(Entity):
    """Represents the Pacman player character."""
    def __init__(self, game, x, y):
        super().__init__(game, x, y, YELLOW, PACMAN_INITIAL_SPEED, size_factor=0.8)
        self.lives = INITIAL_LIVES
        self.score = 0
        self.open_mouth = True
        self.mouth_timer = 0
        self.mouth_speed = 5 # frames per mouth state change
        self.pacman_speed_multiplier = 1.0
        self.next_direction = STOP # Buffered input for smoother turns

    def reset_position(self):
        """Resets Pacman to its starting position for the current level."""
        self.grid_x, self.grid_y = self.game.pacman_start_pos
        self.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
        self.rect.center = (int(self.x), int(self.y))
        self.direction = STOP
        self.next_direction = STOP

    def change_direction(self, new_direction):
        """Sets the next desired direction for Pacman."""
        self.next_direction = new_direction

    def update(self):
        """Updates Pacman's position and animation."""
        current_speed = self.speed * self.pacman_speed_multiplier

        # Try to move in next_direction first (buffered input)
        if self.next_direction != STOP and self.can_move_in_direction(self.next_direction):
            self.direction = self.next_direction
            self.next_direction = STOP # Clear buffered direction once applied

        # If current direction is STOP and a new direction is buffered, try to apply it
        # This happens if pacman hit a wall and then a new direction was pressed
        if self.direction == STOP and self.next_direction != STOP and self.can_move_in_direction(self.next_direction):
            self.direction = self.next_direction
            self.next_direction = STOP

        # If current direction leads to a wall, stop
        if not self.can_move_in_direction(self.direction):
            self.direction = STOP
            # If Pacman is truly stuck and can't move, clear buffered direction too
            if not self.can_move_in_direction(self.next_direction):
                self.next_direction = STOP

        # Apply movement
        self.x += self.direction[0] * current_speed
        self.y += self.direction[1] * current_speed
        self.rect.center = (int(self.x), int(self.y))

        # Mouth animation
        self.mouth_timer += 1
        if self.mouth_timer >= self.mouth_speed:
            self.open_mouth = not self.open_mouth
            self.mouth_timer = 0

    def draw(self, screen):
        """Draws Pacman on the screen, including mouth animation."""
        radius = self.size // 2
        center_x, center_y = self.rect.center

        if self.open_mouth and self.direction != STOP:
            # Draw the full circle body
            pygame.draw.circle(screen, self.color, (center_x, center_y), radius)

            # Define the mouth opening using angles (in radians)
            # These angles define the 'cut-out' part of the mouth.
            mouth_angle_start_rad = 0
            mouth_angle_end_rad = 0

            if self.direction == RIGHT:
                mouth_angle_start_rad = math.radians(315) # -45 degrees
                mouth_angle_end_rad = math.radians(45)
            elif self.direction == LEFT:
                mouth_angle_start_rad = math.radians(135)
                mouth_angle_end_rad = math.radians(225)
            elif self.direction == UP:
                mouth_angle_start_rad = math.radians(225)
                mouth_angle_end_rad = math.radians(315)
            elif self.direction == DOWN:
                mouth_angle_start_rad = math.radians(45)
                mouth_angle_end_rad = math.radians(135)

            # Points for the mouth triangle (drawn in background color to "cut out" the mouth)
            p_center = (center_x, center_y)
            p_mouth_edge1 = (center_x + radius * math.cos(mouth_angle_start_rad),
                             center_y + radius * math.sin(mouth_angle_start_rad))
            p_mouth_edge2 = (center_x + radius * math.cos(mouth_angle_end_rad),
                             center_y + radius * math.sin(mouth_angle_end_rad))

            pygame.draw.polygon(screen, BLACK, [p_center, p_mouth_edge1, p_mouth_edge2])
        else:
            pygame.draw.circle(screen, self.color, (center_x, center_y), radius)


class Ghost(Entity):
    """Represents a Ghost enemy."""
    def __init__(self, game, x, y, color):
        super().__init__(game, x, y, color, GHOST_INITIAL_SPEED, size_factor=0.7)
        self.initial_grid_pos = (x, y)
        self.ghost_speed_multiplier = 1.0
        self.random_direction() # Start moving immediately

    def reset_position(self):
        """Resets the ghost to its initial position for the current level."""
        self.grid_x, self.grid_y = self.initial_grid_pos
        self.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
        self.rect.center = (int(self.x), int(self.y))
        self.direction = STOP
        self.random_direction()

    def random_direction(self):
        """Chooses a random valid direction for the ghost to move."""
        possible_directions = [UP, DOWN, LEFT, RIGHT]
        valid_directions = []

        for d in possible_directions:
            # Avoid immediately reversing direction unless there's no other choice.
            # The 'if valid_directions' and 'elif self.can_move_in_direction'
            # handles the case where reverse is the only option.
            if d == (-self.direction[0], -self.direction[1]):
                # Temporarily skip reverse if other valid directions might exist.
                # If after checking all others, no valid directions are found,
                # the 'elif' block below will allow reversing.
                continue
            if self.can_move_in_direction(d):
                valid_directions.append(d)

        if valid_directions:
            self.direction = random.choice(valid_directions)
        elif self.can_move_in_direction((-self.direction[0], -self.direction[1])): # If no other choice, reverse
            self.direction = (-self.direction[0], -self.direction[1])
        else: # Stuck
            self.direction = STOP

    def update(self):
        """Updates the ghost's position and AI."""
        current_speed = self.speed * self.ghost_speed_multiplier

        # Ghosts try to align with grid for better movement and decision making
        current_grid_x, current_grid_y = self.get_grid_pos()
        target_center_x = current_grid_x * TILE_SIZE + TILE_SIZE // 2
        target_center_y = current_grid_y * TILE_SIZE + TILE_SIZE // 2

        # Check if ghost is close to the center of a tile
        is_aligned_x = abs(self.x - target_center_x) < current_speed + 1
        is_aligned_y = abs(self.y - target_center_y) < current_speed + 1

        # If at an intersection or random chance, change direction
        if (is_aligned_x and is_aligned_y) or random.random() < GHOST_CHANGE_DIR_PROB:
            self.random_direction()

        # If current direction leads to a wall, find a new one
        if not self.can_move_in_direction(self.direction):
            self.random_direction()

        # Move
        self.x += self.direction[0] * current_speed
        self.y += self.direction[1] * current_speed
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, screen):
        """Draws the ghost on the screen with custom shape and eyes."""
        radius = self.size // 2
        center_x, center_y = self.rect.center

        # Body (circle on top, rectangle below)
        # The circle's center is adjusted to sit on top of the rectangle
        circle_center_for_ghost = (center_x, center_y - radius // 2)
        pygame.draw.circle(screen, self.color, circle_center_for_ghost, radius)
        pygame.draw.rect(screen, self.color, (center_x - radius, center_y - radius // 2, self.size, radius + radius // 2))

        # Skirt (scalloped bottom)
        num_scallops = 3
        scallop_width = self.size / num_scallops
        scallop_radius = scallop_width / 2
        for i in range(num_scallops):
            x_pos = center_x - radius + (i * scallop_width) + scallop_radius
            pygame.draw.circle(screen, self.color, (int(x_pos), center_y + radius // 2), int(scallop_radius))

        # Eyes (white circles with black pupils)
        eye_radius = radius // 4
        pupil_radius = radius // 8

        # Determine pupil offset based on ghost's current direction
        pupil_offset_x = self.direction[0] * pupil_radius
        pupil_offset_y = self.direction[1] * pupil_radius

        # Left Eye
        pygame.draw.circle(screen, WHITE, (center_x - radius // 2, center_y - radius // 2), eye_radius)
        pygame.draw.circle(screen, BLACK, (center_x - radius // 2 + pupil_offset_x,
                                          center_y - radius // 2 + pupil_offset_y), pupil_radius)
        # Right Eye
        pygame.draw.circle(screen, WHITE, (center_x + radius // 2, center_y - radius // 2), eye_radius)
        pygame.draw.circle(screen, BLACK, (center_x + radius // 2 + pupil_offset_x,
                                          center_y + radius // 2 + pupil_offset_y), pupil_radius)


class Game:
    """Manages the overall game state, levels, and interactions."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.game_over = False
        self.level_complete_screen = False

        self.pacman = None
        self.ghosts = []
        self.food_dots = []
        self.walls = []

        self.current_level_index = 0
        self.current_level_map = []
        self.pacman_start_pos = (0, 0)
        self.ghost_start_positions = []
        self.total_food_this_level = 0
        self.food_eaten_this_level = 0

        self.load_level(self.current_level_index)

    def load_level(self, level_index):
        """Loads a new level based on its index, sets up game elements."""
        if level_index >= len(LEVEL_MAPS):
            self.game_over = True # All levels completed, game won
            print("Congratulations! You completed all levels!")
            return

        self.current_level_map = LEVEL_MAPS[level_index]
        self.walls = []
        self.food_dots = []
        self.ghost_start_positions = []
        self.total_food_this_level = 0
        self.food_eaten_this_level = 0

        # Initialize or update Pacman
        if self.pacman:
            self.pacman.pacman_speed_multiplier = 1.0 + level_index * 0.2 # Increase speed each level
            self.pacman.direction = STOP
            self.pacman.next_direction = STOP
        else:
            self.pacman = Pacman(self, 0, 0) # Temporary position, will be set by map parsing

        self.ghosts = [] # Clear existing ghosts

        # Define ghost colors - more levels could cycle through more colors or repeat
        ghost_colors = [RED, ORANGE, PINK, CYAN, GREEN]

        for y, row in enumerate(self.current_level_map):
            for x, char in enumerate(row):
                if char == 'W':
                    self.walls.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif char == 'F':
                    self.food_dots.append(pygame.Rect(x * TILE_SIZE + TILE_SIZE // 2 - 3, # Center food dot
                                                      y * TILE_SIZE + TILE_SIZE // 2 - 3, 6, 6)) # 6x6 pixel dot
                    self.total_food_this_level += 1
                elif char == 'P':
                    self.pacman_start_pos = (x, y)
                elif char == 'G':
                    self.ghost_start_positions.append((x, y))

        # Set Pacman's actual starting position and reset state
        self.pacman.grid_x, self.pacman.grid_y = self.pacman_start_pos
        self.pacman.x = self.pacman.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.pacman.y = self.pacman.grid_y * TILE_SIZE + TILE_SIZE // 2
        self.pacman.rect.center = (int(self.pacman.x), int(self.pacman.y))

        # Create ghosts based on start positions and level number
        # Increase number of ghosts for higher levels, but don't exceed available start positions
        num_ghosts_to_spawn = min(len(self.ghost_start_positions), 2 + level_index)

        for i in range(num_ghosts_to_spawn):
            g_x, g_y = self.ghost_start_positions[i % len(self.ghost_start_positions)] # Cycle through ghost start positions
            color_index = i % len(ghost_colors)
            ghost = Ghost(self, g_x, g_y, ghost_colors[color_index])
            ghost.ghost_speed_multiplier = 1.0 + level_index * 0.1 # Ghosts also get faster each level
            self.ghosts.append(ghost)

        print(f"Level {self.current_level_index + 1} loaded with {self.total_food_this_level} food dots and {len(self.ghosts)} ghosts.")
        self.level_complete_screen = False # Reset flag for level transition

    def reset_game_state(self):
        """Resets the entire game for a new playthrough."""
        self.pacman.score = 0
        self.pacman.lives = INITIAL_LIVES
        self.current_level_index = 0
        self.game_over = False
        self.load_level(self.current_level_index)

    def reset_after_death(self):
        """Resets Pacman and ghosts to their starting positions after Pacman loses a life."""
        self.pacman.reset_position()
        for ghost in self.ghosts:
            ghost.reset_position()
        pygame.time.wait(DEATH_PAUSE_MS) # Pause briefly after death

    def handle_input(self):
        """Processes user input (keyboard events)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r: # Restart game
                        self.reset_game_state()
                    elif event.key == pygame.K_q: # Quit game
                        self.running = False
                elif self.level_complete_screen:
                    if event.key == pygame.K_SPACE:
                        self.current_level_index += 1
                        self.load_level(self.current_level_index)
                    elif event.key == pygame.K_q:
                        self.running = False
                else: # Game is active
                    if event.key == pygame.K_LEFT:
                        self.pacman.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.pacman.change_direction(RIGHT)
                    elif event.key == pygame.K_UP:
                        self.pacman.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.pacman.change_direction(DOWN)
                    elif event.key == pygame.K_q: # Quit mid-game
                        self.running = False

    def update(self):
        """Updates all game objects and checks for collisions and game state changes."""
        if self.game_over or self.level_complete_screen:
            return # Don't update game logic if game over or level complete screen is active

        self.pacman.update()
        for ghost in self.ghosts:
            ghost.update()

        # Pacman eats food
        food_eaten_indices = []
        for i, food_rect in enumerate(self.food_dots):
            if self.pacman.rect.colliderect(food_rect):
                food_eaten_indices.append(i)
                self.pacman.score += FOOD_SCORE
                self.food_eaten_this_level += 1

        # Remove eaten food dots (iterate backwards to avoid index issues if multiple eaten in one frame)
        for i in sorted(food_eaten_indices, reverse=True):
            del self.food_dots[i]

        # Pacman-Ghost collision
        for ghost in self.ghosts:
            if self.pacman.rect.colliderect(ghost.rect):
                self.pacman.lives -= 1
                if self.pacman.lives <= 0:
                    self.game_over = True
                else:
                    print(f"Pacman hit a ghost! Lives remaining: {self.pacman.lives}")
                    self.reset_after_death()
                break # Only lose one life per collision event

        # Check for level completion
        if self.food_eaten_this_level >= self.total_food_this_level and self.total_food_this_level > 0:
            self.level_complete_screen = True
            print(f"Level {self.current_level_index + 1} complete!")

    def draw(self):
        """Draws all game elements on the screen."""
        self.screen.fill(BLACK)

        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(self.screen, BLUE, wall)

        # Draw food dots
        for food_rect in self.food_dots:
            pygame.draw.circle(self.screen, WHITE, food_rect.center, food_rect.width // 2)

        # Draw Pacman
        self.pacman.draw(self.screen)

        # Draw Ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen)

        # Draw score, lives, and current level
        score_text = self.font.render(f"Score: {self.pacman.score}", True, WHITE)
        self.screen.blit(score_text, (TILE_SIZE // 2, 5))

        lives_text = self.font.render(f"Lives: {self.pacman.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - TILE_SIZE // 2, 5))

        level_text = self.font.render(f"Level: {self.current_level_index + 1}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 5))


        # Display Game Over or Level Complete messages
        if self.game_over:
            # If all levels completed
            if self.current_level_index >= len(LEVEL_MAPS):
                final_message_text = self.font.render("YOU WON! ALL LEVELS COMPLETED!", True, YELLOW)
            else: # Standard game over
                final_message_text = self.font.render("GAME OVER!", True, RED)

            restart_text = self.font.render("Press 'R' to Restart or 'Q' to Quit", True, WHITE)

            self.screen.blit(final_message_text, (SCREEN_WIDTH // 2 - final_message_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        if self.level_complete_screen:
            next_level_text = self.font.render(f"LEVEL {self.current_level_index + 1} COMPLETE!", True, YELLOW)
            continue_text = self.font.render("Press SPACE for Next Level or 'Q' to Quit", True, WHITE)
            self.screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))


        pygame.display.flip() # Update the full display Surface to the screen

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60) # Control frame rate to 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
