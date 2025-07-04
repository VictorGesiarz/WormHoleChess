from typing import List, Tuple, Dict
import numpy as np 
import torch 
import os
from torch_geometric.data import Data, Batch

from engine.core.layer.LayerBoard import LayerBoard
from engine.core.layer.LayerTile import LayerTile
from engine.core.base.Board import Board
from engine.core.base.NormalBoard import NormalBoard
from engine.core.matrices.matrix_constants import Pieces, Teams


BOARD_FILES = './engine/core/configs/matrix_board/'

class LayerMatrixBoard: 
    def __init__(self, size: Tuple[int, int], game_mode: str = 'wormhole', innitialize: bool = True, 
             load_from_file=True, **kwargs) -> None:
        """ 
        Nodes: list of nodes in the board, the element corresponds to the piece type there and the player
        Edge lists: list of adjacency lists for each piece type. 
            Each adjacency list has 2 lists, one for the outgoing edges and one for the incoming edges.
            Each index stores the index of the node in the nodes list.
        Pattern lists: list of patters of movements for each node in the board. 
            The list contains tuples in the form (piece_type, from_index, to_index)
            The from_index and to_index are the indexes of the edges of that piece type, they indicate what 
            edge starts the pattern and what edge ends it. 
        """
        self.size = size
        self.game_mode = game_mode

        self.nodes: np.array = [] # [piece_index, ...]
        self.node_names: np.array = []
        # Offets
        self.adjacency_list: np.array = [] # List of index of tiles (edges), ordered to be accessed with the offsets. 
        self.patterns_offsets: np.array = [0] # List of the indexes of edges that correspond to a pattern of movement, e.g. the tower going up. 
        self.pieces_offsets: np.array = [0] # List of the indexes of the patterns offsets that correspond to a piece, e.g. the tower, which has many patterns. 
        self.tiles_offsets: np.array = [0] # List of the index of pieces offsets that correspond to a tile, e.g. the tile a1. 
        
        self.num_players = kwargs.get('num_players', 4) 
        self.pieces_per_player = kwargs.get('pieces_per_player', 16)
        self.num_pieces = self.num_players * self.pieces_per_player  # e.g., 4 players × 16 pieces = 64
        self.pieces: np.array = np.full((self.num_pieces, 6), -1, dtype=np.int16)  # [[piece_type, player, position, has_moved?, captured?, custom_flags (bitmasking)], ...]
        self.promotion_zones = np.empty((self.num_players, self.size[1] * (self.num_players-1)), dtype=np.uint8)

        if innitialize: 
            file = f'{BOARD_FILES}{self.size[0]}x{self.size[1]}_{self.game_mode}_LAYER.npz'
            if load_from_file and os.path.exists(file): 
                self.load_matrices(file)
            else:
                self.create_board()
    
    def copy(self) -> 'LayerMatrixBoard': 
        board_copy = LayerMatrixBoard(self.size, self.game_mode, innitialize=False)
        board_copy.set_matrices(self.nodes.copy(), self.node_names, self.adjacency_list, 
                                self.patterns_offsets, self.pieces_offsets, self.tiles_offsets,
                                self.promotion_zones)
        board_copy.num_players = self.num_players
        board_copy.pieces_per_player = self.pieces_per_player
        board_copy.num_pieces = self.num_pieces
        board_copy.pieces = self.pieces.copy()
        return board_copy
    
    def reset(self) -> None: 
        ...

    def set_matrices(self, nodes: np.array, node_names: np.array, adjacency: np.array, 
                     patterns: np.array, pieces_offets: np.array, tiles: np.array,
                     promotion_zones: np.array) -> None: 
        self.nodes = nodes
        self.node_names = node_names
        self.adjacency_list = adjacency
        self.patterns_offsets = patterns 
        self.pieces_offsets = pieces_offets
        self.tiles_offsets = tiles
        self.promotion_zones = promotion_zones
    
    def save_matrices(self) -> None: 
        file = f'{BOARD_FILES}{self.size[0]}x{self.size[1]}_{self.game_mode}_BASE.npz'
        np.savez(file, 
                 nodes=self.nodes,
                 node_names=self.node_names, 
                 adjacency_list=self.adjacency_list,
                 patterns_offsets=self.patterns_offsets,
                 pieces_offsets=self.pieces_offsets,
                 tiles_offsets=self.tiles_offsets,
                 promotion_zones=self.promotion_zones)
        
    def load_matrices(self, file) -> None: 
        matrices = np.load(file)
        self.nodes = matrices['nodes']
        self.node_names = matrices['node_names']
        self.adjacency_list = matrices['adjacency_list']
        self.patterns_offsets = matrices['patterns_offsets']
        self.pieces_offsets = matrices['pieces_offsets']
        self.tiles_offsets = matrices['tiles_offsets']
        self.promotion_zones = matrices['promotion_zones']

    def create_board(self, add_actions=False) -> None:
        b = LayerBoard(self.size, self.game_mode)

        self.nodes = np.full(len(b), -1, dtype=np.int16)
        self.node_names = np.array(list(b.tiles.keys()), dtype=str)
        self.promotion_zones = np.array([b.get_promotion_zones(p) for p in range(self.num_players)], dtype=np.uint8)

        self.actions = []

        adjacency_count = 0
        pattern_count = 0
        pieces_count = 0

        for tile in b.tiles.values():
            piece_layers = {
                Pieces.TOWER:  tile.tower_layer,
                Pieces.KNIGHT: tile.knight_layer,
                Pieces.BISHOP: tile.bishop_layer,
                Pieces.KING:   tile.king_layer,
                Pieces.PAWN:   tile.pawn_layer,
                Pieces.QUEEN:  tile.queen_layer,  # Currently unused
            }

            for piece, layer in piece_layers.items():
                # if piece == Pieces.QUEEN: 
                #     continue 

                # Skip queen layer, we can use a combination of tower and bishop to get the movements
                if piece in (Pieces.TOWER, Pieces.BISHOP): 
                    for i, direction in enumerate(layer.directions): 
                        tiles = self.get_ids(direction)
                        self.adjacency_list += tiles
                        adjacency_count += len(direction)
                        self.patterns_offsets.append(adjacency_count)
                        pattern_count += 1
                        self.__add_actions(tile.id, tiles, add_actions)

                elif piece == Pieces.KNIGHT: 
                    tiles = self.get_ids(layer.movements)
                    self.adjacency_list += tiles
                    adjacency_count += len(layer.movements)
                    self.patterns_offsets.append(adjacency_count)
                    pattern_count += 1
                    self.__add_actions(tile.id, tiles, add_actions)

                elif piece == Pieces.KING: 
                    tiles = self.get_ids(layer.movements)
                    self.adjacency_list += tiles
                    adjacency_count += len(layer.movements)
                    self.patterns_offsets.append(adjacency_count)
                    pattern_count += 1
                    self.__add_actions(tile.id, tiles, add_actions)

                    tiles = self.get_ids(layer.pawn_possible_atacks)
                    self.adjacency_list += tiles
                    adjacency_count += len(layer.pawn_possible_atacks)
                    self.patterns_offsets.append(adjacency_count)
                    pattern_count += 1
                    self.__add_actions(tile.id, tiles, add_actions)

                elif piece == Pieces.PAWN: 
                    for i, team in enumerate(Teams):
                        tiles = self.get_ids(layer.moves[team])
                        self.adjacency_list += self.get_ids(layer.moves[team])
                        adjacency_count += len(layer.moves[team])
                        self.patterns_offsets.append(adjacency_count)
                        pattern_count += 1
                        self.__add_actions(tile.id, tiles, add_actions)

                        tiles = self.get_ids(layer.attacks[team])
                        self.adjacency_list += self.get_ids(layer.attacks[team])
                        adjacency_count += len(layer.attacks[team])
                        self.patterns_offsets.append(adjacency_count)
                        pattern_count += 1
                        self.__add_actions(tile.id, tiles, add_actions)

                self.pieces_offsets.append(pattern_count)
                pieces_count += 1

            self.tiles_offsets.append(pieces_count)

        self.adjacency_list = np.array(self.adjacency_list, dtype=np.uint8)
        self.patterns_offsets = np.array(self.patterns_offsets, dtype=np.uint16)
        self.pieces_offsets = np.array(self.pieces_offsets, dtype=np.uint16)
        self.tiles_offsets = np.array(self.tiles_offsets, dtype=np.uint16)
        
        if add_actions:
            self.actions = np.array(self.actions, dtype=np.uint8)

        self.save_matrices()
    
    def __add_actions(self, tile, tiles, add_actions): 
        if not add_actions:
            return
        for to_tile in tiles: 
            if (tile, to_tile) not in self.__actions: 
                self.actions.append((tile, to_tile))

    def set_piece(self, id: int, type: int, player: int, position: int, has_moved: bool = False, captured: bool = False, custom_flags: int = 0) -> None: 
        self.pieces[id] = [type, player, position, int(has_moved), captured, custom_flags]
        self.nodes[position] = id

    def get_pieces(self, player: int) -> np.array:
        chunk = self.pieces_per_player * player
        return self.pieces[chunk:chunk + self.pieces_per_player]
    
    def get_names(self, index_list: List[int]) -> List[str]: 
        return [str(self.node_names[i]) for i in index_list]
    
    def get_ids(self, tile_list: List[LayerTile]):
        return [tile.id for tile in tile_list]
    
    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)


class BaseMatrixBoard: 
    def __init__(self, size: Tuple[int, int], gamemode: str = 'wormhole', 
             innitialize: bool = True, load_from_file=True, **kwargs) -> None:
        self.size = size
        self.game_mode = gamemode
        
        self.nodes: np.array
        self.edges: np.array

        self.num_players = kwargs.get('num_players', 2) 
        self.piece_types = kwargs.get('piece_types', 6)

        if innitialize: 
            file = f'{BOARD_FILES}{self.size[0]}x{self.size[1]}_{self.game_mode}_BASE.npz'
            if load_from_file and os.path.exists(file): 
                self.load_matrices(file)
            else:
                self.create_board()
        
    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)
    
    def copy(self) -> 'BaseMatrixBoard': 
        board_copy = BaseMatrixBoard(self.size, self.game_mode, False)
        board_copy.nodes = self.nodes.copy()
        board_copy.edges = self.edges.copy()
        board_copy.num_players = self.num_players
        board_copy.piece_types = self.piece_types
        return board_copy

    def save_matrices(self) -> None: 
        file = f'{BOARD_FILES}{self.size[0]}x{self.size[1]}_{self.game_mode}_BASE.npz'
        np.savez(file, 
                 nodes=self.nodes,
                 edges=self.edges, 
            )
        
    def load_matrices(self, file) -> None: 
        matrices = np.load(file)
        self.nodes = matrices['nodes']
        self.edges = matrices['edges']
    
    def create_board(self) -> None: 
        if self.game_mode == 'wormhole': 
            b = Board(self.size)
        elif self.game_mode == 'normal': 
            b = NormalBoard(self.size)

        self.nodes = np.zeros((len(b), len(Pieces) + len(Teams)), dtype=np.uint8)
        self.nodes[:, Pieces.EMPTY] = 1
        
        self.edges = [[], []] 
        
        for tile in b.tiles.values(): 
            for neighbor in tile.neighbors.values():
                if neighbor is not None: 
                    self.edges[0] += [tile.id, neighbor.id]
                    self.edges[1] += [neighbor.id, tile.id]
        
        self.edges = np.array(self.edges, dtype=np.uint8)

        self.save_matrices()

    def set_piece(self, type: int, player: int, position: int) -> None: 
        piece = self.nodes[position]
        piece[:] = 0

        if type == Pieces.EMPTY:
            piece[type] = 1 
        else:
            piece[type] = 1
            piece[self.piece_types + player] = 1

    def update_board(self, movement: Tuple) -> None: 
        player, origin_tile, destination_tile, new_type = movement
        # moving_piece_index should not be necessary because it requires pieces list from the other class. The other variables should give all necessary info? 

        self.set_piece(Pieces.EMPTY, 0, origin_tile)
        self.set_piece(new_type, player, destination_tile)

    def to_pyg_data(self, device):
        x = torch.tensor(self.nodes, dtype=torch.float32, device=device) 
        edge_index = torch.tensor(self.edges, dtype=torch.long, device=device)
        return Data(x=x, edge_index=edge_index)

    def batch_to_pyg_data(self, graph_list, device):
        data_list = []
        edge_index = torch.tensor(self.edges, dtype=torch.long, device=device)
        for graph in graph_list:
            data = Data(x=graph, edge_index=edge_index)
            data_list.append(data)
        batch = Batch.from_data_list(data_list)
        return batch
    