from engine.core.ChessFactory import ChessFactory
from engine.core.matrices.MatrixBoard import LayerMatrixBoard

from numba import njit
from numba.typed import List
import numpy as np
import time

@njit
def get_possible_moves(player_pieces, adjacency_list, patterns_offsets, pieces_offsets, tiles_offsets,
                       out_moves, out_count): 
    count = 0
    for piece in player_pieces:
        piece_type = piece[0]
        tile = piece[2]
        has_moved = piece[3]
        captured = piece[4]
        
        if piece_type == 5: 
            piece_type = 0

        piece_offsets = pieces_offsets[tiles_offsets[tile] : tiles_offsets[tile + 1] + 1]
        pattern_offsets = patterns_offsets[piece_offsets[piece_type] : piece_offsets[piece_type + 1] + 1]
        
        for i in range(len(pattern_offsets) - 1): 
            to_tiles = adjacency_list[pattern_offsets[i] : pattern_offsets[i + 1]]
            for t in to_tiles:
                out_moves[count, 0] = tile
                out_moves[count, 1] = t
                count += 1

    out_count[0] = count


def test(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="matrix",
        game_mode="wormhole",
        size=(8, 8),
    )

    board: LayerMatrixBoard = game.board
    pieces = board.get_pieces(game.turn)

    max_moves = 240 # 104 was the max move count reached in games
    out_moves = np.empty((max_moves, 2), dtype=np.uint8)
    out_count = np.zeros(1, dtype=np.uint8)

    get_possible_moves(pieces, board.adjacency_list, board.patterns_offsets, board.pieces_offsets, board.tiles_offsets, out_moves, out_count)
    
    # for move in out_moves[:out_count[0]]: 
    #     print(board.get_names(move))

    start = time.time()
    for i in range(10000):
        get_possible_moves(pieces, board.adjacency_list, board.patterns_offsets, board.pieces_offsets, board.tiles_offsets, out_moves, out_count)
    end = time.time()
    print(f'Time per call: {(end - start)/10000:.8f} seconds')


    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="layer",
        game_mode="wormhole",
        size=(8, 8),
    )

    start = time.time()
    for i in range(10000):
        player = game.players[game.turn]
        player.get_possible_moves()
    end = time.time()
    print(f'Time per call: {(end - start)/10000:.8f} seconds')


test()