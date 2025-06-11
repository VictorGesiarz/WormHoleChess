from __future__ import annotations
from typing import TYPE_CHECKING

from typing import Dict, List, Tuple

from engine.core.constants import NUMBER_TO_COLOR

if TYPE_CHECKING: 
    from engine.core.layer.LayerTile import LayerTile
    from engine.core.layer.LayerBoard import LayerBoard
    from engine.core.Player import Player


class LayerPiece: 
    def __init__(self, position: LayerTile, team: Player, add_to_player: bool = True, type: str = None) -> None: 
        self.position = position 
        self.position.piece = self
        self.board = position.board
        self.team = team 
        self.captured = False
        self.first_move = True
        self.type = type
        self.type_id = None
        
        self.captured_position = None

        if add_to_player: 
            self.team.add_piece(self)
            self.board.pieces.append(self)
        
    def __eq__(self, other: "LayerPiece") -> bool: 
        if other == "Prueba": return True
        return self.position == other.position and self.team == other.team and self.type == other.type
    
    def __str__(self) -> str: 
        return f"{self.team.color} {self.type} at {self.position}"
    
    def __repr__(self) -> str: 
        return f"{self.team.color} {self.type} at {self.position}"

    def copy(self, new_board: LayerBoard, new_players: List[Player]) -> LayerPiece: 
        PieceObject = LayerPiece.get_piece_type(self.type)
        piece_copy: LayerPiece = PieceObject(new_board[self.position.name], new_players[self.team.team])
        piece_copy.captured = self.captured
        piece_copy.first_move = self.first_move
        piece_copy.captured_position = None if not self.captured_position else new_board[self.captured_position.name]
        return piece_copy

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

    @staticmethod
    def get_piece_type(name: str) -> "LayerPiece": 
        if "Tower" in name: 
            return LayerTower
        elif "Knight" in name: 
            return LayerKnight
        elif "Bishop" in name:
            return LayerBishop
        elif "Queen" in name: 
            return LayerQueen
        elif "King" in name:
            return LayerKing
        elif "Pawn" in name: 
            return LayerPawn
        
        
class LayerTower(LayerPiece): 
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

    def __init__(self, position: LayerTile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player, type='Tower')
        self.first_move = True # True when the player hasn't moved the tower yet. 
        if self.position.name not in LayerTower.TOWERS[self.team.team]['initial_positions']:
            self.first_move = False
        self.type_id = 0
            
    def get_movements(self) -> List[LayerTile]:
        possible_moves = []
        seen = set()
        for path in self.position.tower_layer.directions:
            for move in path:
                if move in seen:
                    continue
                if move.piece:
                    if move.piece.team != self.team:
                        possible_moves.append(move)
                    break
                else:
                    seen.add(move)
                possible_moves.append(move)
        return possible_moves


class LayerKnight(LayerPiece): 
    def __init__(self, position: LayerTile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player, 'Knight')
        self.type_id = 1

    def get_movements(self) -> List[LayerTile]:
        possible_moves = []
        for move in self.position.knight_layer.movements: 
            if not move.piece:
                possible_moves.append(move)
            elif move.piece and move.piece.team != self.team:
                possible_moves.append(move)
                break
        return possible_moves
    

class LayerBishop(LayerPiece): 
    def __init__(self, position: LayerTile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player, 'Bishop')
        self.type_id = 2

    def get_movements(self) -> List[LayerTile]:
        possible_moves = []
        seen = set()
        for path in self.position.bishop_layer.directions:
            for move in path:
                if move in seen:
                    continue
                if move.piece:
                    if move.piece.team != self.team:
                        possible_moves.append(move)
                    break
                else: 
                    seen.add(move)
                possible_moves.append(move)
        return possible_moves
    

class LayerQueen(LayerPiece):
    def __init__(self, position: LayerTile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player, 'Queen') 
        self.type_id = 3

    def get_movements(self) -> List[LayerTile]:
        possible_moves = []
        seen = set()
        for path in self.position.queen_layer.directions:
            for move in path:
                if move in seen:
                    continue
                if move.piece:
                    if move.piece.team != self.team:
                        possible_moves.append(move)
                    break
                else: 
                    seen.add(move)
                possible_moves.append(move)
        return possible_moves
    

class LayerKing(LayerPiece): 
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
        
    def __init__(self, position: LayerTile, team: Player, add_to_player: bool = True) -> None:
        super().__init__(position, team, add_to_player, 'King')
        self.first_move = True # True when the player hasn't moved the King yet. 
        if self.position.name != LayerKing.KINGS[self.team.team]['initial_position']:
            self.first_move = False
        self.type_id = 4

    def get_movements(self) -> List[LayerTile]:
        possible_moves = []
        for move in self.position.king_layer.movements: 
            if not move.piece:
                possible_moves.append(move)
            elif move.piece and move.piece.team != self.team:
                possible_moves.append(move)
        return possible_moves
    
    def get_castle_movements(self) -> List[List[Tuple[LayerTile]]]: 
        positions = []
        if self.first_move: 
            castling_data = LayerKing.KINGS[self.team.team]['castling']
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
            (LayerTower, ['Tower', 'Queen']),
            (LayerBishop, ['Bishop', 'Queen']),
            (LayerKnight, ['Knight']),
            (LayerKing, ['King']),
        ]

        for piece_class, threatening_types in attack_patterns:
            temp_piece = piece_class(original_position, self.team, add_to_player=False)
            movements = temp_piece.get_movements()
            for move in movements:
                piece = move.piece
                if piece and piece.team.alive and piece.type in threatening_types:
                    original_position.piece = self
                    return True
                
            if piece_class == LayerKing: 
                for pawn_tile in self.position.king_layer.pawn_possible_atacks:
                    if pawn_tile.piece is not None and pawn_tile.piece.type == "Pawn" and pawn_tile.piece.team != self.team:
                        if original_position in pawn_tile.pawn_layer.attacks[pawn_tile.piece.team.team]: 
                            original_position.piece = self
                            return True

        original_position.piece = self
        return False


class LayerPawn(LayerPiece): 
    PAWNS = {
        0: {
            'first_row': '2_T', 
            'promotion_rows': ['8_T', '1_B', '8_B', '8'],
        },
        1: {
            'first_row': '7_T',
            'promotion_rows': ['1_T', '8_B', '1_B', '1'],
        },
        2: {
            'first_row': '2_B',
            'promotion_rows': ['8_T', '1_T', '8_B'],
        },
        3: {
            'first_row': '7_B',
            'promotion_rows': ['1_T', '8_T', '1_B'],
        }
    }

    def __init__(self, position: LayerTile, team: Player, add_to_player: bool = True):
        super().__init__(position, team, add_to_player, 'Pawn')
        self.first_move = True # True when the player hasn't moved the pawn yet. 
        if self.position.name[1:] != LayerPawn.PAWNS[self.team.team]['first_row']: 
            self.first_move = False
        self.type_id = 5

    def get_movements(self):
        possible_moves = []
        for move in self.position.pawn_layer.moves[self.team.team]: 
            if move.piece is None: 
                possible_moves.append(move)
            else: 
                break
        for attack in self.position.pawn_layer.attacks[self.team.team]: 
            if attack.piece and attack.piece.team != self.team: 
                possible_moves.append(attack)
        return possible_moves
    
    def is_promoting(self) -> bool: 
        """ The game class handles the promotion of the pawn. """
        promotion_rows = LayerPawn.PAWNS[self.team.team]['promotion_rows']
        if self.position.name[1:] in promotion_rows or (len(self.position.name) == 2 and self.position.name[1] in promotion_rows):
            return True
        return False