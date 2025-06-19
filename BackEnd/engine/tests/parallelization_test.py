import time
import pandas as pd

from engine.ChessFactory import ChessFactory
from collections import defaultdict



def test(players, size, mode, num_workers): 
    game_creation_time = time.time()
    num_players = players
    num_montecarlo = 1
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=num_players, types=["mcts-parallel"] * num_montecarlo + ["random"] * (num_players - num_montecarlo)), 
        program_mode='matrix',
        game_mode=mode,
        size=size,
        num_workers=num_workers
    )
    game_creation_time = time.time() - game_creation_time

    mean_time = game.make_move_bot()
    return mean_time


if __name__ == "__main__":
    results = defaultdict(dict)
    workers = [4, 6, 8, 10, 12, 14]

    for size in [ (8, 8), (6, 6), (5, 5)]: 
        for p in [2, 4]: 
            for mode in ['normal', 'wormhole']: 
                if p == 4 and mode == 'normal': 
                    continue
                if size == (5, 5) and mode == 'wormhole': 
                    continue

                label = f"{size[0]}x{size[1]} {mode}"
                for num_workers in workers:
                    print(f'\nPlayers: {p} size: {size} mode: {mode} num_workers: {num_workers}')
                    # try:
                    mean_time = test(p, size, mode, num_workers)
                    print(mean_time)
                    results[label][num_workers] = round(mean_time, 4)
                    # except Exception as e:
                    #     print(f"Error in test {label}, {program}: {e}")
                    #     results[label][program] = None  # Mark failure

    df = pd.DataFrame(results).T  # transpose so rows = configs
    df = df[workers]  # ensure consistent column order
    print("\nFinal Mean Duration Table (seconds):")
    print(df.to_string())

    df.to_csv("./engine/tests/results/summary_parallelization.csv")