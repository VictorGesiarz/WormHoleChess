from typing import List, Dict, Tuple

from engine.core.base.NormalBoard import NormalBoard
from engine.core.base.Tile import Tile, D
from engine.core.base.Pieces import Piece, Pawn, Knight


class Board(NormalBoard):
    def __init__(self, size: Tuple[int, int] = (8, 8), innitialize: bool = True) -> None:
        self.size = size
        rows, cols = size
        self.rows = [str(i) for i in range(1, rows + 1)]
        self.cols = [chr(i) for i in range(ord('a'), ord('a') + cols)]
        self.cols_dict = {col: i + 1 for i, col in enumerate(self.cols)}
        self.cols_inv_dict = {i + 1: col for i, col in enumerate(self.cols)}
        
        # Adjust these based on size
        if size == (8, 8):
            self.pentagons = ['c3', 'c6', 'f3', 'f6']
            self.loop_cols = ['d', 'e']
            self.loop_rows = ['4', '5']
        elif size == (6, 6):
            self.pentagons = ['b2', 'e2', 'b5', 'e5']
            self.loop_cols = ['c', 'd']
            self.loop_rows = ['3', '4']
        else:
            self.pentagons = []
            self.loop_cols = []
            self.loop_rows = []

        self.tiles: Dict[str, Tile] = {}
        if innitialize:
            self.tiles = self.create_tiles()
            self.connect_tiles()
            self.remap_knight_data()
            self.remap_pawn_data()
        
        self.pieces: List[Piece] = []

    def copy(self) -> 'Board': 
        # If in the future we add parameters to the board for the size we will need to pass them 
        board_copy = Board(size=self.size, innitialize=False)
        
        for tile_name, tile in self.tiles.items(): 
            board_copy.tiles[tile_name] = Tile(tile_name, tile.row, tile.col, board_copy, tile.id, tile.top_side, tile.pentagon, tile.loop)

        for tile_name, tile in self.tiles.items(): 
            neighbors_copy = {}
            for from_direction, neighbor in tile.neighbors.items(): 
                neighbors_copy[from_direction] = None if not neighbor else board_copy.tiles[neighbor.name]
            tile_copy = board_copy.tiles[tile_name]
            tile_copy.set_neighbors(neighbors_copy)
            if tile.pentagon: 
                tile_copy.additional_relations = tile.additional_relations
        return board_copy

    def create_tiles(self) -> Dict[str, Tile]:
        tiles = {}
        top_side = True
        tile_id = 0

        for _ in range(2): 
            for col in self.cols: 
                for row in self.rows: 
                    name = col + row
                    pentagon = name in self.pentagons
                    name += '_T' if top_side else '_B'
                    loop = col in self.loop_cols and row in self.loop_rows
                    tile = Tile(name, int(row), col, self, tile_id, top_side, pentagon, loop)
                    tiles[name] = tile
                    tile_id += 1

                    if loop: 
                        for additional in ['_1', '_2']:
                            additional_name = name[:2] + additional + name[2:]
                            tile = Tile(additional_name, int(row), col, self, tile_id, top_side, False, True)
                            tiles[additional_name] = tile
                            tile_id += 1
            top_side = not top_side
        return tiles
    
    def connect_tiles(self) -> None: 
        top_side_directions = {
            D.UP_LEFT: (1, -1),
            D.UP: (1, 0),
            D.UP_RIGHT: (1, 1),
            D.LEFT: (0, -1),
            D.RIGHT: (0, 1),
            D.DOWN_LEFT: (-1, -1),
            D.DOWN: (-1, 0),
            D.DOWN_RIGHT: (-1, 1),
        }
        bottom_side_directions = {
            D.UP_LEFT: (1, 1), 
            D.UP: (1, 0), 
            D.UP_RIGHT: (1, -1),
            D.LEFT: (0, 1),
            D.RIGHT: (0, -1),
            D.DOWN_LEFT: (-1, 1),
            D.DOWN: (-1, 0),
            D.DOWN_RIGHT: (-1, -1),
        }
        
        max_row, max_col = self.size
        for name, tile in self.tiles.items():
            col = self.cols_dict[name[0]]
            row = int(name[1])
            side = '_T' if tile.top_side else '_B'

            directions = top_side_directions if tile.top_side else bottom_side_directions
            for direction, (dr, dc) in directions.items():
                neighbor_row, neighbor_col = row + dr, col + dc
                if 1 <= neighbor_row <= max_row and 1 <= neighbor_col <= max_col: 
                    neighbor_name = self.cols_inv_dict[neighbor_col] + str(neighbor_row) + side 
                    neighbor_tile = self.tiles[neighbor_name]
                    tile.neighbors[direction] = neighbor_tile

                    self.connect_additional(tile, neighbor_tile)
            tile.make_neighbors_inv()
        self.connect_manual()
        self.relate_pentagons()

    def connect_additional(self, tile: Tile, neighbor_tile: Tile) -> None: 
        if tile.pentagon and (neighbor_tile.loop):
            name = neighbor_tile.name
            neihbor_name = name[:2] + '_1' + name[2:]
            tile.neighbors[D.ADDITIONAL_STRAIGHT] = self.tiles[neihbor_name]
            neihbor_name = name[:2] + '_2' + name[2:]
            tile.neighbors[D.ADDITIONAL_DIAGONAL] = self.tiles[neihbor_name]

    def connect_manual(self) -> None: 
        top_connections = {
            'd3_T': {D.UP_LEFT: 'd4_1_T'},
            'e3_T': {D.UP_RIGHT: 'e4_1_T'},
            'c4_T': {D.DOWN_RIGHT: 'd4_1_T', D.RIGHT: 'd4_2_T', D.UP_RIGHT: 'd5_2_T'},
            'f4_T': {D.DOWN_LEFT: 'e4_1_T', D.LEFT: 'e4_2_T', D.UP_LEFT: 'e5_2_T'},
            'c5_T': {D.DOWN_RIGHT: 'd4_2_T', D.RIGHT: 'd5_2_T', D.UP_RIGHT: 'd5_1_T'},
            'f5_T': {D.DOWN_LEFT: 'e4_2_T', D.LEFT: 'e5_2_T', D.UP_LEFT: 'e5_1_T'},
            'd6_T': {D.DOWN_LEFT: 'd5_1_T'},
            'e6_T': {D.DOWN_RIGHT: 'e5_1_T'},
            
            'd4_T': {D.LEFT: 'd4_1_T', D.UP_LEFT: 'd4_1_B', D.UP: 'd4_B', D.UP_RIGHT: 'e4_B'},
            'd4_1_T': {D.LEFT: 'd4_2_T', D.UP_LEFT: 'd4_2_B', D.UP: 'd4_1_B', D.UP_RIGHT: 'd4_B', D.RIGHT: 'd4_T', D.DOWN_RIGHT: 'd3_T', D.DOWN: 'c3_T', D.DOWN_LEFT: 'c4_T'},
            'd4_2_T': {D.LEFT: 'c4_T', D.UP_LEFT: 'c5_T', D.UP: 'd5_2_T', D.UP_RIGHT: 'd5_2_B', D.RIGHT: 'd4_2_B', D.DOWN_RIGHT: 'd4_1_B', D.DOWN: 'd4_1_T', D.DOWN_LEFT: 'c3_T'},
            'd5_2_T': {D.LEFT: 'c5_T', D.UP_LEFT: 'c6_T', D.UP: 'd5_1_T', D.UP_RIGHT: 'd5_1_B', D.RIGHT: 'd5_2_B', D.DOWN_RIGHT: 'd4_2_B', D.DOWN: 'd4_2_T', D.DOWN_LEFT: 'c4_T'},
            'd5_1_T': {D.LEFT: 'd5_2_T', D.UP_LEFT: 'c5_T', D.UP: 'c6_T', D.UP_RIGHT: 'd6_T', D.RIGHT: 'd5_T', D.DOWN_RIGHT: 'd5_B', D.DOWN: 'd5_1_B', D.DOWN_LEFT: 'd5_2_B'},
            'd5_T': {D.LEFT: 'd5_1_T', D.DOWN_LEFT: 'd5_1_B', D.DOWN: 'd5_B', D.DOWN_RIGHT: 'e5_B'},
            
            'e4_T': {D.RIGHT: 'e4_1_T', D.UP_LEFT: 'd4_B', D.UP: 'e4_B', D.UP_RIGHT: 'e4_1_B'},
            'e4_1_T': {D.LEFT: 'e4_T', D.UP_LEFT: 'e4_B', D.UP: 'e4_1_B', D.UP_RIGHT: 'e4_2_B', D.RIGHT: 'e4_2_T', D.DOWN_RIGHT: 'f4_T', D.DOWN: 'f3_T', D.DOWN_LEFT: 'e3_T'},
            'e4_2_T': {D.LEFT: 'e4_2_B', D.UP_LEFT: 'e5_2_B', D.UP: 'e5_2_T', D.UP_RIGHT: 'f5_T', D.RIGHT: 'f4_T', D.DOWN_RIGHT: 'f3_T', D.DOWN: 'e4_1_T', D.DOWN_LEFT: 'e4_1_B'},
            'e5_2_T': {D.LEFT: 'e5_2_B', D.UP_LEFT: 'e5_1_B', D.UP: 'e5_1_T', D.UP_RIGHT: 'f6_T', D.RIGHT: 'f5_T', D.DOWN_RIGHT: 'f4_T', D.DOWN: 'e4_2_T', D.DOWN_LEFT: 'e4_2_B'},
            'e5_1_T': {D.LEFT: 'e5_T', D.UP_LEFT: 'e6_T', D.UP: 'f6_T', D.UP_RIGHT: 'f5_T', D.RIGHT: 'e5_2_T', D.DOWN_RIGHT: 'e5_2_B', D.DOWN: 'e5_1_B', D.DOWN_LEFT: 'e5_B'},
            'e5_T': {D.RIGHT: 'e5_1_T', D.DOWN_LEFT: 'd5_B', D.DOWN: 'e5_B', D.DOWN_RIGHT: 'e5_1_B'}
        }

        bottom_connections = {
            'd3_B': {D.UP_RIGHT: 'd4_1_B'},
            'e3_B': {D.UP_LEFT: 'e4_1_B'},
            'c4_B': {D.DOWN_LEFT: 'd4_1_B', D.LEFT: 'd4_2_B', D.UP_LEFT: 'd5_2_B'},
            'f4_B': {D.DOWN_RIGHT: 'e4_1_B', D.RIGHT: 'e4_2_B', D.UP_RIGHT: 'e5_2_B'},
            'c5_B': {D.DOWN_LEFT: 'd4_2_B', D.LEFT: 'd5_2_B', D.UP_LEFT: 'd5_1_B'},
            'f5_B': {D.DOWN_RIGHT: 'e4_2_B', D.RIGHT: 'e5_2_B', D.UP_RIGHT: 'e5_1_B'},
            'd6_B': {D.DOWN_RIGHT: 'd5_1_B'},
            'e6_B': {D.DOWN_LEFT: 'e5_1_B'},
            
            'd4_B': {D.RIGHT: 'd4_1_B', D.UP_RIGHT: 'd4_1_T', D.UP: 'd4_T', D.UP_LEFT: 'e4_T'},
            'd4_1_B': {D.RIGHT: 'd4_2_B', D.UP_RIGHT: 'd4_2_T', D.UP: 'd4_1_T', D.UP_LEFT: 'd4_T', D.LEFT: 'd4_B', D.DOWN_LEFT: 'd3_B', D.DOWN: 'c3_B', D.DOWN_RIGHT: 'c4_B'},
            'd4_2_B': {D.RIGHT: 'c4_B', D.UP_RIGHT: 'c5_B', D.UP: 'd5_2_B', D.UP_LEFT: 'd5_2_T', D.LEFT: 'd4_2_T', D.DOWN_LEFT: 'd4_1_T', D.DOWN: 'd4_1_B', D.DOWN_RIGHT: 'c3_B'},
            'd5_2_B': {D.RIGHT: 'c5_B', D.UP_RIGHT: 'c6_B', D.UP: 'd5_1_B', D.UP_LEFT: 'd5_1_T', D.LEFT: 'd5_2_T', D.DOWN_LEFT: 'd4_2_T', D.DOWN: 'd4_2_B', D.DOWN_RIGHT: 'c4_B'},
            'd5_1_B': {D.RIGHT: 'd5_2_B', D.UP_RIGHT: 'c5_B', D.UP: 'c6_B', D.UP_LEFT: 'd6_B', D.LEFT: 'd5_B', D.DOWN_LEFT: 'd5_T', D.DOWN: 'd5_1_T', D.DOWN_RIGHT: 'd5_2_T'},
            'd5_B': {D.RIGHT: 'd5_1_B', D.DOWN_RIGHT: 'd5_1_T', D.DOWN: 'd5_T', D.DOWN_LEFT: 'e5_T'},
            
            'e4_B': {D.LEFT: 'e4_1_B', D.UP_RIGHT: 'd4_T', D.UP: 'e4_T', D.UP_LEFT: 'e4_1_T'},
            'e4_1_B': {D.RIGHT: 'e4_B', D.UP_RIGHT: 'e4_T', D.UP: 'e4_1_T', D.UP_LEFT: 'e4_2_T', D.LEFT: 'e4_2_B', D.DOWN_LEFT: 'f4_B', D.DOWN: 'f3_B', D.DOWN_RIGHT: 'e3_B'},
            'e4_2_B': {D.RIGHT: 'e4_2_T', D.UP_RIGHT: 'e5_2_T', D.UP: 'e5_2_B', D.UP_LEFT: 'f5_B', D.LEFT: 'f4_B', D.DOWN_LEFT: 'f3_B', D.DOWN: 'e4_1_B', D.DOWN_RIGHT: 'e4_1_T'},
            'e5_2_B': {D.RIGHT: 'e5_2_T', D.UP_RIGHT: 'e5_1_T', D.UP: 'e5_1_B', D.UP_LEFT: 'f6_B', D.LEFT: 'f5_B', D.DOWN_LEFT: 'f4_B', D.DOWN: 'e4_2_B', D.DOWN_RIGHT: 'e4_2_T'},
            'e5_1_B': {D.RIGHT: 'e5_B', D.UP_RIGHT: 'e6_B', D.UP: 'f6_B', D.UP_LEFT: 'f5_B', D.LEFT: 'e5_2_B', D.DOWN_LEFT: 'e5_2_T', D.DOWN: 'e5_1_T', D.DOWN_RIGHT: 'e5_T'},
            'e5_B': {D.LEFT: 'e5_1_B', D.DOWN_RIGHT: 'd5_T',D.DOWN: 'e5_T', D.DOWN_LEFT: 'e5_1_T'}
        }

        if self.size == (6, 6):
            top_connections = self.remap_connections(top_connections, -1, -1)
            bottom_connections = self.remap_connections(bottom_connections, -1, -1)

        self.connect_tiles_manual(top_connections)
        self.connect_tiles_manual(bottom_connections)
        
    def connect_tiles_manual(self, connections: dict[dict[str]]):
        for tile_name, tile_connections in connections.items():
            tile = self.tiles[tile_name]
            for direction, neighbor_name in tile_connections.items():
                neighbor_tile = self.tiles.get(neighbor_name)
                if neighbor_tile:
                    tile.modify_neighbors({direction: neighbor_tile})

    def relate_pentagons(self): 
        additional_relations = {
            'c3_T': {D.DOWN: [D.UP, D.ADDITIONAL_STRAIGHT], D.LEFT: [D.RIGHT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.DOWN, D.LEFT], D.DOWN_LEFT: [D.ADDITIONAL_DIAGONAL, D.UP_RIGHT], D.ADDITIONAL_DIAGONAL: [D.DOWN_LEFT]},
            'c3_B': {D.DOWN: [D.UP, D.ADDITIONAL_STRAIGHT], D.RIGHT: [D.LEFT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.DOWN, D.RIGHT], D.DOWN_RIGHT: [D.ADDITIONAL_DIAGONAL, D.UP_LEFT], D.ADDITIONAL_DIAGONAL: [D.DOWN_RIGHT]},
            
            'c6_T': {D.UP: [D.DOWN, D.ADDITIONAL_STRAIGHT], D.LEFT: [D.RIGHT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.UP, D.LEFT], D.UP_LEFT: [D.ADDITIONAL_DIAGONAL, D.DOWN_RIGHT], D.ADDITIONAL_DIAGONAL: [D.UP_LEFT]},
            'c6_B': {D.UP: [D.DOWN, D.ADDITIONAL_STRAIGHT], D.RIGHT: [D.LEFT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.UP, D.RIGHT], D.UP_RIGHT: [D.ADDITIONAL_DIAGONAL, D.DOWN_LEFT], D.ADDITIONAL_DIAGONAL: [D.UP_RIGHT]},
            
            'f3_T': {D.DOWN: [D.UP, D.ADDITIONAL_STRAIGHT], D.RIGHT: [D.LEFT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.DOWN, D.RIGHT], D.DOWN_RIGHT: [D.ADDITIONAL_DIAGONAL, D.UP_LEFT], D.ADDITIONAL_DIAGONAL: [D.DOWN_RIGHT]},
            'f3_B': {D.DOWN: [D.UP, D.ADDITIONAL_STRAIGHT], D.LEFT: [D.RIGHT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.DOWN, D.LEFT], D.DOWN_LEFT: [D.ADDITIONAL_DIAGONAL, D.UP_RIGHT], D.ADDITIONAL_DIAGONAL: [D.DOWN_LEFT]},
            
            'f6_T': {D.UP: [D.DOWN, D.ADDITIONAL_STRAIGHT], D.RIGHT: [D.LEFT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.UP, D.RIGHT], D.UP_RIGHT: [D.ADDITIONAL_DIAGONAL, D.DOWN_LEFT], D.ADDITIONAL_DIAGONAL: [D.UP_RIGHT]},
            'f6_B': {D.UP: [D.DOWN, D.ADDITIONAL_STRAIGHT], D.LEFT: [D.RIGHT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.UP, D.LEFT], D.UP_LEFT: [D.ADDITIONAL_DIAGONAL, D.DOWN_RIGHT], D.ADDITIONAL_DIAGONAL: [D.UP_LEFT]}
        }
        
        if self.size == (6, 6):
            additional_relations = self.remap_relations(additional_relations, -1, -1)

        for tile_name, relations in additional_relations.items():
            tile = self.tiles[tile_name]
            tile.set_relations(relations)

    def shift_tile_name(self, name: str, row_offset: int, col_offset: int) -> str:
        import re
        match = re.match(r'^([a-z])(\d+)(.*)$', name)
        if not match:
            return name  # Not a tile name

        col, row, suffix = match.groups()
        new_col = chr(ord(col) + col_offset)
        new_row = str(int(row) + row_offset)
        return f"{new_col}{new_row}{suffix}"

    def remap_connections(self, connections: dict, row_offset: int, col_offset: int) -> dict:
        new_connections = {}
        for tile_name, tile_dict in connections.items():
            new_tile = self.shift_tile_name(tile_name, row_offset, col_offset)
            new_tile_dict = {d: self.shift_tile_name(n, row_offset, col_offset) for d, n in tile_dict.items()}
            new_connections[new_tile] = new_tile_dict
        return new_connections
    
    def remap_relations(self, relations: dict, row_offset: int, col_offset: int) -> dict:
        new_relations = {}
        for tile_name, direction_map in relations.items():
            new_tile = self.shift_tile_name(tile_name, row_offset, col_offset)
            new_direction_map = {d: v.copy() for d, v in direction_map.items()}  # No names to shift inside values
            new_relations[new_tile] = new_direction_map
        return new_relations
    
    def remap_knight_data(self) -> None: 
        if self.size == (6, 6):
            new_attacks = {}
            for tile_name, moves in Knight.ATTACKS_IN_LOOP.items():
                new_tile = self.shift_tile_name(tile_name, -1, -1)
                new_moves = [self.shift_tile_name(move, -1, -1) for move in moves]
                new_attacks[new_tile] = new_moves
            Knight.ATTACKS_IN_LOOP = new_attacks
    
    def remap_pawn_data(self) -> None: 
        """ This part of the code is horrendous but I don't have time to do it better. """
        for i in range(4): 
            if self.size[0] < 6: 
                Pawn.PAWNS[i]['first_row'] = -1
            elif Pawn.PAWNS[i]['first_row'] != 2: 
                Pawn.PAWNS[i]['first_row'] = self.size[0] - 1
            promotion_rows = Pawn.PAWNS[i]['promotion_rows']
            for j, row in enumerate(promotion_rows):
                promotion_rows[j] = row.replace('8', str(self.size[0]))

        if self.size == (6, 6): 
            new_quadrants = [
                [1, 2, 3],
                [4, 5, 6],
                [1, 2, 3],
                [4, 5, 6]
            ]
            for i in range(4): 
                Pawn.QUADRANTS[i]['rows'] = new_quadrants[i]
