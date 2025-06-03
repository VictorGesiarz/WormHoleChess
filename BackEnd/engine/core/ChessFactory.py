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
POSITIONS_PATH = './engine/core/configs/'
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
        
        if game_mode == 'normal' and len(player_data) != 2: 
            raise ValueError('Normal game mode only supports 2 players')

        if program_mode == 'matrix': 
            return MatrixChessFactory.create_game(player_data, program_mode, game_mode, size, initial_positions, **kwargs)

        board = ChessFactory.create_board(program_mode, game_mode, SIZES[size] if isinstance(size, str) else size)
        players = ChessFactory.create_players(player_data)
        
        if initial_positions is None: 
            if game_mode == 'wormhole': 
                file = POSITIONS_PATH + 'wormhole/' + ('4_players.yaml' if len(players) == 4 else '2_players.yaml')
            else: 
                file = POSITIONS_PATH + 'normal/normal_board.yaml'
            initial_positions = ChessFactory.load_initial_positions(game_mode, file)

        elif isinstance(initial_positions, str):
            initial_positions = ChessFactory.load_initial_positions(game_mode, initial_positions)

        types = ChessFactory.initialize_pieces(board, players, initial_positions, program_mode, game_mode)
        
        return Game(board, players, program_mode='base', turn=0) 
    
    @staticmethod
    def initialize_pieces(board: Board, players: List[Player], initial_positions: str, program_mode: str, game_mode: str) -> int: 
        types = set()
        for player in players:
            player_pieces_positions = initial_positions[NUMBER_TO_COLOR[player.team]]
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
            if data[1] == 'player': 
                player = Player(COLOR_TO_NUMBER[data[0]])
            elif data[1] == 'bot':
                player = Bot(COLOR_TO_NUMBER[data[0]], data[2])
            players.append(player)
        return players
    
    @staticmethod
    def create_bot_data(num_bots: int = 4, difficulties: List[Literal['random', 'mcts', 'alphazero']] = ['random'] * 4) -> List[Tuple[str]]: 
        if num_bots == 4:
            return [
                ('white', 'bot', difficulties[0]),
                ('black', 'bot', difficulties[1]),
                ('blue', 'bot', difficulties[2]),
                ('red', 'bot', difficulties[3]),
            ]
        return [
            ('white', 'bot', difficulties[0]),
            ('black', 'bot', difficulties[1]),
        ]
    
    @staticmethod
    def create_player_data(num_players: int = 4) -> List[Tuple[str]]: 
        if num_players == 4: 
            return [
                ('white', 'player'),
                ('black', 'player'),
                ('blue', 'player'),
                ('red', 'player'),
            ]
        return [
            ('white', 'player'), 
            ('red', 'player')
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
                    program_mode: Literal['layer'] = 'layer',
                    game_mode: Literal['normal', 'wormhole'] = 'wormhole',
                    size: Union[Literal['big', 'small'], Tuple[int]] = 'big',
                    initial_positions: str | Dict[str, str] = None,
                    **kwargs) -> GameMatrices:
        
        if program_mode == 'base': 
            raise ValueError('Cannot create a game with base program mode. ')

        load_from_file = False
        board_file = f'{BOARD_FILES}{str(size)}_{game_mode}.npz'
        if os.path.exists(board_file): 
            load_from_file = board_file

        # Create board and players
        board = LayerMatrixBoard(size, game_mode, load_from_file=load_from_file, **kwargs)
        players = np.array([
            (i, True, data[1]) for i, data in enumerate(player_data)
        ], dtype=PLAYER_DTYPE)

        # Populate board with initial positions 
        if initial_positions is None: 
            if game_mode == 'wormhole': 
                file = POSITIONS_PATH + 'wormhole/' + ('4_players.yaml' if len(players) == 4 else '2_players.yaml')
            else: 
                file = POSITIONS_PATH + 'normal/normal_board.yaml'
            initial_positions = ChessFactory.load_initial_positions(game_mode, file)

        elif isinstance(initial_positions, str):
            initial_positions = ChessFactory.load_initial_positions(game_mode, initial_positions)

        MatrixChessFactory.initialize_pieces(board, players, initial_positions)

        # Get other arguments
        turn = kwargs.get('turn', 0)
        max_turns = kwargs.get('max_turns', 120)
        verbose = kwargs.get('verbose', 0)
        
        return GameMatrices(board, players, turn, verbose, max_turns=max_turns)
    
    @staticmethod
    def initialize_pieces(board: LayerMatrixBoard, players: np.array, initial_positions: str) -> None: 
        for i, player in enumerate(players): 
            j = 0
            chunk = board.pieces_per_player * i

            player_pieces_positions = initial_positions[NUMBER_TO_COLOR[player['team']]]
            for piece_name, piece_positions in player_pieces_positions.items(): 
                for position in piece_positions: 
                    if not position in board.node_names: 
                        raise ValueError(f'Invalid piece position: {position}, for the current board')
                    
                    piece_type = MatrixChessFactory.get_piece_type(piece_name)
                    tile = np.where(board.node_names == position)[0][0]

                    board.set_piece(chunk + j, piece_type, i, tile)
                    j += 1

    @staticmethod
    def create_bot_data(num_bots: int = 4, difficulties: List[Literal['random', 'mcts', 'alphazero']] = ['random'] * 4) -> List[Tuple[str]]: 
        engines_map = {
            'random': 1,
            'mcts': 2,
            'alphazero': 3
        }

        if num_bots == 4:
            return [
                ('white', engines_map[difficulties[0]]),
                ('black', engines_map[difficulties[1]]),
                ('blue', engines_map[difficulties[2]]),
                ('red', engines_map[difficulties[3]]),
            ]
        return [
            ('white', engines_map[difficulties[0]]),
            ('black', engines_map[difficulties[1]]),
        ]

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