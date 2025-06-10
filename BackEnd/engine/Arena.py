from typing import List

from engine.agents.Agent import Agent
from engine.core.Game import Game
from engine.core.GameMatrices import GameMatrices

class Arena: 
    def __init__(self, players: List[Agent], env: Game | GameMatrices) -> None:
        self.players = players
        self.env = env

    def play(self): 
        self.env.reset()
    
        turn = self.env.get_turn()
        while True: 
            player = self.players[turn]
            action = player.compute_action(self.env)
            self.env.make_move(action)

            if self.env.is_finished(): 
                return 
            
            self.env.next_turn()
            self.env.get_turn()
            