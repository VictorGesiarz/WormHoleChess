import numpy as np
import random


class ZobristHasher:
    _shared_table = None

    def __init__(self, 
                 num_piece_types: int = 6, 
                 num_players: int = 4, 
                 num_positions: int = 144, 
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
            ZobristHasher._shared_table = np.array(ZobristHasher._shared_table, dtype=np.uint64)

        self.table = ZobristHasher._shared_table

    def compute_hash(self, pieces: np.array) -> int:
        h = 0
        for piece in pieces: 
            if piece[0] != -1 and not piece[4]: 
                h ^= self.table[piece[0]][piece[1]][piece[2]]
        return h

    def update_hash(self, old_hash: int, movement: np.array, pieces: np.array) -> int: 
        moving_piece_index, origin_tile, destination_tile, captured_piece_index, _, original_type = movement

        piece = pieces[moving_piece_index]
        current_type = piece[0]
        color = piece[1]

        old_hash ^= self.table[original_type][color][origin_tile]
        old_hash ^= self.table[current_type][color][destination_tile]

        if captured_piece_index != -1: 
            captured_piece = pieces[captured_piece_index]
            old_hash ^= self.table[captured_piece[0]][captured_piece[1]][destination_tile]

        return old_hash
    