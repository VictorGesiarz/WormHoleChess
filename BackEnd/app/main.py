from fastapi import FastAPI
from app.api import routes as chess_router

app = FastAPI(title="Chess Game API")

# Include routers for different versions
app.include_router(chess_router.chess_logic, prefix="/chess-logic", tags=["chess"])