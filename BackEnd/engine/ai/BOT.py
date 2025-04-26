from typing import List, Tuple, Literal

from engine.core.Player import Player
from engine.core.base.Tile import Tile
from engine.core.layer.LayerTile import LayerTile

from engine.ai.RandomAI import RandomAI
from engine.ai.MonteCarlo import MonteCarlo
from engine.ai.AlphaZero import AlphaZero


class Bot(Player):
    def __init__(self, team: int, difficulty: Literal['random', 'monte-carlo'] = 'random') -> None:
        super().__init__(team, type="bot")
        self.difficulty = difficulty

        if difficulty == "random":
            self.ai = RandomAI()
        elif difficulty == "monte-carlo":
            self.ai = MonteCarlo()
        else:
            raise NotImplementedError(f"AI difficulty '{difficulty}' not implemented.")

    def choose_move(self, moves: List[Tuple[Tile | LayerTile]]) -> Tuple[Tile | LayerTile]:
        if not moves:
            return None
        return self.ai.choose_move(moves)
