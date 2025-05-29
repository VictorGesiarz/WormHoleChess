from enum import IntEnum
import numpy as np 


PLAYER_DTYPE = np.dtype([
    ('team', np.uint8),
    ('is_bot', np.bool_),
    ('is_alive', np.bool_)
])

MOVE_DTYPE = np.dtype([
    ('piece_type', np.uint8), 
    ('from', np.uint8), 
    ('to', np.uint8),
    ('first_move', np.bool_), 
    ('moves_without_capture', np.uint8), 
    ('captured_piece', np.uint8), 
    ('killed_player', np.uint8) 
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
