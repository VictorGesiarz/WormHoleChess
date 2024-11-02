
class Tile: 
    def __init__(self) -> None:
        self.next_row
        self.next_col
        self.prev_row
        self.prev_col


class Board:
    def __init__(self) -> None:
        self.board = self.create_board()
        
    def create_board(self) -> dict[str: Tile]:
        for row in range(16):
            for col in range(8): 
                


class WormWholeChess: 
    def __init__(self) -> None:
        pass