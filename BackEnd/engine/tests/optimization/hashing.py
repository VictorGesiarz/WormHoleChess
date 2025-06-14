from engine.ChessFactory import ChessFactory


import time 


def simulate_game(game): 
    while not game.is_finished(): 

        moves = game.get_movements()
        for move in moves:
            pre_hash = game.hash
            game.make_move(move, store=False)
            post_hash = game.hash
            print(game.board.pieces[game.history[game.moves_count][0]])
            game.undo_move(remove=False)
            pre_post_hash = game.hash
            
            if pre_hash != pre_post_hash: 
                print(f'Doing move {game.translate_movement_to_str(move)}')
                print(f'Hash before doing move {pre_hash}')
                print(f'Hash after undoing move {pre_post_hash}')
                print(game.history[game.moves_count])
                print(game.board.pieces[game.history[game.moves_count][0]])
                raise RuntimeError("HASH HAS CHANGED!")
            
        game.get_turn()
        game.next_turn()


def test(): 
    num_tests = 10000

    start = time.time()
    for i in range(num_tests): 
        print(f"Simulating game {i}")

        game = ChessFactory.create_game(
            player_data=ChessFactory.create_player_data(num_players=2), 
            program_mode="matrix",
            game_mode="wormhole",
            size=(8, 8)
        )

        simulate_game(game)
    end = time.time()

    print(f"Took {end - start:.4f} seconds")

test()