import numpy as np
import time
import json
from typing import List, Tuple

from engine.core.matrices.MatrixBoard import LayerMatrixBoard
from engine.utils.ZobristHasherMatrices import ZobristHasher
from engine.core.matrices.chess_logic_bounds import (
    get_possible_moves, 
    filter_legal_moves, 
    is_in_check, 
    make_move,
    undo_move
)
from engine.core.matrices.matrix_constants import * 
from engine.core.constants import * 

from engine.agents.RandomAI import RandomAI
from engine.agents.MonteCarlo import MonteCarlo
from engine.agents.MonteCarloParallel import MonteCarloParallel


class GameMatrices: 
    def __init__(self, 
                 board: LayerMatrixBoard,
                 players: np.ndarray,
                 turn: int, 
                 program_mode: str = 'matrix', 
                 verbose: int = 0,
                 hasher: ZobristHasher = None, 
                 max_turns: int = 120): 
    
        self.players = players
        self.number_of_players = len([p for p in players if p['color'] != 'none'])
        self.rewards = [0] * self.number_of_players
        self.turn = turn 
        self.program_mode = program_mode
        self.verbose = verbose
        self.game_state = GameState.PLAYING
        
        self.board = board
        self.hasher = ZobristHasher() if hasher is None else hasher
        self.hash = self.hasher.compute_hash(self.board.pieces)

        self.bot_engines = {
            1: RandomAI(self),
            2: MonteCarlo(self),
            3: MonteCarloParallel(self), 
        }

        self._cached_turn = None
        self._recalculate = True
        self._cached_movements = np.empty((MAX_POSSIBLE_MOVES, 2), dtype=np.uint8) # With margin (to optimize move calculation, instead of creating a new array each time)
        self._cached_hashes = np.empty(MAX_POSSIBLE_MOVES, dtype=np.uint64)
        self._cached_count = np.zeros(1, dtype=np.uint8)

        self.history = np.zeros((max_turns, 7), dtype=np.int16) # [[moving_piece_index, from_tile, to_tile, captured_piece_index, first_move, original_type, new_type]]
        self.initial_positions = self.board.pieces.copy()
        self.positions_counter = {self.hash: 1}
        self.max_turns = max_turns
        self.moves_count = 0
        self.moves_without_capture = 0
        self.killed_player = None

    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)

    def copy(self) -> 'GameMatrices':
        game_copy = GameMatrices(self.board.copy(), self.players.copy(), self.turn, hasher=self.hasher, max_turns=self.max_turns)
        game_copy.history = self.history.copy()
        game_copy.positions_counter = self.positions_counter.copy()
        game_copy.moves_count = self.moves_count
        game_copy.moves_without_capture = self.moves_without_capture
        return game_copy

    def reset(self) -> None: 
        ... 

    def next_turn(self) -> None: 
        self.turn = (self.turn + 1) % self.number_of_players
        self._recalculate = True

    def get_turn(self, auto_play_bots=True) -> int: 
        if not self.players[self.turn]['is_alive']:
            return -1
        elif not self.check_player_state(self.players[self.turn], self.get_movements()):
            return -1 
        elif self.players[self.turn]['opponent_type'] != 0 and auto_play_bots: 
            self.make_move_bot()
        
        return self.turn
    
    def get_movements(self, include_hashes: bool = False) -> np.array:
        if self._cached_turn == self.turn and not self._recalculate: 
            if include_hashes:
                return (
                    self._cached_movements[:self._cached_count[0]],
                        self._cached_hashes[:self._cached_count[0]]
                    )
            else:   
                return self._cached_movements[:self._cached_count[0]]

        
        if self.players[self.turn]['is_alive']: 
            team = self.players[self.turn]['team']
            self.get_possible_moves(team)
            self.filter_legal_moves(team)
            
            # If possible, implement Castles in the future 
            result = self._cached_movements[:self._cached_count[0]]
        else:
            result = []
        
        if include_hashes:
            result = (
                self._cached_movements[:self._cached_count[0]],
                    self._cached_hashes[:self._cached_count[0]]
                )

        self._cached_turn = self.turn 
        self._recalculate = False
        return result
                        
    def get_possible_moves(self, player: int) -> None:
        b = self.board
        get_possible_moves(
            player, 
            b.nodes, 
            b.pieces,
            b.adjacency_list,
            b.patterns_offsets, 
            b.pieces_offsets,
            b.tiles_offsets,
            self._cached_movements, 
            self._cached_count
        )
    
    def filter_legal_moves(self, player: int) -> None:
        b = self.board
        filter_legal_moves(
            player, 
            b.nodes, 
            b.pieces,
            b.adjacency_list,
            b.patterns_offsets, 
            b.pieces_offsets,
            b.tiles_offsets,
            self._cached_movements, 
            self._cached_count,
            self.history, 
            self.moves_count,
            self.board.promotion_zones,
            self.hash, 
            self._cached_hashes, 
            self.hasher.table
        )
    
    def is_in_check(self, player: int) -> bool: 
        b = self.board
        king_tile = None
        for i in range(b.pieces.shape[0]):
            if b.pieces[i, 0] == 3 and b.pieces[i, 1] == player:
                if not b.pieces[i, 4] == 0: 
                    print("Erorr at", player, b.pieces[i], b.node_names[b.pieces[i, 2]])
                    raise RuntimeError("King is dead¿?")
                king_tile = b.pieces[i, 2]
                break

        if king_tile is None:
            raise RuntimeError("King not found for player:", player)

        return is_in_check(
            player, 
            king_tile, 
            b.nodes,
            b.pieces, 
            b.adjacency_list, 
            b.patterns_offsets, 
            b.pieces_offsets, 
            b.tiles_offsets, 
            np.empty((MAX_POSSIBLE_MOVES, 2), dtype=np.uint8)
        )

    def make_move(self, move: np.array, store: bool = True, precomputed_hash: int = 0) -> None: 
        make_move(
            move, 
            self.board.nodes, 
            self.board.pieces, 
            self.history, 
            self.moves_count, 
            self.board.promotion_zones,
            store
        )

        if precomputed_hash: 
            self.hash = precomputed_hash
        else: 
            self.hash = self.hasher.update_hash(self.hash, self.history[self.moves_count], self.board.pieces)

        if store: 
            moving_piece, from_, to, captured_piece_index, _, _, _ = self.history[self.moves_count]
            self.moves_without_capture += 1
            if captured_piece_index != -1: 
                self.moves_without_capture = 0
                captured_piece = self.board.pieces[captured_piece_index]
                if captured_piece[0] == 3: # If a king is a captured
                    player = captured_piece[1]
                    self.kill_player(self.players[player], print_text="by capture")
                    
                    if self.number_of_players == 2:
                        raise RuntimeError("KING CAPTURED", self.board.node_names[from_], self.board.node_names[to])
            self.positions_counter[self.hash] = self.positions_counter.get(self.hash, 0) + 1
            self.moves_count += 1

    def undo_move(self, remove: bool = True) -> None: 
        if remove:
            # This should also remove one from position counter, restore moves without capture, etc. 
            self.moves_count -= 1
        undo_move(
            self.board.nodes,
            self.board.pieces, 
            self.history, 
            self.moves_count
        )
        self.hash = self.hasher.update_hash(self.hash, self.history[self.moves_count], self.board.pieces)

    def make_move_bot(self) -> None: 
        bot = self.players[self.turn]
        engine = self.bot_engines[bot['opponent_type']]
        move = engine.choose_move()
        if move is not None: 
            self.make_move(move)
            return move 

    def check_player_state(self, player: np.array, moves: np.array) -> bool:
        if not player['is_alive']: 
            return False
        self.killed_player = None
        if len(moves) == 0: 
            if self.is_in_check(player['team']):
                self.kill_player(player, print_text="by checkmate")
            else: 
                alive_players = [player for player in self.players if player['is_alive']]
                if len(alive_players) > 2: # If there are more than 2 players, a stalemate is losing for that player. When there are only 2 players, it is a draw
                    self.kill_player(player, print_text="by stalemate")
                else: 
                    self.game_state = GameState.DRAW
            return False
        return True
    
    def kill_player(self, player: int, print_text: str = None) -> None: 
        if print_text and self.verbose > 0: 
            print(f"{player['color']} loses {print_text}")
        player['is_alive'] = False
        self.killed_player = player['color']
        self.rewards[player['id']] = -1 

    def revive_player(self, player: int) -> None: 
        player['is_alive'] = True
    
    def is_finished(self) -> bool: 
        if self.game_state in [GameState.PLAYER_WON, GameState.DRAW]:
            # Don't need to update player states cause already 0 
            # Only when a player dies or wins. 
            return True
        
        if self.moves_count >= self.max_turns:
            self.game_state = GameState.DRAW
            return True
    
        # If only one player is alive, the game is finished
        alive_players = [player for player in self.players if player['is_alive']]
        if len(alive_players) == 1: 
            if self.verbose > 0: print(f"Player {alive_players[0]['id']} wins!")
            self.game_state = GameState.PLAYER_WON
            self.rewards[alive_players[0]['id']] = 1
            return True
        
        if self.is_dead_position() or self.is_draw_by_repetition() or self.is_draw_by_50_moves(): 
            if self.verbose > 0: print("Game is a draw")
            self.game_state = GameState.DRAW
            return True

        return False

    def is_draw_by_repetition(self) -> bool:
        return self.positions_counter.get(self.hash, 0) >= 3

    def is_draw_by_50_moves(self) -> bool: 
        return self.moves_without_capture >= MAX_MOVES_WITHOUT_CAPTURE * self.number_of_players

    def is_dead_position(self) -> bool:
        pieces = list(self.board.pieces)

        piece_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for piece in pieces:
            if not piece[4]:
                piece_counts[piece[0]] = piece_counts.get(piece[0], 0) + 1

        if piece_counts == {0: 0, 1: 0, 2: 0, 3: 2, 4: 0, 5: 0}:
            return True

        if piece_counts[5] == piece_counts[0] == piece_counts[4] == 0:
            if piece_counts[2] + piece_counts[1] == 1:
                return True
                
        return False

    def winner(self) -> int: 
        if self.game_state != GameState.PLAYER_WON: 
            return -1 
        alive_players = [player for player in self.players if player['is_alive']]
        if len(alive_players) == 1: 
            return alive_players[0]['id']
        return -1

    def print_last_move(self) -> None: 
        print("Move made:", self.board.get_names(self.history[self.moves_count-1][1:3]))
        
    def get_last_move(self) -> Tuple[str, str, str]: 
        if self.moves_count == 0:
            return None, None, None
        move = self.history[self.moves_count-1]
        from_tile = self.board.get_names([move[1]])[0]
        to_tile = self.board.get_names([move[2]])[0]
        piece_name = PIECE_TYPES[self.board.pieces[move[0]][0]]
        return piece_name, from_tile, to_tile

    def print_moves(self) -> None: 
        moves = self.get_movements()
        for i, move in enumerate(moves): 
            print(f'{i+1}: {self.board.get_names(move)}')

    def print_history(self) -> None:
        for i, move in enumerate(self.history[:self.moves_count-1, 1:3]): 
            print(f'{i}: {self.board.get_names(move)}')

    def export(self, file: str) -> None: 
        moves = {}
        for i, move in enumerate(self.history[:self.moves_count-1, 1:3]): 
            moves[i] = self.board.get_names(move)
        with open(file, 'w') as f: 
            json.dump(moves, f, indent=4)

    def get_state(self, yaml: bool = False): 
        pieces = []
        current_player = -1
        current_piece = 0
        yaml_txt = ''
        for piece in self.board.pieces: 
            if piece[0] == -1 or piece[4]: 
                continue
            
            if piece[1] != current_player: 
                current_player = piece[1]
                yaml_txt += f'\n{self.players[piece[1] % self.number_of_players]['color']}:'
            if piece[0] != current_piece: 
                current_piece = piece[0]
                yaml_txt += f'\n{PIECE_TYPES[piece[0]]}: '

            type_ = PIECE_TYPES[piece[0]].lower()

            player = self.players[piece[1] % self.number_of_players]
            if player['is_alive']:
                yaml_txt += f'{self.board.get_names([piece[2]])[0].replace('_', '')} '
                player_color = player['color']
            else: 
                player_color = "dead"

            tile = self.board.get_names([piece[2]])[0]
            pieces.append([type_, player_color, tile])
        
        if yaml: 
            print(yaml_txt)
        return pieces
    
    def valid_move(self, from_tile: str, to_tile: str) -> bool:   
        movements = self.get_movements()
        for move in movements:
            if self.board.get_names(move) == [from_tile, to_tile]:
                return True
        return False
    
    def translate_movement(self, from_tile: str, to_tile: str) -> np.array:
        movements = self.get_movements()
        for move in movements:
            if self.board.get_names(move) == [from_tile, to_tile]:
                return move
        raise ValueError(f"Invalid move from {from_tile} to {to_tile}")
    
    def translate_movement_to_str(self, move: np.array) -> Tuple[str, str]: 
        return self.board.get_names(move)