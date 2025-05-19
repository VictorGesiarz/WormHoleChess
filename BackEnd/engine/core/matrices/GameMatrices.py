from typing import List, Tuple 
import numpy as np 
from enum import Enum 


from engine.core.layer.LayerBoard import LayerBoard


class PieceType(Enum):
    TOWER = 0
    KNIGHT = 1
    BISHOP = 2
    QUEEN = 3
    KING = 4
    PAWN = 5


class LayerMatrixBoard: 
    def __init__(self, size: Tuple[int, int], gamemode: str = 'wormhole') -> None:
        """ 
        Nodes: list of nodes in the board, the element corresponds to the piece type there and the player
        Edge lists: list of adjacency lists for each piece type. 
            Each adjacency list has 2 lists, one for the outgoing edges and one for the incoming edges.
            Each index stores the index of the node in the nodes list.
        Pattern lists: list of patters of movements for each node in the board. 
            The list contains tuples in the form (piece_type, from_index, to_index)
            The from_index and to_index are the indexes of the edges of that piece type, they indicate what 
            edge starts the pattern and what edge ends it. 
        """
        self.nodes: np.ndarray = np.zeros(size[0] * size[1], dtype=int) 
        self.edges: np.ndarray = np.empty(len(PieceType), dtype=object)
        self.patterns: np.ndarray = np.empty(size[0], * size[1], dtype=object)
        
    @staticmethod
    def create_board(size: Tuple[int, int], gamemode: str = 'wormhole') -> None:
        """ 
        Create a board of the given size. 
        """
        if gamemode == 'wormhole':
            return LayerMatrixBoard(size)
        else:
            raise ValueError(f"Gamemode {gamemode} not supported")
        
        
class BaseMatrixBoard: 
    ...