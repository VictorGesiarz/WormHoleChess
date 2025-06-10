from engine.ChessFactory import ChessFactory, MatrixChessFactory
from engine.core.matrices.MatrixBoard import LayerMatrixBoard

from engine.core.matrices.chess_logic_bounds import get_possible_moves

import numpy as np
import time


def test(): 

    position = './engine/core/configs/wormhole/tests/mate.yaml'

    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="matrix",
        game_mode="wormhole",
        size=(8, 8),
        initial_positions=position
    )

    moves = game.get_movements()
    game.print_moves()
    game.get_turn()
    print(game.is_finished())
    print(game.game_state)


test()