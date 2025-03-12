
from core.chess_logic import Tile, D


class Piece: 
    teams = {
        0: {
            'rows': [1, 2],
            'top_side': True,
            'direction': D.UP
        },
        1: {
            'rows': [8, 7], 
            'top_side': True,
            'direction': D.DOWN
        },
        2: {
            'rows': [1, 2], 
            'top_side': False,
            'direction': D.UP
        },
        3: {
            'rows': [8, 7], 
            'top_side': False,
            'direction': D.DOWN
        }
    }
    
    def __init__(self, position: Tile, team: int) -> None:
        self.position = position 
        self.position.piece = self
        self.team = team
        
    def get_pos(self) -> Tile:
        return self.position
    
    def get_movements(self):
        ...
    
    def trace_direction(self, last: Tile, current: Tile, limit: int, collisions: bool = True) -> list[Tile]:
        if current is None or limit == 0: 
            return []
        elif collisions and current.piece is not None: 
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
        self.first_move = False # False when the player hasn't moved the pawn yet. 

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
        horizontal = [D.LEFT, D.RIGHT]
        vertical = [D.UP, D.DOWN]
        positions1 = self.make_pattern(horizontal, vertical)
        if self.position.pentagon: vertical += [D.ADDITIONAL_STRAIGHT] 
        positions2 = self.make_pattern(vertical, horizontal)
        positions = positions1.union(positions2)
        return positions
            
    def make_pattern(self, direction1, direction2):
        positions = set()
        for d1 in direction1: 
            next_tile = self.position.neighbors[d1]
            
            tiles = self.trace_direction(self.position, next_tile, limit=2, collisions=False)
            if len(tiles) > 1: 
                tiles = tiles[1:]   
            else:
                continue
            for tile in tiles: 
                for d2 in direction2: 
                    next_next_tile = tile.neighbors[d2]
                    if next_next_tile.piece is not None: 
                        continue
                    positions.add(next_next_tile)
                    
            for d2 in direction2:
                next_next_tile = next_tile.neighbors[d2]
                tiles = self.trace_direction(next_tile, next_next_tile, limit=2, collisions=False)
                if len(tiles) > 1: 
                    tiles = tiles[1:]
                else: 
                    continue 
                for tile in tiles:
                    if tile is not None: 
                        positions.add(tile) 
                
        return positions
        
        
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
        directions = [D.UP_LEFT, D.UP_RIGHT, D.DOWN_LEFT, D.DOWN_RIGHT,
                      D.UP, D.DOWN, D.LEFT, D.RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_DIAGONAL, D.ADDITIONAL_STRAIGHT] 
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions += self.trace_direction(self.position, next_tile, limit=10)
        return positions
    
    
class King(Piece): 
    def __init__(self, position: Tile, team: int) -> None:
        super().__init__(position, team)
        self.first_move = False # False when the player hasn't moved the pawn yet. 
        
    def get_movements(self) -> list[Tile]:
        directions = [D.UP_LEFT, D.UP_RIGHT, D.DOWN_LEFT, D.DOWN_RIGHT,
                      D.UP, D.DOWN, D.LEFT, D.RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_DIAGONAL, D.ADDITIONAL_STRAIGHT] 
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions += self.trace_direction(self.position, next_tile, limit=1)
        return positions
        
        
class Pawn(Piece): 
    def __init__(self, position: Tile, team: int) -> None:
        super().__init__(position, team)
        self.first_move = False # False when the player hasn't moved the pawn yet. 
        
    def get_movements(self) -> list[Tile]:
        limit = 1 if self.first_move else 2
        direction = [Piece.teams['direction']]
        if self.position.pentagon: directions += [D.ADDITIONAL_STRAIGHT] 
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions += self.trace_direction(self.position, next_tile, limit=limit)
        return positions