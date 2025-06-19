import time 
from engine.ChessFactory import ChessFactory


def simulate_game(game): 
    move_count = 0

    game_time = time.time()
    while not game.is_finished(): 
        turn = game.get_turn()
        game.print_last_move()
        game.next_turn()
        move_count += 1
    game_time = time.time() - game_time

    winner = game.winner()
    print(f'Game winner {winner}')
    return winner

def test(num): 
    num_players = 4
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=num_players, types=["random"] * 3 + ['mcts']), 
        program_mode='matrix',
        game_mode='wormhole',
        size=(8, 8),
    )
    print("game created")

    winners = []
    for i in range(num):
        winners.append(simulate_game(game.copy()))

    print(winners)

test(5)