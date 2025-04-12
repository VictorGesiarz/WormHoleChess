from typing import List, Dict, Tuple
import json 
import random
import time

from engine.core.base.Board import Board
from engine.core.layer.LayerBoard import LayerBoard
from engine.core.base.Tile import Tile
from engine.core.layer.LayerTile import LayerTile
from engine.core.base.Pieces import Piece
from engine.core.layer.LayerPieces import LayerPiece
from engine.core.Player import Player, Bot
from engine.core.constants import *
from engine.ai import * 


class Game:
    def __init__(self, board: Board, players: List[Player], turn: int = COLOR_TO_NUMBER['white']) -> None:
        self.turn = turn 
        self.players = players
        self.number_of_players = len(players)
        self.board = board

    def check_size(self) -> None:
        from pympler import asizeof
        print(f"Game size: {asizeof.asizeof(self)} bytes")

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
            movements = player.get_all_possible_moves()
            legal_movements = self.filter_legal_moves(player, movements)
            self.check_player_state(player, legal_movements)
            return legal_movements
        return []

    def filter_legal_moves(self, player: Player, moves: List[Tile | LayerTile]) -> List[Tile | LayerTile]:         
        legal_moves = []

        for move in moves:
            captured_piece = self.make_move(move)
            
            if not self.is_in_check(player):
                legal_moves.append(move)
            
            self.undo_move(move, captured_piece)

        return legal_moves

    def is_in_check(self, player: Player, trace_from_king=False) -> bool: 
        if trace_from_king:
            ...
        else: 
            for enemy_player in self.players: 
                if enemy_player.team != player.team:
                    enemy_moves = enemy_player.get_all_possible_moves()
                    for move in enemy_moves: 
                        oringin_tile = move[0]
                        destination_tile = move[1]
                        if destination_tile.piece == player.pieces['King'][0]:
                            return True
        return False

    def make_move(self, move: Tuple[Tile | LayerTile]) -> Piece | LayerPiece | None: 
        origin_tile = move[0]
        destination_tile = move[1]
        
        moving_piece = origin_tile.piece
        captured_piece = destination_tile.piece

        if captured_piece is not None and captured_piece.team != moving_piece.team:
            captured_piece.team.lose_piece(captured_piece)
            # self.killed_pieces.append(captured_piece)

        moving_piece.move(destination_tile, validate=False) # We do not need to validate, we expect the move to be already valid

        return captured_piece 

    def undo_move(self, move: Tuple[Tile | LayerTile], captured_piece: Piece | LayerPiece | None) -> None: 
        origin_tile = move[0]
        destination_tile = move[1]

        moving_piece = destination_tile.piece 

        moving_piece.move(origin_tile, validate=False) # We do not need to validate, we expect the move to be already valid

        if captured_piece is not None:
            captured_piece.team.revive_piece(captured_piece)
            # self.killed_pieces.remove(captured_piece)

    def make_move_bot(self) -> None: 
        player = self.players[self.turn]
        moves = self.get_movements()
        
        if len(moves) > 0: 
            move = player.choose_move(moves)
            self.make_move(move)

    def check_player_state(self, player: Player, moves: List[Tile | LayerTile]) -> bool:
        if not player.alive: 
            return False
        if len(moves) == 0: 
            if self.is_in_check(player):
                print(f"Player {player.team} is in checkmate!")
            else: 
                print(f"Player {player.team} is in stalemate!")
            player.alive = False
            return False
        return True
    
    def is_finished(self) -> bool: 
        alive_players = [player for player in self.players if player.alive]
        if len(alive_players) == 1: 
            print(f"Player {alive_players[0].team} wins!")
            return True
        return False

    def get_pieces_state(self) -> Dict[str, Dict[str, List[str]]]: 
        pieces_state = {}
        for player in self.players: 
            pieces_state[player.color] = {
                "pawn": [piece.position.name for piece in player.pieces if piece.type == "Pawn"], 
                "tower": [piece.position.name for piece in player.pieces if piece.type == "Tower"],
                "knight": [piece.position.name for piece in player.pieces if piece.type == "Knight"],
                "bishop": [piece.position.name for piece in player.pieces if piece.type == "Bishop"],
                "queen": [piece.position.name for piece in player.pieces if piece.type == "Queen"],
                "king": [piece.position.name for piece in player.pieces if piece.type == "King"]
            }
        return pieces_state
