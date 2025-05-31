from typing import Tuple
from numba import njit
import numpy as np 


@njit(cache=True)
def retrieve_move_bounds(tile: np.int16, piece_type: np.uint8, 
                         tiles_offsets: np.array, pieces_offsets: np.array) -> Tuple[np.uint16, np.uint16]:
    piece_start = pieces_offsets[tiles_offsets[tile] + piece_type]
    piece_end = pieces_offsets[tiles_offsets[tile] + piece_type + 1]
    return piece_start, piece_end


@njit(cache=True)
def basic_filter(player: np.uint8, tile: np.int16, move_start: np.int16, move_end: np.int16, 
                 edges: np.array, nodes: np.array, pieces: np.array, 
                 obstacles: bool, out_moves: np.array, count: np.uint8) -> np.uint8: 
    
    for i in range(move_start, move_end):
        t = edges[i]
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

    return count


@njit(cache=True)
def basic_filter_loop(player: np.uint8, tile: np.uint8, piece_start: np.int16, piece_end: np.int16, 
                      patterns_offsets: np.array, adjacency_list: np.array, nodes: np.array, pieces: np.array,
                      out_moves: np.array, count: np.uint8, obstacles: bool) -> np.uint8:
    for i in range(piece_start, piece_end):
        move_start = patterns_offsets[i]
        move_end = patterns_offsets[i + 1]
        
        count = basic_filter(player, tile, move_start, move_end, adjacency_list, nodes, pieces, 
                             obstacles, out_moves, count)
    return count


@njit(cache=True)
def filter_pawn_moves(player: np.uint8, tile: np.int16, move_start: np.int16, move_end: np.int16, 
                      edges: np.array, nodes: np.array, pieces: np.array, 
                      out_moves: np.array, count: np.uint8) -> np.uint8:
    
    t = edges[move_start]
    is_piece = nodes[t]
    if is_piece != -1: 
        return count
        
    out_moves[count, 0] = tile
    out_moves[count, 1] = t
    count += 1
    
    count = basic_filter(player, tile, move_start + 1, move_end, edges, nodes, pieces,
                         False, out_moves, count)
    return count


@njit(cache=True)
def filter_pawn_attacks(player: np.uint8, tile: np.int16, move_start: np.int16, move_end: np.int16, 
                        edges: np.array, nodes: np.array, pieces: np.array, 
                        out_moves: np.array, count: np.uint8) -> np.uint8: 

    for i in range(move_start, move_end):
        t = edges[i]
        is_piece = nodes[t]
        if is_piece != -1: 
            to_piece = pieces[is_piece]
            to_piece_team = to_piece[1]

            if to_piece_team != player: 
                out_moves[count, 0] = tile
                out_moves[count, 1] = t
                count += 1

    return count 


@njit(cache=True)
def get_possible_moves(player: np.uint8, nodes: np.array, pieces: np.array, adjacency_list: np.array, 
                       patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array,
                       out_moves: np.array, out_count: np.array, pieces_per_player: int = 16) -> None: 
    chunk = pieces_per_player * player
    player_pieces = pieces[chunk : chunk + pieces_per_player]
    
    count = 0
    for piece in player_pieces:
        piece_type = piece[0]
        tile = piece[2]
        captured = piece[4]
        
        if captured: continue

        if piece_type in (0, 2):
            piece_start, piece_end = retrieve_move_bounds(tile, piece_type, tiles_offsets, pieces_offsets)
            count = basic_filter_loop(player, tile, piece_start, piece_end, patterns_offsets, adjacency_list,
                                      nodes, pieces, out_moves, count, True)
            
        elif piece_type == 1:
            piece_start, piece_end = retrieve_move_bounds(tile, piece_type, tiles_offsets, pieces_offsets)
            move_start = patterns_offsets[piece_start]
            move_end = patterns_offsets[piece_end]
            count = basic_filter(player, tile, move_start, move_end, adjacency_list, nodes, pieces, 
                                 False, out_moves, count)

        elif piece_type == 3: 
            piece_start, piece_end = retrieve_move_bounds(tile, piece_type, tiles_offsets, pieces_offsets)
            
            move_start = patterns_offsets[piece_start]
            move_end = patterns_offsets[piece_start + 1]
            
            count = basic_filter(player, tile, move_start, move_end, adjacency_list, nodes, pieces, 
                                 False, out_moves, count)
            
        elif piece_type == 4: 
            piece_start, piece_end = retrieve_move_bounds(tile, piece_type, tiles_offsets, pieces_offsets)
            pawn_chunk = 2 * player
            piece_start += pawn_chunk
            
            pawn_moves_start = patterns_offsets[piece_start]
            pawn_moves_end = patterns_offsets[piece_start + 1]
            count = filter_pawn_moves(player, tile, pawn_moves_start, pawn_moves_end, 
                                      adjacency_list, nodes, pieces, out_moves, count)
            
            pawn_attacks_start = patterns_offsets[piece_start + 1]
            pawn_attacks_end = patterns_offsets[piece_start + 2]
            count = filter_pawn_attacks(player, tile, pawn_attacks_start, pawn_attacks_end, 
                                        adjacency_list, nodes, pieces, out_moves, count)
            
        elif piece_type == 5: 
            piece_start, piece_end = retrieve_move_bounds(tile, 0, tiles_offsets, pieces_offsets)
            count = basic_filter_loop(player, tile, piece_start, piece_end, patterns_offsets, adjacency_list,
                                      nodes, pieces, out_moves, count, True)
            piece_start, piece_end = retrieve_move_bounds(tile, 2, tiles_offsets, pieces_offsets)
            count = basic_filter_loop(player, tile, piece_start, piece_end, patterns_offsets, adjacency_list,
                                      nodes, pieces, out_moves, count, True)
            
    out_count[0] = count