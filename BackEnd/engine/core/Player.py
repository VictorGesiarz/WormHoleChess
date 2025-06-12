from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Dict, List, Tuple, Literal
import random 

from engine.core.constants import COLOR_TO_NUMBER, NUMBER_TO_COLOR

if TYPE_CHECKING:
    from engine.core.base.Pieces import Piece
    from engine.core.layer.LayerPieces import LayerPiece
    from engine.core.base.Tile import Tile
    from engine.core.layer.LayerTile import LayerTile

class Player:
    def __init__(self, team: int, color: str, type: str = "player"):
        self.team = team
        self.color = color
        self.type = type

        self.alive = True
        
        self.pieces: Dict[str, List[Piece | LayerPiece]] = {
            "Tower": [],
            "Knight": [],
            "Bishop": [],
            "Queen": [],
            "King": [], 
            "Pawn": []
        }
        self.dead_pieces = [] # The pieces that the player lost
        self.killed_pieces = [] # The pieces that the player killed

    def __str__(self) -> str: 
        return f"Player {self.team} {self.color} ({self.type})"
    
    def __eq__(self, other: "Player" | int) -> bool:
        if isinstance(other, int):
            return self.team == other
        return self.team == other.team

    def copy(self) -> 'Player': 
        player_copy = Player(self.team, self.type, color=self.color)
        player_copy.alive = self.alive
        return player_copy

    def add_piece(self, piece: Piece | LayerPiece) -> None: 
        self.pieces[piece.type].append(piece)

    def lose_piece(self, piece: Piece | LayerPiece) -> None:
        if piece in self.pieces[piece.type]:
            piece.capture()
            # self.dead_pieces.append(piece)

    def revive_piece(self, piece: Piece | LayerPiece) -> None: 
        if piece in self.pieces[piece.type]: 
            piece.revive()

    def get_possible_moves(self) -> List[Tile | LayerTile]:
        """ Returns a list of possible moves [(from_tile, to_tile), ...] 
        """
        moves = []
        for piece_type in self.pieces.values():
            for piece in piece_type:
                if not piece.captured: 
                    from_ = piece.position
                    moves.extend((from_, move) for move in piece.get_movements())
        return moves


class Bot(Player):
    def __init__(self, team: int, color: str, difficulty: Literal['random', 'mcts'] = 'random') -> None:
        super().__init__(team, type="bot", color=color)
        self.difficulty = difficulty

    def copy(self) -> 'Bot': 
        bot_copy = Bot(self.team, self.color, self.difficulty)
        bot_copy.alive = self.alive
        return bot_copy
