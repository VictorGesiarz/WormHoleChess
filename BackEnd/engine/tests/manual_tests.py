from engine.core.base.Board import *
from engine.core.base.Pieces import * 
from engine.core.Game import Game


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
        Tower(board['b1_T'], p1),
        Pawn(board['b2_T'], p2), # Pawn making check, only option would be to eat the pawn to savehimself. 
    ]

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
