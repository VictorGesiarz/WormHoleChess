
class Tile: 
    def __init__(self, name: str, side: str, row: int, col: str, additional: int = None) -> None:
        self.name = name
        self.side = side
        self.row = row
        self.col = col
        self.additional = additional

        self.up_left = None
        self.up = None
        self.up_right = None
        self.left = None
        self.right = None
        self.down_left = None
        self.down = None
        self.down_right = None

    def __str__(self) -> str:
        return self.name

class Pentagon(Tile): 
    def __init__(self) -> None:
        super().__init__()
        self.additional_up = None
        self.additional_d = None


class Board:
    SIDES = ['T', 'B']
    COLS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    col_to_num = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
    num_to_col = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
    ROWS = 8 

    def __init__(self) -> None:
        self.tiles = {}
        self.board = []
        self.create_board()

    def __str__(self) -> str: 
        string = '\n'
        for side in self.board:
            for row in side:
                for col in row:
                    if type(col) == list:
                        string += f'[{" ".join(f'{tile}' for tile in col)}]'
                    else:
                        string += f'{col}' + ' '
                string += '\n'
            string += '\n' * 2
        return string

    def __is_pentagon(cls, col: int, row: int): 
        if (col == 'c' or col == 'f') and (row == 3 or row == 6): 
            return True
        return False
    
    def __is_12col_row(cls, col: int, row: int): 
        if (row == 4 or row == 5) and (col == 'd' or col == 'e'): 
            return True
        return False

    def create_board(self) -> None:
        for side in Board.SIDES: 
            side_ = []
            for row in range(1, Board.ROWS + 1):
                row_ = []
                for col in Board.COLS: 
                    tile_name = self.__write_notation(side, col, row)
                    if self.__is_12col_row(col, row): 
                        additional_tiles = []
                        for additional_tile in range(1, 4):
                            tile_name = self.__write_notation(side, col, row, additional_tile)
                            tile = Tile(tile_name, side, row, col)
                            self.tiles[tile_name] = tile
                            additional_tiles.append(tile)
                        row_.append(additional_tiles)
                    elif self.__is_pentagon(row, col): 
                        tile = Pentagon(tile_name, side, row, col)
                        self.tiles[tile_name] = tile
                        row_.append(tile)
                    else: 
                        tile = Tile(tile_name, side, row, col)
                        self.tiles[tile_name] = tile
                        row_.append(tile)
                side_.append(row_)
            self.board.append(side_)
        self.board[0] = self.board[0][::-1]
        print(self)
        self.__connect_tiles()
    
    def __connect_tiles(self) -> None:
        for tile in self.tiles.values():
            close_tiles = self.__find_close_tiles(tile)
            
    def __find_close_tiles(self, tile: Tile | Pentagon) -> list[str]: 
        side = tile.side 
        row = tile.row
        col = Board.col_to_num[tile.col]

        if self.__is_pentagon(col, row):
            tile.up_left = self.board[side][row-1][col-1]
            tile.up = self.board[side][row-1][col]
            tile.additional_d = self.board[side][row-1][col+1][0]
            tile.additional_up = self.board[side][row-1][col+1][1]
            tile.up_right = self.board[side][row-1][col+1][2]
            tile.left = self.board[side][row][col-1]
            tile.right = self.board[side][row][col+1]
            tile.down_left = self.board[side][row+1][col-1]
            tile.down = self.board[side][row+1][col]
            tile.down_right = self.board[side][row+1][col+1]

            close_tiles = [
                self.board[side][row+1][col-1], self.board[side][row+1][col], self.board[side][row+1][col+1]
            ]

    def __write_notation(self, side, col, row, additional=None):
        tile_name = f'{side}_{col}{row}'
        if additional is not None: 
            tile_name += f'{additional}'
        return tile_name


class WormWholeChess: 
    def __init__(self) -> None:
        self.board = Board()


b = Board()