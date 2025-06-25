from __future__ import annotations
from typing import TYPE_CHECKING

from tqdm import tqdm, trange
import matplotlib.pyplot as plt
import numpy as np
import random
import os

import torch
import torch.nn.functional as F
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")
print(device)
torch.autograd.set_detect_anomaly(True)

from engine.agents.alpha_zero_training.ReplayBuffer import AlphaZeroReplayBuffer
from engine.agents.alpha_zero_training.GNNetwork import AlphaZeroGNN
from engine.core.matrices.matrix_constants import MAX_POSSIBLE_MOVES
if TYPE_CHECKING: 
    from engine.core.GameMatrices import GameMatrices
    from engine.core.matrices.MatrixBoard import BaseMatrixBoard


MODEL_PATH = './engine/agents/alpha_zero_training/models/'

class AlphaZero:
    def __init__(self, 
                 game: GameMatrices, 
                 representation: BaseMatrixBoard, 
                 initial_model = None, # To fine tune models
                 iterations = 100, 
                 self_play_games = 100, 
                 mcts_simulations = 400, 
                 training_steps = 50, 
                 plays_per_eval = 20, 
                 mcts_simulations_eval = 100, 
                 replay_size = 30_000, 
                 batch_size = 64, 
                 lr = 1e-4, 
                 hidden_layers = 256, 
                 C = 1.4, 
                 update_frozen_threshold = 0.6,
                 save_path = MODEL_PATH) -> None:
        
        self.game = game
        self.representation = representation

        self.iterations = iterations
        self.self_play_games = self_play_games
        self.mcts_simulations = mcts_simulations
        self.training_steps = training_steps
        self.play_per_eval = plays_per_eval
        self.mcts_simulations_eval = mcts_simulations_eval
        self.replay_size = replay_size
        self.batch_size = batch_size
        self.lr = lr
        self.hidden_layers = hidden_layers
        self.C = C
        self.max_moves = MAX_POSSIBLE_MOVES
        self.update_frozen_threshold = update_frozen_threshold
        
        self.tau = 1.0
        self.__initial_tau = self.tau
        self.__final_tau = 1e-3
        self.__decay_rate = 1e-5

        self.replay_buffer = AlphaZeroReplayBuffer(replay_size, self.representation.nodes.shape, self.max_moves)

        if initial_model is None: 
            self.network = AlphaZeroGNN(self.representation.nodes.shape[1] + 2, self.hidden_layers)
        else: 
            self.network = initial_model
        self.network = self.network.to(device)

        self.frozen = AlphaZeroGNN(self.representation.nodes.shape[1] + 2, self.hidden_layers)
        self.frozen.load_state_dict(self.network.state_dict())
        self.frozen = self.frozen.to(device)

        self.optimizer = torch.optim.Adam(self.network.parameters(), lr=self.lr, weight_decay=1e-5)

        self.save_path = save_path
        self.backups_path = save_path + 'backups'
        self.plots_path = save_path + 'plots'

    def train(self):
        all_avg_losses = []

        for iteration in range(self.iterations):
            print(f"\n \n- - - - - - - - Iteration {iteration} - - - - - - - - ")

            # 1. Self-play
            print(" - Self Play")
            for _ in tqdm(range(self.self_play_games), desc="Self-play games"):
                self.run_self_play(self.game.copy(), self.representation.copy())

            # 2. Train
            losses = []
            print(" - Train")
            for _ in tqdm(range(self.training_steps), desc="Training steps"):
                batch = self.replay_buffer.get(self.batch_size)
                if batch is None: 
                    print(f" - Skipping training: not enough samples in buffer yet: {self.replay_buffer.size}")
                    break
                loss = self.learn(batch)
                losses.append(loss)
            if losses:
                avg_loss = sum(losses) / len(losses)
                print(f" --> Average loss of: {avg_loss:.6f}")
                all_avg_losses.append(avg_loss)
                self.plot_loss(iteration, losses)
                self.plot_avg_loss(all_avg_losses)

            wins = 0
            print(" - Evaluate")
            for _ in tqdm(range(self.play_per_eval), desc="Evaluation games"):
                wins += self.evaluate_model(self.game.copy(), self.representation.copy())
            self.update_frozen(wins)

            self.update_temperature(iteration)

    def update_temperature(self, step):
        # τ = final_tau + (initial_tau - final_tau) * exp(-decay_rate * step)
        self.tau = self.__final_tau + (self.__initial_tau - self.__final_tau) * np.exp(-self.__decay_rate * step)

    def run_self_play(self, game, representation):
        visited_states = []

        pbar = trange(game.max_turns - 10, desc="    Self-play progress", leave=False)

        player = game.get_turn(auto_play_bots=False)
        while not game.is_finished(): 
            if player == -1: 
                game.next_turn()
                player = game.get_turn(auto_play_bots=False)
                continue

            # Shouldn't be necessary, but without it an important bug occurs
            if game.moves_count > (game.max_turns - 10): 
                break

            N, W, Q, P = {}, {}, {}, {}
            for sim in range(self.mcts_simulations): 
                game_copy = game.copy()
                representation_copy = representation.copy()
                self.run_simulation(game_copy, representation_copy, N, W, Q, P)

            state = representation.nodes.copy()
            moves, hashes = game.get_movements(include_hashes=True)

            visit_counts = np.array([N.get((player, hash_), 0) for hash_ in hashes], dtype=np.float32)
            adjusted = visit_counts ** (1 / self.tau)
            policy = adjusted / (adjusted.sum() + 1e-8)  # normalize and prevent divide-by-zero

            # Sample move
            move_index = np.random.choice(len(moves), p=policy)
            move = moves[move_index]

            history_movement = game.make_move(move)
            representation.update_board(history_movement)

            visited_states.append((player, state, moves.copy(), policy))

            game.next_turn()
            player = game.get_turn(auto_play_bots=False)

            pbar.update(1)

        rewards = game.rewards

        for visited in visited_states: 
            self.replay_buffer.put(visited[0], visited[1], visited[2], visited[3], rewards[visited[0]])
         
    def run_simulation(self, game, representation, N, W, Q, P, frozen=False):
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

                model = self.frozen if frozen else self.network
                model.eval()
                with torch.no_grad():   
                    prior_policy, v = model(
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

    def evaluate_model(self, game, representation): 
        frozen_team = random.randint(0, 1)
        pbar = trange(game.max_turns - 10, desc="    Eval-play progress", leave=False)

        player = game.get_turn(auto_play_bots=False)
        while not game.is_finished(): 
            if player == -1:
                game.next_turn()
                player = game.get_turn(auto_play_bots=False)
                continue

            if game.moves_count > (game.max_turns - 10): 
                break

            N, W, Q, P = {}, {}, {}, {}
            frozen = False if frozen_team != player else True
            for sim in range(self.mcts_simulations_eval): 
                self.run_simulation(game.copy(), representation.copy(), N, W, Q, P, frozen)

            moves, hashes = game.get_movements(include_hashes=True)

            visit_counts = np.array([N.get((player, hash_), 0) for hash_ in hashes], dtype=np.float32)
            adjusted = visit_counts ** (1 / self.tau)
            policy = adjusted / (adjusted.sum() + 1e-8)  # normalize and prevent divide-by-zero

            best_move_index = np.argmax(policy)
            move = moves[best_move_index]

            history_movement = game.make_move(move)
            representation.update_board(history_movement)

            game.next_turn()
            player = game.get_turn(auto_play_bots=False)

            pbar.update(1)

        winner = game.winner
        if winner != frozen_team and winner != -1: 
            return +1 
        return 0

    def update_frozen(self, wins):
        win_rate = wins / self.play_per_eval
        if win_rate > self.update_frozen_threshold: 
            print(f"Model has imporved! Win rate against frozen: {win_rate:.4f}")
            self.frozen.load_state_dict(self.network.state_dict())
            version = len(os.listdir(self.backups_path))  
            torch.save(self.network.state_dict(), f"{self.backups_path}/version_{version}.pt")
        else:
            print("Model has not improved")

    def learn(self, batch):
        # Unpack the batch of training examples
        player, states, valid_moves, target_policies, target_values = batch  # states ∈ GNN input, policies ∈ probabilities, values ∈ scalars
        player = torch.tensor(player, dtype=torch.long).to(device)
        states = torch.tensor(states, dtype=torch.float32).to(device)
        valid_moves = torch.tensor(valid_moves, dtype=torch.long).to(device)
        target_policies = torch.tensor(target_policies, dtype=torch.float32).to(device)
        target_values = torch.tensor(target_values, dtype=torch.float32).to(device)

        states_batch = self.representation.batch_to_pyg_data(states, device)

        # Forward pass through the network
        self.network.train()
        predicted_policies, predicted_values = self.network(
            x=states_batch.x,
            edge_index=states_batch.edge_index,
            move_index=valid_moves,
            player=player,
            batch=states_batch.batch,
        )

        # Compute losses
        value_loss = F.mse_loss(predicted_values, target_values)
        predicted_policies_log = F.log_softmax(predicted_policies, dim=1)
        policy_loss = F.kl_div(predicted_policies_log, target_policies, reduction='batchmean')

        # Total loss = value error + policy error
        total_loss = value_loss + policy_loss

        # Backpropagation step
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()

        return total_loss.detach().cpu().item()

    def plot_loss(self, iteration, losses):
        fig, ax = plt.subplots()
        ax.plot(losses, label="Loss per training step")
        ax.set_xlabel("Training step")
        ax.set_ylabel("Loss")
        ax.set_title(f"Loss Curve at Iteration {iteration}")
        ax.legend()

        os.makedirs(self.plots_path, exist_ok=True)
        filename = f"loss_plot_iter_{iteration}.png"
        full_path = os.path.join(self.plots_path, filename)
        fig.savefig(full_path)
        plt.close(fig)  

    def plot_avg_loss(self, avg_loss):
        """Plot and overwrite the average loss summary (single file)."""
        fig, ax = plt.subplots()
        ax.plot(avg_loss, marker='o', label="Average Loss")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Average Loss")
        ax.set_title("Average Loss Over Iterations")
        ax.legend()

        os.makedirs(self.plots_path, exist_ok=True)
        filename = "avg_loss.png"
        full_path = os.path.join(self.plots_path, filename)
        fig.savefig(full_path)
        plt.close(fig)
