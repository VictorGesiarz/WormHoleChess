import faulthandler
import sys
faulthandler.enable(sys.stderr)

from engine.ChessFactory import ChessFactory
from engine.agents.alpha_zero_training.AlphaZero import AlphaZero


def train(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=2), 
        program_mode="matrix",
        game_mode="normal",
        size=(6, 6),
        max_turns=60,
    )
    representation = ChessFactory.create_representation(game)

    network = AlphaZero.load_network('./engine/agents/alpha_zero_training/models/backups_0/version_8.pt')
    trainer = AlphaZero(game, representation, network)

    trainer.train()
    

if __name__ == "__main__": 
    train()