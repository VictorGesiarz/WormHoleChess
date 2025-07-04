from enum import Enum

TEAMS = ['white', 'black', 'blue', 'red']

COLOR_TO_NUMBER = {
    "white": 0,
    "black": 1,
    "blue": 2, 
    "red": 3
}

NUMBER_TO_COLOR = {
    0: "white", 
    1: "black", 
    2: "blue",
    3: "red"
}

LOBBY_EXPIRATION_TIME = 60 * 10

DEFAULT_GAME_TIME = 60 * 10

PARAMETERS = {
    'cast_from_king': True, 
    'can_eat_dead': True, 
}


MAX_MOVES_WITHOUT_CAPTURE = 20

class GameState(Enum): 
    PLAYING = 0
    PLAYER_WON = 1
    DRAW = 2