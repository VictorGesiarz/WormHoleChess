from typing import Literal, List, Dict, Tuple
import json

from engine.core.base.Board import Board
from engine.core.layer.LayerBoard import LayerBoard
from engine.core.base.Pieces import Piece
from engine.core.layer.LayerPieces import LayerPiece
from engine.core.Player import Player
from engine.ai.BOT import Bot
from engine.core.Game import Game
from engine.core.constants import COLOR_TO_NUMBER, NUMBER_TO_COLOR


initial_positions_4_players = './engine/core/assets/initial_positions/4_players.json'
initial_positions_2_players = './engine/core/assets/initial_positions/2_players.json'


class ChessFactory:
    @staticmethod
    def create_game(player_data: List[str],
                    mode: str = Literal['base', 'layer'],
                    size: str = Literal['big', 'small'],
                    initial_positions: str | Dict[str, str] = None) -> Game:
        
        board = ChessFactory.create_board(mode, size)
        players = ChessFactory.create_players(player_data)
        
        if initial_positions is None: 
            initial_positions = ChessFactory.load_initial_positions(initial_positions_2_players if len(players) == 2 else initial_positions_4_players)
        elif isinstance(initial_positions, str):
            initial_positions = ChessFactory.load_initial_positions(initial_positions)
        ChessFactory.initialize_pieces(board, players, initial_positions, mode)
        
        return Game(board, players, turn=0)
    
    @staticmethod
    def initialize_pieces(board: Board, players: List[Player], initial_positions: str, mode: str) -> None: 
        for player in players:
            player_pieces_positions = initial_positions[NUMBER_TO_COLOR[player.team]]
            for piece_name, piece_positions in player_pieces_positions.items(): 
                for position in piece_positions: 
                    tile = board[position]
                    ChessFactory.create_piece(piece_name, mode, tile, player)
    
    @staticmethod
    def create_players(player_data: List[Tuple[str]]) -> List[Player]:
        number_of_players = len(player_data)
        if number_of_players not in (2, 4):
            raise ValueError("Number of players must be 2 or 4")
        
        players = []
        for data in player_data:
            if data[1] == "player": 
                player = Player(COLOR_TO_NUMBER[data[0]])
            elif data[1] == "bot":
                player = Bot(COLOR_TO_NUMBER[data[0]], data[2])
            players.append(player)
        return players
    
    @staticmethod
    def create_bot_data(num_bots: int = 4) -> List[Tuple[str]]: 
        if num_bots == 4:
            return [
                ("white", "bot", "random"),
                ("black", "bot", "random"),
                ("blue", "bot", "random"),
                ("red", "bot", "random"),
            ]
        return [
            ("white", "bot", "random"),
            ("red", "bot", "random"),
        ]
    
    @staticmethod
    def create_player_data(num_players: int = 4) -> List[Tuple[str]]: 
        if num_players == 4: 
            return [
                ("white", "player"),
                ("black", "player"),
                ("blue", "player"),
                ("red", "player"),
            ]
        return [
            ("white", "player"), 
            ("red", "player")
        ]

    @staticmethod
    def create_board(mode: str, size: str) -> Board:
        if mode == "base":
            return Board()
        elif mode == "layer":
            return LayerBoard()

    @staticmethod
    def create_piece(piece_name, mode, tile, player):
        if mode == "base":
            PieceObject = Piece.get_piece_type(piece_name)
            piece = PieceObject(tile, player)
        elif mode == "layer":
            PieceObject = LayerPiece.get_piece_type(piece_name)
            piece = PieceObject(tile, player)
        return

    @staticmethod
    def load_initial_positions(file_path: str) -> Dict[str, str]:
        with open(file_path, 'r') as file:
            initial_positions = json.load(file)
        return initial_positions