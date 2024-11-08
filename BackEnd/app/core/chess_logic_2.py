class Tile:
    def __init__(self, name: str, side: str, row: int, col: str, additional: int = None):
        self.name = name
        self.side = side
        self.row = row
        self.col = col
        self.additional = additional

        # Standard neighbors
        self.neighbors = {
            "up_left": None, "up": None, "up_right": None,
            "left": None, "right": None,
            "down_left": None, "down": None, "down_right": None
        }

    def add_neighbor(self, direction: str, tile):
        """Link a neighboring tile in a specific direction."""
        if direction in self.neighbors:
            self.neighbors[direction] = tile

    def __str__(self) -> str:
        return f"{self.name} ({self.side} side, Row {self.row}, Col {self.col})"


class Pentagon(Tile):
    def __init__(self, name: str, side: str, row: int, col: str, additional: int = None):
        super().__init__(name, side, row, col, additional)
        # Additional neighbors for the special pentagon tiles
        self.additional_neighbors = {"additional_up": None, "additional_down": None}

    def add_additional_neighbor(self, direction: str, tile):
        """Link an additional neighbor for a pentagon."""
        if direction in self.additional_neighbors:
            self.additional_neighbors[direction] = tile


class Board:
    def __init__(self):
        self.tiles = {}

    def add_tile(self, tile: Tile):
        self.tiles[tile.name] = tile

    def link_tiles(self, tile_name: str, neighbor_name: str, direction: str):
        """Link two tiles in the specified direction."""
        tile = self.tiles.get(tile_name)
        neighbor = self.tiles.get(neighbor_name)
        if tile and neighbor:
            tile.add_neighbor(direction, neighbor)

    def link_pentagon_special(self, tile_name: str, neighbor_name: str, direction: str):
        """Link additional neighbors for pentagon tiles."""
        tile = self.tiles.get(tile_name)
        neighbor = self.tiles.get(neighbor_name)
        if isinstance(tile, Pentagon) and neighbor:
            tile.add_additional_neighbor(direction, neighbor)

    def create_standard_board(self):
        """Create and link tiles on both 'T' and 'B' sides with special tiles."""
        # Create tiles for both sides
        for side in ['T', 'B']:
            for row in range(1, 9):
                for col in 'abcdefgh':
                    tile_name = f"{side}_{col}{row}"
                    self.add_tile(Tile(name=tile_name, side=side, row=row, col=col))

        # Add special pentagon tiles with multiple adjacencies
        for side in ['T', 'B']:
            for row, col in [(4, 'd'), (4, 'e'), (5, 'd'), (5, 'e')]:
                for i in range(1, 4):
                    tile_name = f"{side}_{col}{row}{i}"
                    self.add_tile(Pentagon(name=tile_name, side=side, row=row, col=col, additional=i))

        # Link standard tiles by rows and columns (up, down, left, right)
        for tile in self.tiles.values():
            self.link_standard_neighbors(tile)

        # Link additional neighbors for pentagons
        self.link_special_tiles()

    def link_standard_neighbors(self, tile: Tile):
        """Define neighbors for each tile on the grid (up, down, etc.)."""
        # Example logic to find neighbors based on position
        row, col, side = tile.row, tile.col, tile.side

        # Define standard neighbors
        directions = {
            "up": (row + 1, col),
            "down": (row - 1, col),
            "left": (row, chr(ord(col) - 1)),
            "right": (row, chr(ord(col) + 1)),
            # Add up_left, up_right, down_left, down_right
        }

        for direction, (n_row, n_col) in directions.items():
            neighbor_name = f"{side}_{n_col}{n_row}"
            if neighbor_name in self.tiles:
                tile.add_neighbor(direction, self.tiles[neighbor_name])

    def link_special_tiles(self):
        """Link additional neighbors for pentagon tiles."""
        special_pairs = [
            ("T_d41", "B_d41"), ("T_e41", "B_e41"),
            ("T_d42", "B_d42"), ("T_e42", "B_e42"),
            # Add all other special pairs
        ]
        for t_name, b_name in special_pairs:
            if t_name in self.tiles and b_name in self.tiles:
                self.tiles[t_name].add_additional_neighbor("additional_down", self.tiles[b_name])
                self.tiles[b_name].add_additional_neighbor("additional_up", self.tiles[t_name])

# Usage
board = Board()
board.create_standard_board()
