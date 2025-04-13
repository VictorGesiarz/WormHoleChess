from typing import Dict, List, Tuple
from dataclasses import dataclass

from engine.core.base.Tile import Tile, D
from engine.core.Player import Player
from engine.core.constants import NUMBER_TO_COLOR, PARAMETERS


@dataclass
class PieceMovement:
    piece: "Piece"
    tile_from: Tile
    tile_to: Tile
    first_move: bool
    captured_piece: "Piece" = None
    castle_movement: "PieceMovement" = None
    killed_player: Player = None

    def __str__(self):
        return f"({self.tile_from}, {self.tile_to})"
    
    def __repr__(self):
        return f"({self.tile_from}, {self.tile_to})"


class Piece: 
    def __init__(self, position: Tile, team: Player, add_to_player=True) -> None:
        self.position = position 
        self.position.piece = self
        self.board = position.board
        self.team = team
        self.captured = False
        self.first_move = True # True when the player hasn't moved the piece yet.
        self.type = self.__class__.__name__
        
        self.captured_position = None

        if add_to_player: 
            self.team.add_piece(self)
    
    def __eq__(self, other: "Piece") -> bool:
        if other is None: 
            return False
        return self.position == other.position and self.team == other.team and self.type == other.type
    
    def __str__(self):
        return f"{NUMBER_TO_COLOR[self.team.team]} {self.type} at: {self.position}"

    def get_movements(self) -> List[Tile]:
        ...
    
    def trace_direction(self, last: Tile, current: Tile, limit: int, collisions: bool = True, can_eat: bool = True) -> list[Tile]:
        """ Trace the direction of the piece and return the positions it can move to. R
        The method is recursive and will stop when it reaches the limit or when it finds a collision.

        Args:
            last (Tile): From what tile the piece is moving
            current (Tile): The current tile. We need this because the direction of the movement changes depending on the tile it comes from. 
            limit (int): How many tiles the piece can move (a pawn can move 1 or 2 tiles, a tower can move 8 tiles, etc.)
            collisions (bool, optional): Wether to stop the trace when a collision is detected. Defaults to True.
            can_eat (bool, optional): Pawns cannot eat in fron of them, so it should be False then. Defaults to True.

        Returns:
            list[Tile]: _description_
        """
        if current is None or limit == 0: 
            return []
        elif collisions and current.piece is not None: 
            if self.team == current.piece.team or not can_eat: 
                return []
            if PARAMETERS['can_eat_dead']: 
                return [current]
            return []
        
        positions = [current]
        from_ = current.neighbors_inv[last.name]
        
        if current.pentagon and from_ in current.additional_relations: 
            to_ = current.additional_relations[from_]
        else:
            to_ = Tile.relations[from_]
        
        for to_i in to_:
            next_tile = current.neighbors[to_i]
            positions += self.trace_direction(current, next_tile, limit-1, collisions=collisions)

        return positions 
    
    def move(self, to: Tile, validate: bool = True) -> bool:
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
    
    @staticmethod
    def get_piece_type(name: str) -> "Piece": 
        if "rook" in name: 
            return Tower
        elif "knight" in name: 
            return Knight
        elif "bishop" in name:
            return Bishop
        elif "queen" in name: 
            return Queen
        elif "king" in name:
            return King
        elif "pawn" in name: 
            return Pawn

    
class Tower(Piece):
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

    def __init__(self, position: Tile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player)
        self.first_move = True # True when the player hasn't moved the tower yet. 
        if self.position.name not in Tower.TOWERS[self.team.team]['initial_positions']:
            self.first_move = False

    def get_movements(self, flatten: bool = True) -> list[Tile]:
        directions = [D.UP, D.DOWN, D.LEFT, D.RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_STRAIGHT] 
        
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions.append(self.trace_direction(self.position, next_tile, limit=10))
        
        if flatten: 
            positions = [tile for sublist in positions for tile in sublist]
        return positions


class Knight(Piece): 
    def __init__(self, position: Tile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player)
        
    def get_movements(self) -> list[Tile]:
        horizontal = [D.LEFT, D.RIGHT]
        vertical = [D.UP, D.DOWN]
        positions1 = self.make_pattern(horizontal, vertical)
        if self.position.pentagon: vertical += [D.ADDITIONAL_STRAIGHT] 
        positions2 = self.make_pattern(vertical, horizontal)
        positions = positions1.union(positions2)
        return list(positions)
            
    def make_pattern(self, direction1: list[D], direction2: list[D]) -> set[Tile]:
        positions = set()
        for d1 in direction1:
            next_tile = self.position.neighbors[d1]
            if next_tile is None: 
                continue
            
            # Advance 2 tiles in the first direction and then 1 tile in the second direction
            tiles = self.trace_direction(self.position, next_tile, limit=2, collisions=False)
            if len(tiles) > 1: 
                for d2 in direction2: 
                    next_next_tile = tiles[1].neighbors[d2]
                    if next_next_tile is not None:
                        positions.add(next_next_tile)

            # Advance 1 tile in the first direction and then 2 tiles in the second direction
            for d2 in direction2:
                next_next_tile = next_tile.neighbors[d2]
                tiles = self.trace_direction(next_tile, next_next_tile, limit=2, collisions=False)
                if len(tiles) > 1: 
                    if tiles[1] is not None: 
                        positions.add(tiles[1]) 

        # Remove positions that are occupied by pieces of the same team
        filtered_positions = {pos for pos in positions if pos.piece is None or self.team != pos.piece.team}
        return filtered_positions
        
        
class Bishop(Piece): 
    def __init__(self, position: Tile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player)
        
    def get_movements(self, flatten: bool = True) -> list[Tile]:
        directions = [D.UP_LEFT, D.UP_RIGHT, D.DOWN_LEFT, D.DOWN_RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_DIAGONAL] 
        
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions.append(self.trace_direction(self.position, next_tile, limit=8))
        
        if flatten: 
            positions = [tile for sublist in positions for tile in sublist]
        return positions
    
    
class Queen(Piece): 
    def __init__(self, position: Tile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player)
        
    def get_movements(self, flatten: bool = True) -> list[Tile]:
        directions = [D.UP_LEFT, D.UP_RIGHT, D.DOWN_LEFT, D.DOWN_RIGHT,
                      D.UP, D.DOWN, D.LEFT, D.RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_DIAGONAL, D.ADDITIONAL_STRAIGHT] 
        
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions.append(self.trace_direction(self.position, next_tile, limit=8))
        
        if flatten: 
            positions = [tile for sublist in positions for tile in sublist]
        return positions
    
    
class King(Piece): 
    KINGS = {
        0: {
            'initial_position': 'e1_T',
            'castling': {
                'king_side': {
                    'middle_tiles': ('f1_T', 'g1_T'), 
                    'king': ('e1_T', 'g1_T'),
                    'tower': ('h1_T', 'f1_T')
                },
                'queen_side': {
                    'middle_tiles': ('d1_T', 'c1_T', 'b1_T'), 
                    'king': ('e1_T', 'c1_T'),
                    'tower': ('a1_T', 'd1_T')
                }
            }
        },
        1: {
            'initial_position': 'e8_T',
            'castling': {
                'king_side': {
                    'middle_tiles': ('f8_T', 'g8_T'), 
                    'king': ('e8_T', 'g8_T'),
                    'tower': ('h8_T', 'f8_T')
                },
                'queen_side': {
                    'middle_tiles': ('d8_T', 'c8_T', 'b8_T'),
                    'king': ('e8_T', 'c8_T'),
                    'tower': ('a8_T', 'd8_T')
                }
            }
        },
        2: {
            'initial_position': 'e1_B',
            'castling': {
                'king_side': {
                    'middle_tiles': ('f1_B', 'g1_B'), 
                    'king': ('e1_B', 'g1_B'),
                    'tower': ('h1_B', 'f1_B')
                },
                'queen_side': {
                    'middle_tiles': ('d1_B', 'c1_B', 'b1_B'), 
                    'king': ('e1_B', 'c1_B'),
                    'tower': ('a1_B', 'd1_B')
                }
            }
        }, 
        3: {
            'initial_position': 'e8_B',
            'castling': {
                'king_side': {
                    'middle_tiles': ('f8_B', 'g8_B'),
                    'king': ('e8_B', 'g8_B'),
                    'tower': ('h8_B', 'f8_B')
                },
                'queen_side': {
                    'middle_tiles': ('d8_B', 'c8_B', 'b8_B'),
                    'king': ('e8_B', 'c8_B'),
                    'tower': ('a8_B', 'd8_B')
                }
            }
        }
    }

    def __init__(self, position: Tile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player)
        self.first_move = True # True when the player hasn't moved the King yet. 
        if self.position.name != King.KINGS[self.team.team]['initial_position']:
            self.first_move = False
        
    def get_movements(self) -> list[Tile]:
        directions = [D.UP_LEFT, D.UP_RIGHT, D.DOWN_LEFT, D.DOWN_RIGHT,
                      D.UP, D.DOWN, D.LEFT, D.RIGHT]
        if self.position.pentagon: directions += [D.ADDITIONAL_DIAGONAL, D.ADDITIONAL_STRAIGHT] 
        
        positions = []
        for direction in directions: 
            next_tile = self.position.neighbors[direction]
            positions += self.trace_direction(self.position, next_tile, limit=1)
        
        return positions
    
    def get_castle_movements(self) -> List[List[Tuple[Tile]]]: 
        """ It returns the list of possible castle moves and the list of tiles it has to check,
        first tuple for first castle and second for the second one. The first item of each list is the castle and all the others are the squares in the middle of the castle that also have to be checked. """
        positions = []
        if self.first_move:
            castling_data = King.KINGS[self.team.team]['castling']
            for side, data in castling_data.items():
                king_from, king_to = data['king']
                rook_from, rook_to = data['tower']
                king_from_tile = self.board[king_from]
                king_to_tile = self.board[king_to]
                rook_from_tile = self.board[rook_from]
                rook_to_tile = self.board[rook_to]

                if king_from_tile != self.position: 
                    continue
                
                rook = self.board[rook_from].piece
                if rook is None or rook.type != 'Tower' or rook.team != self.team or not rook.first_move:
                    continue

                middle_tile = [self.board[tile_name] for tile_name in data['middle_tiles']]
                if any(tile.piece is not None for tile in middle_tile):
                    continue

                positions.append(
                    [(king_from_tile, king_to_tile, rook_from_tile, rook_to_tile), (king_from_tile, middle_tile[0])]
                )
            return positions
        return []
    
    def trace_from_king(self) -> bool:
        original_position = self.position

        attack_patterns = [
            (Tower, ['Tower', 'Queen']),
            (Bishop, ['Bishop', 'Queen']),
            (Knight, ['Knight']),
            (King, ['King']),
        ]

        for piece_class, threatening_types in attack_patterns:
            temp_piece = piece_class(original_position, self.team, add_to_player=False)
            for move in temp_piece.get_movements():
                piece = move.piece
                if piece and piece.team.alive and piece.type in threatening_types:
                    original_position.piece = self
                    return True

        if self.pawn_atacking(original_position):
            original_position.piece = self
            return True

        original_position.piece = self
        return False
    
    def pawn_atacking(self, position: Tile) -> bool:
        """ We look at the diagonals, if there is a pawn we look at its atacking direction and if the current tile is in that direction then the pawn would be atacking the king. """
        directions = [D.UP_LEFT, D.UP_RIGHT, D.DOWN_LEFT, D.DOWN_RIGHT]
        if position.pentagon: 
            directions += [D.ADDITIONAL_DIAGONAL]

        for direction in directions: 
            neighbour = position.neighbors[direction]
            if neighbour:
                piece = neighbour.piece
                if piece and piece.type == 'Pawn': 
                    moves = piece.get_movements(only_atacks=True)
                    for move in moves: 
                        if move == position: 
                            return True 
        return False
        
        
class Pawn(Piece): 
    PAWNS = {
        0: {
            'first_row': '2_T', 
            'promotion_rows': ['8_T', '1_B', '8_B'],
            'direction': D.UP,
            'atacks': [D.UP_LEFT, D.UP_RIGHT]
        },
        1: {
            'first_row': '7_T',
            'promotion_rows': ['1_T', '8_B', '1_B'],
            'direction': D.DOWN,
            'atacks': [D.DOWN_LEFT, D.DOWN_RIGHT]
        },
        2: {
            'first_row': '2_B',
            'promotion_rows': ['8_T', '1_T', '8_B'],
            'direction': D.UP,
            'atacks': [D.UP_LEFT, D.UP_RIGHT]
        },
        3: {
            'first_row': '7_B',
            'promotion_rows': ['1_T', '8_T', '1_B'],
            'direction': D.DOWN,
            'atacks': [D.DOWN_LEFT, D.DOWN_RIGHT]
        }
    }

    # Constant to define the quadrants of the board to determine the direction of the pawn, which changes depending on the start position of the pawn when the quadrant changes. 
    QUADRANTS = {
        0: {
            'rows': [1, 2, 3, 4],
            'top_side': True, 
        }, 
        1: {
            'rows': [5, 6, 7, 8],
            'top_side': True,
        },
        2: {
            'rows': [1, 2, 3, 4],
            'top_side': False,
        },
        3: {
            'rows': [5, 6, 7, 8],
            'top_side': False,
        }
    }
        
    def __init__(self, position: Tile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player)
        self.direction = Pawn.PAWNS[self.team.team]['direction']
        self.atack_directions = Pawn.PAWNS[self.team.team]['atacks']
        self.first_move = True # True when the player hasn't moved the pawn yet. 
        if self.position.name[1:] != Pawn.PAWNS[self.team.team]['first_row']: 
            self.first_move = False # The pawn is not in the first row of the team, so it cannot move 2 tiles.
        self.quadrant = team # The quadrant is represented by the team number.
        self.change_quadrant() # Change the quadrant of the pawn when it is created to make sure it matches the initial position. 

    def get_movements(self, flatten=True, remove_non_valid_atacks=True, only_atacks=False) -> list[Tile]:
        if self.is_promoting(): 
            return []

        positions = []
        if not only_atacks: 
            limit = 1 if not self.first_move else 2
            directions = [self.direction]
            if self.position.pentagon: directions += [D.ADDITIONAL_STRAIGHT] 
            
            for direction in directions: 
                next_tile = self.position.neighbors[direction]
                positions += self.trace_direction(self.position, next_tile, limit=limit, can_eat=False)

        atack_directions = self.atack_directions.copy()
        if self.add_aditional_atack(): 
            atack_directions += [D.ADDITIONAL_DIAGONAL]
        atack_positions = []
        for direction in atack_directions: 
            next_tile = self.position.neighbors[direction]
            atack_positions += self.trace_direction(self.position, next_tile, limit=1, can_eat=True)
        if remove_non_valid_atacks:
            atack_positions = [atack_position for atack_position in atack_positions if atack_position.piece is not None and atack_position.piece.team != self.team]

        if flatten: 
            return positions + atack_positions
        return [positions, atack_positions]
    
    def is_promoting(self) -> bool: 
        """ The game class handles the promotion of the pawn. """
        if self.position.name[1:] in Pawn.PAWNS[self.team.team]['promotion_rows']:
            return True
        return False
    
    def move(self, to: Tile, validate: bool = True) -> bool: 
        moved = super().move(to, validate=validate)
        if moved: 
            self.change_quadrant()
        return moved
    
    def change_quadrant(self) -> None:
        new_quadrant = self.quadrant  
        for quadrant, quadrant_data in Pawn.QUADRANTS.items():
            if self.position.row in quadrant_data['rows'] and self.position.top_side == quadrant_data['top_side']:
                new_quadrant = quadrant
                break

        if self.quadrant != new_quadrant:
            if (self.team.team % 2) == (new_quadrant % 2):
                if self.direction == D.UP:
                    self.direction = D.DOWN
                    self.atack_directions = [D.DOWN_LEFT, D.DOWN_RIGHT]
                else:
                    self.direction = D.UP
                    self.atack_directions = [D.UP_LEFT, D.UP_RIGHT]
            else:
                self.direction = Pawn.PAWNS[self.team.team]['direction']
                self.atack_directions = Pawn.PAWNS[self.team.team]['atacks']
            
            self.quadrant = new_quadrant

    def add_aditional_atack(self) -> bool: 
        if self.position.pentagon: 
            # We look at the opposite of the current pawn direction, then we look the opposite of that with the additional_relations
            # If the current pawn direction is in there that means that the attack in the additional diagonal should be added. 
            # For example in C3_T, going up, the inverse is down and the additional_relation tells us that the current direction UP is in [UP, ADDITIONA_STRAIGH]
            # If we were going down, the opposite is UP and there is no additional direction so it means the additional attack should not be added. 
            opposite_direction = Tile.relations[self.direction][0]
            if opposite_direction in self.position.additional_relations and self.direction in self.position.additional_relations[opposite_direction]: 
                return True 
        return False