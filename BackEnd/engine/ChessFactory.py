from typing import Literal, List, Dict, Tuple, Union
import numpy as np
import yaml 
import os

from engine.core.base.NormalBoard import NormalBoard
from engine.core.base.Board import Board
from engine.core.layer.LayerBoard import LayerBoard
from engine.core.base.Pieces import Piece
from engine.core.layer.LayerPieces import LayerPiece
from engine.core.matrices.MatrixBoard import LayerMatrixBoard, BaseMatrixBoard
from engine.core.matrices.matrix_constants import PLAYER_DTYPE, Pieces
from engine.core.Player import Player, Bot
from engine.core.Game import Game
from engine.core.GameMatrices import GameMatrices
from engine.core.constants import COLOR_TO_NUMBER, NUMBER_TO_COLOR


BOARD_FILES = './engine/core/configs/matrix_board/'
POSITIONS_PATH = './db/starting_positions/'
SIZES = {
    'big': (8, 8),
    'small': (6, 6),
}

class ChessFactory:
    @staticmethod
    def create_game(player_data: List[str],
                    program_mode: Literal['base', 'layer', 'matrix'] = 'layer',
                    game_mode: Literal['normal', 'wormhole'] = 'wormhole',
                    size: Union[Literal['big', 'small'], Tuple[int]] = 'big',
                    initial_positions: str | Dict[str, str] = None,
                    **kwargs) -> Game | GameMatrices:
        
        size = SIZES[size] if size in SIZES else size
        piece_positions = ChessFactory.get_default_positions(len(player_data), size, game_mode, initial_positions)

        if game_mode == 'normal' and len(player_data) != 2: 
            raise ValueError('Normal game mode only supports 2 players')

        if program_mode == 'matrix': 
            return MatrixChessFactory.create_game(player_data, program_mode, game_mode, size, piece_positions, **kwargs)

        board = ChessFactory.create_board(program_mode, game_mode, size)
        players = ChessFactory.create_players(player_data)

        types = ChessFactory.initialize_pieces(board, players, piece_positions, program_mode, game_mode)
        
        return Game(board, players, program_mode=program_mode, turn=0) 
    
    @staticmethod
    def get_default_positions(num_players: int, size: int, game_mode: str, file_name: str) -> str: 
        if file_name is None or file_name == 'default': 
            if size in SIZES: 
                size = SIZES[size]
            file_name = f'{POSITIONS_PATH}{num_players}_{size[0]}x{size[1]}_{game_mode}.yaml'
        else: 
            files = os.listdir(POSITIONS_PATH + 'tests/')
            file_name = f'{num_players}_{size[0]}x{size[1]}_{game_mode}-' + file_name
            for f in files: 
                if file_name in f: 
                    file_name = POSITIONS_PATH + 'tests/' + f
                    break
        return ChessFactory.load_initial_positions(game_mode, file_name)

    @staticmethod
    def initialize_pieces(board: Board, players: List[Player], initial_positions: str, program_mode: str, game_mode: str) -> int: 
        types = set()
        for player in players:
            player_pieces_positions = initial_positions[player.color]
            for piece_name, piece_positions in player_pieces_positions.items(): 
                if len(piece_positions) > 0: 
                    types.add(piece_name)
                for position in piece_positions: 
                    if not position in board: 
                        raise ValueError(f'Invalid piece position: {position}, for the current board')
                    tile = board[position]
                    ChessFactory.create_piece(piece_name, program_mode, game_mode, tile, player)
        return len(types)
    
    @staticmethod
    def create_players(player_data: List[Tuple[str]]) -> List[Player]:
        number_of_players = len(player_data)
        if number_of_players not in (2, 4):
            raise ValueError('Number of players must be 2 or 4')
        
        players = []
        for data in player_data:
            if data[2] == 'human': 
                player = Player(data[1], color=data[3])
            else: 
                player = Bot(data[1], difficulty=data[2], color=data[3])
            players.append(player)
        return players
    
    @staticmethod
    def create_player_data(num_players: int = 4, types: List[Literal['human', 'random', 'mcts', 'alphazero']] = ['random'] * 4) -> List[Tuple[str]]: 
        if len(types) == 1: 
            types *= num_players
        if num_players == 4: 
            return [(i, i, types[i], NUMBER_TO_COLOR[i]) for i in range(num_players)]
        else: 
            return [
                (0, 0, types[0], 'white'), 
                (1, 3, types[1], 'black')
            ]
    
    @staticmethod
    def create_board(program_mode: str, game_mode: str, size: Tuple[int]) -> Board:
        if game_mode == 'normal':
            if program_mode == 'base':
                return NormalBoard(size=size)
            elif program_mode == 'layer':
                return LayerBoard(size=size, game_mode=game_mode)
        elif game_mode == 'wormhole':
            if program_mode == 'base':
                return Board(size=size)
            elif program_mode == 'layer':
                return LayerBoard(size=size)
        else: 
            raise ValueError(f'Invalid program_mode: {program_mode}. Must be "base" or "layer".')

    @staticmethod
    def create_piece(piece_name, program_mode, game_mode, tile, player):
        if program_mode == 'base':
            PieceObject = Piece.get_piece_type(piece_name)
            piece = PieceObject(tile, player)
        elif program_mode == 'layer':
            PieceObject = LayerPiece.get_piece_type(piece_name)
            piece = PieceObject(tile, player)
        return

    @staticmethod
    def load_initial_positions(game_mode: str, file_path: str) -> Dict[str, Dict[str, list]]:
        with open(file_path, 'r') as file:
            initial_positions = yaml.safe_load(file)

        for color, pieces in initial_positions.items(): 
            for piece, positions in pieces.items(): 
                positions = positions.split()

                new_positions = []
                for pos in positions: 
                    if game_mode == 'normal': 
                        if len(pos) == 2:
                            new_positions.append(pos)
                        else: 
                            raise ValueError(f'Invalid position format: {pos}')
                    else: 
                        if len(pos) == 3 and pos[2] in ['T', 'B']: 
                            new_positions.append(pos[:2] + '_' + pos[2])
                        elif len(pos) == 4 and pos[3] in ['T', 'B']: 
                            new_positions.append(pos[:2] + '_' + pos[2] + '_' + pos[3])
                        else:
                            raise ValueError(f'Invalid position format: {pos}')

                initial_positions[color][piece] = new_positions

        return initial_positions
    

class MatrixChessFactory: 
    @staticmethod
    def create_game(player_data: List[str],
                    program_mode: Literal['matrix'] = 'matrix',
                    game_mode: Literal['normal', 'wormhole'] = 'wormhole',
                    size: Tuple[int, int] = (8, 8),
                    piece_positions: Dict = {},
                    **kwargs) -> GameMatrices:
        
        load_from_file = False
        board_file = f'{BOARD_FILES}{size[0]}x{size[1]}_{game_mode}.npz'
        if os.path.exists(board_file): 
            load_from_file = board_file

        # Create board and players
        num_players = 4
        if game_mode == 'normal': 
            num_players = 2
        board = LayerMatrixBoard(size, game_mode, load_from_file=load_from_file, num_players=num_players, **kwargs)
        if not load_from_file: 
            board.save_matrices()
        players = MatrixChessFactory.create_players(player_data, game_mode)

        MatrixChessFactory.initialize_pieces(board, players, piece_positions)

        # Get other arguments
        turn = kwargs.get('turn', 0)
        max_turns = kwargs.get('max_turns', 120)
        verbose = kwargs.get('verbose', 1)
    
        return GameMatrices(board, players, turn, verbose=verbose, max_turns=max_turns)
    
    @staticmethod
    def initialize_pieces(board: LayerMatrixBoard, players: np.array, initial_positions: str) -> None: 
        for i, player in enumerate(players): 
            j = 0
            chunk = board.pieces_per_player * player['team']

            if player['color'] == 'none': 
                continue
            player_pieces_positions = initial_positions[player['color']]
            for piece_name, piece_positions in player_pieces_positions.items(): 
                for position in piece_positions: 
                    if not position in board.node_names: 
                        raise ValueError(f'Invalid piece position: {position}, for the current board')
                    
                    piece_type = MatrixChessFactory.get_piece_type(piece_name)
                    tile = np.where(board.node_names == position)[0][0]

                    board.set_piece(chunk + j, piece_type, player['team'], tile)
                    j += 1

    @staticmethod
    def create_players(player_data, game_mode) -> np.ndarray:
        engines_map = {
            "human":     0,
            "random":    1,
            "mcts":      2,
            "alphazero": 3,
        }
        
        players_list = [(0, 0, False, 0, 'none') for _ in range(4)]
        for id_, team, player_type, color in player_data:
            players_list[id_] = (id_, team, True, engines_map[player_type], color)
        
        players = np.array(players_list, dtype=PLAYER_DTYPE)
        if len(player_data) == 2 and game_mode == 'normal': 
            players[1][1] = 1
        return players
    

    @staticmethod
    def get_piece_type(piece_name: str) -> int: 
        if "Tower" == piece_name: 
            return Pieces.TOWER
        elif "Knight" == piece_name: 
            return Pieces.KNIGHT
        elif "Bishop" == piece_name:
            return Pieces.BISHOP
        elif "Queen" == piece_name: 
            return Pieces.QUEEN
        elif "King" == piece_name:
            return Pieces.KING
        elif "Pawn" == piece_name: 
            return Pieces.PAWN