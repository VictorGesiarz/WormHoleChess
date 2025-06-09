from fastapi import APIRouter, HTTPException
from uuid import uuid4

from app.schemas.local_game import (
    StartLocalGameRequest, 
    StartGameResponse,
    MoveRequest,
    MoveResponse,
    TurnInfo
)

from engine.core.ChessFactory import ChessFactory


class GameManager: 
    def __init__(self):
        self.games = {}

    def _get_turn_info(self, game): 

        if not game.is_finished():
            while game.get_turn(auto_play_bots=False) == -1: 
                game.next_turn()

        valid_moves = game.get_movements()
        if game.program_mode == 'layer':
            valid_moves = [[m[0].name, m[1].name] for m in valid_moves]
            type = 'human' if game.players[game.turn].type == 'player' else 'bot'
        elif game.program_mode == 'matrix': 
            valid_moves = [game.board.get_names(move) for move in valid_moves]
            type = 'human' if game.players[game.turn]['opponent_type'] == 'human' else 'bot'

        return TurnInfo(
            turn=game.turn, 
            type=type,
            validMoves=valid_moves,
            moveCount=game.moves_count
        )

    # ---------- public API ----------------------------------------------
    def create_game(self, payload: StartLocalGameRequest): 
        game_id = str(0) # str(uuid4())
        player_types = [p.type for p in payload.players]
        game = ChessFactory.create_game(
            player_data=ChessFactory.create_player_data(len(payload.players), player_types),
            program_mode=payload.programMode,
            game_mode=payload.gameType,
            size=payload.boardSize,
            # initial_positions= # How do we handle this?
        )
        self.games[game_id] = game

        return StartGameResponse(
            gameId=game_id, 
            initialState={game.moves_count: game.get_state()}, 
            turn=self._get_turn_info(game)
        )
    
    def make_move(self, move: MoveRequest): 
        if move.gameId not in self.games:
            raise HTTPException(status_code=404, detail="Game not found")

        game = self.games[move.gameId]
        try:
            if game.is_finished():
                raise HTTPException(status_code=400, detail="Game is already finished")
            if not game.valid_move(move.from_tile, move.to_tile): 
                raise HTTPException(status_code=400, detail="Invalid move")
            game_movement = game.translate_movement(move.from_tile, move.to_tile)
            game.make_move(game_movement)
            game.next_turn()
        
        except Exception as e:
            raise HTTPException(status_code=400, detail='Invalid move: ' + str(e))
        
        turn = self._get_turn_info(game)
        winner = game.winner()
        if winner != -1: 
            if game.program_mode == 'layer':
                player_won = game.players[winner].color
            elif game.program_mode == 'matrix':
                player_won = game.players[winner]['color']
        else:
            player_won = None
        
        return MoveResponse(
            state={game.moves_count: game.get_state()}, 
            turn=turn, 
            player_killed=game.killed_player,
            player_won=player_won,
            game_finished=game.game_state.name.lower()
        )
