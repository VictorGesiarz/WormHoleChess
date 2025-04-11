from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Dict, List
import random 

from engine.core.constants import COLOR_TO_NUMBER, NUMBER_TO_COLOR

if TYPE_CHECKING:
    from engine.core.Game import Game
    from engine.core.base.Pieces import Piece
    from engine.core.base.Tile import Tile

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

    def add_piece(self, piece: Piece) -> None: 
        self.pieces[piece.type].append(piece)

    def lose_piece(self, piece: Piece) -> None:
        if piece in self.pieces[piece.type]:
            piece.capture()
            # self.dead_pieces.append(piece)

    def revive_piece(self, piece: Piece) -> None: 
        if piece in self.pieces[piece.type]: 
            piece.revive()

    def get_all_possible_moves(self) -> List[Tile]:
        """ Returns a list of possible moves [(from_tile, to_tile), ...] """
        moves = []
        for piece_type in self.pieces.values():
            for piece in piece_type:
                if not piece.captured: 
                    from_ = piece.position
                    moves.extend((from_, move) for move in piece.get_movements())
        return moves


class Bot(Player): 
    def __init__(self, number: int, username: str, color: str):
        super().__init__(number, username, None, color, time=float("inf"), type="bot")

    def make_move(self) -> None:
        """ Implements a basic bot move strategy. """
        possible_moves = self.get_all_possible_moves()
        
        if possible_moves:
            piece, move = random.choice(possible_moves)
            self.move(piece, move) 