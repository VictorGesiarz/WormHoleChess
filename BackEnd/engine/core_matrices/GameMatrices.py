import numpy as np
from typing import List, Tuple


from engine.core_matrices.MatrixBoard import LayerMatrixBoard, Pieces, Teams, PARTITIONS
from engine.core_matrices.Player import Player
from engine.utils.ZobristHasher import ZobristHasher


class GameMatrices: 
    def __init__(self, 
                 board: LayerMatrixBoard,
                 players: list[Player],
                 turn: int, 
                 verbose: int = 0): 
        """ Class that does the same as the other Game class, but using the graph represented as a matrix. 

        Args:
            board (np.ndarray): _description_
            players (int): _description_
            turn (int): _description_
            verbose (int, optional): _description_. Defaults to 0.
        """
    
        self.players = players
        self.number_of_players = len(players)
        self.turn = turn 
        self.verbose = verbose
        
        self.board = board
        self.hasher = ZobristHasher(6, self.number_of_players, board.shape[0])
        
        self._cached_turn = None
        self._cached_movements = None
        self.history = List[Tuple[int, int]]
        self.initial_positions = self.get_pieces_state()
        self.positions_counter = {hash(self): 1}
        self.moves_without_capture = 0
        
    def __hash__(self):
        return self.hasher.compute_hash(self. board)

    def check_size(self) -> None:
        from pympler import asizeof
        return asizeof.asizeof(self)
    
    def copy(self) -> 'GameMatrices':
        ...
        
    def next_turn(self) -> None: 
        self.turn = (self.turn + 1) % self.players
        
    def next_turn(self, auto_play_bots=True) -> int: 
        self.turn = (self.turn + 1) % self.players
        
        if not self.players[self.turn].alive:
            return -1 
        elif not self.check_player_state(self.get_movements()):
            return -1 
        elif self.players[self.turn].is_bot and auto_play_bots: 
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
        
        for piece in player_pieces:
            edge_connections = self.board.node_edges[piece[1]]
            
            
        
    def filter_legal_moves(self, player: int, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        ...
        
    def is_in_chech(self, player: int) -> bool: 
        ... 
        
    def make_move(self, move: Tuple[int, int]) -> None: 
        ...