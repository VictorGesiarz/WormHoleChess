from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import random 

from engine.agents.Agent import Agent

if TYPE_CHECKING: 
    from engine.core.Game import Game
    from engine.core.GameMatrices import GameMatrices
    from engine.core.base.Tile import Tile
    from engine.core.layer.LayerTile import LayerTile



class HumanPlayer(Agent): 
    def __init__(self, game: Game | GameMatrices):
        self.game = game

    def choose_move(self) -> Tuple[Tile | LayerTile]:
        moves = self.game.get_movements()
        self.game.print_moves()

        chosen_move = int(input("Chosen move: "))
        return moves[chosen_move]
