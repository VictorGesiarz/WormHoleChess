from engine.core.base.Board import *
from engine.core.base.Pieces import * 
from engine.core.Game import Game

from engine.core.layer.LayerBoard import * 
from engine.core.layer.LayerTile import * 
from engine.core.layer.LayerPieces import * 

from engine.core.ChessFactory import ChessFactory


def create_board(): 
    b = Board()
    p1 = Player(0)
    king = King(b['c3_T'], p1)
    print(king.get_pawn_possible_atacks())

# create_board()


def check_check(): 
    board = Board()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players)

    pieces = [
        King(board['a2_T'], p1),
        Pawn(board['b2_T'], p1),
        Tower(board['h2_T'], p2) # The tower should not allow the king to move 
    ]

    moves = game.get_movements()
    print(moves)


def check_mate(): 
    board = Board()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players, 0)

    pieces = [
        King(board['a3_T'], p1),
        Tower(board['c4_T'], p2),
        Tower(board['h2_T'], p2), 
        Tower(board['b3_B'], p2), 
        King(board['h8_T'], p2)
    ]

    moves = game.get_movements()
    for move in moves: 
        if move[0] == 'b3_B': 
            print(move[1])
    print(moves)


def stale_mate():
    board = Board()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players)

    pieces = [
        King(board['a1_T'], p1),
        Tower(board['b4_T'], p2),
        Tower(board['d2_T'], p2), 
    ]

    moves = game.get_movements()
    print(moves)


def eat(): 
    board = Board()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players)

    pieces = [
        King(board['a1_T'], p1),
        Pawn(board['a2_T'], p1),
        Tower(board['b1_T'], p1), # If we put a tower the tower can save the king by eating the pawn. If we put a bishop its checkmate
        Pawn(board['b2_T'], p2), # Pawn making check, only option would be to eat the pawn to savehimself. 
        Tower(board['b4_T'], p2) # Tower protecting the pawn, should me check mate 
    ]

    print(game.is_in_check(game.players[0]))
    moves = game.get_movements()
    print(moves)


def castle(): 
    board = Board()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players)

    pieces = [
        King(board['e1_T'], p1),
        Tower(board['a1_T'], p1),
        Tower(board['h1_T'], p1),
        # Bishop(board['c1_T'], p1), # This should block the middle tile and not allow the castle. 
        # Bishop(board['f1_T'], p1), # This also blocks the middle tile. 
        Tower(board['d3_T'], p2), # This should not allow the castle because it checks one of the middle tiles. 
        # Tower(board['e3_T'], p2), # This should not allow castle because king is in check
    ]

    moves = game.get_movements()
    print(moves)


check_check()
check_mate()
stale_mate()
eat()
castle()


# - - - - - - - - - - - - - - - - - - - - - - Layer Board - - - - - - - - - - - - - - - - - - - - - - - - 
print("\nLAYER BOARD TESTS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")

def create_layer_board(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=4), 
        mode="layer",
        size="big",
        # initial_positions='./engine/core/assets/4 pieces.json'
    )
    print(game.get_movements())

# create_layer_board()


def check_check_layer(): 
    board = LayerBoard()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players)

    pieces = [
        LayerKing(board['a2_T'], p1),
        LayerPawn(board['b2_T'], p1),
        LayerTower(board['h2_T'], p2) # The tower should not allow the pawn to move 
    ]

    moves = game.get_movements()
    print(moves)


def check_mate_layer(): 
    board = LayerBoard()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players, 0)

    pieces = [
        LayerKing(board['a3_T'], p1),
        LayerTower(board['c4_T'], p2),
        LayerTower(board['h2_T'], p2), 
        LayerTower(board['b3_B'], p2), 
        LayerKing(board['h8_T'], p2)
    ]

    moves = game.get_movements()
    for move in moves: 
        if move[0] == 'b3_B': 
            print(move[1])
    print(moves)


def stale_mate_layer():
    board = LayerBoard()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players)

    pieces = [
        LayerKing(board['a1_T'], p1),
        LayerTower(board['b4_T'], p2),
        LayerTower(board['d2_T'], p2), 
    ]

    moves = game.get_movements()
    print(moves)


def eat_layer(): 
    board = LayerBoard()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players)

    pieces = [
        LayerKing(board['a1_T'], p1),
        LayerPawn(board['a2_T'], p1),
        LayerTower(board['b1_T'], p1),
        LayerPawn(board['b2_T'], p2), # Pawn making check, only option would be to eat the pawn to savehimself. 
    ]

    print(game.is_in_check(game.players[0]))
    moves = game.get_movements()
    print(moves)


def castle_layer(): 
    board = LayerBoard()
    p1 = Player(0)
    p2 = Player(3)
    players = [p1, p2]
    game = Game(board, players)

    pieces = [
        LayerKing(board['e1_T'], p1),
        LayerTower(board['a1_T'], p1),
        LayerTower(board['h1_T'], p1),
        # LayerBishop(board['c1_T'], p1), # This should block the middle tile and not allow the castle. 
        # LayerBishop(board['f1_T'], p1), # This also blocks the middle tile. 
        LayerTower(board['d3_T'], p2), # This should not allow the castle because it checks one of the middle tiles. 
        # LayerTower(board['e3_T'], p2), # This should not allow castle because king is in check
    ]

    moves = game.get_movements()
    print(moves)


check_check_layer()
check_mate_layer()
stale_mate_layer()
eat_layer()
castle_layer()
