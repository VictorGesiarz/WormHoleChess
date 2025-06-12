from __future__ import annotations
from typing import TYPE_CHECKING

import datetime
import random 
import time
import atexit
from math import log, sqrt
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor, as_completed

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
        self.manager = Manager()
        self.wins = self.manager.dict()
        self.plays = self.manager.dict()

        seconds = kwargs.get('time', 1)
        self.calculation_time = datetime.timedelta(seconds=seconds)
        self.simulations_per_move = kwargs.get('simulations_per_move', 30000)
        self.C = kwargs.get('C', 1.4) # UCB1 Parameter

    def cleanup(self): 
        print("\n \n SHUTING DOWN MANAGER \n \n")

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

        games = 0
        begin = datetime.datetime.now(datetime.timezone.utc)
    
        with ProcessPoolExecutor() as executor:
            futures = []
            for _ in range(self.simulations_per_move):
                game_copy = self.game.copy()  # you must copy it because Game is not shared
                args = (game_copy, self.wins, self.plays, self.C, self.max_depth, self.max_moves)
                futures.append(executor.submit(run_simulation_worker, *args))

            for future in as_completed(futures):
                depth = future.result()
                self.max_depth = max(self.max_depth, depth)


        # Get the hash of the resulting state if we make each move. 
        moves_states = []
        for move in moves: 
            self.game.make_move(move, store=False)
            moves_states.append((move, self.game.hash))
            self.game.undo_move(remove=False)

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
        
        print("Average time per simulation:", simulation_time / games)
        print("Total time spent in simulations:", simulation_time)
        print(" - Average time per move calculation:", self.move_calc_time / games)
        print(" - Total time spent calculating move:", self.move_calc_time)
        print(" - Average time per copy:", self.copytime / games)
        print(" - Time spent copying game:", self.copytime)
        print(" - Average time per update:", self.update_tree_time / games)
        print(" - Total time spent updating tree:", self.update_tree_time)
        print(" - Average time per hashing:", self.hashing_time / games)
        print(" - Total time spent hashing:", self.hashing_time)
        print(" - Average time per backpropagation:", self.back_propagation_time / games)
        print(" - Total time spent backpropagating:", self.back_propagation_time)

        return move


def run_simulation_worker(args):
    game, C, max_depth, max_moves = args
    plays = {}
    wins = {}
    visited_states = set()
    
    game_copy = game.copy()
    player = game_copy.get_turn(auto_play_bots=False)
    move_count = 1
    expand = True

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
            plays[(player, state)] = 0
            wins[(player, state)] = 0
            if move_count > max_depth:
                max_depth = move_count

        visited_states.add((player, state))
        move_count += 1
        game_copy.next_turn()
        player = game_copy.get_turn(auto_play_bots=False)

    winner = game_copy.winner()

    for player, state in visited_states:
        plays.setdefault((player, state), 0)
        wins.setdefault((player, state), 0)
        plays[(player, state)] += 1
        if player == winner:
            wins[(player, state)] += 1

    return plays, wins, max_depth
