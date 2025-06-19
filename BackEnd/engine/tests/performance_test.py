import time
import pandas as pd

from engine.ChessFactory import ChessFactory, MatrixChessFactory
from engine.core.constants import PARAMETERS
from collections import defaultdict



PARAMETERS['cast_from_king'] = True

def simulate_game(game, id=0): 

    total_calc_time = 0.0
    calc_count = 0
    max_memory = game.check_size()
    move_count = 0

    game_time = time.time()
    while not game.is_finished(): 
        turn = game.get_turn()
        game.next_turn()
        move_count += 1
    game_time = time.time() - game_time

    winner = game.winner()

    average_calc_time = total_calc_time / calc_count if calc_count > 0 else 0

    # print(f"Game {id+1}: {move_count} moves, Game duration: {game_time:.4f}s, Total calc time: {total_calc_time:.4f}s, Avg calc time: {average_calc_time:.4f}s, Memory: {max_memory} bytes")
    return move_count, game_time, total_calc_time, average_calc_time, max_memory, winner


def test(players, size, program, mode, tests=100): 
    game_creation_time = time.time()
    num_players = players
    num_montecarlo = 0
    print(players, size, program, mode)
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=num_players, types=["mcts-parallel"] * num_montecarlo + ["random"] * (num_players - num_montecarlo)), 
        program_mode=program,
        game_mode=mode,
        size=size,
    )
    game_creation_time = time.time() - game_creation_time

    results = []
    start = time.time()
    winners = []
    for i in range(tests): 
        move_count, game_duration, total_calc_time, avg_calc_time, peak_memory, winner = simulate_game(game.copy(), i)

        if i == 0: continue  # Skip first result

        results.append([i, move_count, game_duration, total_calc_time, avg_calc_time, peak_memory])
        winners.append(winner)
    end = time.time()

    df = pd.DataFrame(results, columns=["Game", "Move Count", "Total Duration (s)", "Total Calc Time (s)", "Avg Calc Time (s)", "Peak Memory (bytes)"])

    mean_duration = df["Total Duration (s)"].mean()
    return mean_duration




if __name__ == "__main__":
    results = defaultdict(dict)
    programs = ['base', 'layer', 'matrix']
    
    for size in [ (8, 8), (6, 6), (5, 5)]: 
        for p in [2, 4]: 
            for mode in ['normal', 'wormhole']: 
                if p == 4 and mode == 'normal': 
                    continue
                if size == (5, 5) and mode == 'wormhole': 
                    continue

                label = f"{size[0]}x{size[1]} {mode}"
                for program in programs:
                    print(f'\nPlayers: {p} size: {size} mode: {mode} program: {program}')
                    # try:
                    mean_time = test(p, size, program, mode, tests=100)
                    print(mean_time)
                    results[label][program] = round(mean_time, 4)
                    # except Exception as e:
                    #     print(f"Error in test {label}, {program}: {e}")
                    #     results[label][program] = None  # Mark failure

    df = pd.DataFrame(results).T  # transpose so rows = configs
    df = df[programs]  # ensure consistent column order
    print("\nFinal Mean Duration Table (seconds):")
    print(df.to_string())

    df.to_csv("./engine/tests/results/summary_duration_table.csv")