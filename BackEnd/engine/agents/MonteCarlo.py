from __future__ import annotations
from typing import TYPE_CHECKING

import datetime
import random 
import time
from math import log, sqrt

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

        seconds = kwargs.get('time', 20)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.simulations_per_move = kwargs.get('simulations_per_move', 30000)
        self.max_moves = kwargs.get('max_moves', 120)
        self.C = kwargs.get('C', 1.4) # UCB1 Parameter

    def choose_move(self):
        # Causes the AI to calculate the best move from the
        # current game state and return it.
        print("Choosing move (MCTS)")
        
        self.max_depth = 0
        moves, hashes = self.game.get_movements(include_hashes=True)
        player = self.game.get_turn(auto_play_bots=False)
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
        while datetime.datetime.now(datetime.timezone.utc) - begin < self.calculation_time and games < self.simulations_per_move:
            start = time.time()
            self.run_simulation()
            simulation_time += time.time() - start
            games += 1

        moves_states = list(zip(moves, hashes))
        # Get the hash of the resulting state if we make each move. 
        # moves_states = []
        # for move in moves: 
        #     self.game.make_move(move, store=False)
        #     moves_states.append((move, self.game.hash))
        #     self.game.undo_move(remove=False)

        # Display the number of calls of `run_simulation` and the
        # time elapsed.
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

        print("Maximum depth searched:", self.max_depth)

        print("Chosen move:", move)
        
        print(f"Average time per simulation: {simulation_time / games:.6f}")
        print(f"Total time spent in simulations: {simulation_time:.6f}")
        print(f" - Average time per move calculation: {self.move_calc_time / games:.6f}")
        print(f" - Total time spent calculating move: {self.move_calc_time:.6f}")
        print(f" - Average time per copy: {self.copytime / games:.6f}")
        print(f" - Time spent copying game: {self.copytime:.6f}")
        print(f" - Average time per update: {self.update_tree_time / games:.6f}")
        print(f" - Total time spent updating tree: {self.update_tree_time:.6f}")
        print(f" - Average time per hashing: {self.hashing_time / games:.6f}")
        print(f" - Total time spent hashing: {self.hashing_time:.6f}")
        print(f" - Average time per backpropagation: {self.back_propagation_time / games:.6f}")
        print(f" - Total time spent backpropagating: {self.back_propagation_time:.6f}")

        return move

    def run_simulation(self):
        # Optimization for faster accessing
        plays, wins = self.plays, self.wins

        visited_states = set()
        copytime = time.time()
        game_copy = self.game.copy()
        self.copytime += time.time() - copytime
        player = game_copy.get_turn(auto_play_bots=False)

        move_count = 1
        expand = True
        while not game_copy.is_finished():
            if player == -1: 
                game_copy.next_turn()
                player = game_copy.get_turn(auto_play_bots=False)
                continue

            moves, hashes = game_copy.get_movements(include_hashes=True)
            moves_states = list(zip(moves, hashes))

            # moves_states = []
            # hashing_time = time.time()
            # for move in moves: 
            #     game_copy.make_move(move, store=False)
            #     moves_states.append((move, game_copy.hash))
            #     game_copy.undo_move(remove=False)
            # self.hashing_time += time.time() - hashing_time

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

            game_copy.make_move(move, precomputed_hash=state)

            # `player` here and below refers to the player
            # who moved into that particular state.
            if expand and (player, state) not in plays:
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                if move_count > self.max_depth:
                    self.max_depth = move_count

            visited_states.add((player, state))
            move_count += 1

            game_copy.next_turn()
            move_calc_time = time.time()
            player = game_copy.get_turn(auto_play_bots=False)
            self.move_calc_time += time.time() - move_calc_time
        
        winner = game_copy.winner()

        # BackPropagation 
        back_propagation_time = time.time()
        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player, state)] += 1
            if player == winner:
                wins[(player, state)] += 1
        self.back_propagation_time += time.time() - back_propagation_time
