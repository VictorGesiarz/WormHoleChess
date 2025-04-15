import chess
import random
import time
import tracemalloc
import pandas as pd


def simulate_game():
    game_creation_time = time.time()
    board = chess.Board()
    game_creation_time = time.time() - game_creation_time
    
    calc_times = []
    memory_usage = [0]
    move_count = 0
    
    # tracemalloc.start()
    # start_mem, _ = tracemalloc.get_traced_memory()
    game_start_time = time.time()
    
    while not board.is_game_over() and move_count < 120:
        calc_start = time.time()
        legal_moves = list(board.legal_moves)
        calc_end = time.time()
        
        move_start = time.time()
        move = random.choice(legal_moves)
        board.push(move)
        move_end = time.time()
        
        # current_mem, _ = tracemalloc.get_traced_memory()
        # memory_usage.append(current_mem - start_mem)
        
        calc_times.append(calc_end - calc_start)
        move_count += 1
    
    game_duration = time.time() - game_start_time
    tracemalloc.stop()
    
    return move_count, game_duration, sum(calc_times), sum(calc_times) / len(calc_times), max(memory_usage, default=0)

def main():
    results = []
    for i in range(100):
        move_count, game_duration, total_calc_time, avg_calc_time, peak_memory = simulate_game()
        results.append([i+1, move_count, game_duration, total_calc_time, avg_calc_time, peak_memory])
        print(f"Game {i+1}: {move_count} moves, {game_duration:.2f}s, Total calc time: {total_calc_time:.4f}s, Avg calc time: {avg_calc_time:.4f}s, Memory: {peak_memory} bytes")
    
    df = pd.DataFrame(results, columns=["Game", "Move Count", "Total Duration (s)", "Total Calc Time (s)", "Avg Calc Time (s)", "Peak Memory (bytes)"])
    df.to_csv("./engine/tests/results/python_chess_results.csv", index=False)
    
if __name__ == "__main__":
    main()
