from __future__ import annotations
from typing import TYPE_CHECKING

from typing import List, Dict, Tuple
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from engine.core.layer.LayerPieces import LayerPiece
    from engine.core.layer.LayerBoard import LayerBoard


class LayerTile:
    def __init__(self, name: str, board: LayerBoard, id: int, piece: LayerPiece = None):
        self.name = name
        self.board = board
        self.id = id
        self.piece = piece

        self.tower_layer = TowerLayer()
        self.bishop_layer = BishopLayer()
        self.knight_layer = KnightLayer()
        self.queen_layer = QueenLayer()
        self.king_layer = KingLayer()
        self.pawn_layer = PawnLayer()

    def __eq__(self, other): 
        if other is None: 
            return False
        if isinstance(other, str): 
            return self.name == other
        return self.name == other.name
    
    def __str__(self):
        return f"{self.name}"
    
    def __repr__(self):  
        return f"{self.name}"
    
    def __hash__(self): 
        return hash(self.name)
    
    def set_layer(self, layer: Layer):
        match layer:
            case TowerLayer():
                self.tower_layer = layer
            case BishopLayer():
                self.bishop_layer = layer
            case KnightLayer():
                self.knight_layer = layer
            case QueenLayer():
                self.queen_layer = layer
            case KingLayer():
                self.king_layer = layer
            case PawnLayer():
                self.pawn_layer = layer


@dataclass
class Layer:
    pass

@dataclass
class TowerLayer(Layer):
    directions: List[List[LayerTile]] = field(default_factory=list)

    def copy(self, new_board: LayerBoard) -> TowerLayer: 
        return TowerLayer([[new_board[tile.name] for tile in direction] for direction in self.directions])

@dataclass
class KnightLayer:
    movements: List[LayerTile] = field(default_factory=list)

    def copy(self, new_board: LayerBoard) -> KnightLayer:
        return KnightLayer([new_board[tile.name] for tile in self.movements])

@dataclass
class BishopLayer: 
    directions: List[List[LayerTile]] = field(default_factory=list)

    def copy(self, new_board: LayerBoard) -> BishopLayer: 
        return BishopLayer([[new_board[tile.name] for tile in direction] for direction in self.directions])

@dataclass
class QueenLayer:
    directions: List[List[LayerTile]] = field(default_factory=list)

    def copy(self, new_board: LayerBoard) -> QueenLayer:
        return QueenLayer([[new_board[tile.name] for tile in direction] for direction in self.directions])

@dataclass
class KingLayer: 
    movements: List[LayerTile] = field(default_factory=list)
    pawn_possible_atacks: List[LayerTile] = field(default_factory=list)

    def copy(self, new_board: LayerBoard) -> KingLayer: 
        return KingLayer(
            [new_board[tile.name] for tile in self.movements], 
            [new_board[tile.name] for tile in self.pawn_possible_atacks]
        )

@dataclass
class PawnLayer: 
    moves: Dict[int, List[LayerTile]] = field(default_factory=dict)
    attacks: Dict[int, List[LayerTile]] = field(default_factory=dict)

    def copy(self, new_board: LayerBoard) -> PawnLayer: 
        return PawnLayer(
            {team: [new_board[tile.name] for tile in team_moves] for team, team_moves in self.moves.items()}, 
            {team: [new_board[tile.name] for tile in team_attacks] for team, team_attacks in self.attacks.items()}, 
        )
    