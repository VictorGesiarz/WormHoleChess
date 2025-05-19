import time
import pandas as pd

from engine.core.ChessFactory import ChessFactory
from engine.core.constants import PARAMETERS


PARAMETERS['cast_from_king'] = True

def simulate_game(id=0): 
    game_creation_time = time.time()
    num_players = 4
    num_montecarlo = 1
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=num_players, difficulties=["mcts"] * num_montecarlo + ["random"] * (num_players-num_montecarlo)), 
        program_mode="layer",
        game_mode="wormhole",
        size=(8, 8),
        # initial_positions='./engine/core/configs/normal/queen_mate.yaml'
    )
    game_creation_time = time.time() - game_creation_time

    total_calc_time = 0.0
    calc_count = 0
    max_memory = game.check_size()
    move_count = 0

    game_time = time.time()

    while not game.is_finished() and move_count < 120: 
        move_time = time.time()
        turn = game.get_turn()
        move_duration = time.time() - move_time

        if turn >= 0 and game.players[turn].type != 'bot':
            total_calc_time += move_duration
            calc_count += 1

        game.next_turn()
        move_count += 1

    # game.export('./db/random_games/prueba.json')

    game_time = time.time() - game_time

    # print(game.history)

    average_calc_time = total_calc_time / calc_count if calc_count > 0 else 0

    print(f"Game {id+1}: {move_count} moves, Game duration: {game_time:.4f}s, Total calc time: {total_calc_time:.4f}s, Avg calc time: {average_calc_time:.4f}s, Memory: {max_memory} bytes")
    return move_count, game_time, total_calc_time, average_calc_time, max_memory


def test(): 
    results = []
    for i in range(100): 
        move_count, game_duration, total_calc_time, avg_calc_time, peak_memory = simulate_game(i)
        results.append([i+1, move_count, game_duration, total_calc_time, avg_calc_time, peak_memory])

    df = pd.DataFrame(results, columns=["Game", "Move Count", "Total Duration (s)", "Total Calc Time (s)", "Avg Calc Time (s)", "Peak Memory (bytes)"])

    print(f"Mean game duration: {df['Total Duration (s)'].mean():.4f}s")

    df.to_csv("./engine/tests/results/base_board_test.csv", index=False)


if __name__ == "__main__":
    # test()
    simulate_game()