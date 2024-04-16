from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Dict
import numpy as np

class ROW(Enum):
    ONES=0
    TWOS=1
    THREES=2
    FOURS=3
    FIVES=4
    SIXES=5
    MAX=6
    MIN=7
    DVAPARA=8
    TRIS=9
    SKALA=10
    FULL=11
    POKER=12
    YAMB=13
    
class COL(Enum):
    DOLJE=0
    GORE=1
    SLOBODNO=2
    NAJAVA=3
    
@dataclass
class Action:
    roll_number: int  # whether the action is meant to occur after roll 1, 2, 3 - can be considered 'action type'
    keep: np.array # action type 1 and 2, array of length 6 saying which dice we keep
    announce: bool = False # action type 1
    announce_row: ROW = ROW.YAMB # action type 1
    row_to_fill: ROW = ROW.YAMB # action type 3 
    col_to_fill: COL = COL.DOLJE # action type 3

class YambEnv:
    def __init__(self):
        self.turn_number = 0
        self.roll_number = 0
        self.grid = np.full((len(ROW), len(COL)), np.nan)
        self.roll = np.array([0, 0, 0, 0, 0, 0])  # counts of dice in multinomial format
        self.announced = None
        self.announced_row = None
    
    def reset(self) -> dict:
        """
        Reset environment to initial state
        :return: observation of the initial state along with auxiliary information
        """
        for row in ROW:
            for col in COL:
                self.grid[row.value, col.value] = np.nan
        
        self.turn_number = 1
        self.roll = np.random.multinomial(5, [1/6.]*6)
        self.roll_number = 1
        self.announced = False
        self.announced_row = None
        return self.get_observation()
    
    def step(self, action : Action) -> Tuple[dict, float, bool, bool, str]:
        """
        Run one timestep of the environment's dynamics - in total there are 14 * 4 turns and 3 rolls within each turn
        :param action: input action which can be of type 1, 2 or 3 determined by action.roll_number param
        :return: observation, reward, terminated, truncated, truncation_reason
        reward = score - prev score
        terminated is when the game finished properly
        truncated is when the game finished due to unforseen circumstances because the action was 'out of bounds'
        """
        if action.roll_number != self.roll_number:
            return self.get_observation(), -1000, False, True, "Action needs to match state of game"
        
        if self.turn_number > 56:
            raise IndexError("Game only has 56 turns - the game is already finished!")
        
        if action.roll_number not in [1, 2, 3]:
            return self.get_observation(), -1000, False, True, "Action needs to be type 1, 2, or 3 not ".format(action.roll_number)
        
        prev_score = self.get_score()
        valid, reason = True, ""
        if action.roll_number == 1:
            valid, reason = self.step_1(action)
        
        if action.roll_number == 2:
            valid, reason = self.step_2(action)
        
        if action.roll_number == 3:
            valid, reason = self.step_3(action)
        
        if not valid:
            return self.get_observation(), -1000, False, True, reason
        
        grid_square_value = np.nan
        if (self.roll_number == 1) or (self.roll_number==2):
            self.roll_number += 1
        else:
            # we are moving on to the next roll
            self.roll_number = 1
            self.turn_number += 1
            self.announced = False
            self.announced_row = None
            grid_square_value = YambEnv.get_grid_square_value(action.row_to_fill, self.roll)
            self.grid[action.row_to_fill.value, action.col_to_fill.value] = grid_square_value
            self.roll = np.random.multinomial(5, [1/6.]*6)
        
        reward = self.get_score() - prev_score
        terminated = True if self.turn_number > 56 else False
        return self.get_observation(grid_square_value), reward, terminated, False, ""
        
        
    
    def render(self, mode="human"):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError
        
    def step_1(self, action: Action) -> Tuple[bool, str]:
        """
        Does a step of type 1 - only mutates object if it is valid
        :param action: input action of type 1
        :return: valid, reason
        
        Unused: action.row_to_fill, action.col_to_fill
        """
        if self.roll_number != 1: raise IndexError("Can only do step 1 after roll 1")
        
        if any( (self.roll - action.keep) < 0 ):
            return False, "Can't keep {} when you only have {}".format(action.keep, self.roll)
        
        if action.announce:
            if not self.valid_announce_row(action.announce_row):
                return False, "Announce row {} not valid".format(action.announce_row)
            
        number_of_dice_to_roll = sum(self.roll - action.keep)
        self.roll = np.random.multinomial(number_of_dice_to_roll, [1/6.]*6) + action.keep
        
        self.announced = action.announce
        self.announced_row = action.announce_row
        return True, ""
    
    def step_2(self, action: Action) -> Tuple[bool, str]:
        """
        Does a step of type 2 - only mutates object if it is valid
        :param action: input action of type 2
        :return: valid, reason
        
        Unused: action.row_to_fill, action.col_to_fill, action.announce, action.announce_row
        """
        if self.roll_number != 2: raise IndexError("Can only do step 2 after roll 2")
        
        if any( (self.roll - action.keep) < 0 ):
            return False, "Can't keep {} when you only have {}".format(action.keep, self.roll)
        
        number_of_dice_to_roll = sum(self.roll - action.keep)
        self.roll = np.random.multinomial(number_of_dice_to_roll, [1/6.]*6) + action.keep
        
        return True, ""
    
    def step_3(self, action: Action) -> Tuple[bool, str]:
        """
        Does a step of type 3 - only mutates object if it is valid
        :param action: input action of type 3
        :return: valid, reason
        
        Unused: action.keep, action.announce, action.announce_row
        """
        if self.roll_number != 3: raise IndexError("Can only do step 3 after roll 3")
        
        if (action.row_to_fill not in ROW) or (action.col_to_fill not in COL):
            return False, "Out of bounds {}, {}".format(action.row_to_fill, action.col_to_fill)
        
        if not np.isnan(self.grid[action.row_to_fill.value, action.col_to_fill.value]):
            return False, "{}, {} already filled in ".format(action.row_to_fill, action.col_to_fill)
        
        if (action.col_to_fill == COL.GORE) and (action.row_to_fill != self.get_next_gore()):
            return False, "Gore needed {} but trying {}".format(self.get_next_gore(), action.row_to_fill)
        
        if (action.col_to_fill == COL.DOLJE) and (action.row_to_fill != self.get_next_dolje()):
            return False, "Dolje needed {} but trying {}".format(self.get_next_gore(), action.row_to_fill)
        
        if self.announced and ((action.col_to_fill != COL.NAJAVA) or (action.row_to_fill != self.announced_row)):
            return False, "Announced {} but trying to fill {}, {}".format(self.announced_row, action.row_to_fill, action.col_to_fill)
        
        return True, ""
    
    def valid_announce_row(self, row: ROW) -> bool:
        """
        :param row: a row which you which to announce
        :return: bool indicated whether you can actually announce that row
        """
        if row not in ROW:
            return False
        
        if np.isnan(self.grid[row.value, COL.NAJAVA.value]):
            return True
        else:
            return False
        
    def get_observation(self, grid_square_value=np.nan) -> dict:
        observation = {
            "turn_number": self.turn_number,
            "roll_number": self.roll_number,
            "grid": self.grid.copy(),
            "roll": self.roll.copy(),
            "announced": self.announced,
            "announced_row": self.announced_row,
            "score": self.get_score(),
            "dolje": self.get_next_dolje().name,
            "gore": self.get_next_gore().name,
            "grid_square_value": grid_square_value
        }
        return observation
    
    def get_score(self) -> int:
        """
        :return: game score thus far, anything with an nan will be assigned zero
        """
        result = 0
        for col in COL:
            A = 0
            for row in [ROW.ONES, ROW.TWOS, ROW.THREES, ROW.FOURS, ROW.FIVES, ROW.SIXES]:
                A += 0 if np.isnan(self.grid[row.value, col.value]) else self.grid[row.value, col.value]
                
            if (A >= 60):
                A += 30
            
            B = self.grid[ROW.MAX.value, col.value] - self.grid[ROW.MIN.value, col.value]
            B *= self.grid[ROW.ONES.value, col.value]
            B = 0 if np.isnan(B) else B
            
            C = 0
            for row in [ROW.DVAPARA, ROW.TRIS, ROW.SKALA, ROW.FULL, ROW.POKER, ROW.YAMB]:
                C += 0 if np.isnan(self.grid[row.value, col.value]) else self.grid[row.value, col.value]
                
            result = result + A + B + C
                
        return result
    
    def get_next_dolje(self) -> ROW:
        """
        Gets the next row we need to fill out in the dolje column, if we've completed it return nan
        """
        for row in ROW:
            if np.isnan(self.grid[row.value, COL.DOLJE.value]): return row
        
        return np.nan
    
    def get_next_gore(self) -> ROW:
        """
        Gets the next row we need to fill out in the gore column, if we've completed it return nan
        """
        for row in reversed(ROW):
            if np.isnan(self.grid[row.value, COL.GORE.value]): return row
        
        return np.nan
    
    @staticmethod
    def get_grid_square_value(row: ROW, cnts: np.array) -> int:
        """
        :param row: which row do you want the grid square value for
        :param cnts: array of size six which tells you tells you mapping of face value to how many dice
        :return: grid square value
        """
        
        if row == ROW.ONES:
            return 1 * cnts[0]
        elif row == ROW.TWOS:
            return 2 * cnts[2]
        elif row == ROW.THREES:
            return 3 * cnts[2]
        elif row == ROW.FOURS:
            return 4 * cnts[3]
        elif row == ROW.FIVES:
            return 5 * cnts[4]
        elif row == ROW.SIXES:
            return 6 * cnts[5]
        elif row == ROW.MAX:
            return sum( (i+1)*item for i, item in enumerate(cnts) )
        elif row == ROW.MIN:
            return sum( (i+1)*item for i, item in enumerate(cnts) )
        elif row == ROW.DVAPARA:
            return YambEnv.dvapara(cnts)
        elif row == ROW.TRIS:
            return YambEnv.tris(cnts)
        elif row == ROW.SKALA:
            return YambEnv.skala(cnts)
        elif row == ROW.FULL:
            return YambEnv.full(cnts)
        elif row == ROW.POKER:
            return YambEnv.poker(cnts)
        elif row == ROW.YAMB:
            return YambEnv.yamb(cnts)
        else:
            raise IndexError("Row {} not found in possible rows".format(row))
    
    @staticmethod
    def dvapara(cnts : np.array) -> int:
        if not (sum(cnts >= 2) >= 2): return 0
        s = 0
        for i, cnt in enumerate(cnts):
            if cnt >= 2:
                s += 2 * (i+1)
        return s + 10
    
    @staticmethod
    def tris(cnts : np.array) -> int:
        if not any(cnts >= 3): return 0
        s = 0
        for i, cnt in enumerate(cnts):
            if cnt >= 3:
                s += 3 * (i+1)
                
        return s + 20
    
    @staticmethod
    def skala(cnts : np.array) -> int:
        if all(np.array([1,1,1,1,1,0]) == cnts):
            return 45
        elif all(np.array([0,1,1,1,1,1]) == cnts):
            return 50
        else:
            return 0
    
    @staticmethod
    def full(cnts : np.array) -> int:
        if not (any(cnts == 3) * any(cnts == 2)): return 0
        s = sum( (i+1)*item for i, item in enumerate(cnts) )
        return s + 40
    
    @staticmethod
    def poker(cnts : np.array) -> int:
        if not any(cnts >= 4): return 0
        s = 0
        for i, cnt in enumerate(cnts):
            if cnt >= 4:
                s += 4 * (i+1)
        
        return s + 50
    
    @staticmethod
    def yamb(cnts : np.array) -> int:
        if not any(cnts >= 5): return 0
        s = sum( (i+1)*item for i, item in enumerate(cnts) )
        return s + 60
    