from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict
import random
import time
import asyncio

from core.game import Game, Player, Bot
from core.constants import * 
from schemas.game import StartGameRequest
from services.user_service import user_dependency
from api.websockets.events import notify_all_players, notify_player

router = APIRouter(prefix="/game", tags=["game"])


games: Dict[str, Game] = {} # {'game_code': GameInstance}


def assign_colors(player_colors):
    available_colors = {'white', 'black', 'blue', 'red'}
    assigned_colors = [color for color in player_colors if color != 'None']
    remaining_colors = list(available_colors - set(assigned_colors))
    
    result = []
    for color in player_colors:
        if color == 'None':
            chosen_color = random.choice(remaining_colors)
            remaining_colors.remove(chosen_color)
            result.append(chosen_color)
        else:
            result.append(color)
    
    return result


def start_game(game_code, lobby):
    if game_code in games: 
        raise HTTPException(status_code=400, detail="Game already running")

    for game in games.values():
        for player_id in lobby['players'].keys():
            if game.is_player_in_game(player_id):
                raise HTTPException(status_code=400, detail="User already in an existing game")
    
    players = []
    assigned_colors = assign_colors(lobby['colors'])

    index = 0
    for player_id, player_info in lobby['players'].items(): 
        player = Player(
            id=player_id, 
            username=player_info['username'],
            socket=player_info['socket'],
            color=assigned_colors[index],
            time=lobby['time']
        )
        players.append(player)
        index += 1
    
    for bot_number, bot_info in lobby['bots'].items(): 
        bot = Bot(
            number=bot_number,
            username=bot_info['name'],
            color=assigned_colors[index],
        )
        players.append(bot)
        index += 1

    games[game_code] = Game(game_code, players)

    print("Game started correctly")


@router.get("/active-game")
def get_active_game(user: user_dependency):
    """
    Returns the active game for the given user, if they are in a game.
    """

    if not user:
        raise HTTPException(status_code=400, detail="User email is required")

    for game_id, game in games.items():
        if game.is_player_in_game(user.id):
            return {"game_id": game_id}
    
    return {"game_id": None}


@router.post("/leave/{game_code}")
def end_game(game_code: str, user: user_dependency):
    """ If a player wants to leave a game. """
    if game_code not in games:
        raise HTTPException(status_code=400, detail="Game not found")

    # del games[game_code]

    return {"game_id": game_code}


@router.post("/move/{game_code}")
def move(game_code: str, from_: str, to_: str, user: user_dependency): 
    """ Handles movement of pieces, respecting turns and players that are alive """
    if game_code not in games: 
        raise HTTPException(status_code=400, detail="Game not found")

    game = games[game_code]

    # if game.


async def check_game_timeouts():
    """Continuously checks all active games for player timeouts."""
    while True:
        for game_code, game in list(games.items()):
            if game.check_time_expired():
                print(f"Player {game.get_current_player().username} timed out. Forcing turn change.")
                game.force_turn_timeout()

            game.get_current_player().time_remaining -= 1 

        await asyncio.sleep(1)


# This wont work yet 
import asyncio
player_disconnect_timers = {}
async def handle_disconnect(game_code, player_id):
    await asyncio.sleep(30)  # Allow 30 seconds for reconnection
    if player_id not in games[game_code]:  # Check if they rejoined
        print(f"Player {player_id} did not reconnect, ending game.")
        del games[game_code]  # End the game