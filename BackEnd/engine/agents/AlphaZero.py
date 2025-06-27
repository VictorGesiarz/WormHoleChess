from __future__ import annotations
from typing import TYPE_CHECKING

from math import log, sqrt
import numpy as np 
import torch
device = torch.device("cpu")

from engine.agents.Agent import Agent
from engine.agents.alpha_zero_training.GNNetwork import AlphaZeroGNN

if TYPE_CHECKING: 
    from engine.core.GameMatrices import GameMatrices
    from engine.core.matrices.MatrixBoard import BaseMatrixBoard


class AlphaZero(Agent): 
    def __init__(self, 
                 game: GameMatrices, 
                 representation: BaseMatrixBoard, 
                 network, 
                 mcts_simulations: int = 1500,
                 C: int = 1.4):
        self.game = game
        self.representation = representation
    
        self.network = network.to(device)

        self.mcts_simulations = mcts_simulations
        self.C = C

    def choose_move(self): 
        player = self.game.get_turn(auto_play_bots=False)

        N, W, Q, P = {}, {}, {}, {}
        for sim in range(self.mcts_simulations): 
            self.run_simulation(self.game.copy(), self.representation.copy(), N, W, Q, P)

        moves, hashes = self.game.get_movements(include_hashes=True)

        visit_counts = np.array([N.get((player, hash_), 0) for hash_ in hashes])
        best_move_index = np.argmax(visit_counts)
        move = moves[best_move_index]

        return move
    
    def run_simulation(self, game, representation, N, W, Q, P): 
        trajectory = []

        player = game.get_turn(auto_play_bots=False)
        expand = True
        v = None

        while not game.is_finished():
            if player == -1:
                game.next_turn()
                player = game.get_turn(auto_play_bots=False)
                continue

            moves, hashes = game.get_movements(include_hashes=True)

            if any((player, child_hash) not in P for child_hash in hashes) and expand:
                expand = False  # Only expand once per simulation
                state = representation.to_pyg_data(device)

                moves_tensor = torch.tensor(moves, dtype=torch.long).to(device)
                player_tensor = torch.tensor([player], dtype=torch.long).to(device)

                with torch.no_grad():   
                    prior_policy, v = self.network(
                        x=state.x,
                        edge_index=state.edge_index,
                        move_index=moves_tensor,
                        player=player_tensor,
                    )
                prior_policy = prior_policy[0]
                v = v[0]

                probs = torch.softmax(prior_policy, dim=0).detach().cpu().numpy()

                for i, state_hash in enumerate(hashes):
                    P[(player, state_hash)] = probs[i]

                break  # Stop simulation, backpropagate value v

            # Otherwise select move by UCB as usual
            total_N = sum(N.get((player, h), 1) for h in hashes)
            best_score = -float('inf')
            best_move, best_state = None, None

            for i, (move, state_hash) in enumerate(zip(moves, hashes)):
                key = (player, state_hash)

                n = N.get(key, 0)
                q = Q.get(key, 0)
                p = P.get(key, 0)

                ucb = q + self.C * p * np.sqrt(total_N + 1) / (1 + n)
                if ucb > best_score:
                    best_score = ucb
                    best_move = move
                    best_state = state_hash

            history_movement = game.make_move(best_move, precomputed_hash=best_state)
            representation.update_board(history_movement)

            trajectory.append((player, best_state))

            game.next_turn()
            player = game.get_turn(auto_play_bots=False)

        rewards = [0, 0]
        if v is not None: 
            rewards[1 - player] = -v
        else: 
            rewards = game.rewards

        # BackPropagate
        for player, state_hash in trajectory:
            key = (player, state_hash)
            reward = rewards[player]

            N[key] = N.get(key, 0) + 1
            W[key] = W.get(key, 0) + reward
            Q[key] = W[key] / N[key]

        return trajectory
    
    @staticmethod
    def load_network(network_path): 
        network = AlphaZeroGNN(13, 256)
        state_dict = torch.load(network_path)
        network.load_state_dict(state_dict)
        network.eval()
        return network