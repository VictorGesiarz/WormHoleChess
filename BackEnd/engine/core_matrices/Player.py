from dataclasses import dataclass


@dataclass
class Player: 
    id: int
    team: int
    alive: bool
    is_bot: bool 