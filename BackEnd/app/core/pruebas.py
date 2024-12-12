from chess_logic import *
from pieces import * 


def add_neighbors(tile, up_left=None, up=None, up_right=None, 
                        left=None, right=None, 
                        down_left=None, down=None, down_right=None,
                        additional_straight=None, additional_diag=None,
                        relations=True): 
    neighbors = {
        D.UP_LEFT: up_left, D.UP: up, D.UP_RIGHT: up_right,
        D.LEFT: left, D.RIGHT: right,
        D.DOWN_LEFT: down_left, D.DOWN: down, D.DOWN_RIGHT: down_right
    }
 
    if tile.pentagon:
        neighbors[D.ADDITIONAL_STRAIGHT] = additional_straight
        neighbors[D.ADDITIONAL_DIAGONAL] = additional_diag

    tile.set_neighbors(neighbors)
	
    if relations: add_relations(tile)


def add_relations(tile, up_left=[D.UP_RIGHT], up=[D.DOWN], up_right=[D.UP_LEFT], 
                        left=[D.RIGHT], right=[D.LEFT], 
                        down_left=[D.DOWN_RIGHT], down=[D.UP], down_right=[D.DOWN_LEFT],
                        additional_straight=[D.DOWN, D.LEFT], additional_diag=[D.DOWN_LEFT]):
    relations = {
        D.UP_LEFT: up_left, D.UP: up, D.UP_RIGHT: up_right,
        D.LEFT: left, D.RIGHT: right,
        D.DOWN_LEFT: down_left, D.DOWN: down, D.DOWN_RIGHT: down_right
    }

    if tile.pentagon: 
        relations[D.ADDITIONAL_DIAGONAL] = additional_diag
        relations[D.ADDITIONAL_STRAIGHT] = additional_straight
	
    tile.set_relations(relations)



def create_tiles(): 
    a1, a2, a3, a4 = Tile("a1", "T"), Tile("a2", "T"), Tile("a3", "T"), Tile("a4", "T")
    b1, b2, b3, b4= Tile("b1", "T"), Tile("b2", "T"), Tile("b3", "T"), Tile("b4", "T")
    c1, c2, c3, c4 = Tile("c1", "T"), Tile("c2", "T"), Tile("c3", "T", pentagon=True), Tile("c4", "T")
    d1, d2, d3, d4 = Tile("d1", "T"), Tile("d2", "T"), Tile("d3", "T"), Tile("d4", "T", loop=True)
    d4_1, d4_2 = Tile("d4_1", "T", loop=True), Tile("d4_2", "T", loop=True) 

    add_neighbors(a1, up=a2, up_right=b2, right=b1)
    add_neighbors(a2, up=a3, down=a1, up_right=b3, right=b2, down_right=b1)
    add_neighbors(a3, up=a4, down=a2, up_right=b4, right=b3, down_right=b2)
    add_neighbors(a4, down=a3, right=b4, down_right=b3)

    add_neighbors(b1, left=a1, up_left=a2, up=b2, up_right=c2, right=c1)
    add_neighbors(b2, left=a2, up_left=a3, up=b3, up_right=c3, right=c2, down_right=c1, down=b1, down_left=a1)
    add_neighbors(b3, left=a3, up_left=a4, up=b4, up_right=c4, right=c3, down_right=c2, down=b2, down_left=a2)
    add_neighbors(b4, left=a4, right=c4, down_right=c3, down=b3, down_left=a3)

    add_neighbors(c1, left=b1, up_left=b2, up=c2, up_right=d2, right=d1)
    add_neighbors(c2, left=b2, up_left=b3, up=c3, up_right=d3, right=d2, down_right=d1, down=c1, down_left=b1)
    add_neighbors(c3, left=b3, up_left=b4, up=c4, up_right=d4, right=d3, down_right=d2, down=c2, down_left=b2, additional_straight=d4_1, additional_diag=d4_2, relations=False)
    add_relations(c3, down=[D.UP, D.ADDITIONAL_STRAIGHT], left=[D.RIGHT, D.ADDITIONAL_STRAIGHT],
                      down_left=[D.ADDITIONAL_DIAGONAL, D.UP_LEFT], 
                      additional_diag=[D.DOWN_LEFT], additional_straight=[D.DOWN, D.LEFT])
    add_neighbors(c4, left=b4, right=d4_2, down_right=d4_1, down=c3, down_left=b3)

    add_neighbors(d1, left=c1, up_left=c2, up=d2)
    add_neighbors(d2, left=c2, up_left=c3, up=d3, down=d1, down_left=c1)
    add_neighbors(d3, left=c3, up_left=d4_1, up=d4, down=d2, down_left=c2)
    add_neighbors(d4, left=d4_1, down=d3, down_left=c3)
    add_neighbors(d4_1, left=d4_2, right=d4, down=c3, down_left=c4, down_right=d3)
    add_neighbors(d4_2, left=c4, down_left=c3, down=d4_1)

    tiles = [a1, a2, a3, a4, b1, b2, b3, b4, c1, c2, c3, c4, d1, d2, d3, d4, d4_1, d4_2]
    return tiles


def print_neighbors(neighbors):
    for direction, neighbor in neighbors.items():
        print(direction, neighbor)

def create_board():
    b = Board() 
    b.check_size()

    # print_neighbors(b.tiles['e4_T'].neighbors)

    tower = Tower(b.tiles['c1_T'], 1)
    bishop = Bishop(b.tiles['a1_T'], 0)
    king = King(b.tiles['b3_T'], 0)
    knight = Knight(b.tiles['d4_T'], 0)
    b.add_pieces([tower, bishop, king, knight])

    positions = knight.get_movements()
    for pos in positions: 
    	print(pos)


create_board()

