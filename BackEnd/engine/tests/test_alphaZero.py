import time 
import random
from engine.ChessFactory import ChessFactory
from engine.agents.AlphaZero import AlphaZero
from engine.agents.RandomAI import RandomAI


def arena(game, representation, agents): 
    game_time = time.time()
    while not game.is_finished(): 
        turn = game.get_turn(auto_play_bots = False)
    
        if turn == -1: 
            continue

        if game.moves_count > game.max_turns - 10: 
            game.game_state = 2
            break

        agent = agents[turn]
        move = agent.choose_move()
        history_movement = game.make_move(move)
        representation.update_board(history_movement)

        print(game.moves_count, end=': ')
        game.print_last_move()

        game.next_turn()
        
    game_time = time.time() - game_time

    winner = game.winner()
    return winner


def test(num): 
    num_players = 2
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=num_players, types=["human"] * num_players), 
        program_mode='matrix',
        game_mode='wormhole',
        size=(6, 6),
        max_turns=70,
    )

    representation = ChessFactory.create_representation(game)

    network = AlphaZero.load_network('./engine/agents/alpha_zero_training/models/backups/version_1.pt')

    wins, draws, loses = 0, 0, 0
    for i in range(num):
        game_copy = game.copy()
        representation_copy = representation.copy()
        agents = [RandomAI(game_copy), AlphaZero(game_copy, representation_copy, network, 400)]

        alphazero_team = random.randint(0, 1)
        if alphazero_team == 0: 
            agents = agents[::-1]

        print(f'\n - - - - - - Playing game: {i}, AlphaZero Team: {alphazero_team} - - - - - -')
        winner = arena(game_copy, representation_copy, agents)
        if winner == alphazero_team: 
            print("Alpha zero won")
            wins += 1
        elif winner == -1: 
            draws += 1
            print("Draw")
        else: 
            loses += 1
            print("Alpha zero lost")

    print(f"Wins: {wins}, Draws: {draws}, Loses: {loses}")

test(20)