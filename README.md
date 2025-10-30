# Snake Game - Build Instructions

A classic Snake game built with Python and Pygame.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installing uv

If you don't have `uv` installed, install it using one of these methods:

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Using pip:**
```bash
pip install uv
```

## Setup and Run

### Option 1: Quick Run (Recommended)

Use `uv` to automatically create a virtual environment and install dependencies:

```bash
uv run snake_game.py
```

This command will:
- Create a virtual environment (if needed)
- Install all dependencies from `requirements.txt`
- Run the game

### Option 2: Manual Setup

1. **Create a virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

2. **Run the game:**
   ```bash
   python snake_game.py
   ```

### Option 3: Using uv sync (for project management)

If you want to manage this as a proper project:

1. **Initialize a project (creates pyproject.toml):**
   ```bash
   uv init --name snake-game
   ```

2. **Add dependencies:**
   ```bash
   uv add pygame
   ```

3. **Run the game:**
   ```bash
   uv run snake_game.py
   ```

## How to Play

- **Movement Controls:**
  - Arrow keys or WASD to move the snake
  - UP/W: Move up
  - DOWN/S: Move down
  - LEFT/A: Move left
  - RIGHT/D: Move right

- **Objective:** Eat the red food items to grow your snake and increase your score

- **Game Over:** The game ends if you hit a wall or run into yourself

- **After Game Over:**
  - Press 'R' to restart
  - Press 'Q' to quit

## Features

- Score tracking
- High score persistence (saved to `highscore.txt`)
- Increasing difficulty (speed increases as snake grows)
- Collision detection for walls and self
- Clean, grid-based movement

## Troubleshooting

**Issue: pygame not found**
```bash
uv pip install pygame --break-system-packages
```

**Issue: Display not working on Linux**

You may need to install SDL dependencies:
```bash
sudo apt-get install python3-pygame
# or
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

**Issue: uv command not found**

Make sure `uv` is in your PATH. After installation, you may need to restart your terminal or run:
```bash
source ~/.cargo/env  # On macOS/Linux
```

## File Structure

```
.
├── snake_game.py       # Main game file
├── requirements.txt    # Python dependencies
├── highscore.txt      # High score storage (created on first run)
├── LICENSE            # MIT License
└── README.md          # This file
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Author:** Gourav Shah, School of Devops
