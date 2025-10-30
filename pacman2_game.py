import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 20 # Size of each grid cell

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

# Game States
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_LEVEL_COMPLETE = 3

# Game FPS - controls how often update is called (ticks per second)
GAME_FPS = 10

# Maze Definition (40x30 grid, (SCREEN_WIDTH/TILE_SIZE) x (SCREEN_HEIGHT/TILE_SIZE))
MAZE_GRID = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1],
    [1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,1],
    [1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,0,1,1,0,1,1,0,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,0,1,1,0,1,1,0,1,1,1,1,0,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,0,1,1,1,0,1],
    [1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]
MAZE_ROWS = len(MAZE_GRID)
MAZE_COLS = len(MAZE_GRID[0])

# Starting positions for Pacman and Ghosts (grid coordinates (col, row))
PACMAN_START_GRID_POS = (1, 1)
GHOST_START_GRID_POS = (MAZE_COLS // 2, MAZE_ROWS // 2)

# --- Classes ---

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size, speed_tiles_per_sec):
        super().__init__()
        self.size = size
        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.color = color

        self.grid_x = x
        self.grid_y = y
        # Center the entity within its tile
        self.rect.topleft = (x * TILE_SIZE + (TILE_SIZE - size) // 2, y * TILE_SIZE + (TILE_SIZE - size) // 2)

        self.dx = 0 # current direction x
        self.dy = 0 # current direction y

        # Speed handling: determines how many game ticks before the entity moves one tile
        # move_interval_ticks = GAME_FPS / speed_tiles_per_sec
        # Example: if GAME_FPS=10 and speed_tiles_per_sec=5, then move_interval_ticks = 2.
        # Entity moves every 2 game ticks.
        self.speed_tiles_per_sec = speed_tiles_per_sec
        # Ensure that if speed_tiles_per_sec is higher than GAME_FPS, it still moves every tick or faster
        if speed_tiles_per_sec > 0:
            self.move_interval_ticks = max(1, round(GAME_FPS / speed_tiles_per_sec))
        else: # If speed is 0, it never moves, set interval to effectively infinite
            self.move_interval_ticks = float('inf')
        self.move_tick_counter = 0 # Counts ticks until next move

    def set_direction(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def get_grid_pos(self):
        return self.grid_x, self.grid_y

    def set_grid_pos(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.rect.topleft = (x * TILE_SIZE + (TILE_SIZE - self.size) // 2, y * TILE_SIZE + (TILE_SIZE - self.size) // 2)

    def can_move_to(self, next_grid_x, next_grid_y, maze):
        if 0 <= next_grid_x < MAZE_COLS and 0 <= next_grid_y < MAZE_ROWS:
            return maze[next_grid_y][next_grid_x] == 0 # 0 means path, 1 means wall
        return False

    def update_position(self, maze):
        # Only move if enough ticks have passed
        self.move_tick_counter += 1
        if self.move_interval_ticks == float('inf') or self.move_tick_counter < self.move_interval_ticks:
            return False # Not time to move yet or entity is stationary

        self.move_tick_counter = 0 # Reset counter for next move

        if self.dx == 0 and self.dy == 0: # If not trying to move
            return False

        next_grid_x = self.grid_x + self.dx
        next_grid_y = self.grid_y + self.dy

        if self.can_move_to(next_grid_x, next_grid_y, maze):
            self.set_grid_pos(next_grid_x, next_grid_y)
            return True # Moved successfully
        return False # Could not move (hit a wall)


class Pacman(Entity):
    def __init__(self, x, y, speed_tiles_per_sec):
        super().__init__(x, y, YELLOW, TILE_SIZE - 4, speed_tiles_per_sec)
        self.lives = 3
        self.score = 0
        self.current_direction = (0, 0) # (dx, dy) - direction currently moving in
        self.next_direction = (0, 0) # (dx, dy) - queued direction from input

    def reset_position(self, start_x, start_y):
        self.set_grid_pos(start_x, start_y)
        self.dx = 0
        self.dy = 0
        self.current_direction = (0,0)
        self.next_direction = (0,0)
        self.move_tick_counter = 0 # Reset movement timing

    def set_direction(self, dx, dy):
        self.next_direction = (dx, dy)

    def update(self, maze):
        # 1. Try to initiate a turn from `next_direction`
        if self.next_direction != (0,0):
            next_grid_x_turn = self.grid_x + self.next_direction[0]
            next_grid_y_turn = self.grid_y + self.next_direction[1]
            if self.can_move_to(next_grid_x_turn, next_grid_y_turn, maze):
                self.current_direction = self.next_direction
                self.next_direction = (0,0) # Consume the queued direction

        # 2. Set the actual movement direction for update_position
        self.dx, self.dy = self.current_direction

        # 3. Attempt to move
        moved = self.update_position(maze) # This handles the actual grid movement based on speed

        # 4. If not moved (hit a wall) and was trying to move, stop
        if not moved and self.current_direction != (0,0):
            # Check if current direction is actually blocked
            next_grid_x_check = self.grid_x + self.current_direction[0]
            next_grid_y_check = self.grid_y + self.current_direction[1]
            if not self.can_move_to(next_grid_x_check, next_grid_y_check, maze):
                self.dx = 0
                self.dy = 0
                self.current_direction = (0,0) # Stop if blocked
                self.next_direction = (0,0) # Clear any pending turn


class Ghost(Entity):
    def __init__(self, x, y, speed_tiles_per_sec, color):
        super().__init__(x, y, color, TILE_SIZE - 4, speed_tiles_per_sec)
        self.scatter_target = (1, 1) # A fixed corner for scatter mode (grid coords)
        self.state = "scatter" # "scatter", "chase"
        self.state_timer = 0
        self.scatter_time = 7 * GAME_FPS # 7 seconds in ticks
        self.chase_time = 20 * GAME_FPS # 20 seconds in ticks
        self.reset_direction() # Set an initial random direction

    def reset_position(self, start_x, start_y):
        self.set_grid_pos(start_x, start_y)
        self.reset_direction()
        self.state = "scatter"
        self.state_timer = 0
        self.move_tick_counter = 0 # Reset movement timing

    def reset_direction(self):
        # Pick a random initial direction
        possible_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        self.dx, self.dy = random.choice(possible_directions)

    def update_state(self):
        self.state_timer += 1
        if self.state == "scatter" and self.state_timer >= self.scatter_time:
            self.state = "chase"
            self.state_timer = 0
        elif self.state == "chase" and self.state_timer >= self.chase_time:
            self.state = "scatter"
            self.state_timer = 0

    def calculate_next_move(self, maze, pacman_pos):
        self.update_state()

        target_x, target_y = self.scatter_target
        if self.state == "chase":
            target_x, target_y = pacman_pos

        current_x, current_y = self.grid_x, self.grid_y
        best_direction = (self.dx, self.dy) # Default to current direction if no better option
        min_distance = float('inf')

        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        opposite_direction = (-self.dx, -self.dy)

        # Shuffle to add some randomness when multiple paths are equally good
        random.shuffle(possible_moves)

        # Prioritize moves that reduce distance to target and are not immediately reversing
        for move_dx, move_dy in possible_moves:
            if (move_dx, move_dy) == opposite_direction:
                continue # Ghosts generally avoid reversing unless necessary

            next_x, next_y = current_x + move_dx, current_y + move_dy

            if self.can_move_to(next_x, next_y, maze):
                distance = math.hypot(next_x - target_x, next_y - target_y)
                if distance < min_distance:
                    min_distance = distance
                    best_direction = (move_dx, move_dy)

        # If no non-reversing valid moves were found (e.g., at a dead end or junction where only reverse is valid)
        if min_distance == float('inf'):
            valid_moves = []
            for move_dx, move_dy in possible_moves: # Re-check all moves including reverse
                 next_x, next_y = current_x + move_dx, current_y + move_dy
                 if self.can_move_to(next_x, next_y, maze):
                     valid_moves.append((move_dx, move_dy))
            if valid_moves:
                best_direction = random.choice(valid_moves) # Pick any valid move if stuck
            else:
                best_direction = (0,0) # Completely stuck, stop moving

        self.dx, self.dy = best_direction

    def update(self, maze, pacman_pos):
        # Calculate next move based on AI only when it's time for the ghost to move
        if self.move_tick_counter == 0:
            self.calculate_next_move(maze, pacman_pos)

        self.update_position(maze) # This handles the actual grid movement based on speed


class FoodDot:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        # Rect for drawing, actual collision is grid-based
        self.rect = pygame.Rect(x * TILE_SIZE + TILE_SIZE // 2 - 2,
                                y * TILE_SIZE + TILE_SIZE // 2 - 2,
                                4, 4)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, self.rect.center, 2)


# --- Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.game_state = GAME_STATE_MENU
        self.running = True
        self.maze = MAZE_GRID

        self.pacman = None
        self.ghosts = []
        self.food_dots = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.ghost_colors = [RED, PINK, CYAN, ORANGE] # Distinct colors for ghosts

        self.pacman_base_speed = 5 # tiles per second
        self.ghost_base_speed = 4 # tiles per second

        # --- New Ghost Spawning Configuration Parameters (in game ticks) ---
        self.max_active_ghosts = 4 # Maximum number of ghosts allowed on screen at once
        self.ghost_spawn_interval_min = 5 * GAME_FPS # Minimum time (ticks) between dynamic ghost spawns (5 seconds)
        self.ghost_spawn_interval_max = 15 * GAME_FPS # Maximum time (ticks) between dynamic ghost spawns (15 seconds)
        self.time_to_next_ghost_spawn = 0 # Timer for the next dynamic ghost spawn (in ticks)

        # Identify ghost spawn points. For now, use GHOST_START_GRID_POS and can add more.
        # This list can be expanded to include other strategic path tiles if desired.
        self.ghost_spawn_points = [GHOST_START_GRID_POS]

        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.setup_level()

    def setup_level(self):
        # Pacman speed increases by 1 tile/sec per level
        pacman_current_speed = self.pacman_base_speed + (self.level - 1) * 1
        self.pacman = Pacman(PACMAN_START_GRID_POS[0], PACMAN_START_GRID_POS[1], pacman_current_speed)
        self.pacman.lives = self.lives # Carry over lives from previous level
        self.pacman.score = self.score # Carry over score from previous level

        self.ghosts = []
        # Number of ghosts increases by 1 per level, up to self.max_active_ghosts
        num_initial_ghosts = min(self.level + 1, self.max_active_ghosts)
        # Ghost speed also increases slightly per level
        ghost_current_speed = self.ghost_base_speed + (self.level - 1) * 0.5
        for i in range(num_initial_ghosts):
            color = self.ghost_colors[i % len(self.ghost_colors)]
            # Spawn initial ghosts at GHOST_START_GRID_POS
            ghost = Ghost(GHOST_START_GRID_POS[0], GHOST_START_GRID_POS[1], ghost_current_speed, color)
            self.ghosts.append(ghost)

        # Initialize the timer for the *first* dynamic ghost spawn in this level
        self.time_to_next_ghost_spawn = random.uniform(
            self.ghost_spawn_interval_min,
            self.ghost_spawn_interval_max
        )

        self.generate_food()
        self.game_state = GAME_STATE_PLAYING

    def _spawn_ghost(self):
        """
        Attempts to spawn a new ghost if the maximum active ghost limit hasn't been reached.
        Chooses a random spawn point and resets the spawn timer.
        """
        if len(self.ghosts) < self.max_active_ghosts:
            if not self.ghost_spawn_points:
                # Fallback if no specific spawn points are defined
                spawn_x, spawn_y = GHOST_START_GRID_POS
            else:
                # Choose a random spawn point from the list of available points
                spawn_x, spawn_y = random.choice(self.ghost_spawn_points)

            # Check if the chosen spawn point is currently free from other ghosts
            # This prevents multiple ghosts from spawning on the exact same tile.
            is_spawn_point_clear = True
            for ghost in self.ghosts:
                if (ghost.grid_x, ghost.grid_y) == (spawn_x, spawn_y):
                    is_spawn_point_clear = False
                    break

            if is_spawn_point_clear:
                # Ghost speed increases slightly per level
                ghost_current_speed = self.ghost_base_speed + (self.level - 1) * 0.5
                color = self.ghost_colors[len(self.ghosts) % len(self.ghost_colors)] # Cycle colors for new ghosts
                new_ghost = Ghost(spawn_x, spawn_y, ghost_current_speed, color)
                self.ghosts.append(new_ghost)

        # Reset the timer for the *next* dynamic ghost spawn, regardless if one was spawned
        self.time_to_next_ghost_spawn = random.uniform(
            self.ghost_spawn_interval_min,
            self.ghost_spawn_interval_max
        )


    def generate_food(self):
        self.food_dots = []
        for r in range(MAZE_ROWS):
            for c in range(MAZE_COLS):
                if self.maze[r][c] == 0: # If it's a path
                    # Don't place food at Pacman's start position or any ghost spawn points
                    if (c, r) != PACMAN_START_GRID_POS and (c, r) not in self.ghost_spawn_points:
                        self.food_dots.append(FoodDot(c, r))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_state == GAME_STATE_MENU:
                    if event.key == pygame.K_RETURN:
                        self.game_state = GAME_STATE_PLAYING
                elif self.game_state == GAME_STATE_GAME_OVER or self.game_state == GAME_STATE_LEVEL_COMPLETE:
                    if event.key == pygame.K_r: # Restart game or advance level
                        if self.game_state == GAME_STATE_LEVEL_COMPLETE:
                            # Advance to next level, keeping score and lives
                            self.setup_level()
                        else: # GAME_OVER
                            self.reset_game() # Reset everything
                    if event.key == pygame.K_q: # Quit
                        self.running = False
                elif self.game_state == GAME_STATE_PLAYING:
                    if event.key == pygame.K_LEFT:
                        self.pacman.set_direction(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.pacman.set_direction(1, 0)
                    elif event.key == pygame.K_UP:
                        self.pacman.set_direction(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.pacman.set_direction(0, 1)

    def update(self):
        if self.game_state != GAME_STATE_PLAYING:
            return

        # Update Pacman
        self.pacman.update(self.maze)

        # Update Ghosts
        pacman_grid_pos = self.pacman.get_grid_pos()
        for ghost in self.ghosts:
            ghost.update(self.maze, pacman_grid_pos)

        # --- Dynamic Ghost Spawning Logic ---
        self.time_to_next_ghost_spawn -= 1 # Decrement by 1 game tick
        if self.time_to_next_ghost_spawn <= 0:
            self._spawn_ghost()

        # Check Pacman-Food collision (grid-based)
        food_eaten = []
        for food in self.food_dots:
            if self.pacman.get_grid_pos() == (food.grid_x, food.grid_y):
                food_eaten.append(food)
                self.score += 10 # Each food dot gives 10 points
                self.pacman.score = self.score # Update pacman's internal score too

        for food in food_eaten:
            self.food_dots.remove(food)

        # Check Pacman-Ghost collision (grid-based)
        for ghost in self.ghosts:
            if self.pacman.get_grid_pos() == ghost.get_grid_pos():
                self.pacman.lives -= 1
                self.lives = self.pacman.lives # Update game's lives
                if self.pacman.lives <= 0:
                    self.game_state = GAME_STATE_GAME_OVER
                else:
                    # Reset Pacman and Ghosts to start positions after losing a life
                    self.pacman.reset_position(PACMAN_START_GRID_POS[0], PACMAN_START_GRID_POS[1])
                    for g in self.ghosts:
                        g.reset_position(GHOST_START_GRID_POS[0], GHOST_START_GRID_POS[1])
                break # Only lose one life per collision event

        # Check for level complete
        if not self.food_dots:
            self.level += 1
            self.game_state = GAME_STATE_LEVEL_COMPLETE
            # The actual setup for the next level will happen when 'R' is pressed from GAME_STATE_LEVEL_COMPLETE

    def draw(self):
        self.screen.fill(BLACK)

        # Draw Maze walls
        for r in range(MAZE_ROWS):
            for c in range(MAZE_COLS):
                if self.maze[r][c] == 1: # Wall
                    pygame.draw.rect(self.screen, BLUE, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Draw Food dots
        for food in self.food_dots:
            food.draw(self.screen)

        # Draw Pacman
        if self.pacman:
            pygame.draw.circle(self.screen, self.pacman.color, self.pacman.rect.center, self.pacman.size // 2)

        # Draw Ghosts
        for ghost in self.ghosts:
            pygame.draw.circle(self.screen, ghost.color, ghost.rect.center, ghost.size // 2)

        # Draw Score, Lives, Level HUD
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_text, (5, SCREEN_HEIGHT - 40))
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 5, SCREEN_HEIGHT - 40))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT - 40))


        # Draw Game State Overlays (Menu, Game Over, Level Complete)
        if self.game_state == GAME_STATE_MENU:
            title_text = self.font.render("Pacman", True, YELLOW)
            start_text = self.small_font.render("Press ENTER to Start", True, WHITE)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        elif self.game_state == GAME_STATE_GAME_OVER:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.small_font.render("Press 'R' to Restart or 'Q' to Quit", True, WHITE)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        elif self.game_state == GAME_STATE_LEVEL_COMPLETE:
            # Display current level as completed (which is self.level - 1, as self.level was already incremented)
            level_complete_text = self.font.render(f"LEVEL {self.level - 1} COMPLETE!", True, YELLOW)
            next_level_text = self.small_font.render("Press 'R' for Next Level or 'Q' to Quit", True, WHITE)
            self.screen.blit(level_complete_text, (SCREEN_WIDTH // 2 - level_complete_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip() # Update the full display Surface to the screen

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(GAME_FPS) # Control game speed (frames per second)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
