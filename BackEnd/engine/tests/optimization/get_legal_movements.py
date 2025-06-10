from engine.ChessFactory import ChessFactory, MatrixChessFactory
from engine.core.matrices.MatrixBoard import LayerMatrixBoard

from engine.core.matrices.chess_logic_bounds import get_possible_moves

import numpy as np
import time


def test(): 
    num_tests = 10000

    position = './engine/core/configs/wormhole/tests/checks.yaml'

    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=2), 
        program_mode="matrix",
        game_mode="wormhole",
        size=(8, 8),
        # initial_positions=position
    )

    board: LayerMatrixBoard = game.board
    pieces = board.get_pieces(game.turn)

    moves = game.get_movements()

    start = time.time()
    for i in range(num_tests):
        moves = game.get_movements()
        # print("- - - - - - Move - - - - -")
        # print(len(moves))
        # game.print_moves()
        game.next_turn()
    end = time.time()
    print(f'Time per call: {(end - start)/num_tests:.8f} seconds')


    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=2), 
        program_mode="layer",
        game_mode="wormhole",
        size=(8, 8),
        # initial_positions=position
    )

    start = time.time()
    for i in range(num_tests):
        moves = game.get_movements()
        # print(len(moves), moves)
        game.next_turn()
    end = time.time()
    print(f'Time per call: {(end - start)/num_tests:.8f} seconds')


test()