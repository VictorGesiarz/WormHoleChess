from pydantic import BaseModel
from typing import List, Literal, Dict, Optional


class PlayerData(BaseModel):
    name: str
    index: int
    type: Literal["human", "random", "mcts", "mcts-parallel", "alphazero"]
    color: str

class TurnInfo(BaseModel):
    turn: int
    type: Literal['human', 'bot']
    validMoves: List[List[str]]
    moveCount: int
    player_killed: Optional[str] = None 
    player_won: Optional[str] = None
    game_state: Literal['playing', 'draw', 'checkmate', 'player_won'] = 'playing' # 'draw', 'checkmate'


class StartLocalGameRequest(BaseModel):
    players: List[PlayerData]
    programMode: Literal["layer", "matrix"]
    gameType: Literal["normal", "wormhole"]
    boardSize: Literal["small", "big"] | int
    initialPosition: Optional[str] = None

class StartGameResponse(BaseModel):
    gameId: str
    initialState: Dict
    turn: TurnInfo

class MoveRequest(BaseModel):
    gameId: str
    from_tile: str
    to_tile: str

class MoveResponse(BaseModel):
    state: Dict
    turn: TurnInfo
    moveDescription: str
    
class BotMoveRequest(BaseModel):
    gameId: str

class LoadGameResponse(BaseModel): 
    gameId: str
    gameType: str
    boardSize: str
    states: Dict
    playerCount: int
    turn: TurnInfo
    players: List[PlayerData]

class GameStoreRequest(BaseModel):
    name: str