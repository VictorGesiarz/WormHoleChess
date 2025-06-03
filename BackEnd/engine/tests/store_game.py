from engine.core.ChessFactory import ChessFactory


def store_game(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="layer",
        game_mode="wormhole",
        size=(8, 8),
    )

    move_count = 0
    while not game.is_finished() and move_count < 120: 
        turn = game.get_turn()
        game.next_turn()
        move_count += 1

    game.export('./db/prueba2.json')


store_game()