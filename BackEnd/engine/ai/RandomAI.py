from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import random 

if TYPE_CHECKING: 
    from engine.core.Game import Game
    from engine.core.base.Tile import Tile
    from engine.core.layer.LayerTile import LayerTile


class RandomAI:     
    def __init__(self, game: Game):
        self.game = game

    def choose_move(self) -> Tuple[Tile | LayerTile]:
        moves = self.game.get_movements()
        if len(moves) > 0:
            random_move = random.choice(moves)
            return random_move
        return None
