import unittest
from yamb.flatten_grid import FlattenGrid
from yamb.yamb_env import YambEnv
from stable_baselines3.common.env_checker import check_env

class TestFlattenGrid(unittest.TestCase):
    def test_check_env(self):
        env = YambEnv()
        env = FlattenGrid(env)
        check_env(env)