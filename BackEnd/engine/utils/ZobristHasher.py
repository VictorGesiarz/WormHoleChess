import random


class ZobristHasher:
    def __init__(self, num_piece_types, num_players, num_positions, include_turn=True, seed=42):
        self.num_piece_types = num_piece_types
        self.num_players = num_players
        self.num_positions = num_positions
        self.include_turn = include_turn
        random.seed(seed)
        self.table = [
            [
                [random.getrandbits(64) for _ in range(num_positions)]
                for _ in range(num_players)
            ]
            for _ in range(num_piece_types)
        ]
        if include_turn:
            self.turn_keys = [random.getrandbits(64) for _ in range(num_players)]

    def compute_hash(self, state):
        h = 0
        for piece in state.pieces:
            h ^= self.table[piece.type_id][piece.player_id][piece.position_id]
        if self.include_turn:
            h ^= self.turn_keys[state.current_player]
        return h

    def update_hash(self, old_hash, move, state):
        piece = move.piece
        old_hash ^= self.table[piece.type_id][piece.player_id][move.from_pos]
        old_hash ^= self.table[piece.type_id][piece.player_id][move.to_pos]
        # Update turn
        if self.include_turn:
            old_hash ^= self.turn_keys[state.previous_player]
            old_hash ^= self.turn_keys[state.current_player]
        return old_hash
