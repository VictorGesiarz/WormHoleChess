from __future__ import annotations
from typing import TYPE_CHECKING

from math import log, sqrt
import numpy as np
import torch
import random

from engine.agents.alpha_zero_training.ReplayBuffer import AlphaZeroReplayBuffer
from engine.agents.alpha_zero_training.GNNetwork import AlphaZeroGNN
from engine.core.matrices.MatrixBoard import BaseMatrixBoard

if TYPE_CHECKING: 
    from engine.core.GameMatrices import GameMatrices


class AlphaZero:
    def __init__(self, 
                 game: GameMatrices, 
                 representation: BaseMatrixBoard, 
                 iterations = 100, 
                 self_play_games = 100, 
                 mcts_simulations = 400, 
                 training_steps = 1000, 
                 plays_per_eval = 100, 
                 replay_size = 100_000, 
                 batch_size = 128, 
                 lr = 0.03, 
                 hidden_layers = 256, 
                 C = 1.4) -> None:
        
        self.game = game
        self.representation = representation

        self.iterations = iterations
        self.self_play_games = self_play_games
        self.mcts_simulations = mcts_simulations
        self.training_steps = training_steps
        self.play_per_eval = plays_per_eval
        self.replay_size = replay_size
        self.batch_size = batch_size
        self.lr = lr

        self.action_to_index, self.index_to_action = self.game.get_action_space()

        self.replay_buffer = AlphaZeroReplayBuffer(replay_size, self.representation.nodes.shape, len(self.action_to_index))
        self.network = AlphaZeroGNN(self.representation.nodes.shape, hidden_layers, len(self.action_to_index))

        self.C = C

    def train(self):
        frozen_model = self.network.load_state_dict(self.network.state_dict())

        for iteration in range(self.iterations):
            print(f"\n \n- - - - - - - - Iteration {iteration} - - - - - - - - ")

            game_copy = self.game.copy()
            representation_copy = self.representation.copy()

            # 1. Self-play
            print("Self play")
            for game in range(self.self_play_games):
                self.run_self_play(game_copy, representation_copy)

            # 2. Train
            print("Training")
            for _ in range(self.training_steps):
                batch = self.replay_buffer.get(self.batch_size)
                loss = self.learn(batch)

                print(f" - Loss {loss:.8f}")

            self.evaluate_model(game_copy, representation_copy, frozen_model)

    def run_self_play(self, game, representation):
        N = {}
        W = {}
        Q = {}

        visited_states = []

        player = game.get_turn(auto_play_bots=False)
        while not game.is_finished(): 
            if player == -1: 
                game.next_turn()
                player = game.get_turn(auto_play_bots=False)

            for sim in range(self.mcts_simulations): 
                self.run_simulation(game.copy(), representation.copy(), N, W, Q)

            moves = game.get_movements(include_hashes=True)
            # Should transform moves to a way that the network can predict them? 

            policy = None # Calculate from Q
            move = None # select best move from policy

            game.make_move(move)
            representation.update_state(game.history[game.move_count])
            state = representation.to_pyg()

            visited_states.append((player, state, policy))

            game.next_turn()
            player = game.get_turn(auto_play_bots=False)

        rewards = game.rewards

        for visited in visited_states: 
            self.replay_buffer.put(visited[0], visited[1], visited[2], rewards[visited[0]])
         

    def run_simulation(self, game, repr, N, W, Q):
        trajectory = []

        player = game.get_turn(auto_play_bots=False)
        expand = True
        while not game.is_finished():
            if player == -1: 
                game.next_turn()
                player = game.get_turn(auto_play_bots=False)
                continue

            valid_moves, hashes = game.get_movements(add_hashes=True)
            move_states = (valid_moves, hashes)
            prior_policy, v = self.network(repr.to_pyg())  

            # Mask logits for illegal moves
            legal_action_indices = []
            for move in valid_moves:
                action_idx = self.action_to_index[tuple(move)]
                legal_action_indices.append(action_idx)

            mask = torch.full_like(prior_policy, float('-inf'))
            mask[legal_action_indices] = 0
            masked_logits = prior_policy + mask
            probs = torch.softmax(masked_logits, dim=0).detach().cpu().numpy()

            # Save priors P(s, a)
            for (move, state_hash) in moves_states:
                key = (player, state_hash)
                action_idx = self.action_to_index[tuple(move)]
                P[key, action_idx] = probs[action_idx]

            # Select move using UCB
            total_N = sum(N.get((player, hash_), 1) for (_, hash_) in moves_states)
            best_score = -float('inf')
            best_move, best_state = None, None

            for (move, state_hash) in moves_states:
                key = (player, state_hash)
                action_idx = self.action_to_index[tuple(move)]

                n = N.get(key, 0)
                q = Q.get(key, 0)
                p = P.get(key, action_idx)

                ucb = q + self.C * p * np.sqrt(total_N + 1) / (1 + n)
                if ucb > best_score:
                    best_score = ucb
                    best_move = move
                    best_state = state_hash

            game.make_move(best_move, precomputed_hash=best_state)
            last_history = game.history[game.moves_count]
            last_history[0] = last_history[0][1]
            repr.update_board(last_history)
            visited_states.append((player, best_state, self.action_to_index[tuple(best_move)]))

            game.next_turn()
            player = game.get_turn(auto_play_bots=False)

        rewards = game.rewards

        # BackPropagate
        for player, state_hash, action_idx in visited_states:
            key = (player, state_hash)
            reward = rewards[player]

            N[key] = N.get(key, 0) + 1
            W[key] = W.get(key, 0) + reward
            Q[key] = W[key] / N[key]

        return trajectory

    def evaluate_model(self, game, repr, frozen_model): 
        wins = 0
        for game in range(self.play_per_eval): 
            frozen_team = random.ranint(0, 1)

            player = game.get_turn()
            while not game.is_finished(): 
                moves = game.get_movements()
                state = repr.to_pyg()
                policy, v = self.network(state) if player != frozen_team else frozen_model(state)

                # Mask the moves again
                moves.mask(policy)

                move = max(moves)

                game.make_move(move)
                repr.update_state(game.history[game.moves_count])

            winner = game.winner
            if winner != frozen_team: 
                wins += 1

        if wins > self.update_frozen_threshold: 
            frozen_model.update_parameters()

    def learn(self, batch):
        # Unpack the batch of training examples
        states, target_policies, target_values = batch  # states ∈ GNN input, policies ∈ probabilities, values ∈ scalars

        # Forward pass through the network
        predicted_policies, predicted_values = self.network(states)

        # Compute losses
        value_loss = MSE(predicted_values, target_values)
        policy_loss = CrossEntropy(predicted_policies, target_policies)  # or KLDiv if using soft targets

        # Total loss = value error + policy error
        total_loss = value_loss + policy_loss

        # Backpropagation step
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()

        return total_loss
