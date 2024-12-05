
from chess_logic_2 import Tile

class Piece: 
    def __init__(self, position: Tile) -> None:
        self.position = position 
        
    def get_pos(self) -> Tile:
        return self.position
    
    def get_movements(self) -> list[Tile]: 
        ...
    
    def check_tile(self, tile: Tile) -> bool:
        if tile.piece is not None:
            return True
    
    def move(self, to: Tile) -> bool:
        if to in self.get_movements(): 
            self.position = to
            return True
        return False 
    
    
class Tower(Piece):
    def __init__(self, position: Tile) -> None:
        super().__init__(position)
        
    def get_movements(self) -> list[Tile]:
        positions = []
        directions = ["up", "left", "right", "down"]
        for direction in directions: 
            current = self.position.neighbors[direction]
            while (current is not None) and (not self.check_tile(current)): 
                positions.append(current)
                current = current.neighbors[direction]
        return positions
                
                
class Knight(Piece): 
    def __init__(self, position: Tile) -> None:
        super().__init__(position)
        
    def get_movements(self) -> list[Tile]:
        ... 
        
    def make_pattern(self, tile: Tile) -> Tile: 
        ...    
        
        
class Bishop(Piece): 
    def __init__(self, position: Tile) -> None:
        super().__init__(position)
        
    def get_movements(self) -> list[Tile]:
        positions = []
        directions = ["up_left", "down_left", "up_right", "down_right"]
        for direction in directions: 
            current = self.position.neighbors[direction]
            while (current is not None) and (not self.check_tile(current)): 
                positions.append(current)
                current = current.neighbors[direction]
        return positions 
    
    
class Queen(Piece): 
    def __init__(self, position: Tile) -> None:
        super().__init__(position)
        
    def get_movements(self) -> list[Tile]:
        positions = []
        directions = ["up", "left", "right", "down", 
                      "up_left", "down_left", "up_right", "down_right"]
        for direction in directions: 
            current = self.position.neighbors[direction]
            while (current is not None) and (not self.check_tile(current)): 
                positions.append(current)
                current = current.neighbors[direction]
        return positions 
    
    
class King(Piece): 
    def __init__(self, position: Tile) -> None:
        super().__init__(position)
        
    def get_movements(self) -> list[Tile]:
        positions = []
        directions = ["up", "left", "right", "down", 
                      "up_left", "down_left", "up_right", "down_right"]
        for direction in directions: 
            current = self.position.neighbors[direction]
            if (current is not None) and (not self.check_tile(current)): 
                positions.append(current)
        return positions 