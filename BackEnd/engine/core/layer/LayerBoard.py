import json 
from typing import Dict

from engine.core.Player import Player
from engine.core.base.Board import Board
from engine.core.base.Pieces import Tower, Bishop, Knight, Queen, King, Pawn
from engine.core.layer.LayerTile import LayerTile


class LayerBoard: 
    def __init__(self) -> None:
        self.tiles = self

    def __getitem__(self, key: str | LayerTile) -> LayerTile: 
        if isinstance(key, LayerTile): 
            return self.tiles[key.name]
        self.tiles[key]
        
    def create_layer_board(): 
        PAWN_INVALID_POSITIONS = {
            "whtie": ["a1_T", "b1_T", "c1_T", "d1_T", "e1_T", "f1_T", "g1_T", "h1_T"],
            "black": ["a8_T", "b8_T", "c8_T", "d8_T", "e8_T", "f8_T", "g8_T", "h8_T"],
            "blue": ["a1_B", "b1_B", "c1_B", "d1_B", "e1_B", "f1_B", "g1_B", "h1_B"],
            "red": ["a8_B", "b8_B", "c8_B", "d8_B", "e8_B", "f8_B", "g8_B", "h8_B"],
        }
        
        player1 = Player(0, "player")
        player2 = Player(1, "player")
        player3 = Player(2, "player")
        player4 = Player(3, "player")
        
        b = Board()
        layer_board = {}
        for tile in b.tiles.values(): 
            layer_board[tile.name] = LayerTile(tile.name)
        
        for tile in b.tiles.values(): 
            tower = Tower(tile, player1)
            tower_movements = tower.get_movements(flatten=False)
            tower_movements = [movements for movements in tower_movements if len(movements) > 0]

            knight = Knight(tile, player1)
            knight_movements = knight.get_movements()

            bishop = Bishop(tile, player1)
            bishop_movements = bishop.get_movements(flatten=False)
            tower_movements = [movements for movements in bishop_movements if len(movements) > 0]

            # Castling is handled in the game logic
            king = King(tile, player1)
            king_movements = king.get_movements()

            pawn_white_movements = []
            if tile.name not in PAWN_INVALID_POSITIONS["whtie"]:
                pawn_white = Pawn(tile, player1)
                pawn_white_movements = pawn_white.get_movements(flatten=False, remove_non_valid_atacks=False)

            pawn_black_movements = []
            if tile.name not in PAWN_INVALID_POSITIONS["black"]:
                pawn_black = Pawn(tile, player2)
                pawn_black_movements = pawn_black.get_movements(flatten=False, remove_non_valid_atacks=False)

            pawn_blue_movements = []
            if tile.name not in PAWN_INVALID_POSITIONS["blue"]: 
                pawn_blue = Pawn(tile, player3)
                pawn_blue_movements = pawn_blue.get_movements(flatten=False, remove_non_valid_atacks=False)

            pawn_red_movements = []
            if tile.name not in PAWN_INVALID_POSITIONS["red"]: 
                pawn_red = Pawn(tile, player4)
                pawn_red_movements = pawn_red.get_movements(flatten=False, remove_non_valid_atacks=False)

            layer_board[tile.name] = {
                "tower": tower_movements,
                "knight": knight_movements, 
                "bishop": bishop_movements, 
                "king": king_movements, 
                "pawn_white": pawn_white_movements,
                "pawn_black": pawn_black_movements,
                "pawn_blue": pawn_blue_movements, 
                "pawn_red": pawn_red_movements, 
            }

            tile.remove_piece()

        return layer_board