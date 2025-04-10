from typing import List, Dict
import json 
import random
import time

from engine.core.base.Board import Board
from engine.core.base.Tile import D, Tile
from engine.core.base.Pieces import Piece, Tower, Knight, Bishop, Queen, King, Pawn
from engine.core.Player import Player, Bot
from engine.core.constants import *
from engine.ai import * 


board_file = './json/big_board_first_method.json'
initial_positions_file = './json/initial_position.json'


class Game:
    def __init__(self, players: List[Player], turn: int = COLOR_TO_NUMBER['white'], board_file: str = board_file, initial_positions_file: str = initial_positions_file) -> None:
        self.turn = turn 
        self.players = players
        self.board = Board()
        self.initialize_pieces(initial_positions_file)
        print(self.players[0].pieces)

    def initialize_pieces(self, initial_positions_file: str) -> None: 
        with open(initial_positions_file, 'r') as f: 
            positions = json.load(f)
        for player in self.players:
            player_pieces_positions = positions[NUMBER_TO_COLOR[player.team]]
            for piece_name, position in player_pieces_positions.items(): 
                PieceObject = Piece.get_piece_type(piece_name)
                tile = self.board[position]
                piece = PieceObject(tile, player)

    def next_turn(self) -> None: 
        """ Changes to the next turn, skipping dead players and handling bots. """
        self.turn = (self.turn + 1) % 4
        self.turn_start_time = time.time()  # Reset timer for the next player

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
            legal_movements = player.filter_legal_moves(movements)
            return legal_movements
        return []

    def get_pieces_state(self) -> Dict[str, Dict[str, List[str]]]: 
        pieces_state = {}
        for player in self.players: 
            pieces_state[player.color] = {
                "pawn": [piece.name for piece in player.pieces if piece.type == "Pawn"], 
                "tower": [piece.name for piece in player.pieces if piece.type == "Tower"],
                "knight": [piece.name for piece in player.pieces if piece.type == "Knight"],
                "bishop": [piece.name for piece in player.pieces if piece.type == "Bishop"],
                "queen": [piece.name for piece in player.pieces if piece.type == "Queen"],
                "king": [piece.name for piece in player.pieces if piece.type == "King"]
            }
        return pieces_state
