from enum import IntEnum
import numpy as np 

# An average of 37 moves and a max of 104 moves can be made at each turn of the game. 
# We set a higher threshold to make sure we have enough room for calculating moves. 
# This way we do not have to use dinamyc lists to get movements for each player and 
# also it works as a way of storing the calculated moves. 
MAX_POSSIBLE_MOVES = 160

# When looking the movements a piece can make, the max number is 22 (rook placed in e4)
# Used to create the king trace array
MAX_POSSIBLE_TRACE = 22

PLAYER_DTYPE = np.dtype([
    ('id', np.uint8),
    ('team', np.uint8),
    ('is_alive', np.bool_),
    ('opponent_type', np.uint8),
    ('color', 'U6'),
])

class Pieces(IntEnum):
    TOWER = 0
    KNIGHT = 1
    BISHOP = 2
    KING = 3
    PAWN = 4
    QUEEN = 5
    EMPTY = 6

class Teams(IntEnum): 
    WHITE = 0
    BLACK = 1
    BLUE = 2
    RED = 3

class PieceInfo(IntEnum): 
    PieceType = 0
    Player = 1
    Position = 2
    Moved = 3
    Flag = 4
