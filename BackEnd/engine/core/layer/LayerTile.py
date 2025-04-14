from __future__ import annotations
from typing import TYPE_CHECKING

from typing import List, Dict 

if TYPE_CHECKING:
    from engine.core.layer.LayerPieces import LayerPiece
    from engine.core.layer.LayerBoard import LayerBoard


class LayerTile: 
    def __init__(self, name: str, board: LayerBoard) -> None: 
        self.name = name
        self.board = board
        self.piece = None
        # The tower, bishop are lists of lists of tiles because we need to trace each direction to check if there are pieces blocking
        # The pawn is a list of lists because we need the move positions and the atack positions. 
        # We have to store the pawn of each team
        # The queen is the result of combining the tower and bishop movements
        self.layers: Dict[str, List[List[LayerTile]] | List[LayerTile] | Dict[str, List[List[LayerTile]]]] = {
            "Tower": [], 
            "Bishop": [],
            "Knight": [],
            "King": [], 
            "Pawn": {
                "white": [], 
                "black": [], 
                "blue": [], 
                "red": []
            }
        }

    def __getitem__(self, key: str) -> LayerPiece: 
        return self.layers[key]

    def __hash__(self): 
        return hash(self.name)
    
    def __eq__(self, other): 
        if other is None: 
            return False
        if isinstance(other, str): 
            return self.name == other
        return self.name == other.name
    
    def set_layer(self, layer: str, neighbors: List["LayerTile"]) -> None: 
        self.layers[layer] = neighbors
        