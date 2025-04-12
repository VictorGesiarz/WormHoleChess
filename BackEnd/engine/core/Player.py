from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Dict, List, Tuple
import random 

from engine.core.constants import COLOR_TO_NUMBER, NUMBER_TO_COLOR

if TYPE_CHECKING:
    from engine.core.base.Pieces import Piece
    from engine.core.layer.LayerPieces import LayerPiece
    from engine.core.base.Tile import Tile
    from engine.core.layer.LayerTile import LayerTile

class Player:
    def __init__(self, team: int,  type: str = "player"):
        self.team = team
        self.type = type
        
        self.alive = True
        
        self.pieces = {
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
        return f"Player {self.team} {NUMBER_TO_COLOR[self.team]} ({self.type})"
    
    def __eq__(self, other: "Player" | int) -> bool:
        if isinstance(other, int):
            return self.team == other
        return self.team == other.team

    def add_piece(self, piece: Piece | LayerPiece) -> None: 
        self.pieces[piece.type].append(piece)

    def lose_piece(self, piece: Piece | LayerPiece) -> None:
        if piece in self.pieces[piece.type]:
            piece.capture()
            # self.dead_pieces.append(piece)

    def revive_piece(self, piece: Piece | LayerPiece) -> None: 
        if piece in self.pieces[piece.type]: 
            piece.revive()

    def get_all_possible_moves(self) -> List[Tile | LayerTile]:
        """ Returns a list of possible moves [(from_tile, to_tile), ...] """
        moves = []
        for piece_type in self.pieces.values():
            for piece in piece_type:
                if not piece.captured: 
                    from_ = piece.position
                    moves.extend((from_, move) for move in piece.get_movements())
        return moves


class Bot(Player): 
    def __init__(self, team: int, difficulty: str = "random"):
        super().__init__(team, type="bot")
        self.difficulty = difficulty

    def choose_move(self, moves: List[Tuple[Tile | LayerTile]]) -> Tuple[Tile | LayerTile]:
        if self.difficulty == "random":
            if len(moves) > 0: 
                random_move = random.choice(moves)
                return random_move
            return None
        else: 
            raise NotImplemented(f"Difficulty level {self.difficulty} not implemented")