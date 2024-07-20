from gymnasium import spaces, ObservationWrapper
from .row_enum import ROW
from .col_enum import COL

class FlattenGrid(ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)
        self.observation_space = spaces.Dict({
            "turn_number": spaces.Discrete(len(ROW)*len(COL),start=0),
            "roll_number": spaces.Discrete(3,start=0),
            "grid": spaces.Box(low=-1, high=1, shape=(len(ROW)*len(COL),), dtype=float),
            "roll": spaces.Box(low=-1, high=1, shape=(6,), dtype=float),
            "announced": spaces.Discrete(2,start=0),
            "announced_row": spaces.Discrete(len(ROW), start=0),
        })

    def observation(self, obs):
        obs["grid"] = obs["grid"].flatten() / 145.0
        obs["roll"] = (obs["roll"] - 1.0) / 5.0 
        return obs