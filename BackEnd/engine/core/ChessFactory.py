from engine.core.base.Board import Board
from engine.core.layer.LayerBoard import LayerBoard
from engine.core.base.Pieces import Piece
from engine.core.layer.LayerPieces import LayerPiece
from engine.logic.move_generator import SpeedMoveGenerator, MemoryMoveGenerator


class ChessFactory:
    @staticmethod
    def create_board(mode):
        if mode == "speed":
            return Board()
        elif mode == "memory":
            return LayerBoard()
        else:
            raise ValueError("Invalid mode: choose 'speed' or 'memory'")

    @staticmethod
    def create_move_generator(mode):
        if mode == "speed":
            return SpeedMoveGenerator()
        elif mode == "memory":
            return MemoryMoveGenerator()
        else:
            raise ValueError("Invalid mode: choose 'speed' or 'memory'")

    @staticmethod
    def create_piece(piece_type, mode, position):
        if mode == "speed":
            return Piece(piece_type, position)
        elif mode == "memory":
            return LayerPiece(piece_type, position)
        else:
            raise ValueError("Invalid mode: choose 'speed' or 'memory'")
