import numpy as np 


class AlphaZeroReplayBuffer:
    def __init__(self, capacity, obs_shape, action_space_size):
        self.capacity = capacity
        self.ptr = 0
        self.size = 0

        self.player_buf = np.zeros(capacity, dtype=np.uint8)
        self.obs_buf = np.zeros((capacity, *obs_shape), dtype=np.uint8)
        self.moves_buf = np.full((capacity, action_space_size, 2), fill_value=-1, dtype=np.int16)
        self.policy_buf = np.full((capacity, action_space_size), fill_value=0, dtype=np.float32) # Should be the number of edges in the base board
        self.value_buf = np.zeros(capacity, dtype=np.int8) 

    def put(self, player, obs, moves, policy, value):
        self.player_buf[self.ptr] = player
        self.obs_buf[self.ptr] = obs
        self.moves_buf[self.ptr][:] = -1
        self.moves_buf[self.ptr][:len(moves)] = moves
        self.policy_buf[self.ptr][:] = 0 
        self.policy_buf[self.ptr][:len(policy)] = policy 
        self.value_buf[self.ptr] = value

        self.ptr = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def get(self, batch_size):
        if self.size < batch_size: 
            return None 
        
        idxs = np.random.choice(self.size, batch_size, replace=False)
        return (
            self.player_buf[idxs], 
            self.obs_buf[idxs],
            self.moves_buf[idxs], 
            self.policy_buf[idxs],
            self.value_buf[idxs],
        )

    def __len__(self):
        return self.size
    