

class GameManager:
	def __init__(self) -> None:
		pass


class Game:
	def __init__(self) -> None:
		pass


class Player:
    def __init__(self, player_id, name, color):
        self.player_id = player_id
        self.name = name
        self.color = color
        self.pieces = []  # List of Piece instances
        self.is_in_check = False

    def lose_piece(self, piece):
        self.pieces.remove(piece)