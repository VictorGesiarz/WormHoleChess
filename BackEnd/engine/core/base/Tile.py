from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

if TYPE_CHECKING:
    from engine.core.base.Pieces import Piece
    from engine.core.base.Board import Board


class D(Enum): 
    UP_LEFT = 0
    UP = 1
    UP_RIGHT = 2
    LEFT = 3
    RIGHT = 4
    DOWN_LEFT = 5
    DOWN = 6
    DOWN_RIGHT = 7
    ADDITIONAL_STRAIGHT = 8
    ADDITIONAL_DIAGONAL = 9


class Tile:
    relations = {
        D.UP_LEFT: [D.DOWN_RIGHT], D.UP: [D.DOWN], D.UP_RIGHT: [D.DOWN_LEFT],
        D.LEFT: [D.RIGHT], D.RIGHT: [D.LEFT],
        D.DOWN_LEFT: [D.UP_RIGHT], D.DOWN: [D.UP], D.DOWN_RIGHT: [D.UP_LEFT]
    }

    def __init__(self, 
                 name: str, row: int, col: int, board: Board, id: int, 
                 top_side: bool = True, pentagon: bool = False, loop: bool = False, piece: Piece = None) -> None:
        self.name = name
        self.row = row
        self.col = col
        self.board = board
        self.id = id
        self.top_side = top_side
        self.loop = loop 
        self.pentagon = pentagon
        self.piece = piece

        # Surrounding tiles
        self.neighbors = {
            D.UP_LEFT: None, D.UP: None, D.UP_RIGHT: None,
            D.LEFT: None, D.RIGHT: None,
            D.DOWN_LEFT: None, D.DOWN: None, D.DOWN_RIGHT: None
        }
        self.neighbors_inv = {}
        
        if self.pentagon: 
            self.additional_relations = {}

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: "Tile" | str | None) -> bool:
        if other is None: 
            return False
        if isinstance(other, str): 
            return self.name == other
        return self.name == other.name
    
    def __str__(self) -> str:
        return f"{self.name}"
    
    def __repr__(self):
        return f"{self.name}"

    def set_neighbors(self, neighbors: dict["Tile"]) -> None: 
        self.neighbors = neighbors
        self.make_neighbors_inv()

    def modify_neighbors(self, neighbors: dict["Tile"]) -> None:
        for direction, neighbor in neighbors.items():
            self.neighbors[direction] = neighbor
        self.make_neighbors_inv()

    def make_neighbors_inv(self) -> None: 
        self.neighbors_inv = {tile.name: direction for direction, tile in self.neighbors.items() if tile is not None}

    def set_relations(self, relations: dict[list["Tile"]]) -> None:
        if self.pentagon: 
            self.additional_relations = relations

    def set_piece(self, piece) -> None: 
        self.piece = piece
        piece.position = self

    def get_piece(self) -> Piece:
        return self.piece
    
    def remove_piece(self) -> None:
        if self.piece is not None: 
            self.piece.position = None
        self.piece = None