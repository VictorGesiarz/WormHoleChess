from numba import njit
import numpy as np 


@njit(cache=True)
def retrieve_moves(tile: np.int16, piece_type: np.uint8, 
                   tiles_offsets: np.array, pieces_offsets: np.array, patterns_offsets: np.array):
    piece_offsets = pieces_offsets[tiles_offsets[tile] : tiles_offsets[tile + 1] + 1]
    pattern_offsets = patterns_offsets[piece_offsets[piece_type] : piece_offsets[piece_type + 1] + 1]
    return pattern_offsets


@njit(cache=True)
def basic_filter(player: np.uint8, tile: np.int16, moves: np.array, nodes: np.array, pieces: np.array, 
                 obstacles: bool, out_moves: np.array, out_count: np.array): 
    count = out_count[0]

    for t in moves:
        is_piece = nodes[t]
        if is_piece != -1: 
            to_piece = pieces[is_piece]
            to_piece_team = to_piece[1]
            
            if obstacles:
                if to_piece_team != player: 
                    out_moves[count, 0] = tile
                    out_moves[count, 1] = t
                    count += 1
                break
            elif to_piece_team == player: 
                continue

        out_moves[count, 0] = tile
        out_moves[count, 1] = t
        count += 1

    out_count[0] = count


@njit(cache=True)
def filter_pawn_moves(player: np.uint8, tile: np.int16, moves: np.array, nodes: np.array, pieces: np.array, 
                      out_moves: np.array, out_count: np.array):
    count = out_count[0]
    
    to_tile = moves[0]
    is_piece = nodes[to_tile]
    piece_found = False
    if is_piece != -1: 
        to_piece = pieces[is_piece]
        to_piece_team = to_piece[1]
        
        if to_piece_team == player: 
            return 
        piece_found = True
        
    out_moves[count, 0] = tile
    out_moves[count, 1] = to_tile
    out_count[0] += 1
    
    if not piece_found and len(moves) > 1:
        basic_filter(player, tile, moves[1:], nodes, pieces, False, out_moves, out_count)


@njit(cache=True)
def filter_pawn_attacks(player: np.uint8, tile: np.int16, moves: np.array, nodes: np.array, pieces: np.array, 
                        out_moves: np.array, out_count: np.array): 
    count = out_count[0]

    for t in moves:
        is_piece = nodes[t]
        if is_piece != -1: 
            to_piece = pieces[is_piece]
            to_piece_team = to_piece[1]

            if to_piece_team != player: 
                out_moves[count, 0] = tile
                out_moves[count, 1] = t
                count += 1

    out_count[0] = count


@njit(cache=True)
def get_possible_moves(player: np.uint8, nodes: np.array, pieces: np.array, adjacency_list: np.array, 
                       patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array,
                       out_moves: np.array, out_count: np.array, pieces_per_player: int = 16): 
    chunk = pieces_per_player * player
    player_pieces = pieces[chunk : chunk + pieces_per_player]
    
    count = 0
    for piece in player_pieces:
        piece_type = piece[0]
        tile = piece[2]
        captured = piece[4]
        
        if captured: continue

        if piece_type in (0, 1, 2):
            pattern_offsets = retrieve_moves(tile, piece_type, tiles_offsets, pieces_offsets, patterns_offsets)
        elif piece_type == 3: 
            pattern_offsets = retrieve_moves(tile, piece_type, tiles_offsets, pieces_offsets, patterns_offsets)
            pattern_offsets = pattern_offsets[:-1]
        elif piece_type == 4: 
            pattern_offsets = retrieve_moves(tile, piece_type, tiles_offsets, pieces_offsets, patterns_offsets)
            pawn_chunk = 2 * player
            pattern_offsets = pattern_offsets[pawn_chunk : pawn_chunk + 3]
        elif piece_type == 5: 
            tower_offsets = retrieve_moves(tile, 0, tiles_offsets, pieces_offsets, patterns_offsets)
            bishop_offsets = retrieve_moves(tile, 2, tiles_offsets, pieces_offsets, patterns_offsets)
            pattern_offsets = np.concatenate((tower_offsets, bishop_offsets))
        
        for i in range(len(pattern_offsets) - 1): 
            to_tiles = adjacency_list[pattern_offsets[i] : pattern_offsets[i + 1]]
            
            obstacles = False
            if piece_type in (0, 2, 5): 
                obstacles = True
            
            if piece_type == 4: 
                if i == 0: 
                    filter_pawn_moves(player, tile, to_tiles, nodes, pieces, out_moves, out_count)
                else:
                    filter_pawn_attacks(player, tile, to_tiles, nodes, pieces, out_moves, out_count)
            else:
                basic_filter(player, tile, to_tiles, nodes, pieces, obstacles, out_moves, out_count)

    out_count[0] = count