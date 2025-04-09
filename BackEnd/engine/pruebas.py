from engine.core.base.Board import *
from engine.core.base.Pieces import * 


def create_board():
    b = Board() 
    b.check_size()

    # print_neighbors(b.tiles['e4_T'].neighbors)

    player = Player(0, "player")
    tower1 = Tower(b['a8_T'], player)
    tower2 = Tower(b['h8_T'], player)
    # bishop = Bishop(b.tiles['b4_T'], 1)
    # knight = Knight(b.tiles['e4_2_T'], 0)
    # queen = Queen(b.tiles['f3_T'], 0)
    
    # implemented but no taking into account checks, and possible checks 
    king = King(b.tiles['e8_T'], player)
    
    # pawn = Pawn(b.tiles['a5_T'], 0)
    # print(pawn.type)

    positions = king.get_movements()
    for pos in positions: 
    	print(pos)


create_board()

