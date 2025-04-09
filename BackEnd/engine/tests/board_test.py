from engine.core.Board import Board
import random
import time
import tracemalloc
import pandas as pd


def simulate_game(): 
    board = Board()
    move_times = []
    calc_times = []
    memory_usage = []
    move_count = 0
    
    tracemalloc.start()
    start_mem, _ = tracemalloc.get_traced_memory()
    game_start_time = time.time()

    while not board.is_game_over() and move_count < 100: 
        calc_start = time.time()
        legal_moves = board.get_legal_moves()
        calc_end = time.time()

        move_start = time.time()
        move = random.choice(legal_moves)
        board.move(move)
        move_end = time.time()

        current_mem, _ = tracemalloc.get_traced_memory()
        memory_usage.append(current_mem - start_mem)
        
        calc_times.append(calc_end - calc_start)
        move_times.append(move_end - move_start)
        move_count += 1

    game_duration = time.time() - game_start_time
    tracemalloc.stop()
    
    return move_count, game_duration, sum(calc_times), sum(move_times), max(memory_usage, default=0)

def main():
    results = []
    for i in range(100):
        move_count, game_duration, total_calc_time, total_move_time, peak_memory = simulate_game()
        results.append([i+1, move_count, game_duration, total_calc_time, total_move_time, peak_memory])
        print(f"Game {i+1}: {move_count} moves, {game_duration:.2f}s, Calc: {total_calc_time:.4f}s, Move: {total_move_time:.4f}s, Memory: {peak_memory} bytes")
    
    df = pd.DataFrame(results, columns=["Game", "Move Count", "Total Duration (s)", "Total Calc Time (s)", "Total Move Time (s)", "Peak Memory (bytes)"])
    df.to_csv("./chess/tests/results/python_chess_results.csv", index=False)
    
if __name__ == "__main__":
    main()
