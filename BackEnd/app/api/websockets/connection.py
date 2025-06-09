from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from jose import JWTError

from app.db.database import db_dependency
from app.services.user_service import get_current_user
from app.api.lobby import lobbies, player_lobby_map, remove_player_from_lobby


router = APIRouter(prefix="/ws", tags=["websockets"])

@router.websocket("/{game_code}")
async def websocket_endpoint(websocket: WebSocket, game_code: str, db: db_dependency):
    """Handles WebSocket authentication and communication."""
    
    await websocket.accept()  # Accept connection first
    
    # Wait for the first message (should contain the token)
    try:
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")

        if not token:
            await websocket.send_json({"type": "auth_failed"})
            await websocket.close()
            return

        # Verify token and get user info
        try:
            user = get_current_user(token, db)
            player_id = user.id
        except JWTError:
            await websocket.send_json({"type": "auth_failed"})
            await websocket.close()
            return

        # Ensure player is in the correct lobby
        if game_code not in lobbies or player_id not in lobbies[game_code]['players']:
            await websocket.send_json({"type": "auth_failed"})
            await websocket.close()
            return

        # Store the WebSocket connection
        lobbies[game_code]['players'][player_id]["socket"] = websocket
        await websocket.send_json({"type": "auth_success"})

        # Handle real-time messages
        try:
            while True:
                data = await websocket.receive_text()
                for _, player_info in lobbies[game_code]['players'].items():
                    ws = player_info["socket"]
                    if ws != websocket:
                        await ws.send_text(data)

        except WebSocketDisconnect:
            await remove_player_from_lobby(player_id)

    except Exception:
        await websocket.close()