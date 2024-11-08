from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

chess_logic = APIRouter()


class ChessMoveRequest(BaseModel):
    piece: str
    position: str

def is_valid_position(position):
    # Validate position format (e.g., "e2")
    return len(position) == 2 and position[0] in 'abcdefgh' and position[1] in '12345678'


@chess_logic.post("/legal_moves/")
async def legal_moves(request: ChessMoveRequest):
    if not is_valid_position(request.position):
        raise HTTPException(status_code=400, detail="Invalid position format.")
    moves = get_legal_moves(request.piece, request.position)
    return {"legal_moves": moves}