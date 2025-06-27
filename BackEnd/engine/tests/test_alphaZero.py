import time 
import random
from engine.ChessFactory import ChessFactory
from engine.agents.AlphaZero import AlphaZero
from engine.agents.RandomAI import RandomAI
from engine.agents.MonteCarlo import MonteCarlo
from engine.agents.MonteCarloParallel import MonteCarloParallel


def arena(game, representation, agents): 
    game_time = time.time()
    while not game.is_finished(): 
        turn = game.get_turn(auto_play_bots = False)
    
        if turn == -1: 
            continue

        agent = agents[turn]
        start = time.time()
        move = agent.choose_move()
        end = time.time()
        print(f'Took: {end - start:.4f} seconds')
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
        max_turns=60,
        # initial_positions='queen_mate'
    )

    representation = ChessFactory.create_representation(game)

    network_old = AlphaZero.load_network('./engine/agents/alpha_zero_training/models/backups_0/version_0.pt')
    network_new = AlphaZero.load_network('./engine/agents/alpha_zero_training/models/backups_0/version_4.pt')

    wins, draws, loses = 0, 0, 0
    for i in range(num):
        game_copy = game.copy()
        representation_copy = representation.copy()
        agents = [
            # AlphaZero(game_copy, representation_copy, network_old, 1500),
            MonteCarlo(game_copy),
            # MonteCarloParallel(game_copy),
            AlphaZero(game_copy, representation_copy, network_new, 1500)
            # RandomAI(game_copy),
        ]

        new_network_team = random.randint(0, 1)
        # new_network_team = 0
        if new_network_team == 0: 
            agents = agents[::-1]

        print(f'\n - - - - - - Playing game: {i}, New network Team: {new_network_team} - - - - - -')
        winner = arena(game_copy, representation_copy, agents)
        if winner == new_network_team: 
            print("New network won")
            wins += 1
        elif winner == -1: 
            draws += 1
            print("Draw")
        else: 
            loses += 1
            print("New network lost")

    print(f"Wins: {wins}, Draws: {draws}, Loses: {loses}")

test(20)