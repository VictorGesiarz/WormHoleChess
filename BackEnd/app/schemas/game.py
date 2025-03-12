
from pydantic import BaseModel
from typing import Optional, List, Dict


class Player(BaseModel):
    id: str
    email: str


class StartGameRequest(BaseModel):
    players: List[str]