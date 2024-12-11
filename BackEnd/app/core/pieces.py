
from chess_logic import Tile, D


class Piece: 
    def __init__(self, position: Tile, team: int) -> None:
        self.position = position 
        self.position.piece = self
        self.team = team
        
    def get_pos(self) -> Tile:
        return self.position
    
    def get_movements(self):
        ...
    
    def trace_direction(self, last: Tile, current: Tile, limit: int) -> list[Tile]:
        if current is None or limit == 0: 
            return []
        elif current.piece is not None: 
            if self.team == current.piece.team: 
                return []
            return [current]
        
        positions = [current]
        from_ = current.neighbors_inv[last.name]
        
        if current.pentagon and from_ in current.additional_relations: 
            to_ = current.additional_relations[from_]
        else:
            to_ = Tile.relations[from_]
        
        for to_i in to_:
            next_tile = current.neighbors[to_i]
            positions += self.trace_direction(current, next_tile, limit-1)

        return positions 
    
    def check_tile(self, tile: Tile) -> bool:
        if tile.piece is not None:
            return True
        return False
    
    def move(self, to: Tile) -> bool:
        if to in self.get_movements(): 
            self.position = to
            return True
        return False 

    
class Tower(Piece):
    def __init__(self, position: Tile, team: int) -> None:
        super().__init__(position, team)

    def get_movements(self) -> list[Tile]:
        directions = [D.UP, D.DOWN, D.LEFT, D.RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_STRAIGHT] 
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions += self.trace_direction(self.position, next_tile, limit=10)
        return positions


class Knight(Piece): 
    def __init__(self, position: Tile, team: int) -> None:
        super().__init__(position, team)
        
    def get_movements(self) -> list[Tile]:
        ... 
        
        
class Bishop(Piece): 
    def __init__(self, position: Tile, team: int) -> None:
        super().__init__(position, team)
        
    def get_movements(self) -> list[Tile]:
        directions = [D.UP_LEFT, D.UP_RIGHT, D.DOWN_LEFT, D.DOWN_RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_DIAGONAL] 
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions += self.trace_direction(self.position, next_tile, limit=8)
        return positions
    
    
class Queen(Piece): 
    def __init__(self, position: Tile, team: int) -> None:
        super().__init__(position, team)
        
    def get_movements(self) -> list[Tile]:
        ...
    
    
class King(Piece): 
    def __init__(self, position: Tile, team: int) -> None:
        super().__init__(position, team)
        
    def get_movements(self) -> list[Tile]:
        ...
        
        
class Pawn(Piece): 
    def __init__(self, position: Tile, team: int) -> None:
        super().__init__(position, team)
        
    def get_movements(self) -> list[Tile]:
        directions = [D.UP_LEFT, D.UP_RIGHT, D.DOWN_LEFT, D.DOWN_RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_DIAGONAL] 
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions += self.trace_direction(self.position, next_tile, limit=10)
        return positions