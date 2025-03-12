from typing import List, Dict
import json 

from core.chess_logic import D, Tile, Board
from core.pieces import Tower, Knight, Bishop, Queen, King, Pawn
from core.ai import * 




class GameManager:
	def __init__(self) -> None:
		pass


class Game:
    def __init__(self, game_id: str, players: List[str], initial_state: Dict):
        self.game_id = game_id
        self.players = players 
        self.state = initial_state

        print(game_id)

    def is_player_in_game(self, username):
        return username in self.players


class Player:
    def __init__(self, player_id, name, color):
        self.player_id = player_id
        self.name = name
        self.color = color
        self.pieces = {}
        self.is_in_check = False

    def loose_piece(self, piece):
        self.pieces.remove(piece)