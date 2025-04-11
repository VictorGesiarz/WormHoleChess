from __future__ import annotations
from typing import TYPE_CHECKING

from typing import Dict

if TYPE_CHECKING:
    from engine.core.layer.LayerPieces import LayerPiece
    from engine.core.layer.LayerBoard import LayerBoard


class LayerTile: 
    def __init__(self, name: str) -> None: 
        self.name = name
        self.piece = None
        self.layers = {}

    def __hash__(self): 
        return hash(self.name)
    
    def __eq__(self, other): 
        return self.name == other.name
    
    def set_layer(self, layer: str, neighbors: Dict[str, "LayerTile"]) -> None: 
        self.layers[layer] = neighbors