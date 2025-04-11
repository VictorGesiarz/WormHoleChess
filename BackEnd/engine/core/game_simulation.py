import random
import time

from engine.core.Game import Game
from engine.core.Player import Player


def simulate_game(): 
    players = [Player(0), Player(1), Player(2), Player(3)]
    game = Game(players)

    max_turns = 200 # 50 per player
    times = []
    while not game.is_finished() and max_turns > 0: 
        move_calc_time = time.time()
        moves = game.get_movements()
        move_calc_time = time.time() - move_calc_time
        print(f"Move calculation time: {move_calc_time:.4f}s")
        times.append(move_calc_time)
        # print(moves)

        if len(moves) > 0: 
            random_move = random.choice(moves)
            game.make_move(random_move)

        game.next_turn()

        max_turns -= 1
    print(f"Total move calc time: {sum(times):.4f}s")


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