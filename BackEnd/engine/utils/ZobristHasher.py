import random
from typing import Tuple

from engine.core.base.Board import Board
from engine.core.base.Tile import Tile
from engine.core.layer.LayerBoard import LayerBoard
from engine.core.layer.LayerTile import LayerTile
from engine.core.base.Pieces import PieceMovement


class ZobristHasher:
    _shared_table = None

    def __init__(self, 
                 num_piece_types: int = 6, 
                 num_players: int = 4, 
                 num_positions: int = 64, 
                 hash_size: int = 64, 
                 seed: int = 42) -> None:

        self.num_piece_types = num_piece_types
        self.num_players = num_players
        self.num_positions = num_positions
        self.hash_size = hash_size

        if ZobristHasher._shared_table is None:
            rng = random.Random(seed)
            ZobristHasher._shared_table = [
                [
                    [rng.getrandbits(hash_size) for _ in range(num_positions)]
                    for _ in range(num_players)
                ]
                for _ in range(num_piece_types)
            ]

        self.table = ZobristHasher._shared_table

    def compute_hash(self, state: Board | LayerBoard) -> int:
        h = 0
        for piece in state.pieces:
            if not piece.captured: 
                h ^= self.table[piece.type_id][piece.team.team][piece.position.id]
        return h

    def update_hash(self, old_hash: int, movement: PieceMovement) -> int: 
        piece = movement.piece
        from_ = movement.tile_from
        to_ = movement.tile_to

        old_hash ^= self.table[piece.type_id][piece.team.team][from_.id]
        old_hash ^= self.table[piece.type_id][piece.team.team][to_.id]

        if movement.captured_piece: 
            captured = movement.captured_piece
            old_hash ^= self.table[captured.type_id][captured.team.team][to_.id]

        if movement.castle_movement: 
            old_hash = self.update_hash(old_hash, movement.castle_movement)

        return old_hash
