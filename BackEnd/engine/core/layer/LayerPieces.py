from typing import Dict, List

from engine.core.layer.LayerTile import LayerTile
from engine.core.Player import Player


class LayerPiece: 
    def __init__(self, position: LayerTile, team: Player) -> None: 
        self.position = position 
        self.position.piece = self
        self.board = position.board
        self.team = team 
        self.captured = False
        self.first_move = True
        self.type = self.__class__.__name__
        
        self.captured_position = None
        self.team.add_piece(self)
        
    def __eq__(self, other: "LayerPiece") -> bool: 
        return self.position == other.position and self.team == other.team and self.type == other.type
    
    def get_movements(self) -> List[LayerTile]:
        ...
        
    def move(self, to: LayerTile, validate: bool = True) -> bool:
        if validate and to not in self.get_movements(): 
            return False
        
        self.position.piece = None  
        self.position = to  
        to.piece = self  
        self.first_move = False
        return True
    
    def capture(self) -> None:
        self.captured_position = self.position
        self.position.piece = None  
        self.position = None  
        self.captured = True

    def revive(self) -> None: 
        self.captured = False
        self.position = self.captured_position
        self.captured_position = None
        self.position.piece = self
        
        
class LayerTower: 
    TOWERS = {
        0: {
            'initial_positions': ['a1_T', 'h1_T'],
        },
        1: {
            'initial_positions': ['a8_T', 'h8_T'],
        },
        2: {
            'initial_positions': ['a1_B', 'h1_B'],
        }, 
        3: {
            'initial_positions': ['a8_B', 'h8_B'],
        }
    }

    def __init__(self, position: LayerTile, team: Player) -> None:
        super().__init__(position, team)
        self.first_move = True # True when the player hasn't moved the tower yet. 
        if self.position.name not in LayerTower.TOWERS[self.team.team]['initial_positions']:
            self.first_move = False
            
    def get_movements(self) -> List[LayerTile]: 
        ...