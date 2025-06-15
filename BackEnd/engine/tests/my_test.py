import time
import pandas as pd

from engine.ChessFactory import ChessFactory, MatrixChessFactory
from engine.core.constants import PARAMETERS


PARAMETERS['cast_from_king'] = True

def simulate_game(id=0): 
    game_creation_time = time.time()
    num_players = 2
    num_montecarlo = 1
    game = ChessFactory.create_game(
        # player_data=ChessFactory.create_player_data(num_players=num_players, types=["mcts-parallel"] * num_montecarlo + ["random"] * (num_players-num_montecarlo)), 
        player_data=ChessFactory.create_player_data(num_players=2, types=['mcts', 'mcts-parallel']),
        program_mode="matrix",
        game_mode="normal",
        size=(5, 5),
    )
    game_creation_time = time.time() - game_creation_time

    total_calc_time = 0.0
    calc_count = 0
    max_memory = game.check_size()
    move_count = 0

    game_time = time.time()
    while not game.is_finished(): 
        turn = game.get_turn()
        game.print_last_move()
        game.next_turn()
        move_count += 1
    game_time = time.time() - game_time

    winner = game.winner()

    average_calc_time = total_calc_time / calc_count if calc_count > 0 else 0

    print(f"Game {id+1}: {move_count} moves, Game duration: {game_time:.4f}s, Total calc time: {total_calc_time:.4f}s, Avg calc time: {average_calc_time:.4f}s, Memory: {max_memory} bytes")
    return move_count, game_time, total_calc_time, average_calc_time, max_memory, winner


def test(): 
    results = []
    start = time.time()
    winners = []
    for i in range(10): 
        move_count, game_duration, total_calc_time, avg_calc_time, peak_memory, winner = simulate_game(i)
        results.append([i+1, move_count, game_duration, total_calc_time, avg_calc_time, peak_memory])
        winners.append(winner)
    end = time.time()

    df = pd.DataFrame(results, columns=["Game", "Move Count", "Total Duration (s)", "Total Calc Time (s)", "Avg Calc Time (s)", "Peak Memory (bytes)"])

    print(f"Mean game duration: {df['Total Duration (s)'].mean():.4f}s")
    print(f'Test duration: {end-start:.4f}')
    print(winners)

    df.to_csv("./engine/tests/results/base_board_test.csv", index=False)


if __name__ == "__main__":
    test()
    # simulate_game()