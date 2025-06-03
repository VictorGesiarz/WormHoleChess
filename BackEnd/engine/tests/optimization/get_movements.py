from engine.core.ChessFactory import ChessFactory
from engine.core.matrices.MatrixBoard import LayerMatrixBoard

from engine.core.matrices.chess_logic_bounds import get_possible_moves

import numpy as np
import time


def test(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="matrix",
        game_mode="wormhole",
        size=(8, 8),
    )

    board: LayerMatrixBoard = game.board
    pieces = board.get_pieces(game.turn)

    num_tests = 10000

    max_moves = 120 # 104 was the max move count reached in games
    out_moves = np.empty((max_moves, 2), dtype=np.uint8)
    out_count = np.zeros(1, dtype=np.uint8)
    
    get_possible_moves(game.turn, 
                    board.nodes, 
                    pieces, 
                    board.adjacency_list, 
                    board.patterns_offsets, 
                    board.pieces_offsets, 
                    board.tiles_offsets,
                    out_moves, 
                    out_count)
    
    for move in out_moves[:out_count[0]]: 
        print(board.get_names(move))

    start = time.time()
    for i in range(num_tests):
        get_possible_moves(game.turn, 
                           board.nodes, 
                           pieces, 
                           board.adjacency_list, 
                           board.patterns_offsets, 
                           board.pieces_offsets, 
                           board.tiles_offsets,
                           out_moves, 
                           out_count)
    end = time.time()
    print(f'Time per call: {(end - start)/num_tests:.8f} seconds')


    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="layer",
        game_mode="wormhole",
        size=(8, 8),
    )

    start = time.time()
    for i in range(num_tests):
        player = game.players[game.turn]
        player.get_possible_moves()
    end = time.time()
    print(f'Time per call: {(end - start)/num_tests:.8f} seconds')


test()