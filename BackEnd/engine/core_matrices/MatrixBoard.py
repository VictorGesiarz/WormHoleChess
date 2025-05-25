from typing import List, Tuple, Dict
from enum import IntEnum 
import numpy as np 


from engine.core.layer.LayerBoard import LayerBoard
from engine.core.base.Board import Board
from engine.core.base.NormalBoard import NormalBoard


class Pieces(IntEnum):
    TOWER = 0
    KNIGHT = 1
    BISHOP = 2
    QUEEN = 3
    KING = 4
    PAWN = 5
    EMPTY = 6

class Teams(IntEnum): 
    WHITE = 0
    BLACK = 1
    BLUE = 2
    RED = 3
    NONE = 4

# Hard Coded distribution of the node_edges array
ELEMENTS = 22 
PARTITIONS = {
    Pieces.TOWER: (0, 6), 
    Pieces.KNIGHT: (6, 7), 
    Pieces.BISHOP: (7, 12), 
    Pieces.KING: (12, 14),
    Pieces.PAWN: (14, 22)
}


class LayerMatrixBoard: 
    def __init__(self, size: Tuple[int, int], game_mode: str = 'wormhole', innitialize: bool = True) -> None:
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

        self.nodes: np.array = [] # [[piece_type, team], ...]
        self.edges: np.array = [] # [[from, ...], [to, ...]]
        self.node_edges: np.array = [] # [[piece_type, from_index, to_index], ...]
        self.node_names: np.array = []
        
        self.pieces: np.array = [] # [[piece_type, position, team], ...]

        if innitialize: 
            self.create_board()
            
    def set_pieces(self, pieces: List[np.array]) -> None:
        ...
        
    def get_pieces(self, player: int) -> Tuple[np.array, np.array]:
        mask = self.pieces[:, 2] == player
        return self.pieces[mask]
        
    def create_board(self) -> None:
        b = LayerBoard(self.size, self.game_mode)

        self.nodes = [(Pieces.EMPTY, Teams.NONE)] * len(b)
        self.node_names = list(b.tiles.keys())

        self.edges = []
        self.node_edges = [[-1 for _ in range(ELEMENTS)] for _ in range(len(b))]

        count = 0
        for tile in b.tiles.values():
            piece_layers = {
                Pieces.TOWER:  tile.tower_layer,
                Pieces.KNIGHT: tile.knight_layer,
                Pieces.BISHOP: tile.bishop_layer,
                Pieces.QUEEN:  tile.queen_layer,  # Currently unused
                Pieces.KING:   tile.king_layer,
                Pieces.PAWN:   tile.pawn_layer
            }

            for piece, layer in piece_layers.items():
                if piece == Pieces.QUEEN: 
                    continue 

                start = PARTITIONS[piece][0]

                # Skip queen layer, we can use a combination of tower and bishop to get the movements
                if piece in (Pieces.TOWER, Pieces.BISHOP): 
                    for i, direction in enumerate(layer.directions): 
                        self.edges.append([to_tile.id for to_tile in direction])
                        self.node_edges[tile.id][start + i] = count
                        count += 1

                elif piece == Pieces.KNIGHT: 
                    self.edges.append([to_tile.id for to_tile in layer.movements])
                    self.node_edges[tile.id][start] = count
                    count += 1

                elif piece == Pieces.KING: 
                    self.edges.append([to_tile.id for to_tile in layer.movements])
                    self.node_edges[tile.id][start] = count
                    count += 1
                    self.edges.append([to_tile.id for to_tile in layer.pawn_possible_atacks])
                    self.node_edges[tile.id][start + 1] = count
                    count += 1

                elif piece == Pieces.PAWN: 
                    for i, team in enumerate(Teams):
                        if team == Teams.NONE:
                            continue
                        self.edges.append([to_tile.id for to_tile in layer.moves[team]])
                        self.node_edges[tile.id][start + i] = count
                        count += 1
                        self.edges.append([to_tile.id for to_tile in layer.attacks[team]])
                        self.node_edges[tile.id][start + i + 1] = count
                        count += 1

        self.nodes = np.array(self.nodes, dtype=np.int8)
        self.edges = np.array(self.node_edges, dtype=np.int8)
        self.node_edges = np.array(self.node_edges, dtype=np.int16)
        self.node_names = np.array(self.node_names, dtype=str)

    def get_names(self, index_list: List[int]) -> List[str]: 
        return [self.node_names[i] for i in index_list]
    
    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)

        
class BaseMatrixBoard: 
    def __init__(self, size: Tuple[int, int], gamemode: str = 'wormhole') -> None:
        self.size = size
        self.gamemode = gamemode
        
        self.nodes: np.array
        self.edges: np.array
        self.create_board()
        
    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)
    
    def create_board(self) -> None: 
        if self.gamemode == 'wormhole': 
            b = Board(self.size)
        elif self.gamemode == 'normal': 
            b = NormalBoard(self.size)
                
        empty_tile = [0] * len(Pieces) + [0] * len(Teams)
        empty_tile[Pieces.EMPTY] = 1
        
        self.nodes = [empty_tile for _ in range(len(b))] 
        self.edges = [[], []] 
        
        for tile in b.tiles.values(): 
            for neighbor in tile.neighbors.values():
                if neighbor is not None: 
                    self.edges[0] += [tile.id, neighbor.id]
                    self.edges[1] += [neighbor.id, tile.id]
        
        self.nodes = np.array(self.nodes, dtype=int)
        self.edges = np.array(self.edges, dtype=int)
        