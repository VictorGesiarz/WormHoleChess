from engine.ChessFactory import ChessFactory


import time 


def test(): 
    num_tests = 1000

    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=2), 
        program_mode="matrix",
        game_mode="wormhole",
        size=(8, 8)
    )

    start = time.time()

    for _ in range(num_tests):
        game_copy = game.copy()
        while not game_copy.is_finished(): 
            game_copy.copy()
            game_copy.get_turn()
            game_copy.next_turn()
    end = time.time()

    print(f"Took {end - start:.4f} seconds")

test()