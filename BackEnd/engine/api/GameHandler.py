from typing import List, Dict
import json 
import random
import time

from engine.core.ChessFactory import ChessFactory
from engine.core.Board import Board
from engine.core.Tile import D, Tile
from engine.core.Pieces import Piece, Tower, Knight, Bishop, Queen, King, Pawn
from engine.core.Player import Player, Bot
from engine.core.constants import *
from engine.ai import * 


board_file = './json/big_board_first_method.json'
initial_positions_file = './json/initial_position.json'


class Game:
    def __init__(self, players: List[Player], turn: int = 0, board_file: str = board_file, initial_positions_file: str = initial_positions_file) -> None:
        self.players = players 
        self.board = Board()
        self.turn = turn 
        
        self.turn_start_time = time.time()

        self.__populate_board(initial_positions_file)

    def __populate_board(self, initial_positions_file: str) -> None: 
        with open(initial_positions_file, 'r') as f: 
            positions = json.load(f)

        for player in self.players:
            pieces = {}
            player_pieces_positions = positions[player.color]

            for piece_name, position in player_pieces_positions.items(): 
                PieceObject = Piece.get_piece_type(piece_name)
                tile = self.board.tiles[position]
                piece = PieceObject(tile, player.color)
                pieces[piece_name] = piece
                self.board.add_piece(piece)
            
            player.pieces = pieces

    def is_player_in_game(self, player_id: str) -> bool:
        for player in self.players: 
            if player.type == "player" and player.id == player_id:
                return True
        return False

    def is_players_turn(self, player_id: str) -> bool:
        current_player = self.players[self.turn]
        return current_player.id == player_id

    def get_turn(self) -> str: 
        return NUMBER_TO_COLOR[self.turn]

    def get_current_player(self) -> Player:
        return self.players[self.turn]
    
    def check_time_expired(self) -> bool:
        """ Returns True if the current player's time has expired. """
        current_time = time.time()
        player = self.get_current_player()

        if player.type == "player":
            elapsed_time = current_time - self.turn_start_time
            if player.time_remaining - int(elapsed_time) <= 0:
                return True  
        return False

    def force_turn_timeout(self):
        """ Forces a player to lose due to time expiration. """
        player = self.get_current_player()

        if player.type == "player":
            player.alive = False  
            print(f"{player.username} lost due to timeout!") 

        self.next_turn()

    def next_turn(self) -> None: 
        """ Changes to the next turn, skipping dead players and handling bots. """
        self.turn = (self.turn + 1) % 4
        self.turn_start_time = time.time()  # Reset timer for the next player

        next_player = self.players[self.get_player_turn()]
        
        if not next_player.alive:
            self.next_turn()  # Skip dead players

        elif next_player.type == "bot":
            next_player.make_move(self)  # Bot makes a move instantly
            self.next_turn()