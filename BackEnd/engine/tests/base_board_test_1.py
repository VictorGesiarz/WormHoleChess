
""" 
Test of base board with: 
 - No stopping after finding the king when looking for checks 
 - Looking for the king from all the pieces, instead of casting from the king outside
 - Doing random moves
 - 200 moves limit, 50 per player
"""

import time

from engine.core.ChessFactory import ChessFactory

player_data = [
    ("white", "bot", "random"),
    ("black", "bot", "random"),
    ("blue", "bot", "random"),
    ("red", "bot", "random"),
]

def simulate_game(): 
    game_creation_time = time.time()
    game = ChessFactory.create_game(
        player_data = player_data, 
        mode = "base",
        size = "big"
    )
    game_creation_time = time.time() - game_creation_time
    game.check_size()
    print(f"Game created in {game_creation_time:.4f}s")

    max_turns = 100 # 25 per player
    total_calc_time = 0
    game_time = time.time()

    while not game.is_finished() and max_turns > 0: 
        calculate_moves = game.get_turn()
        game.next_turn()
        max_turns -= 1

    game_time = time.time() - game_time

    print(f"Total move calc time: {total_calc_time:.4f}s")
    print(f"Total game time: {game_time:.4f}s")

def test(): 
    times = []
    for i in range(100): 
        start_time = time.time()
        simulate_game()
        end_time = time.time()
        times.append(end_time - start_time)
        print(f"Game {i+1}: {end_time - start_time:.2f}s")
    print(f"Average time: {sum(times)/len(times):.2f}s")


if __name__ == "__main__":
    simulate_game()
    # test()