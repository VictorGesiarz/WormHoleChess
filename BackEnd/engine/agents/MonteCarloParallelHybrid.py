from __future__ import annotations
from typing import TYPE_CHECKING

import datetime
import random 
import time
from pympler import asizeof
from math import log, sqrt
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from engine.agents.Agent import Agent

if TYPE_CHECKING: 
    from engine.core.Game import Game
    from engine.core.GameMatrices import GameMatrices


class MonteCarloParallel(Agent):
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

        seconds = kwargs.get('time', 30)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.simulations_per_move = kwargs.get('simulations_per_move', 30000)
        self.C = kwargs.get('C', 1.4) # UCB1 Parameter

    def _merge_stats(self, sim_wins, sim_plays):
        for key, value in sim_wins.items():
            self.wins[key] = self.wins.get(key, 0) + value
        for key, value in sim_plays.items():
            self.plays[key] = self.plays.get(key, 0) + value

    def choose_move(self):
        # Causes the AI to calculate the best move from the
        # current game state and return it.
        self.max_depth = 0
        moves = self.game.get_movements()
        player = self.game.get_turn(auto_play_bots=False)
        if len(moves) == 0: 
            return 
        if len(moves) == 1: 
            return moves[0]
        
        print("\n \n - - - - - - - - - - - Choosing move (MCTS - parallel) - - - - - - - - - - - - - - ")

        start_time = datetime.datetime.now(datetime.timezone.utc)
        end_time = start_time + self.calculation_time
        games = 0

        simulation_time = 0.0
        dispatch_time = 0.0
        merge_time = 0.0

        max_workers = 12
        batches = 5

        # Run tree construction in parallel 
        current_batch = 0
        while datetime.datetime.now(datetime.timezone.utc) < end_time and games < self.simulations_per_move: 
            current_batch += 1

            with ProcessPoolExecutor(
                max_workers=max_workers,
                max_tasks_per_child=1
            ) as executor:

                print("Batch number", current_batch)

                # ⏱ Dispatch timing
                dispatch_start = time.time()
                futures = []
                for _ in range(max_workers):
                    game_copy = self.game.copy()
                    f = executor.submit(MonteCarloParallel.construct_tree_worker, game_copy, self.plays, self.wins, self.C, end_time, self.simulations_per_move / max_workers / batches)
                    futures.append(f)
                dispatch_time += time.time() - dispatch_start
                # print(f'Took {time.time() - dispatch_start:.4f} seconds to create jobs')

                # ⏱ Simulation timing
                sim_start = time.time()
                merge_batch_time = 0
                for future in as_completed(futures):
                    sim_plays, sim_wins, depth, sim_games = future.result()
                    merge_start = time.time()
                    self._merge_stats(sim_wins, sim_plays)
                    merge_batch_time += time.time() - merge_start
                    self.max_depth = max(self.max_depth, depth)
                    games += sim_games
                simulation_time += time.time() - sim_start - merge_batch_time
                merge_time += merge_batch_time
                # print(f'Took {merge_batch_time:.4f} seconds to merge dictionaries')
                # print(f"Took {time.time()- sim_start:.4f} to run simulations")

        # Get the hash of the resulting state if we make each move. 
        moves_states = []
        for move in moves: 
            self.game.make_move(move, store=False)
            moves_states.append((move, self.game.hash))
            self.game.undo_move(remove=False)

        # Display the number of calls of `run_simulation` and the
        # time elapsed.
        print(games, datetime.datetime.now(datetime.timezone.utc) - start_time)
        
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
        
        print(f"Tree size: {asizeof.asizeof(self.plays)} (plays) + {asizeof.asizeof(self.wins)} (wins)")
        print("Average time per simulation:", simulation_time / games)
        print("Total time spent in simulations:", simulation_time)
        print(" - Time creating parallel processes:", dispatch_time)
        print(" - Time merging dcitionaries", merge_time)

        return move


    @staticmethod
    def construct_tree_worker(game, plays, wins, C, end_time, max_games): 
        new_plays = {}
        new_wins = {}

        games = 0
        max_depth = 0
        while datetime.datetime.now(datetime.timezone.utc) < end_time and games < max_games: 
            max_depth = MonteCarloParallel.run_simulation_worker(game, plays, new_plays, wins, new_wins, C, max_depth)
            games += 1

        return new_plays, new_wins, max_depth, games 
    

    @staticmethod
    def run_simulation_worker(game, plays, new_plays, wins, new_wins, C, max_depth):
        visited_states = set()
        
        game_copy = game.copy()
        player = game_copy.get_turn(auto_play_bots=False)
        move_count = 1
        expand = True
        initialized_state = None

        while not game_copy.is_finished():
            if player == -1:
                game_copy.next_turn()
                player = game_copy.get_turn(auto_play_bots=False)
                continue

            moves = game_copy.get_movements()
            moves_states = []
            for move in moves:
                game_copy.make_move(move, store=False)
                moves_states.append((move, game_copy.hash))
                game_copy.undo_move(remove=False)

            if all((player, S) in plays for _, S in moves_states):
                log_total = log(sum(plays[(player, S)] for _, S in moves_states))
                _, move, state = max(
                    (
                        ((wins[(player, S)] / plays[(player, S)]) +
                        C * sqrt(log_total / plays[(player, S)]), move, S)
                        for move, S in moves_states
                    ),
                    key=lambda x: x[0]
                )
            else:
                move, state = random.choice(moves_states)

            game_copy.make_move(move)

            if expand and (player, state) not in plays:
                expand = False
                initialized_state = (player, state)
                plays[(player, state)] = 1
                wins[(player, state)] = 0
                new_plays[(player, state)] = 1
                new_wins[(player, state)] = 0
                if move_count > max_depth:
                    max_depth = move_count

            visited_states.add((player, state))
            move_count += 1
            game_copy.next_turn()
            player = game_copy.get_turn(auto_play_bots=False)

        rewards = game_copy.rewards

        for player, state in visited_states:
            if (player, state) not in plays:
                continue

            if (player, state) not in new_plays:
                new_plays[(player, state)] = 0
                new_wins[(player, state)] = 0

            if not (player, state) == initialized_state: 
                plays[(player, state)] += 1
                new_plays[(player, state)] += 1

            reward = rewards[player]
            wins[(player, state)] += reward
            new_wins[(player, state)] += reward

        return max_depth