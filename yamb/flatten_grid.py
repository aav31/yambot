from gymnasium import spaces, ObservationWrapper
from .yamb_row import YambRow
from .yamb_column import YambColumn
from .constants import (
    NAN,
    NUM_DICE,
    DICE_SIDES,
)


class FlattenGrid(ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)
        grid_rows, grid_cols = len(YambRow), len(YambColumn)
        self.observation_space = spaces.Dict(
            {
                "turn_number": spaces.Discrete(n=grid_rows * grid_cols, start=0),
                "roll_number": spaces.Discrete(n=3, start=0),
                "grid": spaces.Box(
                    low=-1, high=1, shape=(grid_rows * grid_cols,), dtype=float
                ),
                "roll": spaces.Box(low=-1, high=1, shape=(DICE_SIDES,), dtype=float),
                "announced": spaces.Discrete(n=2, start=0),
                "announced_row": spaces.Discrete(n=grid_rows, start=0),
            }
        )

    def observation(self, obs):
        obs["grid"] = obs["grid"].flatten() / float(NAN)
        obs["roll"] = (obs["roll"] - 1.0) / float(NUM_DICE)
        return obs
