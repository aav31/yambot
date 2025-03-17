from enum import Enum

class YambRow(Enum):
    """Enum representing each row in yamb grid.
    """
    ONES=0
    TWOS=1
    THREES=2
    FOURS=3
    FIVES=4
    SIXES=5
    MAX=6
    MIN=7
    TWO_PAIRS=8
    THREE_OF_A_KIND=9
    STRAIGHT=10
    FULL_HOUSE=11
    FOUR_OF_A_KIND=12
    YAMB=13