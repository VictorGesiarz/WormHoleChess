from typing import List, Dict, Tuple
import json 
import random
import time

from engine.core.base.Board import Board
from engine.core.base.Tile import D, Tile
from engine.core.base.Pieces import Piece, Tower, Knight, Bishop, Queen, King, Pawn
from engine.core.Player import Player, Bot
from engine.core.constants import *
from engine.ai import * 


initial_positions_file = './engine/core/assets/initial_position.json'


class Game:
    def __init__(self, players: List[Player], turn: int = COLOR_TO_NUMBER['white'], initial_positions_file: str = initial_positions_file) -> None:
        self.turn = turn 
        self.players = players
        self.board = Board()
        self.initialize_pieces(initial_positions_file)

    def initialize_pieces(self, initial_positions_file: str) -> None: 
        with open(initial_positions_file, 'r') as f: 
            positions_json = json.load(f)
        for player in self.players:
            player_pieces_positions = positions_json[NUMBER_TO_COLOR[player.team]]
            for piece_name, piece_positions in player_pieces_positions.items(): 
                for position in piece_positions: 
                    PieceObject = Piece.get_piece_type(piece_name)
                    tile = self.board[position]
                    piece = PieceObject(tile, player)

    def next_turn(self) -> None: 
        """ Changes to the next turn, skipping dead players and handling bots. """
        self.turn = (self.turn + 1) % 4

        next_player = self.players[self.turn]
        
        if not next_player.alive:
            self.next_turn()  # Skip dead players

        elif next_player.type == "bot":
            next_player.make_move(self)  # Bot makes a move instantly
            self.next_turn()

    def get_movements(self) -> List[Tile]: 
        """ Returns a list of possible movements for the current player. """
        player = self.players[self.turn]
        if player.alive: 
            movements = player.get_all_possible_moves()
            legal_movements = self.filter_legal_moves(player, movements)
            return legal_movements
        return []

    def filter_legal_moves(self, player: Player, moves: List[Tile]) -> List[Tile]:         
        legal_moves = []

        for move in moves:
            captured_piece = self.make_move(move)
            
            if not self.is_in_check(player):
                legal_moves.append(move)
            
            self.undo_move(move, captured_piece)

        self.check_player_state(player, legal_moves)
        return legal_moves

    def is_in_check(self, player: Player) -> bool: 
        for enemy_player in self.players: 
            if enemy_player.team != player.team:
                enemy_moves = enemy_player.get_all_possible_moves()
                for move in enemy_moves: 
                    oringin_tile = move[0]
                    destination_tile = move[1]
                    if destination_tile.piece == player.pieces['King'][0]:
                        return True
        return False

    def make_move(self, move: Tuple[Tile, Tile]) -> Piece | None: 
        origin_tile = move[0]
        destination_tile = move[1]
        
        moving_piece = origin_tile.piece
        captured_piece = destination_tile.piece

        # Check if piece is
        if captured_piece is not None and captured_piece.team != moving_piece.team:
            captured_piece.team.lose_piece(captured_piece)
            # self.killed_pieces.append(captured_piece)

        moving_piece.move(destination_tile, validate=False) # We do not need to validate, we expect the move to be already valid

        return captured_piece 

    def undo_move(self, move: Tuple[Tile, Tile], captured_piece: Piece | None) -> None: 
        origin_tile = move[0]
        destination_tile = move[1]

        moving_piece = destination_tile.piece 

        moving_piece.move(origin_tile, validate=False) # We do not need to validate, we expect the move to be already valid

        if captured_piece is not None:
            captured_piece.team.revive_piece(captured_piece)
            # self.killed_pieces.remove(captured_piece)

    def check_player_state(self, player: Player, moves: List[Tile]) -> bool:
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
