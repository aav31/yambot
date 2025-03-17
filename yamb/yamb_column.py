from enum import Enum

class YambColumn(Enum):
    """Enum representing each column in the yamb grid.
    """
    DOWN=0
    UP=1
    FREE=2
    ANNOUNCE=3