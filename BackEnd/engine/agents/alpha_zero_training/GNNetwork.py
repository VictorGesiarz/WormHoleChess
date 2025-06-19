import torch
import torch.nn.functional as F
from torch.nn import Linear, LayerNorm, BatchNorm1d, Dropout
from torch_geometric.nn import GINConv, global_mean_pool

class AlphaZeroGNN(torch.nn.Module):
    def __init__(self, node_feat_dim, hidden_dim):
        super().__init__()
        # GIN layers for node embedding
        self.gnn1 = GINConv(Linear(node_feat_dim, hidden_dim))
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

    def forward(self, x, edge_index, batch):
        # x: [num_nodes, node_feat_dim]
        # edge_index: [2, num_edges]
        # batch: [num_nodes], to aggregate nodes belonging to the same graph

        residual = x
        x = F.relu(self.norm1(self.gnn1(x, edge_index)))
        x = F.relu(self.norm2(self.gnn2(x, edge_index)))
        x = self.norm3(self.gnn3(x, edge_index))
        x += residual
        x = F.relu(x)

        # Value head: global graph embedding -> scalar
        graph_embed = global_mean_pool(x, batch)  # [num_graphs, hidden_dim]
        v = self.drop1(F.relu(self.bn1(self.fc1(graph_embed))))
        v = self.drop2(F.relu(self.bn2(self.fc2(v))))
        value = torch.tanh(self.value_head(v))  # [-1,1]

        # Policy head: compute logits for each edge (move)
        # Gather source and target node embeddings for each edge
        source_nodes = edge_index[0]  # indices of source nodes per edge
        target_nodes = edge_index[1]  # indices of target nodes per edge

        source_embed = x[source_nodes]  # [num_edges, hidden_dim]
        target_embed = x[target_nodes]  # [num_edges, hidden_dim]

        edge_embed = torch.cat([source_embed, target_embed], dim=1)  # [num_edges, 2*hidden_dim]
        policy_logits = self.policy_edge_mlp(edge_embed).squeeze(-1)  # [num_edges]

        return policy_logits, value
