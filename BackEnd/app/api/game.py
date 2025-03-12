from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict

from core.game import Game
from schemas.game import StartGameRequest
from services.user_service import user_dependency
from api.websockets.events import notify_all_players, notify_player


router = APIRouter(prefix="/game", tags=["game"])


games: Dict[str, Game] = {}  # {game_code: GameInstance}


def start_game(game_code, lobby):
    players = lobby['players']
    bots = lobby['bots']
    games[game_code] = Game(game_code, players)


@router.get("/active-game")
def get_active_game(user: user_dependency):
    """
    Returns the active game for the given user, if they are in a game.
    """
    
    print(games)

    if not user:
        raise HTTPException(status_code=400, detail="User email is required")

    for game_id, game in games.items():
        print(game)
        if game.is_player_in_game(user.name):
            return {"game_id": game_id}
    
    return {"game_id": None}


# @router.post("/start/{game_code}")
# def start_game(game_code: str, request: StartGameRequest):
#     """Starts a game using the existing lobby code."""
#     if len(request.players) != 4:
#         raise HTTPException(status_code=400, detail="There must be 4 players to start a game")

#     if game_code in games:
#         raise HTTPException(status_code=400, detail="Game already started for this lobby")

#     games[game_code] = Game(game_code, request.players)

#     return {"game_id": game_code}


@router.post("/end/{game_code}")
def end_game(game_code: str, user: user_dependency):
    """Ends a game using the existing lobby code."""
    if game_code not in games:
        raise HTTPException(status_code=400, detail="Game not found")

    del games[game_code]



    return {"game_id": game_code}


# This wont work yet 
import asyncio
player_disconnect_timers = {}
async def handle_disconnect(game_code, player_id):
    await asyncio.sleep(30)  # Allow 30 seconds for reconnection
    if player_id not in games[game_code]:  # Check if they rejoined
        print(f"Player {player_id} did not reconnect, ending game.")
        del games[game_code]  # End the game