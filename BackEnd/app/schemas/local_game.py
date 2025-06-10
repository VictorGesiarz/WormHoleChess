from pydantic import BaseModel
from typing import List, Literal, Dict, Optional


class PlayerData(BaseModel):
    name: str
    index: int
    type: Literal["human", "random", "mcts", "alphazero"]
    color: str

class TurnInfo(BaseModel):
    turn: int
    type: Literal['human', 'bot']
    validMoves: List[List[str]]
    moveCount: int

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
    player_killed: Optional[str] = None 
    player_won: Optional[str] = None
    game_state: str = 'playing' # 'draw', 'checkmate'
