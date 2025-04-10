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
            "King": None, 
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
        if piece not in self.pieces[piece.type]:
            raise ValueError("Piece not found in player's pieces.")

        piece.captured = True
        self.dead_pieces.append(piece)

    def move(self, from_: Tile, to: Tile) -> None: 
        if from_ == to: 
            raise ValueError("Cannot move to the same tile.")
        if from_.piece is None:
            raise ValueError("No piece to move from the tile.")
        if from_.piece.team != self:
            raise ValueError("Cannot move a piece that does not belong to the player.")
        if from_.piece.captured: 
            raise ValueError("Cannot move a captured piece.")
        if to.piece is not None:
            raise ValueError("Cannot move to a tile that is already occupied.")

        piece_from = from_.piece
        piece_to = to.piece
        piece_from.move(to, validate=False)

    def get_all_possible_moves(self) -> List[Tile]:
        """ Returns a list of possible moves [(from_tile, to_tile), ...] """
        moves = []
        for piece in self.pieces.values():
            from_ = piece.tile
            moves.extend((from_, move) for move in piece.get_movements())
        return moves
    
    def filter_legal_moves(self, moves: List[Tile]) -> List[Tile]:
        ...


class Bot(Player): 
    def __init__(self, number: int, username: str, color: str):
        super().__init__(number, username, None, color, time=float("inf"), type="bot")

    def make_move(self, game: Game) -> None:
        """ Implements a basic bot move strategy. """
        possible_moves = self.get_all_possible_moves(game.board)
        
        if possible_moves:
            piece, move = random.choice(possible_moves)
            self.move(piece, move) 