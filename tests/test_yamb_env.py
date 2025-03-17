import unittest
import numpy as np
from yamb.yamb_env import YambEnv
from yamb.yamb_row import YambRow
from yamb.yamb_column import YambColumn
from yamb.constants import (
    NAN,
    TRUNCATION_PENALTY,
    NUM_DICE,
    DICE_SIDES,
)

# TODO: need to split this into tests cases and refactor, this is really long

class TestYambEnv(unittest.TestCase):
    def test_convert_row_col_fill(self):
        row, col = YambEnv.convert_row_col_fill(0)
        self.assertEqual(0, row)
        self.assertEqual(0, col)
        
        row, col = YambEnv.convert_row_col_fill(14)
        self.assertEqual(0, row)
        self.assertEqual(1, col)
        
        row, col = YambEnv.convert_row_col_fill(55)
        self.assertEqual(13, row)
        self.assertEqual(3, col)
        
    def test_convert_row_fill_col_fill(self):
        idx = YambEnv.convert_row_fill_col_fill(1, 0)
        self.assertEqual(1, idx)
        
        idx = YambEnv.convert_row_fill_col_fill(0, 1)
        self.assertEqual(14, idx)
        
        idx = YambEnv.convert_row_fill_col_fill(13, 3)
        self.assertEqual(55, idx)
    
    def test_get_next_down(self):
        env = YambEnv()
        
        # start of game nothing is filled out
        self.assertEqual(YambRow.ONES, YambRow(env.get_next_down()))
        
        
        # when we add stuff to other columns nothing should change
        env.grid[YambRow.ONES.value, YambColumn.UP.value] = 1
        env.grid[YambRow.ONES.value, YambColumn.FREE.value] = 1
        self.assertEqual(YambRow.ONES, YambRow(env.get_next_down()))
        
        # when we fill out the rows in order, check the function works as expected
        rows = list(YambRow)
        for row in rows[:-1]:
            env.grid[row.value, YambColumn.DOWN.value] = 0
            self.assertEqual(rows[row.value+1], YambRow(env.get_next_down()))
        
        # once we've filled everything out check that this returns nan
        env.grid[rows[-1].value, YambColumn.DOWN.value] = 0
        self.assertEqual(env.get_next_down(), NAN)
        
    def test_get_next_up(self):
        env = YambEnv()
        
        # start of game nothing is filled out
        self.assertEqual(YambRow.YAMB, YambRow(env.get_next_up()))
        
        
        # when we add stuff to other columns nothing should change
        env.grid[YambRow.YAMB.value, YambColumn.DOWN.value] = 1
        env.grid[YambRow.YAMB.value, YambColumn.FREE.value] = 1
        self.assertEqual(YambRow.YAMB, YambRow(env.get_next_up()))
        
        # when we fill out the rows in order, check the function works as expected
        rows = list(YambRow)
        for row in reversed(rows[1:]):
            env.grid[row.value, YambColumn.UP.value] = 0
            self.assertEqual(rows[row.value-1], YambRow(env.get_next_up()))
        
        # once we've filled everything out check that this returns nan
        env.grid[rows[0].value, YambColumn.UP.value] = 0
        self.assertEqual(env.get_next_up(), NAN)
        
    def test_get_score(self):
        env = YambEnv()
        self.assertEqual(0, env.get_score())
        
        env.grid = np.array(
        [[-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145]]
        )
        self.assertEqual(0, env.get_score())
        
        env.grid = np.array(
        [[1     , -145, 2     , -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, 10    , -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, 55    , -145, -145]]
        )
        self.assertEqual(1+55+2, env.get_score())
        
        env.grid = np.array(
        [[1     , -145, 2     , -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, 20    , -145],
         [-145, -145, 10    , -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, 55    , -145, -145]]
        )
        self.assertEqual(1+55+2+2*(20-10), env.get_score())
        
        env.grid = np.array(
        [[1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],
         [1     , 1     , 1     , 1     ],]
        )
        self.assertEqual(6*4 + 6*4, env.get_score())
        
        env.grid = np.array(
        [[-145, -145, -145, 2     ],
         [-145, -145, -145, 4     ],
         [-145, -145, -145, 3     ],
         [-145, -145, -145, 12    ],
         [-145, -145, -145, 15    ],
         [-145, -145, -145, 24    ],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145]]
        )
        self.assertEqual(90, env.get_score())
        
        env.grid = np.array(
        [[1     , 0     , 6     , 0     ],
         [4     , 2     , 12    , 0     ],
         [3     , 3     , 15    , 0     ],
         [12    , 16    , 20    , 0     ],
         [15    , 20    , 25    , 0     ],
         [24    , 6     , 30    , 0     ],
         [20    , 30    , 10    , 0     ],
         [10    , 5     , 5     , 0     ],
         [16    , 0     , 20    , 0     ],
         [33    , 0     , 0     , 0     ],
         [45    , 0     , 0     , 0     ],
         [55    , 0     , 0     , 0     ],
         [54    , 0     , 0     , 0     ],
         [65    , 0     , 0     , 0     ]]
        )
        self.assertEqual(337+47+188+0, env.get_score())
        
    def test_valid_announce_row(self):
        env = YambEnv()
        env.grid = np.array(
        [[-145, -145, -145, 2     ],
         [-145, -145, -145, 4     ],
         [-145, -145, -145, 3     ],
         [-145, -145, -145, 12    ],
         [-145, -145, -145, 15    ],
         [-145, -145, -145, 24    ],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145],
         [-145, -145, -145, -145]]
        )
        self.assertFalse(env.valid_announce_row(YambRow.SIXES.value))
        self.assertTrue(env.valid_announce_row(YambRow.MAX.value))
        self.assertTrue(env.valid_announce_row(10))
        
    def test_need_to_announce(self):
        env = YambEnv()
        env.grid = np.array(
        [[1     , 0     , 6     , 0     ],
         [4     , 2     , 12    , 0     ],
         [3     , 3     , 15    , 0     ],
         [12    , 16    , 20    , 0     ],
         [15    , 20    , 25    , 0     ],
         [24    , 6     , 30    , 0     ],
         [20    , 30    , 10    , 0     ],
         [10    , 5     , 5     , 0     ],
         [16    , 0     , 20    , 0     ],
         [33    , 0     , 0     , 0     ],
         [45    , 0     , 0     , 0     ],
         [55    , 0     , 0     , 0     ],
         [54    , 0     , 0     , 0     ],
         [65    , 0     , 0     , -145     ]]
        )
        self.assertTrue(env.need_to_announce())
        env.grid = np.array(
        [[1     , 0     , 6     , 0     ],
         [4     , 2     , 12    , 0     ],
         [3     , 3     , 15    , 0     ],
         [12    , 16    , 20    , 0     ],
         [15    , 20    , 25    , 0     ],
         [24    , 6     , 30    , 0     ],
         [20    , 30    , 10    , 0     ],
         [10    , 5     , 5     , 0     ],
         [16    , 0     , 20    , 0     ],
         [33    , 0     , 0     , 0     ],
         [45    , 0     , 0     , 0     ],
         [55    , 0     , -145     , 0     ],
         [54    , 0     , 0     , 0     ],
         [65    , 0     , 0     , -145     ]]
        )
        self.assertFalse(env.need_to_announce())
        
    def test_get_grid_square_value(self):
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.ONES.value, np.array([1,1,1,1,1,0])), 1)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.TWOS.value, np.array([0,2,1,1,1,0])), 4)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.THREES.value, np.array([5,0,0,0,0,0])), 0)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FOURS.value, np.array([4,0,0,1,0,0])), 4)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FIVES.value, np.array([0,0,0,0,5,0])), 25)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.SIXES.value, np.array([0,1,0,0,0,3])), 18)
        
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.MAX.value, np.array([1,1,1,1,1,0])), 15)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.MIN.value, np.array([4,1,0,0,0,0])), 6)
        
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.TWO_PAIRS.value, np.array([4,1,0,0,0,0])), 0)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.TWO_PAIRS.value, np.array([2,3,0,0,0,0])), 10+6)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.TWO_PAIRS.value, np.array([1,0,0,0,2,2])), 10+22)
        
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.THREE_OF_A_KIND.value, np.array([4,1,0,0,0,0])), 20+3)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.THREE_OF_A_KIND.value, np.array([2,3,0,0,0,0])), 20+6)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.THREE_OF_A_KIND.value, np.array([1,0,0,0,2,2])), 0)
        
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.STRAIGHT.value, np.array([1,1,1,1,1,0])), 45)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.STRAIGHT.value, np.array([1,1,1,1,0,1])), 0)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.STRAIGHT.value, np.array([0,1,1,1,1,1])), 50)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.STRAIGHT.value, np.array([0,1,2,0,1,1])), 0)
        
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FULL_HOUSE.value, np.array([0,0,0,0,0,5])), 0)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FULL_HOUSE.value, np.array([0,0,0,0,2,3])), 40 + 28)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FULL_HOUSE.value, np.array([0,0,0,1,2,2])), 0)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FULL_HOUSE.value, np.array([0,0,0,0,3,2])), 40 + 27)
        
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FOUR_OF_A_KIND.value, np.array([0,4,1,0,0,0])), 50+8)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FOUR_OF_A_KIND.value, np.array([0,5,0,0,0,0])), 50+8)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.FOUR_OF_A_KIND.value, np.array([0,0,0,0,2,3])), 0)
        
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.YAMB.value, np.array([0,0,0,0,0,5])), 60+30)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.YAMB.value, np.array([0,5,0,0,0,0])), 60+10)
        self.assertEqual(YambEnv.get_grid_square_value(YambRow.YAMB.value, np.array([0,0,0,0,1,4])), 0)
        
        
    def test_step(self):
        env = YambEnv()
        observation, _ = env.reset()
        
        # step should fail because trying to keep more dice than we have
        action = np.array([
            observation["roll"][0]+1,
            observation["roll"][1],
            observation["roll"][2],
            observation["roll"][3],
            observation["roll"][4],
            observation["roll"][5],
            0,
            0,
            0 + 0*14,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertEqual(reward, TRUNCATION_PENALTY)
        self.assertEqual(terminated, False)
        self.assertEqual(truncated, True)
        
        # step should pass
        action = np.array([
            observation["roll"][0],
            observation["roll"][1],
            observation["roll"][2],
            observation["roll"][3],
            observation["roll"][4],
            observation["roll"][5],
            1,
            YambRow.YAMB.value,
            0 + 0*14,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertEqual(observation["turn_number"], 0)
        self.assertEqual(observation["roll_number"], 1)
        for i in range(6):
            self.assertEqual(observation["roll"][i], action[i]) # should be the same because we kept everything
        
        self.assertEqual(info["score"], 0)
        self.assertEqual(reward, 0)
        self.assertEqual(terminated, False)
        self.assertEqual(truncated, False)
        last_roll = np.copy(observation["roll"])
        
        # step should pass
        action = np.array([
            0,
            0,
            0,
            0,
            0,
            0,
            -145,
            -145,
            -145,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertEqual(observation["turn_number"], 0)
        self.assertEqual(observation["roll_number"], 2)
        with np.testing.assert_raises(AssertionError):
            np.testing.assert_array_equal(observation["roll"], last_roll) # roll should be different because we didn't keep anything
        self.assertEqual(info["score"], 0)
        self.assertEqual(reward, 0)
        self.assertEqual(terminated, False)
        self.assertEqual(truncated, False)
        last_roll = np.copy(observation["roll"])
        
        # step should fail because we're trying to fill out column which isn't najava
        action = np.array([
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            YambRow.YAMB.value + 14 * YambColumn.UP.value,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertEqual(reward, TRUNCATION_PENALTY)
        self.assertEqual(terminated, False)
        self.assertEqual(truncated, True)
        
        # step should fail because we're trying to fill out row which isn't the one announced
        action = np.array([
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            YambRow.ONES.value + 14 * YambColumn.ANNOUNCE.value,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertEqual(reward, TRUNCATION_PENALTY)
        self.assertEqual(terminated, False)
        self.assertEqual(truncated, True)
        
        # step should pass
        action = np.array([
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            -145,
            YambRow.YAMB.value + 14 * YambColumn.ANNOUNCE.value,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertEqual(observation["turn_number"], 1)
        self.assertEqual(observation["roll_number"], 0)
        with np.testing.assert_raises(AssertionError):
            np.testing.assert_array_equal(observation["roll"], last_roll) # since we're moving onto next turn roll should differ
        self.assertEqual(info["score"], 0) # score very likely to be zero because we probs didn't get a yamb
        self.assertEqual(terminated, False)
        self.assertEqual(truncated, False)
        self.assertEqual(observation["grid"][YambRow.YAMB.value, YambColumn.ANNOUNCE.value], info["score"])
        last_roll = np.copy(observation["roll"])
        
        # try to announce row which has already been announced - should fail
        action = np.array([
            observation["roll"][0],
            observation["roll"][1],
            observation["roll"][2],
            observation["roll"][3],
            observation["roll"][4],
            observation["roll"][5],
            1,
            YambRow.YAMB.value,
            0 + 14 * 0,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        np.testing.assert_array_equal(observation["roll"], last_roll)  # should be the same because we failed action
        self.assertEqual(reward, TRUNCATION_PENALTY)
        self.assertEqual(terminated, False)
        self.assertEqual(truncated, True)
        
        # step should pass
        action = np.array([
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0 + 14 * 0,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertEqual(observation["turn_number"], 1)
        self.assertEqual(observation["roll_number"], 1)
        
        # step should pass
        action = np.array([
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0 + 14 * 0,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertEqual(observation["turn_number"], 1)
        self.assertEqual(observation["roll_number"], 2)
        
        # step should fail as we are trying to fill out halfway down the dolje col
        action = np.array([
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            YambRow.TWO_PAIRS.value + 14 * YambColumn.DOWN.value,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertTrue(truncated)
        self.assertEqual(observation["turn_number"], 1)
        self.assertEqual(observation["roll_number"], 2)
        
        # step should fail as we are trying to fill out halfway up the gore col
        action = np.array([
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            YambRow.TWO_PAIRS.value + 14 * YambColumn.UP.value,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertTrue(truncated)
        self.assertEqual(observation["turn_number"], 1)
        self.assertEqual(observation["roll_number"], 2)
        
        # step should fail as we are trying to fill out najava but we didn't announce
        action = np.array([
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            YambRow.TWO_PAIRS.value + 14 * YambColumn.ANNOUNCE.value,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertTrue(truncated)
        self.assertEqual(observation["turn_number"], 1)
        self.assertEqual(observation["roll_number"], 2)
        
        # step should pass
        action = np.array([
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            YambRow.TWO_PAIRS.value + 14 * YambColumn.FREE.value,
        ], dtype=np.int64)
        observation, reward, terminated, truncated, info = env.step(action)
        self.assertFalse(truncated)
        self.assertEqual(observation["turn_number"], 2)
        self.assertEqual(observation["roll_number"], 0)
        