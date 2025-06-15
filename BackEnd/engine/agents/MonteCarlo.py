from __future__ import annotations
from typing import TYPE_CHECKING

import datetime
import random 
import time
from math import log, sqrt
from pympler import asizeof

from engine.agents.Agent import Agent

if TYPE_CHECKING: 
    from engine.core.Game import Game
    from engine.core.GameMatrices import GameMatrices


class MonteCarlo(Agent):
    def __init__(self, game: Game | GameMatrices, **kwargs) -> None:
        """ Monte Carlo Tree Search AI. Implements MCTS algorithm to decide the move to make for the bots. One instance can cover all bots at once, since the tree can store the values for each player.  

        Args:
            game (Game): instance of game in wich we will simulate.
            time: seconds to let the AI spend calculating the move. Defaults to 30
            max_moves: maximum number of moves per simulation. Defaults to 120
            C: UCB1 hyperparameter to encourage more or less exploration. Defaults to 1.4
        """
        self.game = game
        self.wins = {}
        self.plays = {}

        seconds = kwargs.get('time', 25)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.simulations_per_move = kwargs.get('simulations_per_move', 30000)
        self.C = kwargs.get('C', 1.4) # UCB1 Parameter

    def choose_move(self):
        # Causes the AI to calculate the best move from the
        # current game state and return it.
        print("\n \n - - - - - - - - - - - Choosing move (MCTS) - - - - - - - - - - - - - - ")
        
        self.max_depth = 0
        player = self.game.get_turn(auto_play_bots=False)
        moves, hashes = self.game.get_movements(include_hashes=True)
        if len(moves) == 0: 
            return 
        if len(moves) == 1: 
            return moves[0]

        games = 0
        begin = datetime.datetime.now(datetime.timezone.utc)
    
        simulation_time = 0
        self.move_calc_time = 0
        self.copytime = 0
        self.update_tree_time = 0
        self.back_propagation_time = 0
        self.hashing_time = 0
        self.make_move_time = 0
        self.invalid_player_time = 0
        self.move_and_hash_extraction_time = 0
        self.expansion_time = 0
        while datetime.datetime.now(datetime.timezone.utc) - begin < self.calculation_time and games < self.simulations_per_move:
            start = time.time()
            self.run_simulation()
            simulation_time += time.time() - start
            games += 1

        moves_states = list(zip(moves, hashes))

        # Display the number of calls of `run_simulation` and the time elapsed.
        print(games, datetime.datetime.now(datetime.timezone.utc) - begin)
        
        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            ((self.wins.get((player, S), 0) /
            self.plays.get((player, S), 1), move)
            for move, S in moves_states),
            key=lambda x: x[0]  # compare only by win rate
        )

        # Display the stats for each possible play.
        for x in sorted(  # x = (percent, wins, plays, move)
            ((100 * self.wins.get((player, S), 0) /
            self.plays.get((player, S), 1),
            self.wins.get((player, S), 0),
            self.plays.get((player, S), 0), move)
            for move, S in moves_states),
            key=lambda x: x[0],  # sort only by percent
            reverse=True
        ):
            print("{3}: {0:.2f}% ({1} / {2})".format(*x))

        # print("Maximum depth searched:", self.max_depth)

        # print("Chosen move:", move)
        
        # print(f"Tree size: {asizeof.asizeof(self.plays)} (plays) + {asizeof.asizeof(self.wins)} (wins)")
        # print(f"Average time per simulation: {simulation_time / games:.6f}")
        # print(f"Total time spent in simulations: {simulation_time:.6f}")
        # print(f" - Average time per move calculation: {self.move_calc_time / games:.6f}")
        # print(f" - Total time spent calculating move: {self.move_calc_time:.6f}")
        # print(f" - Average time per skiping player: {self.invalid_player_time / games:.6f}")
        # print(f" - Total time spent skiping players: {self.invalid_player_time:.6f}")
        # print(f" - Average time per hash extraction: {self.move_and_hash_extraction_time / games:.6f}")
        # print(f" - Total time hash extraction: {self.move_and_hash_extraction_time:.6f}")
        # print(f" - Average time per do move: {self.make_move_time / games:.6f}")
        # print(f" - Total time doing moves: {self.make_move_time:.6f}")
        # print(f" - Average time per copy: {self.copytime / games:.6f}")
        # print(f" - Time spent copying game: {self.copytime:.6f}")
        # print(f" - Average time per update: {self.update_tree_time / games:.6f}")
        # print(f" - Total time spent updating tree: {self.update_tree_time:.6f}")
        # print(f" - Average time per expansion: {self.expansion_time / games:.6f}")
        # print(f" - Total time expanding tree: {self.expansion_time:.6f}")
        # print(f" - Average time per hashing: {self.hashing_time / games:.6f}")
        # print(f" - Total time spent hashing: {self.hashing_time:.6f}")
        # print(f" - Average time per backpropagation: {self.back_propagation_time / games:.6f}")
        # print(f" - Total time spent backpropagating: {self.back_propagation_time:.6f}")

        return move

    def run_simulation(self):
        # Optimization for faster accessing
        plays, wins = self.plays, self.wins

        visited_states = set()
        copytime = time.time()
        game_copy = self.game.copy()
        player = game_copy.get_turn(auto_play_bots=False)
        self.copytime += time.time() - copytime

        move_count = 1
        expand = True
        while not game_copy.is_finished():
            invalid_player_time = time.time()
            if player == -1: 
                game_copy.next_turn()
                player = game_copy.get_turn(auto_play_bots=False)
                continue
            self.invalid_player_time += time.time() - invalid_player_time

            move_and_hash_extraction_time = time.time()
            moves, hashes = game_copy.get_movements(include_hashes=True)
            moves_states = list(zip(moves, hashes))
            self.move_and_hash_extraction_time += time.time() - move_and_hash_extraction_time 

            update_tree_time = time.time()
            if all(plays.get((player, S), 0) > 0 for _, S in moves_states):
                # If we have stats on all of the legal moves here, use them with UCB1.
                log_total = log(
                    sum(plays[(player, S)] for move, S in moves_states))
                value, move, state = max(
                    (
                        ((wins[(player, S)] / plays[(player, S)]) +
                        self.C * sqrt(log_total / plays[(player, S)]), move, S)
                        for move, S in moves_states
                    ),
                    key=lambda x: x[0]  # compare only by the score
                )
            else:
                # Otherwise, just make an arbitrary decision.
                move, state = random.choice(moves_states)
            self.update_tree_time += time.time() - update_tree_time

            make_move_time = time.time()
            game_copy.make_move(move, precomputed_hash=state)
            self.make_move_time += time.time() - make_move_time

            # `player` here and below refers to the player
            # who moved into that particular state.
            expansion_time = time.time()
            if expand and (player, state) not in plays:
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                if move_count > self.max_depth:
                    self.max_depth = move_count

            visited_states.add((player, state))
            move_count += 1
            self.expansion_time += time.time() - expansion_time

            move_calc_time = time.time()
            game_copy.next_turn()
            player = game_copy.get_turn(auto_play_bots=False)
            self.move_calc_time += time.time() - move_calc_time
        
        rewards = game_copy.rewards
        # print(rewards)

        # BackPropagation 
        back_propagation_time = time.time()
        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player, state)] += 1

            reward = rewards[player]
            wins[(player, state)] += reward

        self.back_propagation_time += time.time() - back_propagation_time

        