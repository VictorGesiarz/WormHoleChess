from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from jose import jwt, JWTError
from typing import Dict, List
import asyncio
import uuid
import time

from core.constants import * 
from schemas.game import StartGameRequest
from api.game import start_game
from services.user_service import user_dependency
from api.websockets.events import notify_all_players, notify_player


router = APIRouter(prefix="/lobby", tags=["lobby"])

# Store active lobbies
lobbies: Dict[str, Dict[str, Dict[str, str]]] = {}  
""" lobbies = {
    "game_code": {
		"host": "player_id",
		"players": {
			"player_id": {
                "username": "player_name",
                "socket": "WebSocket"
            },
        },
        "bots": {
            "bot_number": {
                "name": "bot_name",
                "difficulty": "easy"
            }
        },
        "expires_at": "timestamp", 
        "colors": List["color"],
        "time": int
    }
} """

player_lobby_map: Dict[str, str] = {}  # {player_id: game_code}


def generate_game_code() -> str:
    """Generates a unique game code of length 6."""
    return str(uuid.uuid4())[:6]

def get_bot_number(lobby) -> str:
    """Generates a unique bot name."""
    bots = lobby['bots']
    for number in range(1, 5):
        if number not in bots: 
            return number

async def remove_player_from_lobby(player_id: str):
    """Removes a player from their current lobby, notifying others if needed."""

    if player_id not in player_lobby_map:
        return

    game_code = player_lobby_map[player_id]

    if game_code in lobbies:
        lobby = lobbies[game_code]
        player = lobby['players'].get(player_id)

        if player:
            del lobby['players'][player_id] 

            # Notify remaining players
            await notify_all_players(lobby, message={"type": "player_removed", "username": player["username"]})

            if len(lobby['players']) == 0:
                del lobbies[game_code]

    # Remove player from tracking
    del player_lobby_map[player_id]


@router.post("/create")
async def create_lobby(user: user_dependency):
    """Creates a new game lobby and adds the creator as the first player."""
    await remove_player_from_lobby(user.id)  # Ensure player is not in another lobby
    game_code = generate_game_code()

    if game_code not in lobbies:
        lobbies[game_code] = {'host': user.id, 'players': {}, 'bots': {}, 'expires_at': time.time() + LOBBY_EXPIRATION_TIME, "time": DEFAULT_GAME_TIME}
    else: 
        raise HTTPException(status_code=400, detail="Game code already exists")

    lobbies[game_code]['players'][user.id] = {"username": user.username, "socket": None}
    player_lobby_map[user.id] = game_code

    return {"game_code": game_code}


@router.post("/join/{game_code}")
async def join_lobby(game_code: str, user: user_dependency):
    """Allows a player to join a lobby using a game code."""
    if game_code not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")

    if len(lobbies[game_code]['players']) + len(lobbies[game_code]['bots']) >= 4:
        raise HTTPException(status_code=400, detail="Lobby is full")

    for player in lobbies[game_code]['players'].values():
        if player["username"] == user.username:
            raise HTTPException(status_code=400, detail="User already in the lobby")

    await remove_player_from_lobby(user.id) 

    lobbies[game_code]['players'][user.id] = {"username": user.username, "socket": None}
    player_lobby_map[user.id] = game_code

    await notify_all_players(lobbies[game_code], message={"type": "player_joined", "username": user.username})

    return {"message": "Player joined"}


@router.post("/{game_code}/remove_player")
async def remove_player(game_code: str, player_name: str, user: user_dependency):
    """ Removes a player from the lobby. But this function does not remove the lobby if there are only bots left. """

    if game_code not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")

    if user.id != lobbies[game_code]['host']:
        raise HTTPException(status_code=403, detail="Only the host can remove players")

    if player_name.startswith("Bot_"):
        bot_number = next((bot_number for bot_number, bot_info in lobbies[game_code]['bots'].items() if bot_info["name"] == player_name), None)

        if bot_number not in lobbies[game_code]['bots']:
            raise HTTPException(status_code=404, detail="Bot not found")

        del lobbies[game_code]['bots'][bot_number]

    else: 
        player_id = next((player_id for player_id, player_info in lobbies[game_code]['players'].items() if player_info["username"] == player_name), None)

        if player_id not in lobbies[game_code]['players']:
            raise HTTPException(status_code=404, detail="Player not found")

        if player_id == user.id: 
            raise HTTPException(status_code=403, detail="Host cannot remove themselves")

        player = lobbies[game_code]['players'][player_id]
        await remove_player_from_lobby(player_id)
        await notify_player(player, message={"type": "you_are_removed", "username": player["username"]})

        del lobbies[game_code]['players'][player_id]

    await notify_all_players(lobbies[game_code], message={"type": "player_removed", "username": player_name})

    return {"message": "Player removed"}


@router.post("/{game_code}/add_bot")
async def add_bot(game_code: str, user: user_dependency):
    """Adds a bot to the lobby."""
    if game_code not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")

    if user.id != lobbies[game_code]['host']:
        raise HTTPException(status_code=403, detail="Only the host can add bots")

    if len(lobbies[game_code]['players']) + len(lobbies[game_code]['bots']) >= 4:
        raise HTTPException(status_code=400, detail="Lobby is full")

    bot_number = get_bot_number(lobbies[game_code])
    bot_name = f"Bot_{bot_number}"
    lobbies[game_code]['bots'][bot_number] = {"name": bot_name, "difficulty": "normal"}

    await notify_all_players(lobbies[game_code], message={"type": "bot_added", "bot_name": bot_name})

    return {"message": f"Added bot {bot_name}"}


@router.post("/{game_code}/change_bot_difficulty")
async def change_bot_difficulty(game_code: str, user: user_dependency, bot_name: str, difficulty: str):
    """Changes the difficulty of a bot."""
    if game_code not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")

    if user.id != lobbies[game_code]['host']:
        raise HTTPException(status_code=403, detail="Only the host can change bot difficulty")

    if bot_name not in lobbies[game_code]['bots']:
        raise HTTPException(status_code=404, detail="Bot not found")

    lobbies[game_code]['bots'][bot_name]['difficulty'] = difficulty
    return {"message": "Bot difficulty changed"}


@router.get("/{game_code}/players")
async def get_lobby_players(game_code: str, user: user_dependency):
    """Returns the list of players' usernames in a lobby."""
    if game_code not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    if user.id not in lobbies[game_code]['players']:
        raise HTTPException(status_code=403, detail="You are not in this lobby")

    players = [player_info["username"] for player_info in lobbies[game_code]['players'].values()]
    bots = [bot_info["name"] for bot_info in lobbies[game_code]['bots'].values()]
    return {"players": players + bots}


@router.post("/start/{game_code}")
async def start_game_lobby(game_code: str, colors: StartGameRequest, user: user_dependency):
    """Starts the game if there are exactly 2 players."""
    
    print(lobbies)

    if game_code not in lobbies:
        print("HERE")
        raise HTTPException(status_code=404, detail="Lobby not found")

    if user.id != lobbies[game_code]['host']:
        print("HERE1")
        raise HTTPException(status_code=403, detail="Only the host can start the game")

    if len(lobbies[game_code]['players']) + len(lobbies[game_code]['bots']) != 4:
        print("HERE2")
        raise HTTPException(status_code=400, detail="Game cannot start until there are exactly 4 players or bots")

    colors_set = {color for color in colors.colors if color != 'None'}

    if any(color not in TEAMS for color in colors_set):
        raise HTTPException(status_code=400, detail="Unexpected color found")

    if len(colors_set) + colors.colors.count('None') != 4:
        raise HTTPException(status_code=400, detail="Invalid colors selected")

    # Notify both players via WebSockets
    await notify_all_players(lobbies[game_code], message={"type": "game_start", "game_code": game_code})

    # Start the game
    lobbies[game_code]['colors'] = colors.colors
    start_game(game_code, lobbies[game_code])
    del lobbies[game_code]
    
    return {"message": "Game started"}


async def remove_expired_lobbies():
    """Removes lobbies that have expired."""
    while True:
        current_time = time.time()
        expired_lobbies = [code for code, lobby in lobbies.items() if lobby["expires_at"] < current_time]

        for game_code in expired_lobbies:
            print(f"Lobby {game_code} expired and is being removed.")
            await notify_all_players(lobbies[game_code], message={"type": "lobby_expired"})
            del lobbies[game_code]

        await asyncio.sleep(60 * 5)