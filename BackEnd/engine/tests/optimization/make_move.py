from engine.ChessFactory import ChessFactory
from engine.core.matrices.MatrixBoard import LayerMatrixBoard

from engine.core.matrices.chess_logic_bounds import make_move

import numpy as np
import time


def test(): 
    num_tests = 1

    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="matrix",
        game_mode="wormhole",
        size=(8, 8),
        max_turns=120
    )

    board: LayerMatrixBoard = game.board
    pieces = board.get_pieces(game.turn)

    move = np.array([1, 2])
    game.make_move(move)
    game.undo_move()
    
    start = time.time()
    for i in range(num_tests):
        game.make_move(move)
        game.undo_move()
    end = time.time()
    print(f'Time per call: {(end - start):.8f} seconds')


    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="layer",
        game_mode="wormhole",
        size=(8, 8),
    )

    move = (game.board.tiles['a2_T'], game.board.tiles['a3_B'])
    start = time.time()
    for i in range(num_tests):
        piece_movement = game.make_move(move)
        game.undo_move(piece_movement)
    end = time.time()
    print(f'Time per call: {(end - start):.8f} seconds')


test()