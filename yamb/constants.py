"""
This module defines constants used throughout the Yamb board game environment.

Constants in this module represent fixed values such as grid dimensions, rendering settings, and game rules.
These values ensure consistency and avoid magic numbers throughout the codebase.

Constants:
- NAN: Represents empty cells in the grid (-1).
- GRID_ROWS: Number of rows in the Yamb grid (12).
- GRID_COLUMNS: Number of columns in the Yamb grid (4).
- NUM_DICE: Number of dice used in the game (5).
- DICE_SIDES: Number of sides on each die (6).
- MAX_ROLLS: Maximum number of rolls per turn (3).
- TOTAL_TURNS: Total number of turns in a Yamb game (14 * 4 = 56).
- RENDER_FPS: Frames per second for rendering (60).
- SCREEN_WIDTH: Width of the game window (800 pixels).
- SCREEN_HEIGHT: Height of the game window (600 pixels).
- BACKGROUND_COLOR: RGB color for the background (dark gray, (30, 30, 30)).

Usage:
Import constants in other modules to ensure uniformity and maintainability.
Example:
    from constants import GRID_ROWS, GRID_COLUMNS
"""
# Dice Settings
NUM_DICE = 5
DICE_SIDES = 6

# Game Structure
ACTION_ANNOUNCE_IDX = 6
ACTION_ANNOUNCE_ROW_IDX = 7
ACTION_ROW_COL_FILL_IDX = 8

# Rendering Settings
RENDER_FPS = 10
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
BACKGROUND_COLOR = (30, 30, 30)  # Dark gray

# Other
NAN = -145  # Represents empty cells in the grid
TRUNCATION_PENALTY = -1000  # Represents the truncation penalty in reinforcement learning