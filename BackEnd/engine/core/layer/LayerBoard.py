from typing import Dict, List, Tuple

from engine.core.Player import Player
from engine.core.base.NormalBoard import NormalBoard
from engine.core.base.Board import Board
from engine.core.base.Tile import Tile
from engine.core.base.Pieces import Tower, Bishop, Knight, Queen, King, Pawn
from engine.core.layer.LayerPieces import LayerPiece, LayerPawn
from engine.core.layer.LayerTile import LayerTile, TowerLayer, KnightLayer, BishopLayer, QueenLayer, KingLayer, PawnLayer


class LayerBoard(NormalBoard): 
    def __init__(self, size: Tuple[int] = (8, 8), game_mode: str = 'wormhole', innitialize: bool = True) -> None:
        self.size = size # Not used yet
        self.game_mode = game_mode
        
        self.tiles: Dict[str, LayerTile] = {}
        if innitialize: 
            self.tiles = self.create_tiles()
            self.connect_tiles()
            self.remap_pawn_data()
        
        self.pieces: List[LayerPiece] = []

    def __len__(self):
        return len(self.tiles)

    def copy(self) -> 'LayerBoard': 
        board_copy = LayerBoard(size=self.size, game_mode=self.game_mode, innitialize=False)
    
        for tile_name, tile in self.tiles.items(): 
            board_copy.tiles[tile_name] = LayerTile(tile_name, board_copy, tile.id)
        
        for tile_name, tile in self.tiles.items(): 
            tile_copy: LayerTile = board_copy.tiles[tile_name]
            tile_copy.set_layer(tile.tower_layer.copy(board_copy))
            tile_copy.set_layer(tile.bishop_layer.copy(board_copy))
            tile_copy.set_layer(tile.knight_layer.copy(board_copy))
            tile_copy.set_layer(tile.queen_layer.copy(board_copy))
            tile_copy.set_layer(tile.king_layer.copy(board_copy))
            tile_copy.set_layer(tile.pawn_layer.copy(board_copy))
            
        return board_copy

    def create_tiles(self) -> Dict[str, LayerTile]: 
        if self.game_mode == 'wormhole': 
            b = Board(size=self.size)
        elif self.game_mode == 'normal':
            b = NormalBoard(size=self.size)
        tiles = {}
        tile_id = 0
        for tile in b.tiles.values(): 
            tiles[tile.name] = LayerTile(tile.name, self, tile_id)
            tile_id += 1
        return tiles

    def connect_tiles(self) -> None: 
        PAWN_INVALID_ROWS = ['1_T', '8_T', '1_B', '8_B', '1', '8']
        for j, row in enumerate(PAWN_INVALID_ROWS): 
            PAWN_INVALID_ROWS[j] = row.replace('8', str(self.size[0]))
        
        player1 = Player(0, "player")
        player2 = Player(1, "player")
        player3 = Player(2, "player")
        player4 = Player(3, "player")
        
        if self.game_mode == 'wormhole': 
            b = Board(size=self.size)
        elif self.game_mode == 'normal':
            b = NormalBoard(size=self.size)
            
        for tile in b.tiles.values(): 
            layer_tile = self.tiles[tile.name]

            tower = Tower(tile, player1)
            tower_movements = tower.get_movements(flatten=False)
            filtered_tower_movements = self._filter_movements(tower_movements, separate=True)
            tower_layer = TowerLayer(filtered_tower_movements)

            knight = Knight(tile, player1)
            knight_movements = knight.get_movements()
            knight_converted_moves = self._convert_to_layer_tile(knight_movements)
            knight_layer = KnightLayer(knight_converted_moves)

            bishop = Bishop(tile, player1)
            bishop_movements = bishop.get_movements(flatten=False)
            filtered_bishop_movements = self._filter_movements(bishop_movements, separate=True)
            bishop_layer = BishopLayer(filtered_bishop_movements)

            queen_layer = QueenLayer(filtered_tower_movements + filtered_bishop_movements)

            # Castling is handled in the game logic
            king = King(tile, player1)
            king_movements = king.get_movements()
            king_pawn_possible_atacks = king.get_pawn_possible_atacks()
            king_converted_moves = self._convert_to_layer_tile(king_movements)
            king_pawn_attacks_converted_moves = self._convert_to_layer_tile(king_pawn_possible_atacks)
            king_layer = KingLayer(king_converted_moves, king_pawn_attacks_converted_moves)

            pawn_moves = {0: [], 1: [], 2: [], 3: []}
            pawn_atacks = {0: [], 1: [], 2: [], 3: []}

            if not tile.name[1:] in PAWN_INVALID_ROWS: 
                pawn_white = Pawn(tile, player1)
                pawn_white_movements = pawn_white.get_movements(flatten=False, remove_non_valid_atacks=False)
                pawn_moves[0] = self._convert_to_layer_tile(pawn_white_movements[0])
                pawn_atacks[0] = self._convert_to_layer_tile(pawn_white_movements[1])

                pawn_black = Pawn(tile, player2)
                pawn_black_movements = pawn_black.get_movements(flatten=False, 
                remove_non_valid_atacks=False)
                pawn_moves[1] = self._convert_to_layer_tile(pawn_black_movements[0])
                pawn_atacks[1] = self._convert_to_layer_tile(pawn_black_movements[1])

                pawn_blue = Pawn(tile, player3)
                pawn_blue_movements = pawn_blue.get_movements(flatten=False, remove_non_valid_atacks=False)
                pawn_moves[2] = self._convert_to_layer_tile(pawn_blue_movements[0])
                pawn_atacks[2] = self._convert_to_layer_tile(pawn_blue_movements[1])

                pawn_red = Pawn(tile, player4)
                pawn_red_movements = pawn_red.get_movements(flatten=False, remove_non_valid_atacks=False)
                pawn_moves[3] = self._convert_to_layer_tile(pawn_red_movements[0])
                pawn_atacks[3] = self._convert_to_layer_tile(pawn_red_movements[1])

            pawn_layer = PawnLayer(pawn_moves, pawn_atacks)

            layer_tile.set_layer(tower_layer)
            layer_tile.set_layer(knight_layer)
            layer_tile.set_layer(bishop_layer)
            layer_tile.set_layer(queen_layer)
            layer_tile.set_layer(king_layer)
            layer_tile.set_layer(pawn_layer)

            tile.remove_piece()
    
    def _filter_movements(self, movements: List[List[Tile]], separate: bool = False) -> List[List[Tile]]: 
        filtered_movements = []
        for movement in movements: 
            if movement: 
                if separate: 
                    filtered_movements += self._separate_pentagon_movements(movement)
                else: 
                    filtered_movements.append(movement)
        converted_movements = []
        for movement in filtered_movements: 
            converted_movements.append(self._convert_to_layer_tile(movement))
        return converted_movements
    
    def _convert_to_layer_tile(self, movement: List[Tile]) -> List[LayerTile]: 
        return [self.tiles[tile] for tile in movement]

    def _separate_pentagon_movements(self, movement: List[Tile]) -> List[List[Tile]]:
        
        splits_len = {
            (6, 6): {
                'tower_pentagon_loop': [2, 2, 3], 
                'bishop_pentagon': [8, 5, 9],
                'tower_pentagon': [9, 5, 10]
            }, 
            (8, 8): {
                'tower_pentagon_loop': [4, 3, 5], 
                'bishop_pentagon': [10, 6, 11], 
                'tower_pentagon': [12, 6]
            }
        }

        board_splits = splits_len[self.size]

        for i, tile in enumerate(movement): 
            if tile.pentagon:

                branches = []

                # No split of paths 
                if len(movement[i+1:]) < board_splits['tower_pentagon_loop'][0]: break 

                # When tower splits at pentagon (coming from the loop) there are 2 paths, each of 2 tiles
                elif len(movement[i+1:]) == board_splits['tower_pentagon_loop'][0]: 
                    first_split = board_splits['tower_pentagon_loop'][1]
                    second_split = board_splits['tower_pentagon_loop'][2]
                    branches = [movement[i+1 : i+first_split], movement[i+first_split : i+second_split]]
                
                # When bishop splits at pentagon there are 2 paths, each of 5 tiles
                elif len(movement[i+1:]) == board_splits['bishop_pentagon'][0]: 
                    first_split = board_splits['bishop_pentagon'][1]
                    second_split = board_splits['bishop_pentagon'][2]
                    branches = [movement[i+1 : i+first_split], movement[i+first_split : i+second_split]]
                
                # When tower splits at pentagon there are 2 paths, one of 5 and the other of 7, which also splits at the next pentagon into 2 and 2 (first case) 
                elif len(movement[i+1:]) == board_splits['tower_pentagon'][0]: 
                    first_split = board_splits['bishop_pentagon'][1]
                    branches = [movement[i+1:i+first_split]] + self._separate_pentagon_movements(movement[i+first_split:])

                if branches:
                    paths = [movement[:i+1] + branch for branch in branches]
                    return paths
                break

        return [movement]
    
    def remap_pawn_data(self) -> None: 
        for i in range(4): 
            if self.size[0] < 6: 
                LayerPawn.PAWNS[i]['first_row'] = 'none'
            else: 
                LayerPawn.PAWNS[i]['first_row'] = LayerPawn.PAWNS[i]['first_row'].replace('7', str(self.size[0] - 1))
            promotion_rows = LayerPawn.PAWNS[i]['promotion_rows']
            for j, row in enumerate(promotion_rows): 
                promotion_rows[j] = row.replace('8', str(self.size[0]))

    def get_promotion_zones(self, player: int) -> List[int]: 
        promotion_rows = Pawn.PAWNS[player]['promotion_rows']
        tiles = []
        for tile in self.tiles.values(): 
            if tile.name[1:] in promotion_rows or (len(tile.name) == 2 and tile.name[1] in promotion_rows): 
                tiles.append(tile.id)
        return tiles 