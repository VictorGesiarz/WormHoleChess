import numpy as np
from typing import List, Tuple

from engine.core.matrices.MatrixBoard import LayerMatrixBoard, Pieces, Teams, PieceInfo
from engine.utils.ZobristHasherMatrices import ZobristHasher


class GameMatrices: 
    def __init__(self, 
                 board: LayerMatrixBoard,
                 players: np.ndarray,
                 turn: int, 
                 verbose: int = 0,
                 hasher: ZobristHasher = None): 
        """ Class that does the same as the other Game class, but using the graph represented as a matrix. 

        Args:
            board (LayerMatrixBoard): _description_
            players (np.ndarray): _description_
            turn (int): _description_
            verbose (int, optional): _description_. Defaults to 0.
        """
    
        self.players = players
        self.number_of_players = len(players)
        self.turn = turn 
        self.verbose = verbose
        
        self.board = board
        self.hasher = ZobristHasher(6, self.number_of_players, board.nodes.shape[0]) if hasher is None else hasher
        self.hash = self.hasher.compute_hash(self.board.pieces)

        self._cached_turn = None
        self._cached_movements = None
        self.history: List = []
        self.initial_positions = self.board.pieces.copy()
        self.positions_counter = {hash(self): 1}
        self.moves_without_capture = 0
        
    def __hash__(self):
        return self.hash

    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)
    
    def copy(self) -> 'GameMatrices':
        game_copy = GameMatrices(self.board.copy(), self.players.copy(), self.turn, hasher=self.hasher)
        game_copy.history = self.history.copy()
        game_copy.positions_counter = self.positions_counter.copy()
        game_copy.moves_without_capture = self.moves_without_capture
        return game_copy
        
    def next_turn(self) -> None: 
        self.turn = (self.turn + 1) % self.players

    def get_turn(self, auto_play_bots=True) -> int: 
        if not self.players[self.turn]['is_alive']:
            return -1 
        elif not self.check_player_state(self.get_movements()):
            return -1 
        elif self.players[self.turn]['is_bot'] and auto_play_bots: 
            self.make_bot_move()
        
        return self.turn
    
    def get_movements(self) -> List[Tuple[int]]:
        if self._cached_turn == self.turn and self._cached_movements is not None: 
            return self._cached_movements
        
        if self.players[self.turn]: 
            movements = self.get_possible_moves(self.turn)
            legal_movements = self.filter_legal_moves(self.turn, movements)
            
            castles = []
            # if not self.is_in_check(self.turn):
            #     castles = self.get_castles(self.turn)
            #     ...
            
            result = legal_movements + castles
        else:
            result = []
        
        self._cached_turn = self.turn 
        self._cached_movements = result
        return result
                        
    def get_possible_moves(self, player: int) -> List[Tuple[int, int]]:
        player_pieces = self.board.get_pieces(player)
        
        movements = []
        for piece in player_pieces:
            piece_type = piece[0]
            tile = piece[2]
            has_moved = piece[3]
            captured = piece[4]
            
            tiles_offsets = self.board.tiles_offsets
            pieces_offsets = self.board.pieces_offsets[tiles_offsets[tile] : tiles_offsets[tile+1] + 1]
            patterns_offsets = self.board.patterns_offsets[pieces_offsets[piece_type] : pieces_offsets[piece_type + 1] + 1]
            
            for i in range(len(patterns_offsets) - 1): 
                to_tiles = self.board.adjacency_list[patterns_offsets[i] : patterns_offsets[i + 1]]
    

    def discard_moves(self, player: int, piece_type: int, to_tiles: np.array) -> List[int]: 
        ... 
        
    def filter_legal_moves(self, player: int, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        ...
        
    def is_in_chech(self, player: int) -> bool: 
        ... 
        
    def make_move(self, move: List[int]) -> np.array: 
        ...

    def undo_move(self, move: np.array) -> None: 
        ...