import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import users, lobby, game
from api.websockets import connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the background task for cleaning up expired lobbies."""
    lobby_task = asyncio.create_task(lobby.remove_expired_lobbies())  
    game_task = asyncio.create_task(game.check_game_timeouts())  
    yield  
    lobby_task.cancel()
    game_task.cancel()


app = FastAPI(title="Chess Game API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include user-related routes
app.include_router(users.router)
app.include_router(lobby.router)
app.include_router(game.router)
app.include_router(connection.router)
