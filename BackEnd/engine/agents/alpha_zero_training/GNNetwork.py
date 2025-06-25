import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Linear, LayerNorm, BatchNorm1d, Dropout
from torch_geometric.nn import GINConv, global_mean_pool

class AlphaZeroGNN(torch.nn.Module):
    def __init__(self, node_feat_dim, hidden_dim):
        super().__init__()
        self.input_proj = nn.Linear(node_feat_dim, hidden_dim)

        # GIN layers for node embedding
        self.gnn1 = GINConv(Linear(hidden_dim, hidden_dim))
        self.norm1 = LayerNorm(hidden_dim)

        self.gnn2 = GINConv(Linear(hidden_dim, hidden_dim))
        self.norm2 = LayerNorm(hidden_dim)

        self.gnn3 = GINConv(Linear(hidden_dim, hidden_dim))
        self.norm3 = LayerNorm(hidden_dim)

        # Fully connected layers for global board embedding (value head)
        self.fc1 = Linear(hidden_dim, hidden_dim)
        self.bn1 = BatchNorm1d(hidden_dim)
        self.drop1 = Dropout(0.3)

        self.fc2 = Linear(hidden_dim, hidden_dim)
        self.bn2 = BatchNorm1d(hidden_dim)
        self.drop2 = Dropout(0.3)

        # Policy head: maps edge embeddings to logits for moves
        self.policy_edge_mlp = torch.nn.Sequential(
            Linear(2 * hidden_dim, hidden_dim),  # concatenate source+target node embeddings
            torch.nn.ReLU(),
            Linear(hidden_dim, 1)  # output logit per edge
        )

        # Value head: scalar evaluation of the position
        self.value_head = Linear(hidden_dim, 1)

    def forward(self, x, edge_index, move_index, player, batch=None):
        # x: [num_nodes, node_feat_dim]
        # edge_index: [2, num_edges] - adjacency (for message passing)
        # batch: [num_nodes] - for global pooling across graphs
        # move_index: [2, num_legal_moves] - (source, target) node indices for legal moves

        device = x.device 
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=device)  
        else:
            batch = batch.to(device)  

        # Add Current Player to node embedings 
        player_tensor = F.one_hot(player, num_classes=2).float()  
        player_per_node = player_tensor[batch]  
        x = torch.cat([x, player_per_node], dim=1)

        x = self.input_proj(x)  # shape: (num_nodes, hidden_dim)

        residual = x
        x = F.relu(self.norm1(self.gnn1(x, edge_index)))
        x = F.relu(self.norm2(self.gnn2(x, edge_index)))
        x = self.norm3(self.gnn3(x, edge_index))
        x += residual
        x = F.relu(x)

        # Value head (global evaluation)
        graph_embed = global_mean_pool(x, batch)
        v = self.drop1(F.relu(self.bn1(self.fc1(graph_embed))))
        v = self.drop2(F.relu(self.bn2(self.fc2(v))))
        value = torch.tanh(self.value_head(v))  # scalar output per board
        predicted_values = value.squeeze(-1)

        # Policy head (predict scores for legal moves only)
        if move_index.dim() == 2:
            # no batch: add batch dim = 1
            move_index = move_index.unsqueeze(0)
        
        B, M, _ = move_index.shape

        policy_logits_per_graph = []
        for i in range(B):
            moves_i = move_index[i]  
            valid_i = ~(moves_i == -1).any(dim=1)  

            src = moves_i[valid_i, 0]
            tgt = moves_i[valid_i, 1]

            edge_feat = torch.cat([x[src], x[tgt]], dim=1)          
            logits_i  = self.policy_edge_mlp(edge_feat).squeeze(-1) 

            full_logits = torch.full((M,), -1e9, device=device)  
            full_logits[valid_i] = logits_i
            policy_logits_per_graph.append(full_logits)
        
        policy_logits = torch.stack(policy_logits_per_graph, dim=0)

        return policy_logits, predicted_values
