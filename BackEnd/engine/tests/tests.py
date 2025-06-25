import time 
from engine.ChessFactory import ChessFactory


def simulate_game(game): 
    move_count = 0

    game_time = time.time()
    while not game.is_finished(): 
        turn = game.get_turn()
        game.next_turn()
        move_count += 1
    game_time = time.time() - game_time

    winner = game.winner()
    print(f'Game winner {winner}')
    print(f'Move count: {move_count}, {game.moves_count}')
    return winner

def test(num): 
    num_players = 2
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=num_players, types=["random"] * num_players), 
        program_mode='matrix',
        game_mode='normal',
        size=(5, 5),
        max_turns=60,
    )
    print("game created")

    winners = []
    for i in range(num):
        winners.append(simulate_game(game.copy()))

    # print(winners)

test(100)