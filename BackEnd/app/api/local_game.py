from fastapi import APIRouter
import os

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

@router.get("/get-possible-positions")
def get_possible_positions(): 
    """ Read available files of positions in the folder """
    folder_path = './engine/core/configs/tests/'
    files = os.listdir(folder_path)

    player_counts = [2, 4]
    sizes = [4, 5, 6, 7, 8]
    modes = ['normal', 'wormhole']

    positions = {}
    for p in player_counts: 
        for s in sizes: 
            for m in modes: 
                if s not in [6, 8] and m == 'wormhole': 
                    continue
                if p == 4 and m == 'normal': 
                    continue
                
                name = f'{p}_{s}x{s}_{m}'
                if name not in positions:
                    positions[name] = ['default']

                for f in files: 
                    if name in f: 
                        position_name = f.split('-')[1].split('.')[0]
                        positions[name].append(position_name)

    return positions