"""
This module defines the YambEnv class, which represents the environment for the Yamb board game.
YambEnv includes attributes which represent game state - the RL problem we are solving is an MDP therefore environment state is equivalent to agent state.
YambEnv also provides methods for resetting the environment, taking a step in the environment, rendering the environment, and validating actions.

Attributes:
- turn_number: This tells us which turn we are on. There are 14 * 4 turns in Yamb, each consisting of 3 rolls.
- roll_number: Each turn in Yamb consists of three rolls. This tells you which roll we are on.
- grid: This is the 14 * 4 grid in Yamb which needs to be filled out. -145 indicates not filled.
- roll: This tells us the roll we just had in multinomial format. This means roll[2] is the number of 3s.
- announced: This tells us whether we have announced in our current turn.
- announced_row: This tells us the row we have announced in our current turn.

Available functions:
- __init__: Initializes the YambEnv environment with default values.
- reset: Resets the environment to its initial state, including rolling the dice.
- step: Runs one timestep of the environment's dynamics based on the provided action.
- render: Renders the current state of the environment using Pygame.
- close: Closes the Pygame window and cleans up resources.
- valid_announce_row: Validates if the provided row is a valid announcement row.
"""

import numpy as np
from numpy.typing import NDArray
import gymnasium as gym
import pygame
from .yamb_row import YambRow
from .yamb_column import YambColumn
from .constants import (
    NAN,
    TRUNCATION_PENALTY,
    RENDER_FPS,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ACTION_ANNOUNCE_IDX,
    ACTION_ANNOUNCE_ROW_IDX,
    ACTION_ROW_COL_FILL_IDX,
    NUM_DICE,
    DICE_SIDES,
)



class YambEnv(gym.Env):
    """Environment for the Yamb board game."""

    def __init__(self):
        """
        Initializes the YambEnv environment with default values.

        :param int turn_number: This tells us which turn we are on. There are 14 * 4 turns in Yamb, each consisting of 3 rolls.
        :param int roll_number: Each turn in Yamb consists of three rolls. This tells you which roll we are on.
        :param ndarray grid: This is the 14 * 4 grid in Yamb which needs to be filled out. -145 indicates not filled.
        :param ndarray roll: This tells us the roll we just had in multinomial format. This means roll[2] is the number of 3s.
        :param int announced: This tells us whether we have announced in our current turn.
        :param int announced_row: This tells us the row we have announced in our current turn.
        """
        super().__init__()
        self.turn_number = 0
        self.roll_number = 0
        grid_rows, grid_cols = len(YambRow), len(YambColumn)
        self.grid = np.full((grid_rows, grid_cols), NAN)
        self.roll = np.array([0] * DICE_SIDES) 
        self.announced = 0
        self.announced_row = 0

        self.observation_space = gym.spaces.Dict(
            {
                "turn_number": gym.spaces.Discrete(n=grid_rows * grid_cols, start=0),
                "roll_number": gym.spaces.Discrete(n=3, start=0),
                "grid": gym.spaces.Box(
                    low=NAN, high=-NAN, shape=(grid_rows, grid_cols), dtype=int
                ),
                "roll": gym.spaces.Box(low=0, high=NUM_DICE, shape=(DICE_SIDES,), dtype=int),
                "announced": gym.spaces.Discrete(n=2, start=0),
                "announced_row": gym.spaces.Discrete(n=len(YambRow), start=0),
            }
        )

        # [num1s, num2s, num3s, num4s, num5s, num6s, announce, announce_row, row_col_fill]
        self.action_space = gym.spaces.MultiDiscrete(
            np.array([NUM_DICE + 1] * DICE_SIDES + [2, grid_rows] + [grid_rows * grid_cols])
        )

        # pygame parameters and objects
        self.screen = None
        self.clock = None

    def reset(self, seed=None, options=None) -> tuple[dict, dict]:
        """Reset environment to initial state - remember this also includes rolling the dice

        :return: observation of the initial state along with auxiliary information
        """
        np.random.seed(seed)
        self.turn_number = 0
        self.roll_number = 0
        for row in YambRow:
            for col in YambColumn:
                self.grid[row.value, col.value] = NAN
        self.roll = np.random.multinomial(NUM_DICE, [1 / float(DICE_SIDES)] * DICE_SIDES)
        self.announced = 0
        self.announced_row = 0
        return self.get_observation(), {}

    def step(self, action: NDArray[np.int64]) -> tuple[dict, float, bool, bool, dict]:
        """Run one timestep of the environment's dynamics.
        In total there are 56 turns, and 3 rolls within each turn.

        :param action: numpy array of length 9
            [num1s, num2s, num3s, num4s, num5s, num6s, announce, announce_row, row_col_fill]

        :return: observation, reward, terminated, truncated, info
            observation:dict
            reward:float score - prev score or TRUNCATION_PENALTY if the game finishes because of a bad action
            terminated:bool true when the game finished properly
            truncated:bool true when the game finished due to unforseen circumstances; action was out of bounds
            info:dict other relevant information for example the score / why the game truncated?
        """

        prev_score = self.get_score()

        valid, info = True, {}
        if self.roll_number == 0:
            valid = self.step_1_valid(action, info)

        if self.roll_number == 1:
            valid = self.step_2_valid(action, info)

        if self.roll_number == 2:
            valid = self.step_3_valid(action[ACTION_ROW_COL_FILL_IDX], info)

        if not valid:
            return self.get_observation(), TRUNCATION_PENALTY, False, True, info

        # if the action is valid, we can mutate the state
        if self.roll_number == 0:
            self.roll_number += 1
            keep = action[:ACTION_ANNOUNCE_IDX]
            number_of_dice_to_roll = sum(self.roll - keep)
            self.roll = (
                np.random.multinomial(number_of_dice_to_roll, [1 / float(DICE_SIDES)] * DICE_SIDES) + keep
            )
            self.announced = action[ACTION_ANNOUNCE_IDX]
            self.announced_row = action[ACTION_ANNOUNCE_ROW_IDX]
        elif self.roll_number == 1:
            self.roll_number += 1
            keep = action[:ACTION_ANNOUNCE_IDX]
            number_of_dice_to_roll = sum(self.roll - keep)
            self.roll = (
                np.random.multinomial(number_of_dice_to_roll, [1 / float(DICE_SIDES)] * DICE_SIDES) + keep
            )
        elif self.roll_number == 2:
            # we are moving on to the next turn
            self.roll_number = 0
            self.turn_number += 1
            self.announced = 0
            self.announced_row = 0
            r, c = YambEnv.convert_row_col_fill(action[ACTION_ROW_COL_FILL_IDX])
            self.grid[r, c] = self.get_grid_square_value(r, self.roll)
            self.roll = np.random.multinomial(NUM_DICE, [1 / float(DICE_SIDES)] * DICE_SIDES)

        info["score"] = self.get_score()
        reward = info["score"] - prev_score
        terminated = True if self.turn_number >= len(YambRow) * len(YambColumn) else False

        if self.render_mode == "human":
            self.render()

        return self.get_observation(), reward, terminated, False, info

    def render(self):
        """Displays the state of the game - there is no interaction with the user here"""
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
            )

        if self.clock is None:
            self.clock = pygame.time.Clock()

        cell_size = 32
        dot_radius = 2
        black = (0, 0, 0)
        white = (255, 255, 255)
        self.screen.fill(white)

        font = pygame.font.Font(None, 24)
        text = font.render(
            f"TURN: {self.turn_number}, ROLL: {self.roll_number}", True, black
        )
        text_rect = text.get_rect()
        text_rect.topleft = (SCREEN_WIDTH // 2, cell_size)
        self.screen.blit(text, text_rect)

        text = font.render(f"SCORE: {self.get_score()}", True, black)
        text_rect = text.get_rect()
        text_rect.topleft = (SCREEN_WIDTH // 2, 2 * cell_size)
        self.screen.blit(text, text_rect)

        text = font.render(f"ANNOUNCED: {bool(self.announced)}", True, black)
        text_rect = text.get_rect()
        text_rect.topleft = (SCREEN_WIDTH // 2, 4 * cell_size)
        self.screen.blit(text, text_rect)

        if self.announced == 1:
            text = font.render(f"ANNOUNCED ROW: {YambRow(self.announced_row)}", True, black)
            text_rect = text.get_rect()
            text_rect.topleft = (SCREEN_WIDTH // 2, 5 * cell_size)
            self.screen.blit(text, text_rect)

        # draw rows
        font = pygame.font.Font(None, 12)
        for row in YambRow:
            rect = pygame.Rect(0, (1 + row.value) * cell_size, 2 * cell_size, cell_size)
            text = font.render(str(row.value) + ". " + row.name, True, black)
            pygame.draw.rect(self.screen, black, rect, 1)
            self.screen.blit(text, rect.move(cell_size // 4, cell_size // 4))

        # draw cols
        for col in YambCol:
            rect = pygame.Rect(
                (2 + 2 * col.value) * cell_size, 0, 2 * cell_size, cell_size
            )
            text = font.render(str(col.value) + ". " + col.name, True, black)
            pygame.draw.rect(self.screen, black, rect, 1)
            self.screen.blit(text, rect.move(cell_size // 4, cell_size // 4))

        # fill out the grid
        font = pygame.font.Font(None, 20)
        for row in YambRow:
            for col in YambCol:
                rect = pygame.Rect(
                    (2 + 2 * col.value) * cell_size,
                    (1 + row.value) * cell_size,
                    2 * cell_size,
                    cell_size,
                )
                s = (
                    ""
                    if self.grid[row.value, col.value] == NAN
                    else str(self.grid[row.value, col.value])
                )
                text = font.render(s, True, black)
                pygame.draw.rect(self.screen, black, rect, 1)
                self.screen.blit(text, rect.move(cell_size // 4, cell_size // 4))

        # draw roll
        def draw_dot(position):
            pygame.draw.circle(self.screen, black, position, dot_radius)

        def draw_one(x, y):
            draw_dot((x + cell_size // 2, y + cell_size // 2))

        def draw_two(x, y):
            draw_dot((x + cell_size // 4, y + cell_size // 4))
            draw_dot((x + cell_size * 3 // 4, y + cell_size * 3 // 4))

        def draw_three(x, y):
            draw_dot((x + cell_size // 4, y + cell_size // 4))
            draw_dot((x + cell_size // 2, y + cell_size // 2))
            draw_dot((x + cell_size * 3 // 4, y + cell_size * 3 // 4))

        def draw_four(x, y):
            draw_dot((x + cell_size // 4, y + cell_size // 4))
            draw_dot((x + cell_size * 3 // 4, y + cell_size // 4))
            draw_dot((x + cell_size // 4, y + cell_size * 3 // 4))
            draw_dot((x + cell_size * 3 // 4, y + cell_size * 3 // 4))

        def draw_five(x, y):
            draw_dot((x + cell_size // 4, y + cell_size // 4))
            draw_dot((x + cell_size * 3 // 4, y + cell_size // 4))
            draw_dot((x + cell_size // 2, y + cell_size // 2))
            draw_dot((x + cell_size // 4, y + cell_size * 3 // 4))
            draw_dot((x + cell_size * 3 // 4, y + cell_size * 3 // 4))

        def draw_six(x, y):
            draw_dot((x + cell_size // 4, y + cell_size // 4))
            draw_dot((x + cell_size * 3 // 4, y + cell_size // 4))
            draw_dot((x + cell_size // 4, y + cell_size // 2))
            draw_dot((x + cell_size * 3 // 4, y + cell_size // 2))
            draw_dot((x + cell_size // 4, y + cell_size * 3 // 4))
            draw_dot((x + cell_size * 3 // 4, y + cell_size * 3 // 4))

        top_left_x, top_left_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        for i, count in enumerate(self.roll):
            for die in range(count):
                rect = pygame.Rect(top_left_x, top_left_y, cell_size, cell_size)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

                if (i + 1) == 1:
                    draw_one(top_left_x, top_left_y)
                if (i + 1) == 2:
                    draw_two(top_left_x, top_left_y)
                if (i + 1) == 3:
                    draw_three(top_left_x, top_left_y)
                if (i + 1) == 4:
                    draw_four(top_left_x, top_left_y)
                if (i + 1) == 5:
                    draw_five(top_left_x, top_left_y)
                if (i + 1) == 6:
                    draw_six(top_left_x, top_left_y)

                top_left_x += cell_size

        self.clock.tick(RENDER_FPS)
        pygame.display.flip()

    def close(self):
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()

    def get_observation(self) -> dict:
        observation = {
            "turn_number": self.turn_number,
            "roll_number": self.roll_number,
            "grid": self.grid,
            "roll": self.roll,
            "announced": self.announced,
            "announced_row": self.announced_row,
        }
        return observation

    def action_masks(self) -> list[bool]:
        """Returns a one hot encoded list whether an action is valid

        :return: list of size sum([6, 6, 6, 6, 6, 6, 2, 14, 56])
        """
        num1s = [False] * 6
        num2s = [False] * 6
        num3s = [False] * 6
        num4s = [False] * 6
        num5s = [False] * 6
        num6s = [False] * 6
        announce = [False] * 2
        announce_row = [False] * len(YambRow)
        row_col_fill = [False] * len(YambRow) * len(YambColumn)

        # can only keep dice that you have
        if (self.roll_number == 0) or (self.roll_number == 1):
            num1s = [True] * (self.roll[0] + 1) + [False] * (5 - self.roll[0])
            num2s = [True] * (self.roll[1] + 1) + [False] * (5 - self.roll[1])
            num3s = [True] * (self.roll[2] + 1) + [False] * (5 - self.roll[2])
            num4s = [True] * (self.roll[3] + 1) + [False] * (5 - self.roll[3])
            num5s = [True] * (self.roll[4] + 1) + [False] * (5 - self.roll[4])
            num6s = [True] * (self.roll[5] + 1) + [False] * (5 - self.roll[5])

        if self.roll_number == 0:
            announce_row = [self.valid_announce_row(i) for i in range(len(YambRow))]
            announce = [not self.need_to_announce(), any(announce_row)]

        if self.roll_number == 2:
            for i in range(len(YambColumn) * len(YambRow)):
                row_col_fill[i] = self.step_3_valid(i, {})

        mask = (
            num1s
            + num2s
            + num3s
            + num4s
            + num5s
            + num6s
            + announce
            + announce_row
            + row_col_fill
        )
        return mask

    def step_1_valid(self, action: NDArray[np.int64], info: dict) -> bool:
        """Checks whether an action of type 1 is valid

        :param action: numpy array of length 9
            [num1s, num2s, num3s, num4s, num5s, num6s, announce, announce_row, row_col_fill]

        :return: whether the action was valid or not, truncation reason will be added to info dict

        unused: row_col_fill
        """
        keep = action[:ACTION_ANNOUNCE_IDX]
        if any((self.roll - keep) < 0):
            info["truncation_reason"] = (
                f"Can't keep {keep} when you only have {self.roll}"
            )
            return False

        if action[ACTION_ANNOUNCE_IDX] == 1:
            if not self.valid_announce_row(action[ACTION_ANNOUNCE_ROW_IDX]):
                info["truncation_reason"] = (
                    f"Announce row {YambRow(action[ACTION_ANNOUNCE_ROW_IDX])} not valid"
                )
                return False

        if action[ACTION_ANNOUNCE_IDX] == 0:
            if self.need_to_announce():
                info["truncation_reason"] = "Only najava column left so must use it"
                return False

        return True

    def step_2_valid(self, action: NDArray[np.int64], info: dict) -> bool:
        """Checks whether an action of type 2 is valid

        :param action: numpy array of length 9
            [num1s, num2s, num3s, num4s, num5s, num6s, announce, announce_row, row_col_fill]

        :return: whether the action was valid or not, truncation reason will be added to info dict

        unused: announce, announce_row, row_col_fill
        """
        keep = action[:ACTION_ANNOUNCE_IDX]
        if any((self.roll - keep) < 0):
            info["truncation_reason"] = (
                f"Can't keep {keep} when you only have {self.roll}"
            )
            return False

        return True

    def step_3_valid(self, row_col_fill: int, info: dict) -> bool:
        """Checks whether an action of type 3 is valid

        :param row_col_fill: int indicating which row and col of the grid to fill out

        :return: whether the action was valid or not, truncation reason will be added to info dict
        """
        r, c = YambEnv.convert_row_col_fill(row_col_fill)
        if self.grid[r, c] != NAN:
            info["truncation_reason"] = f"{r}, {c} already filled in "
            return False

        if (c == YambColumn.UP.value) and (r != self.get_next_up()):
            info["truncation_reason"] = (
                f"Gore needed {YambRow(self.get_next_up())} but trying {YambRow(r)}"
            )
            return False

        if (c == YambColumn.DOWN.value) and (r != self.get_next_down()):
            info["truncation_reason"] = (
                f"Dolje needed {YambRow(self.get_next_down())} but trying {YambRow(r)}"
            )
            return False

        if self.announced and ((c != YambColumn.ANNOUNCE.value) or (r != self.announced_row)):
            info["truncation_reason"] = (
                f"Announced {YambRow(self.announced_row)} but trying to fill {YambRow(r)}, {YambColumn(c)}"
            )
            return False

        if (self.announced == 0) and (c == YambColumn.ANNOUNCE.value):
            info["truncation_reason"] = (
                f"Have not announced so cannot fill out najava column"
            )
            return False

        return True

    def valid_announce_row(self, row: int) -> bool:
        """
        :param row: a row which you which to announce

        :return: bool indicated whether you can actually announce that row
        """

        if self.grid[row, YambColumn.ANNOUNCE.value] == NAN:
            return True
        else:
            return False

    def need_to_announce(self) -> bool:
        """You must announce on your first roll when the rest of the grid has been filled
        :return: whether you need to announce on your first roll
        """
        for col in [YambColumn.DOWN, YambColumn.UP, YambColumn.FREE]:
            for row in YambRow:
                if self.grid[row.value, col.value] == NAN:
                    # there's something you can fill out
                    return False

        return True

    def get_score(self) -> int:
        """
        :return: game score thus far, anything with an nan will be assigned zero
        """
        result = 0
        for col in YambColumn:
            A = 0
            for row in [
                YambRow.ONES,
                YambRow.TWOS,
                YambRow.THREES,
                YambRow.FOURS,
                YambRow.FIVES,
                YambRow.SIXES,
            ]:
                A += (
                    0
                    if self.grid[row.value, col.value] == NAN
                    else self.grid[row.value, col.value]
                )

            if A >= 60:
                A += 30

            if (
                (self.grid[YambRow.MAX.value, col.value] == NAN)
                or (self.grid[YambRow.MIN.value, col.value] == NAN)
                or (self.grid[YambRow.ONES.value, col.value] == NAN)
            ):
                B = 0
            else:
                B = (
                    self.grid[YambRow.MAX.value, col.value]
                    - self.grid[YambRow.MIN.value, col.value]
                )
                B *= self.grid[YambRow.ONES.value, col.value]

            C = 0
            for row in [
                YambRow.TWO_PAIRS,
                YambRow.THREE_OF_A_KIND,
                YambRow.STRAIGHT,
                YambRow.FULL_HOUSE,
                YambRow.FOUR_OF_A_KIND,
                YambRow.YAMB,
            ]:
                C += (
                    0
                    if self.grid[row.value, col.value] == NAN
                    else self.grid[row.value, col.value]
                )

            result = result + A + B + C

        return result

    def get_next_down(self) -> int:
        """
        Gets the next row we need to fill out in the dolje column, if we've completed it return nan.
        """
        for row in YambRow:
            if self.grid[row.value, YambColumn.DOWN.value] == NAN:
                return row.value

        return NAN

    def get_next_up(self) -> int:
        """
        Gets the next row we need to fill out in the gore column, if we've completed it return nan.
        """
        for row in reversed(YambRow):
            if self.grid[row.value, YambColumn.UP.value] == NAN:
                return row.value

        return NAN

    @staticmethod
    def get_grid_square_value(row: int, cnts: np.array) -> int:
        """
        :param row: which row do you want the grid square value for
        :param cnts: array of size six which tells you tells you mapping of face value to how many dice
        :return: grid square value
        """

        if row == YambRow.ONES.value:
            return 1 * cnts[0]
        elif row == YambRow.TWOS.value:
            return 2 * cnts[1]
        elif row == YambRow.THREES.value:
            return 3 * cnts[2]
        elif row == YambRow.FOURS.value:
            return 4 * cnts[3]
        elif row == YambRow.FIVES.value:
            return 5 * cnts[4]
        elif row == YambRow.SIXES.value:
            return 6 * cnts[5]
        elif row == YambRow.MAX.value:
            return sum((i + 1) * item for i, item in enumerate(cnts))
        elif row == YambRow.MIN.value:
            return sum((i + 1) * item for i, item in enumerate(cnts))
        elif row == YambRow.TWO_PAIRS.value:
            return YambEnv.dvapara(cnts)
        elif row == YambRow.THREE_OF_A_KIND.value:
            return YambEnv.tris(cnts)
        elif row == YambRow.STRAIGHT.value:
            return YambEnv.skala(cnts)
        elif row == YambRow.FULL_HOUSE.value:
            return YambEnv.full(cnts)
        elif row == YambRow.FOUR_OF_A_KIND.value:
            return YambEnv.poker(cnts)
        elif row == YambRow.YAMB.value:
            return YambEnv.yamb(cnts)
        else:
            raise IndexError(f"Row {row} not found in possible rows")

    @staticmethod
    def dvapara(cnts: np.array) -> int:
        if not (sum(cnts >= 2) >= 2):
            return 0
        s = 0
        for i, cnt in enumerate(cnts):
            if cnt >= 2:
                s += 2 * (i + 1)
        return s + 10

    @staticmethod
    def tris(cnts: np.array) -> int:
        if not any(cnts >= 3):
            return 0
        s = 0
        for i, cnt in enumerate(cnts):
            if cnt >= 3:
                s += 3 * (i + 1)

        return s + 20

    @staticmethod
    def skala(cnts: np.array) -> int:
        if all(np.array([1, 1, 1, 1, 1, 0]) == cnts):
            return 45
        elif all(np.array([0, 1, 1, 1, 1, 1]) == cnts):
            return 50
        else:
            return 0

    @staticmethod
    def full(cnts: np.array) -> int:
        if not (any(cnts == 3) * any(cnts == 2)):
            return 0
        s = sum((i + 1) * item for i, item in enumerate(cnts))
        return s + 40

    @staticmethod
    def poker(cnts: np.array) -> int:
        if not any(cnts >= 4):
            return 0
        s = 0
        for i, cnt in enumerate(cnts):
            if cnt >= 4:
                s += 4 * (i + 1)

        return s + 50

    @staticmethod
    def yamb(cnts: np.array) -> int:
        if not any(cnts >= 5):
            return 0
        s = sum((i + 1) * item for i, item in enumerate(cnts))
        return s + 60

    @staticmethod
    def convert_row_col_fill(row_col_to_fill: int) -> tuple[int, int]:
        """Converts a single index representing a grid square to fill in into two indices
        representing a row and column to fill

        :param row_col_to_fill: single index representing a grid square we want to fill

        :return: row we want to fill in, col we want to fill in
        """
        assert 0 <= row_col_to_fill < len(YambRow) * len(YambColumn)
        col_to_fill, row_to_fill = divmod(row_col_to_fill, len(YambRow))
        return row_to_fill, col_to_fill

    @staticmethod
    def convert_row_fill_col_fill(row_to_fill: int, col_to_fill: int) -> int:
        """Converts two indices representing a row and column to fill into a single
        index representing a grid square to fill

        :param row_to_fill: row we want to fill in
        :param col_to_fill: col we want to fill in

        :return: single index representing a grid square we want to fill
        """
        assert 0 <= row_to_fill < len(YambRow)
        assert 0 <= col_to_fill < len(YambColumn)
        return row_to_fill + len(YambRow) * col_to_fill
