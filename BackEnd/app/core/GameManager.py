from fastapi import APIRouter, HTTPException
from uuid import uuid4

from app.schemas.local_game import (
    StartLocalGameRequest, 
    StartGameResponse,
    MoveRequest,
    MoveResponse,
    TurnInfo,
    BotMoveRequest,
    PlayerData,
    LoadGameResponse, 
    GameStoreRequest
)

import os
from engine.ChessFactory import ChessFactory


class GameManager: 
    def __init__(self):
        self.games = {}

    def _get_turn_info(self, game): 

        if not game.is_finished():
            while game.get_turn(auto_play_bots=False) == -1: 
                game.next_turn()


        valid_moves = []
        if not game.is_finished():
            valid_moves = game.get_movements()
        if game.program_mode == 'layer':
            valid_moves = [[m[0].name, m[1].name] for m in valid_moves]
            type = 'human' if game.players[game.turn].type == 'player' else 'bot'
        elif game.program_mode == 'matrix': 
            valid_moves = [game.board.get_names(move) for move in valid_moves]
            type = 'human' if game.players[game.turn]['opponent_type'] == 0 else 'bot'

        winner = game.winner()
        if winner != -1: 
            if game.program_mode == 'layer':
                player_won = game.players[winner].color
            elif game.program_mode == 'matrix':
                player_won = game.players[winner]['color']
        else:
            player_won = None

        return TurnInfo(
            turn=game.turn, 
            type=type,
            validMoves=valid_moves,
            moveCount=game.moves_count,
            player_killed=game.killed_player,
            player_won=player_won,
            game_state=game.game_state.name.lower()
        )

    def _get_move_description(self, game):
        piece, from_tile, to_tile = game.get_last_move()
        
        if game.number_of_players == 4:
            moveDescription = f'{piece}\n{from_tile}\n{to_tile}';
        else: 
            moveDescription = f'{piece} {from_tile}-{to_tile}';
        return moveDescription

    # ---------- public API ----------------------------------------------
    def create_game(self, payload: StartLocalGameRequest): 
        game_id = str(0) # str(uuid4())
        player_types = [p.type for p in payload.players]
        game = ChessFactory.create_game(
            player_data=ChessFactory.create_player_data(len(payload.players), player_types),
            program_mode=payload.programMode,
            game_mode=payload.gameType,
            size=(payload.boardSize, payload.boardSize),
            initial_positions=payload.initialPosition
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
        moveDescription = self._get_move_description(game)
        print(moveDescription)
        
        return MoveResponse(
            state={game.moves_count: game.get_state()}, 
            turn=turn,
            moveDescription=moveDescription
        )

    def make_move_bot(self, bot_move: BotMoveRequest): 
        game_id = bot_move.gameId
        if game_id not in self.games:
            raise HTTPException(status_code=404, detail="Game not found")

        game = self.games[game_id]

        if game.is_finished():
            raise HTTPException(status_code=400, detail="Game is already finished")
        game_movement = game.make_move_bot()
        game.next_turn()
        
        turn = self._get_turn_info(game)
        
        moveDescription = self._get_move_description(game)
        
        return MoveResponse(
            state={game.moves_count: game.get_state()}, 
            turn=turn,
            moveDescription=moveDescription
        )
    
    def store_game(self, data: GameStoreRequest): 
        ChessFactory.store_game(self.games['0'], data.name)

    def load_game(self, data: GameStoreRequest): 
        game, moves = ChessFactory.load_game(data.name)
        self.games['0'] = game

        states = {0: game.get_state()}

        for move in moves: 
            game.get_turn(auto_play_bots=False)
            game.make_move(move)
            game.next_turn()
            states[game.moves_count] = game.get_state()

        engines_map = {
            0: "human",
            1: "random",
            2: "mcts",
            3: "mcts-parallel",
            4: "alphazero",
        }

        turn_info = TurnInfo(
            turn=-1, 
            type='human',
            validMoves=[[]], 
            moveCount=game.moves_count, 
            game_state='checkmate', 
        )

        players = [
            PlayerData(
                name=f'Player {p['id']}',
                index=p['id'], 
                type=engines_map[p['opponent_type']], 
                color=p['color']
            )
            for p in game.players if p['color'] != 'none'
        ]

        return LoadGameResponse(
            gameId='0', 
            gameType=game.board.game_mode, 
            boardSize=str(game.board.size[0]), 
            states=states, 
            playerCount=game.number_of_players, 
            turn=turn_info, 
            players=players
        )
    