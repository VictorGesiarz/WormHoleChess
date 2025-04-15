from typing import List, Dict, Tuple, Optional
import time

from engine.core.base.Board import Board
from engine.core.layer.LayerBoard import LayerBoard
from engine.core.base.Tile import Tile
from engine.core.layer.LayerTile import LayerTile
from engine.core.base.Pieces import Piece, PieceMovement
from engine.core.layer.LayerPieces import LayerPiece
from engine.core.Player import Player
from engine.core.constants import *
from engine.ai import * 


class Game:
    def __init__(self, board: Board | LayerBoard, players: List[Player], turn: int = COLOR_TO_NUMBER['white']) -> None:
        self.turn = turn 
        self.players = players
        self.number_of_players = len(players)
        self.board = board
        self.history = []

    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)

    def next_turn(self) -> None:
        self.turn = (self.turn + 1) % self.number_of_players

    def get_turn(self) -> int:
        """ Returns the current turn and -1 if the current player lost or is a bot """ 
        current_player = self.players[self.turn]
        if not current_player.alive:
            return -1
        if current_player.type == "bot":
            self.make_move_bot()
            return -1
        return self.turn

    def get_movements(self) -> List[Tuple[Tile | LayerTile]]: 
        """ Returns a list of possible movements for the current player. """
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

            self.check_player_state(player, legal_movements)
            return legal_movements + castles
        return []

    def filter_legal_moves(self, player: Player, moves: List[Tile | LayerTile]) -> List[Tile | LayerTile]:         
        legal_moves = []
        for move in moves:
            piece_movement = self.make_move(move, store=False) # Do not add to histroy
            if not self.is_in_check(player):
                legal_moves.append(move)
            self.undo_move(piece_movement, remove=False) # Do not remove from history
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

    def make_move(self, move: Tuple[Tile | LayerTile], store: bool = True) -> PieceMovement: 
        origin_tile = move[0]
        destination_tile = move[1]

        moving_piece = origin_tile.piece
        captured_piece = destination_tile.piece

        piece_movement = PieceMovement(moving_piece, origin_tile, destination_tile, moving_piece.first_move)
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

        if store: 
            self.history.append(piece_movement)

        return piece_movement

    def undo_move(self, piece_movement: PieceMovement, remove: bool = True) -> None: 
        piece_movement.piece.move(piece_movement.tile_from, validate=False)
        piece_movement.piece.first_move = piece_movement.first_move
        if piece_movement.captured_piece is not None:
            piece_movement.captured_piece.team.revive_piece(piece_movement.captured_piece)
            # self.killed_pieces.remove(captured_piece)
        if piece_movement.castle_movement: 
            self.undo_move(piece_movement.castle_movement, remove=False)    
        if piece_movement.killed_player: 
            self.revive_player(player=piece_movement.killed_player)

        if remove: 
            self.history.pop()

        return 

    def make_move_bot(self) -> None: 
        bot = self.players[self.turn]
        moves = self.get_movements()
        
        if len(moves) > 0: 
            move = bot.choose_move(moves)
            self.make_move(move)

    def check_player_state(self, player: Player, moves: List[Tile | LayerTile]) -> bool:
        if not player.alive: 
            return False
        if len(moves) == 0: 
            if self.is_in_check(player):
                self.kill_player(player, print_text="by checkmate")
            else: 
                self.kill_player(player, print_text="by stalemate")
            return False
        return True
    
    def kill_player(self, player: Player, print_text: str = None) -> None: 
        if print_text: print(f"{NUMBER_TO_COLOR[player.team]} loses {print_text}")
        player.alive = False

    def revive_player(self, player: Player) -> None: 
        player.alive = True
    
    def is_finished(self) -> bool: 
        alive_players = [player for player in self.players if player.alive]
        if len(alive_players) == 1: 
            print(f"Player {alive_players[0].team} wins!")
            return True
        return False

    def get_pieces_state(self) -> Dict[str, Dict[str, List[str]]]: 
        pieces_state = {}
        for player in self.players: 
            player_state = {}
            for piece_type, pieces in player.pieces.items(): 
                pieces_str = []
                for piece in pieces: 
                    if piece.captured: 
                        pieces_str.append(f"{piece.captured_position} (Captured)")
                    else: 
                        pieces_str.append(f"{piece.position}")
                player_state[piece_type] = pieces_str
            pieces_state[NUMBER_TO_COLOR[player.team]] = player_state
        return pieces_state
