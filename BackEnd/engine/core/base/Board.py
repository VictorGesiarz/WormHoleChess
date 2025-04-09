import json

from engine.core.base.Tile import Tile, D
from engine.core.base.Pieces import Piece
from engine.core.constants import NUMBER_TO_COLOR


class Board:
    rows = [str(i) for i in range(1, 9)]
    cols = [chr(i) for i in range(ord('a'), ord('h') + 1)]
    cols_dict = {col: i + 1 for i, col in enumerate(cols)}
    cols_inv_dict = {i + 1: col for i, col in enumerate(cols)}
    pentagons = ['c3', 'c6', 'f3', 'f6']
    loop_cols = ['d', 'e']
    loop_rows = ['4', '5']

    def __init__(self) -> None:
        self.tiles = {}
        tiles = self.create_tiles()
        self.set_tiles(tiles)
        self.connect_tiles()

    def __getitem__(self, key: str | Tile) -> Tile:
        if isinstance(key, Tile):
            return self.tiles[key.name]
        return self.tiles[key]

    def __contains__(self, key: str) -> bool:
        return key in self.tiles

    def __iter__(self):
        return iter(self.tiles.items())

    def keys(self):
        return self.tiles.keys()

    def values(self):
        return self.tiles.values()

    def add_tile(self, tile: Tile) -> None:
        self.tiles[tile.name] = tile

    def set_tiles(self, tiles: list[Tile]) -> None: 
        for tile in tiles: 
            self.add_tile(tile)

    def check_size(self) -> None:
        from pympler import asizeof
        print(f"Total size of the instance: {asizeof.asizeof(self)} bytes")

    def create_tiles(self) -> list[Tile]:
        tiles = []
        top_side = True
        for _ in range(2): 
            for i, col in enumerate(Board.cols): 
                for j, row in enumerate(Board.rows): 
                    name = col + row
                    pentagon = True if name in Board.pentagons else False
                    name += ('_T' if top_side else '_B')
                    loop = True if col in Board.loop_cols and row in Board.loop_rows else False 
                    tile = Tile(name, int(row), col, self, top_side, pentagon, loop)
                    tiles.append(tile)

                    if loop: 
                        for additional in ['_1', '_2']:
                            additional_name = name[:2] + additional + name[2:]
                            tile = Tile(additional_name, int(row), col, self, top_side, False, True)
                            tiles.append(tile)
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
        
        for name, tile in self.tiles.items():
            col = Board.cols_dict[name[0]]
            row = int(name[1])
            side = '_T' if tile.top_side else '_B'

            directions = top_side_directions if tile.top_side else bottom_side_directions
            for direction, (dr, dc) in directions.items():
                neighbor_row, neighbor_col = row + dr, col + dc
                if 1 <= neighbor_row <= 8 and 1 <= neighbor_col <= 8: 
                    neighbor_name = Board.cols_inv_dict[neighbor_col] + str(neighbor_row) + side 
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
            'c3_B': {D.DOWN: [D.UP, D.ADDITIONAL_STRAIGHT], D.LEFT: [D.RIGHT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.DOWN, D.LEFT], D.DOWN_LEFT: [D.ADDITIONAL_DIAGONAL, D.UP_RIGHT], D.ADDITIONAL_DIAGONAL: [D.DOWN_LEFT]},
            
            'c6_T': {D.UP: [D.DOWN, D.ADDITIONAL_STRAIGHT], D.LEFT: [D.RIGHT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.UP, D.LEFT], D.UP_LEFT: [D.ADDITIONAL_DIAGONAL, D.DOWN_RIGHT], D.ADDITIONAL_DIAGONAL: [D.UP_LEFT]},
            'c6_B': {D.UP: [D.DOWN, D.ADDITIONAL_STRAIGHT], D.LEFT: [D.RIGHT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.UP, D.LEFT], D.UP_LEFT: [D.ADDITIONAL_DIAGONAL, D.DOWN_RIGHT], D.ADDITIONAL_DIAGONAL: [D.UP_LEFT]},
            
            'f3_T': {D.DOWN: [D.UP, D.ADDITIONAL_STRAIGHT], D.RIGHT: [D.LEFT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.DOWN, D.RIGHT], D.DOWN_RIGHT: [D.ADDITIONAL_DIAGONAL, D.UP_LEFT], D.ADDITIONAL_DIAGONAL: [D.DOWN_RIGHT]},
            'f3_B': {D.DOWN: [D.UP, D.ADDITIONAL_STRAIGHT], D.RIGHT: [D.LEFT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.DOWN, D.RIGHT], D.DOWN_RIGHT: [D.ADDITIONAL_DIAGONAL, D.UP_LEFT], D.ADDITIONAL_DIAGONAL: [D.DOWN_RIGHT]},
            
            'f6_T': {D.UP: [D.DOWN, D.ADDITIONAL_STRAIGHT], D.RIGHT: [D.LEFT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.UP, D.RIGHT], D.UP_RIGHT: [D.ADDITIONAL_DIAGONAL, D.DOWN_LEFT], D.ADDITIONAL_DIAGONAL: [D.UP_RIGHT]},
            'f6_B': {D.UP: [D.DOWN, D.ADDITIONAL_STRAIGHT], D.RIGHT: [D.LEFT, D.ADDITIONAL_STRAIGHT], D.ADDITIONAL_STRAIGHT: [D.UP, D.RIGHT], D.UP_RIGHT: [D.ADDITIONAL_DIAGONAL, D.DOWN_LEFT], D.ADDITIONAL_DIAGONAL: [D.UP_RIGHT]}
        }
        
        for tile_name, relations in additional_relations.items():
            tile = self.tiles[tile_name]
            tile.set_relations(relations)
