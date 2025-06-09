from fastapi import APIRouter

from app.schemas.local_game import StartLocalGameRequest, MoveRequest
from app.core.GameManager import GameManager

router = APIRouter(prefix="/game-local", tags=["game-local"])

games = GameManager()

@router.post("/start-local-game")
def start_local_game(payload: StartLocalGameRequest):
    return games.create_game(payload)

@router.post("/make-move")
def make_move(move: MoveRequest):
    return games.make_move(move)

@router.post("/reset-game")
def reset_game():
    return games.reset_game()

@router.post("/leave-game")
def leave_game(): 
    games.remove_game()