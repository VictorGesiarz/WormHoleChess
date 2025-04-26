import random 
from typing import List, Tuple

from engine.core.base.Tile import Tile
from engine.core.layer.LayerTile import LayerTile


class RandomAI:     
    def choose_move(self, moves: List[Tuple[Tile | LayerTile]]) -> Tuple[Tile | LayerTile]:
        if len(moves) > 0: 
            random_move = random.choice(moves)
            return random_move
        return None
