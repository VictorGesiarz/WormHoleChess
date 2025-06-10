from typing import List, Dict, Tuple

from engine.core.base.Tile import Tile, D
from engine.core.base.Pieces import Piece, Pawn


class NormalBoard:
    def __init__(self, size: Tuple[int] = (8, 8), innitialize: bool = True) -> None:
        self.size = size
        
        self.tiles: Dict[str, Tile] = {}
        if innitialize:
            self.tiles = self.create_tiles()
            self.connect_tiles()
            self.remap_pawn_data()
        
        self.pieces: List[Piece] = []

    def __getitem__(self, key: str | Tile) -> Tile:
        if isinstance(key, Tile):
            return self.tiles[key.name]
        return self.tiles[key]

    def __contains__(self, key: str) -> bool:
        return key in self.tiles

    def __iter__(self):
        return iter(self.tiles.items())
    
    def __hash__(self):
        return 
    
    def __len__(self): 
        return len(self.tiles)

    def keys(self):
        return self.tiles.keys()

    def values(self):
        return self.tiles.values()

    def check_size(self) -> None:
        from pympler import asizeof
        print(f"Total size of the instance: {asizeof.asizeof(self)} bytes")

    def copy(self) -> 'NormalBoard': 
        # If in the future we add parameters to the board for the size we will need to pass them 
        board_copy = NormalBoard(size=self.size, innitialize=False)
        
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
        rows = [str(i) for i in range(1, self.size[0] + 1)]
        cols = [chr(i) for i in range(ord('a'), ord('a') + self.size[1])]
        tiles = {}

        tile_id = 0
        for i, col in enumerate(cols): 
            for j, row in enumerate(rows): 
                name = col + row
                tile = Tile(name, int(row), col, self, tile_id, True, False, False)
                tiles[name] = tile
                tile_id += 1
        return tiles 
    
    def connect_tiles(self) -> None: 
        rows = [str(i) for i in range(1, self.size[0] + 1)]
        cols = [chr(i) for i in range(ord('a'), ord('a') + self.size[1])]
        cols_dict = {col: i + 1 for i, col in enumerate(cols)}
        cols_inv_dict = {i + 1: col for i, col in enumerate(cols)}

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
            col = cols_dict[name[0]]
            row = int(name[1])

            directions = top_side_directions if tile.top_side else bottom_side_directions
            for direction, (dr, dc) in directions.items():
                neighbor_row, neighbor_col = row + dr, col + dc
                if 1 <= neighbor_row <= self.size[0] and 1 <= neighbor_col <= self.size[1]: 
                    neighbor_name = cols_inv_dict[neighbor_col] + str(neighbor_row) 
                    neighbor_tile = self.tiles[neighbor_name]
                    tile.neighbors[direction] = neighbor_tile
                    
            tile.make_neighbors_inv()

    def remap_pawn_data(self) -> None: 
        """ This part of the code is horrendous but I don't have time to do it better. """
        for i in range(2): 
            if self.size[0] < 6: 
                Pawn.PAWNS[i]['first_row'] = -1
            elif Pawn.PAWNS[i]['first_row'] != 2: 
                Pawn.PAWNS[i]['first_row'] = self.size[0] - 1
            promotion_rows = Pawn.PAWNS[i]['promotion_rows']
            for j, row in enumerate(promotion_rows):
                promotion_rows[j] = row.replace('8', str(self.size[0]))
