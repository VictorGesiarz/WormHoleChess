import json
import time
from typing import List, Dict, Tuple

from engine.utils.ZobristHasher import ZobristHasher
from engine.core.base.Board import Board
from engine.core.layer.LayerBoard import LayerBoard
from engine.core.base.Tile import Tile
from engine.core.layer.LayerTile import LayerTile
from engine.core.base.Pieces import PieceMovement
from engine.core.Player import Player
from engine.core.constants import *

from engine.ai.RandomAI import RandomAI
from engine.ai.MonteCarlo import MonteCarlo


class Game:
    def __init__(self, 
                 board: Board | LayerBoard, 
                 players: List[Player], 
                 program_mode: str = 'base', 
                 game_mode: str = 'wormhole',
                 max_turns: int = 120, 
                 turn: int = COLOR_TO_NUMBER['white'], 
                 verbose: int = 1) -> None:
        
        self.turn = turn 
        self.players = players
        self.number_of_players = len(players)
        self.program_mode = program_mode
        self.game_mode = game_mode
        self.game_state = GameState.PLAYING
        self.verbose = verbose

        self.board = board
        self.hasher = ZobristHasher()
        self.hash = self.hasher.compute_hash(self.board)

        self.bot_engines = {
            "random": RandomAI(self),
            "mcts": MonteCarlo(self)
        }

        self._cached_turn = None
        self._cached_movements = None
        self.history: List[PieceMovement] = []
        self.initial_positions = self.get_pieces_state()
        self.positions_counter = {self.hash: 1}
        self.max_turns = max_turns
        self.moves_count = 0
        self.moves_without_capture = 0
        self.killed_player = None

    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)

    def copy(self) -> 'Game': 
        board_copy = self.board.copy()
        players_copy = [player.copy() for player in self.players]

        for piece in self.board.pieces: 
            # We don't have to do anything with the piece copy, just create it 
            piece_copy = piece.copy(board_copy, players_copy)

        # For now we don't care about copying the history and the initial positions cause we won't be using that, we just have to be able to simulate games from the current state without modifying the original game. 
        game_copy = Game(board_copy, players_copy, self.turn, verbose=0) # We dont want to print anything in the copy
        return game_copy

    def next_turn(self) -> None:
        self.turn = (self.turn + 1) % self.number_of_players

    def get_turn(self, auto_play_bots=True) -> int:
        """ Returns the current turn and -1 if the current player lost or is a bot """ 
        current_player = self.players[self.turn]
        if not current_player.alive:
            return -1
        if not self.check_player_state(current_player, self.get_movements()): 
            return -1
        if current_player.type == "bot":
            if auto_play_bots: 
                self.make_move_bot()
        return self.turn

    def get_movements(self) -> List[Tuple[Tile | LayerTile]]: 
        """ Returns a list of possible movements for the current player. """
        if self._cached_turn == self.turn and self._cached_movements is not None:
            return self._cached_movements
    
        player = self.players[self.turn]
        if player.alive: 
            movements = player.get_possible_moves()
            legal_movements = self.filter_legal_moves(player, movements)
            
            castles = []
            if not self.is_in_check(player): 
                king = player.pieces['King'][0]
                castling_moves = king.get_castle_movements()
                for castle_side in castling_moves: 
                    legal_castle = self.filter_legal_moves(player, castle_side)
                    if len(castle_side) == len(legal_castle):
                        castles.append(castle_side[0])
            computed_result = legal_movements + castles
        else: 
            computed_result = []

        self._cached_turn = self.turn
        self._cached_movements = computed_result
        return computed_result

    def filter_legal_moves(self, player: Player, moves: List[Tile | LayerTile]) -> List[Tile | LayerTile]:         
        legal_moves = []
        for move in moves:
            piece_movement = self.make_move(move, store=False, update_hash=False) # Do not add to histroy
            if not self.is_in_check(player):
                legal_moves.append(move)
            self.undo_move(piece_movement, remove=False, update_hash=False) # Do not remove from history
        return legal_moves

    def is_in_check(self, player: Player) -> bool: 
        if PARAMETERS['cast_from_king']:
            king = player.pieces['King'][0]
            return king.trace_from_king()
        else: 
            for enemy_player in self.players: 
                if enemy_player != player and enemy_player.alive:
                    enemy_moves = enemy_player.get_possible_moves()
                    for move in enemy_moves: 
                        oringin_tile = move[0]
                        destination_tile = move[1]
                        if destination_tile.piece == player.pieces['King'][0]:
                            return True
        return False

    def make_move(self, move: Tuple[Tile | LayerTile], store: bool = True, update_hash: bool = True) -> PieceMovement: 
        origin_tile = move[0]
        destination_tile = move[1]

        moving_piece = origin_tile.piece
        captured_piece = destination_tile.piece

        piece_movement = PieceMovement(moving_piece, origin_tile, destination_tile, moving_piece.first_move, self.moves_without_capture)
        if captured_piece is not None and captured_piece.team != moving_piece.team:
            captured_piece.team.lose_piece(captured_piece)
            piece_movement.captured_piece = captured_piece

            # If we capture a king (when a player makes a movement where leaves us making check to another player) 
            if captured_piece.type == 'King' and captured_piece.team.alive: 
                piece_movement.killed_player = captured_piece.team
                self.kill_player(player=captured_piece.team, print_text=f"eaten by {NUMBER_TO_COLOR[moving_piece.team.team]}" if store else None)

        moving_piece.move(destination_tile, validate=False) # We do not need to validate, we expect the move to be already valid

        if len(move) == 4: # It is a castle
            rook_origin_tile = move[2]
            rook_destination_tile = move[3]
            rook = rook_origin_tile.piece
            piece_movement.castle_movement = PieceMovement(rook, rook_origin_tile, rook_destination_tile, rook.first_move)
            rook.move(rook_destination_tile, validate=False)

        if update_hash: 
            self.hash = self.hasher.update_hash(self.hash, piece_movement)

        if store: 
            self.moves_count += 1
            if captured_piece is not None: 
                self.moves_without_capture = 0
            else: 
                self.moves_without_capture += 1
            self.history.append(piece_movement)
            self.positions_counter[self.hash] = self.positions_counter.get(self.hash, 0) + 1

        return piece_movement

    def undo_move(self, piece_movement: PieceMovement, remove: bool = True, update_hash: bool = True) -> None: 
        if remove: 
            self.moves_count -= 1
            self.history.pop()
            self.positions_counter[self.hash] -= 1
            self.moves_without_capture = piece_movement.moves_without_capture
        
        if update_hash: 
            self.hash = self.hasher.update_hash(self.hash, piece_movement)

        piece_movement.piece.move(piece_movement.tile_from, validate=False)
        piece_movement.piece.first_move = piece_movement.first_move
        if piece_movement.captured_piece is not None:
            piece_movement.captured_piece.team.revive_piece(piece_movement.captured_piece)
        if piece_movement.castle_movement: 
            self.undo_move(piece_movement.castle_movement, remove=False, update_hash=update_hash)    
        if piece_movement.killed_player: 
            self.revive_player(player=piece_movement.killed_player)

    def make_move_bot(self) -> None: 
        bot = self.players[self.turn]
        engine = self.bot_engines[bot.difficulty]
        move = engine.choose_move()
        self.make_move(move)

    def check_player_state(self, player: Player, moves: List[Tile | LayerTile]) -> bool:
        if not player.alive: 
            return False
        self.killed_player = None
        if len(moves) == 0: 
            if self.is_in_check(player):
                self.kill_player(player, print_text="by checkmate")
            else: 
                alive_players = [player for player in self.players if player.alive]
                if len(alive_players) > 2: # If there are more than 2 players, a stalemate is losing for that player. When there are only 2 players, it is a draw
                    self.kill_player(player, print_text="by stalemate")
                else: 
                    self.game_state = GameState.DRAW
            return False
        return True
    
    def kill_player(self, player: Player, print_text: str = None) -> None: 
        if print_text and self.verbose > 0: 
            print(f"{NUMBER_TO_COLOR[player.team]} loses {print_text}")
        player.alive = False
        self.killed_player = player.color

    def revive_player(self, player: Player) -> None: 
        player.alive = True
    
    def is_finished(self) -> bool: 
        if self.game_state in [GameState.PLAYER_WON, GameState.DRAW]:
            return True
        
        if self.moves_count >= self.max_turns:
            self.game_state = GameState.DRAW
            return True
    
        # If only one player is alive, the game is finished
        alive_players = [player for player in self.players if player.alive]
        if len(alive_players) == 1: 
            if self.verbose > 0: print(f"Player {alive_players[0].team} wins!")
            self.game_state = GameState.PLAYER_WON
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

        piece_counts = {
            'Knight': 0,
            'Queen': 0,
            'Tower': 0,
            'Bishop': 0,
            'King': 0,
            'Pawn': 0
        }

        for piece in pieces:
            if not piece.captured:
                piece_counts[piece.type] += 1

        if piece_counts == {'Knight': 0, 'Queen': 0, 'Tower': 0, 'Bishop': 0, 'King': 2, 'Pawn': 0}:
            return True

        if piece_counts['Queen'] == piece_counts['Tower'] == piece_counts['Pawn'] == 0:
            if piece_counts['Bishop'] + piece_counts['Knight'] == 1:
                return True
                
        return False

    def winner(self) -> int: 
        if self.game_state != GameState.PLAYER_WON: 
            return -1 
        alive_players = [player for player in self.players if player.alive]
        if len(alive_players) == 1: 
            return alive_players[0].team
        return -1

    def get_pieces_state(self) -> Dict[str, Dict[str, List[str]]]: 
        pieces_state = {}
        for player in self.players: 
            player_state = {}
            for piece_type, pieces in player.pieces.items(): 
                pieces_str = []
                for piece in pieces: 
                    if piece.captured: 
                        pieces_str.append(None)
                    else: 
                        pieces_str.append(f"{piece.position}")
                player_state[piece_type] = pieces_str
            pieces_state[NUMBER_TO_COLOR[player.team]] = player_state
        return pieces_state

    def get_state(self) -> List[List[str]]: 
        """ USED FOR THE FRONTEND """
        pieces = []
        for player in self.players: 
            for piece_type, pieces_list in player.pieces.items():
                for piece in pieces_list:
                    if not piece.captured:
                        team = NUMBER_TO_COLOR[player.team] if player.alive else 'dead'
                        pieces.append([piece_type.lower(), team, piece.position.name])
        return pieces

    def get_game_history(self) -> List[Dict[str, str]]: 
        history = []
        for move in self.history: 
            move_dict = {
                'from': move.tile_from.name,
                'to': move.tile_to.name, 
                'moving_piece': {
                    'type': move.piece.type,
                    'color': NUMBER_TO_COLOR[move.piece.team.team]
                }, 
                'captured_piece': None if move.captured_piece is None else {
                    'type': move.captured_piece.type, 
                    'color': NUMBER_TO_COLOR[move.captured_piece.team.team]
                }, 
                'killed_player': None if move.killed_player is None else {
                    'color': NUMBER_TO_COLOR[move.killed_player.team]
                }
            }
            history.append(move_dict)
        return history
    
    def export(self, export_path: str) -> None: 
        game_data = {
            'pieces_state': self.initial_positions,
            'game_history': self.get_game_history()
        }

        with open(export_path, 'w') as f:
            json.dump(game_data, f, indent=4)

    def valid_move(self, from_tile: str, to_tile: str) -> bool:
        """ Validates if a move is valid for the current player. """
        movements = self.get_movements()
        for move in movements:
            if move[0].name == from_tile and move[1].name == to_tile:
                return True
        return False
    
    def translate_movement(self, from_tile: str, to_tile: str) -> Tuple[Tile | LayerTile, Tile | LayerTile]:
        """ Translates a movement from tile names to Tile objects. """
        movements = self.get_movements()
        for move in movements:
            if move[0].name == from_tile and move[1].name == to_tile:
                return move
        raise ValueError(f"Invalid movement from {from_tile} to {to_tile}")