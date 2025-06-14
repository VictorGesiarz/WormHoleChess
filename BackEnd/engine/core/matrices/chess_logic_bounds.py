from typing import Tuple
from numba import njit
import numpy as np 

from engine.core.matrices.matrix_constants import *


# When board is 8x8 Wormhole
# NAMES = np.array(['a1_T', 'a2_T', 'a3_T', 'a4_T', 'a5_T', 'a6_T', 'a7_T', 'a8_T', 'b1_T', 'b2_T', 'b3_T', 'b4_T', 'b5_T', 'b6_T', 'b7_T', 'b8_T', 'c1_T', 'c2_T', 'c3_T', 'c4_T', 'c5_T', 'c6_T', 'c7_T', 'c8_T', 'd1_T', 'd2_T', 'd3_T', 'd4_T', 'd4_1_T', 'd4_2_T', 'd5_T', 'd5_1_T', 'd5_2_T', 'd6_T', 'd7_T', 'd8_T', 'e1_T', 'e2_T', 'e3_T', 'e4_T', 'e4_1_T', 'e4_2_T', 'e5_T', 'e5_1_T', 'e5_2_T', 'e6_T', 'e7_T', 'e8_T', 'f1_T', 'f2_T', 'f3_T', 'f4_T', 'f5_T', 'f6_T', 'f7_T', 'f8_T', 'g1_T', 'g2_T', 'g3_T', 'g4_T', 'g5_T', 'g6_T', 'g7_T', 'g8_T', 'h1_T', 'h2_T', 'h3_T', 'h4_T', 'h5_T', 'h6_T', 'h7_T', 'h8_T', 'a1_B', 'a2_B', 'a3_B', 'a4_B', 'a5_B', 'a6_B', 'a7_B', 'a8_B', 'b1_B', 'b2_B', 'b3_B', 'b4_B', 'b5_B', 'b6_B', 'b7_B', 'b8_B', 'c1_B', 'c2_B', 'c3_B', 'c4_B', 'c5_B', 'c6_B', 'c7_B', 'c8_B', 'd1_B', 'd2_B', 'd3_B', 'd4_B', 'd4_1_B', 'd4_2_B', 'd5_B', 'd5_1_B', 'd5_2_B', 'd6_B', 'd7_B', 'd8_B', 'e1_B', 'e2_B', 'e3_B', 'e4_B', 'e4_1_B', 'e4_2_B', 'e5_B', 'e5_1_B', 'e5_2_B', 'e6_B', 'e7_B', 'e8_B', 'f1_B', 'f2_B', 'f3_B', 'f4_B', 'f5_B', 'f6_B', 'f7_B', 'f8_B', 'g1_B', 'g2_B', 'g3_B', 'g4_B', 'g5_B', 'g6_B', 'g7_B', 'g8_B', 'h1_B', 'h2_B', 'h3_B', 'h4_B', 'h5_B', 'h6_B', 'h7_B', 'h8_B'], dtype=str)z

# When board is 6x6 Wormhole
NAMES = np.array(['a1_T', 'a2_T', 'a3_T', 'a4_T', 'a5_T', 'a6_T', 'b1_T', 'b2_T', 'b3_T', 'b4_T', 'b5_T', 'b6_T', 'c1_T', 'c2_T', 'c3_T', 'c3_1_T', 'c3_2_T', 'c4_T', 'c4_1_T', 'c4_2_T', 'c5_T', 'c6_T', 'd1_T', 'd2_T', 'd3_T', 'd3_1_T', 'd3_2_T', 'd4_T', 'd4_1_T', 'd4_2_T', 'd5_T', 'd6_T', 'e1_T', 'e2_T', 'e3_T', 'e4_T', 'e5_T', 'e6_T', 'f1_T', 'f2_T', 'f3_T', 'f4_T', 'f5_T', 'f6_T', 'a1_B', 'a2_B', 'a3_B', 'a4_B', 'a5_B', 'a6_B', 'b1_B', 'b2_B', 'b3_B', 'b4_B', 'b5_B', 'b6_B', 'c1_B', 'c2_B', 'c3_B', 'c3_1_B', 'c3_2_B', 'c4_B', 'c4_1_B', 'c4_2_B', 'c5_B', 'c6_B', 'd1_B', 'd2_B', 'd3_B', 'd3_1_B', 'd3_2_B', 'd4_B', 'd4_1_B', 'd4_2_B', 'd5_B', 'd6_B', 'e1_B', 'e2_B', 'e3_B', 'e4_B', 'e5_B', 'e6_B', 'f1_B', 'f2_B', 'f3_B', 'f4_B', 'f5_B', 'f6_B'])


@njit(cache=True)
def retrieve_move_bounds(tile: np.int16, piece_type: np.uint8, 
                         tiles_offsets: np.array, pieces_offsets: np.array) -> Tuple[np.uint16, np.uint16]:
    piece_start = pieces_offsets[tiles_offsets[tile] + piece_type]
    piece_end = pieces_offsets[tiles_offsets[tile] + piece_type + 1]
    return piece_start, piece_end



@njit(cache=True)
def basic_filter_simple(player: np.uint8, tile: np.int16, move_start: np.int16, move_end: np.int16, 
                 edges: np.array, nodes: np.array, pieces: np.array, 
                 obstacles: bool, out_moves: np.array, count: np.uint8, can_eat: bool = True) -> np.uint8: 
    
    for i in range(move_start, move_end):
        t = edges[i]

        is_piece = nodes[t]
        if is_piece != -1: 
            to_piece = pieces[is_piece]
            to_piece_team = to_piece[1]
            
            if to_piece_team != player and can_eat: 
                out_moves[count, 0] = tile
                out_moves[count, 1] = t
                count += 1
                if obstacles:
                    break
            elif to_piece_team == player: 
                continue
        else: 
            out_moves[count, 0] = tile
            out_moves[count, 1] = t
            count += 1

    return count


@njit(cache=True)
def basic_filter_duplicates(player: np.uint8, tile: np.int16, move_start: np.int16, move_end: np.int16, 
                 edges: np.array, nodes: np.array, pieces: np.array, 
                 obstacles: bool, out_moves: np.array, count: np.uint8,
                 visited_array: np.array, visited_len: np.uint8) -> np.uint8: 

    for i in range(move_start, move_end):
        t = edges[i]
        
        skip = False
        for j in range(visited_len):
            if visited_array[j] == t:
                skip = True
                break
        if skip:
            continue

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
        else:
            visited_array[visited_len] = t
            visited_len += 1
        out_moves[count, 0] = tile
        out_moves[count, 1] = t
        count += 1

    return count, visited_len


@njit(cache=True)
def basic_filter_loop(player: np.uint8, tile: np.uint8, piece_start: np.int16, piece_end: np.int16, 
                      patterns_offsets: np.array, adjacency_list: np.array, nodes: np.array, pieces: np.array,
                      out_moves: np.array, count: np.uint8, obstacles: bool) -> np.uint8:
    
    visited_array = np.zeros(MAX_POSSIBLE_TRACE, dtype=np.uint8)
    visited_len = 0

    for i in range(piece_start, piece_end):
        move_start = patterns_offsets[i]
        move_end = patterns_offsets[i + 1]
        
        count, visited_len = basic_filter_duplicates(player, tile, move_start, move_end, adjacency_list,  nodes, pieces, obstacles, out_moves, count,visited_array, visited_len)
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
    
    count = basic_filter_simple(player, tile, move_start + 1, move_end, edges, nodes, pieces,
                         False, out_moves, count, can_eat=False)
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
def get_tower_movements(player: np.uint8, tile: np.int16, nodes: np.array, pieces: np.array, 
                        adjacency_list: np.array, patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array, 
                        out_moves: np.array, count: np.uint8): 
    piece_start, piece_end = retrieve_move_bounds(tile, 0, tiles_offsets, pieces_offsets)
    count = basic_filter_loop(player, tile, piece_start, piece_end, patterns_offsets, adjacency_list,
                              nodes, pieces, out_moves, count, True)
    return count

@njit(cache=True)
def get_bishop_movements(player: np.uint8, tile: np.int16, nodes: np.array, pieces: np.array, 
                        adjacency_list: np.array, patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array, 
                        out_moves: np.array, count: np.uint8): 
    piece_start, piece_end = retrieve_move_bounds(tile, 2, tiles_offsets, pieces_offsets)
    count = basic_filter_loop(player, tile, piece_start, piece_end, patterns_offsets, adjacency_list,
                              nodes, pieces, out_moves, count, True)
    return count

@njit(cache=True)
def get_knight_movements(player: np.uint8, tile: np.int16, nodes: np.array, pieces: np.array, 
                        adjacency_list: np.array, patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array, 
                        out_moves: np.array, count: np.uint8): 
    piece_start, piece_end = retrieve_move_bounds(tile, 1, tiles_offsets, pieces_offsets)
    move_start = patterns_offsets[piece_start]
    move_end = patterns_offsets[piece_end]
    count = basic_filter_simple(player, tile, move_start, move_end, adjacency_list, nodes, pieces, 
                            False, out_moves, count)
    
    return count

@njit(cache=True)
def get_king_movements(player: np.uint8, tile: np.int16, nodes: np.array, pieces: np.array, 
                        adjacency_list: np.array, patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array, 
                        out_moves: np.array, count: np.uint8): 
    piece_start, piece_end = retrieve_move_bounds(tile, 3, tiles_offsets, pieces_offsets)
    move_start = patterns_offsets[piece_start]
    move_end = patterns_offsets[piece_start + 1]
    count = basic_filter_simple(player, tile, move_start, move_end, adjacency_list, nodes, pieces, 
                            False, out_moves, count)    
    return count

@njit(cache=True)
def get_king_possible_atacks(player: np.uint8, tile: np.int16, nodes: np.array, pieces: np.array, 
                        adjacency_list: np.array, patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array, 
                        out_moves: np.array, count: np.uint8): 
    piece_start, piece_end = retrieve_move_bounds(tile, 3, tiles_offsets, pieces_offsets)
    move_start = patterns_offsets[piece_start + 1]
    move_end = patterns_offsets[piece_start + 2]
    for i in range(move_start, move_end): 
        t = adjacency_list[i]
        if t == -1: 
            continue

        piece = pieces[nodes[t]]
        if piece[0] == 4 and piece[1] != player and not piece[4]: 
            out_moves[count, 0] = tile
            out_moves[count, 1] = t
            count += 1
    return count 


@njit(cache=True)
def get_pawn_movements(player: np.uint8, tile: np.int16, nodes: np.array, pieces: np.array, 
                        adjacency_list: np.array, patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array, 
                        out_moves: np.array, count: np.uint8, only_atacks: bool = False): 
    piece_start, piece_end = retrieve_move_bounds(tile, 4, tiles_offsets, pieces_offsets)

    pawn_chunk = 2 * player
    piece_start += pawn_chunk

    if not only_atacks:
        pawn_moves_start = patterns_offsets[piece_start]
        pawn_moves_end = patterns_offsets[piece_start + 1]

        if pawn_moves_end - pawn_moves_start == 3: 
            count = filter_pawn_moves(player, tile, pawn_moves_start, pawn_moves_end, 
                                    adjacency_list, nodes, pieces, out_moves, count)
        else: 
            count = basic_filter_simple(player, tile, pawn_moves_start, pawn_moves_end, 
                                        adjacency_list, nodes, pieces, True, out_moves, count, can_eat=False)
    
    pawn_attacks_start = patterns_offsets[piece_start + 1]
    pawn_attacks_end = patterns_offsets[piece_start + 2]
    count = filter_pawn_attacks(player, tile, pawn_attacks_start, pawn_attacks_end, 
                                adjacency_list, nodes, pieces, out_moves, count)
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

        if piece_type == 0:
            count = get_tower_movements(player, tile, nodes, pieces, adjacency_list, patterns_offsets, 
                                        pieces_offsets, tiles_offsets, out_moves, count)
            
        elif piece_type == 1:
            count = get_knight_movements(player, tile, nodes, pieces, adjacency_list, patterns_offsets, 
                                        pieces_offsets, tiles_offsets, out_moves, count)

        elif piece_type == 2:
            count = get_bishop_movements(player, tile, nodes, pieces, adjacency_list, patterns_offsets, 
                                        pieces_offsets, tiles_offsets, out_moves, count)

        elif piece_type == 3: 
            count = get_king_movements(player, tile, nodes, pieces, adjacency_list, patterns_offsets, 
                                        pieces_offsets, tiles_offsets, out_moves, count)
            
        elif piece_type == 4: 
            count = get_pawn_movements(player, tile, nodes, pieces, adjacency_list, patterns_offsets, 
                                        pieces_offsets, tiles_offsets, out_moves, count)
            
        elif piece_type == 5: 
            count = get_tower_movements(player, tile, nodes, pieces, adjacency_list, patterns_offsets, 
                                        pieces_offsets, tiles_offsets, out_moves, count)
            count = get_bishop_movements(player, tile, nodes, pieces, adjacency_list, patterns_offsets, 
                                        pieces_offsets, tiles_offsets, out_moves, count)
                  
    out_count[0] = count


@njit
def get_king_tile(pieces: np.ndarray, player: np.uint8) -> np.array:
    for i in range(pieces.shape[0]):
        if pieces[i, 0] == 3 and pieces[i, 1] == player and pieces[i, 4] == 0:
            return pieces[i]
    return np.empty(6, dtype=np.int16)


@njit(cache=True)
def filter_legal_moves(player: np.uint8, nodes: np.array, pieces: np.array, adjacency_list: np.array, 
                       patterns_offsets: np.array, pieces_offsets: np.array, tiles_offsets: np.array,
                       out_moves: np.array, out_count: np.array, history: np.array, history_index: int,
                       promotion_zones: np.array, current_hash: int, hashes: np.array, hasher: np.array) -> None:
    count = 0

    player_king = get_king_tile(pieces, player)
    king_trace = np.empty((MAX_POSSIBLE_MOVES, 2), dtype=np.uint8)

    for i in range(out_count[0]): 
        move = out_moves[i]
        make_move(move, nodes, pieces, history, history_index, promotion_zones, False)
        king_tile = player_king[2]
        if not is_in_check(player, king_tile, nodes, pieces, adjacency_list, patterns_offsets, 
                           pieces_offsets, tiles_offsets, king_trace): 
            hashes[count] = update_hash(current_hash, history[history_index], pieces, hasher) 
            out_moves[count] = move
            count += 1
        undo_move(nodes, pieces, history, history_index)

    out_count[0] = count


@njit(cache=True)
def move_makes_check(king_trace, count, nodes, pieces, valid_types) -> bool: 
    for i in range(count):
        tile = king_trace[i][1]
        piece_index = nodes[tile]
        if piece_index == -1:
            continue
        piece = pieces[piece_index]
        if not piece[4]:  # not captured
            ptype = piece[0]
            for j in range(len(valid_types)):
                if ptype == valid_types[j]:
                    return True
    return False


@njit(cache=True)
def move_makes_check_pawn(pawn_positions, tile, count, nodes, pieces,
                          adjacency_list, patterns_offsets, pieces_offsets, tiles_offsets) -> bool: 
    pawn_atacks = np.empty((3, 2), dtype=np.uint8)
    for i in range(count): 
        pawn_tile = pawn_positions[i][1]
        pawn = pieces[nodes[pawn_tile]]
        player = pawn[1]
        pawn_atacks_count = get_pawn_movements(player, pawn_tile, nodes, pieces, 
                            adjacency_list, patterns_offsets, pieces_offsets, tiles_offsets, 
                            pawn_atacks, 0, only_atacks=True)
        
        for j in range(pawn_atacks_count): 
            pawn_atack_tile = pawn_atacks[j][1]
            if tile == pawn_atack_tile: 
                return True
    return False


@njit(cache=True)
def is_in_check(player: np.uint8, king_tile: np.int16, nodes, pieces, 
                adjacency_list, patterns_offsets, pieces_offsets, tiles_offsets, 
                king_trace) -> bool: 

    # print("Tower - queen check")
    if move_makes_check(
            king_trace, 
            get_tower_movements(player, king_tile, nodes, pieces, adjacency_list, 
                patterns_offsets, pieces_offsets, tiles_offsets, king_trace, 0), 
            nodes,
            pieces, 
            np.array([0, 5], dtype=np.int16)):
        # print("Tower or Queen makes check")
        return True

    # print("Bishop - queen check")
    if move_makes_check(
            king_trace, 
            get_bishop_movements(player, king_tile, nodes, pieces, adjacency_list, 
                patterns_offsets, pieces_offsets, tiles_offsets, king_trace, 0), 
            nodes,
            pieces, 
            np.array([2, 5], dtype=np.int16)):
        # print("Bishop or Queen makes check")
        return True

    # print("Knight check")
    if move_makes_check(
            king_trace, 
            get_knight_movements(player, king_tile, nodes, pieces, adjacency_list, 
                patterns_offsets, pieces_offsets, tiles_offsets, king_trace, 0), 
            nodes,
            pieces, 
            np.array([1], dtype=np.int16)):
        # print("Knight makes check")
        return True

    # print("King check")
    if move_makes_check(
            king_trace, 
            get_king_movements(player, king_tile, nodes, pieces, adjacency_list, 
                patterns_offsets, pieces_offsets, tiles_offsets, king_trace, 0), 
            nodes,
            pieces, 
            np.array([3], dtype=np.int16)): 
        # print("King makes check")
        return True

    # print("Pawn check")
    if move_makes_check_pawn(
            king_trace, 
            king_tile, 
            get_king_possible_atacks(player, king_tile, nodes, pieces, adjacency_list, 
                patterns_offsets, pieces_offsets, tiles_offsets, king_trace, 0),
            nodes, pieces, adjacency_list, patterns_offsets, pieces_offsets, tiles_offsets 
            ):
        # print("Pawn makes check")
        return True

    return False 


@njit(cache=True)
def update_hash(old_hash: int, movement: np.array, pieces: np.array, hasher: np.array) -> int: 
    moving_piece_index, origin_tile, destination_tile, captured_piece_index, _, original_type = movement

    piece = pieces[moving_piece_index]
    current_type = piece[0]
    color = piece[1]

    old_hash ^= hasher[original_type][color][origin_tile]
    old_hash ^= hasher[current_type][color][destination_tile]

    if captured_piece_index != -1: 
        captured_piece = pieces[captured_piece_index]
        old_hash ^= hasher[captured_piece[0]][captured_piece[1]][destination_tile]

    return old_hash


@njit(cache=True)
def make_move(move: np.array, nodes: np.array, pieces: np.array, history: np.array, history_index: int, promotions: np.array, store: bool) -> None: 
    origin_tile = move[0]
    destination_tile = move[1]

    moving_piece_index = nodes[origin_tile]
    captured_piece_index = nodes[destination_tile]
    
    history[history_index, 0] = moving_piece_index
    history[history_index, 1] = origin_tile
    history[history_index, 2] = destination_tile
    history[history_index, 3] = captured_piece_index
    history[history_index, 4] = pieces[moving_piece_index][3]
    history[history_index, 5] = pieces[moving_piece_index][0]

    pieces[moving_piece_index, 2] = destination_tile
    pieces[moving_piece_index, 3] = 0 # Mark as moved
    nodes[origin_tile] = -1
    nodes[destination_tile] = moving_piece_index

    if captured_piece_index != -1: 
        # if pieces[captured_piece_index][0] == 3 and store: 
        #     print("CAPTURED KING?", captured_piece_index, NAMES[origin_tile], NAMES[destination_tile], pieces[moving_piece_index][0], pieces[captured_piece_index][0])
        pieces[captured_piece_index, 4] = 1 # Mark as captured

    # Promotion logic
    piece_type = pieces[moving_piece_index, 0]
    team = pieces[moving_piece_index, 1]
    if piece_type == 4: 
        for promotion_tile in promotions[team]:
            if destination_tile == promotion_tile:
                print("coronation")
                pieces[moving_piece_index, 0] = 5
                break


@njit(cache=True)
def undo_move(nodes: np.array, pieces: np.array, history: np.array, history_index: int) -> None: 
    moving_piece_index, origin_tile, destination_tile, captured_piece_index, first_move, original_type = history[history_index]

    pieces[moving_piece_index, 0] = original_type
    pieces[moving_piece_index, 2] = origin_tile
    pieces[moving_piece_index, 3] = first_move
    nodes[origin_tile] = moving_piece_index
    nodes[destination_tile] = captured_piece_index

    if captured_piece_index != -1: 
        pieces[captured_piece_index, 4] = 0 # Revive Piece


@njit(cache=True)
def print_tiles(tiles: np.ndarray):
    for i in range(tiles.shape[0]):
        row = tiles[i]
        print(NAMES[row[0]], NAMES[row[1]])