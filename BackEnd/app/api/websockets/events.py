from typing import Dict
import asyncio


async def notify_all_players(lobby, message: Dict) -> None:
    tasks = [player["socket"].send_json(message) for player in lobby['players'].values() if player["socket"]]
    await asyncio.gather(*tasks, return_exceptions=True)

async def notify_player(player, message: Dict) -> None:
    """Notifies a single player in a lobby."""
    ws = player["socket"]
    if ws is not None:
        try:
            await ws.send_json(message)
        except RuntimeError:
            pass