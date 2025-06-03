from engine.core.ChessFactory import ChessFactory, MatrixChessFactory
from engine.core.matrices.MatrixBoard import LayerMatrixBoard

from engine.core.matrices.chess_logic_bounds import get_possible_moves

import numpy as np
import time


def test(): 
    num_tests = 10000

    position = './engine/core/configs/wormhole/tests/checks2.yaml'

    game = ChessFactory.create_game(
        player_data=MatrixChessFactory.create_bot_data(num_bots=2), 
        program_mode="matrix",
        game_mode="wormhole",
        size=(8, 8),
        # initial_positions=position
    )

    board: LayerMatrixBoard = game.board
    pieces = board.get_pieces(game.turn)

    moves = game.get_movements()
    for move in moves: 
        print(game.board.get_names(move))

    start = time.time()
    for i in range(num_tests):
        moves = game.get_movements()
        game.next_turn()
    end = time.time()
    print(f'Time per call: {(end - start)/num_tests:.8f} seconds')


    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="layer",
        game_mode="wormhole",
        size=(8, 8),
        # initial_positions=position
    )

    print(game.get_movements())

    start = time.time()
    for i in range(num_tests):
        game.get_movements()
        game.next_turn()
    end = time.time()
    print(f'Time per call: {(end - start)/num_tests:.8f} seconds')


test()