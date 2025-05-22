import time 
import random 

from engine.core.base.NormalBoard import * 
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


# check_check()
# check_mate()
# stale_mate()
# eat()
# castle()


# - - - - - - - - - - - - - - - - - - - - - - Layer Board - - - - - - - - - - - - - - - - - - - - - - - - 
print("\nLAYER BOARD TESTS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")

def create_layer_board(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=4), 
        program_mode="layer",
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


# check_check_layer()
# check_mate_layer()
# stale_mate_layer()
# eat_layer()
# castle_layer()


# - - - - - - - - - - - - - - - - - - - - - - HASHING - - - - - - - - - - - - - - - - - - - - - - - - 
print("\nHASHING TESTING - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")

def test_hash(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=4), 
        program_mode="layer",
        size="big"
    )
    game_copy = game.copy()
    
    print("Game hash:", hash(game))
    game.get_turn()
    game.next_turn()
    print("Game hash:", hash(game))
    game.get_turn()
    game.next_turn()
    print("Game hash:", hash(game))

    print("Game Copy Hash:", hash(game_copy))
    game_copy.get_turn()
    game_copy.next_turn()
    print("Game Copy Hash:", hash(game_copy))


def time_hash(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=4), 
        program_mode="layer",
        size="big"
    )
    
    timer = time.time()
    hash_ = hash(game)
    print("Hash calculated in:", time.time() - timer)
    

def copy_game(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=4), 
        program_mode="layer",
        size="big"
    )
    print('\nGame state:', game.get_pieces_state())

    game_copy = game.copy()    
    for _ in range(10): 
        game_copy.get_turn()
        game_copy.next_turn()
    print('\nGame Copy state after 10 moves:', game_copy.get_pieces_state())

    print('\nOriginal Game state should stay the same:', game.get_pieces_state())


def time_copy(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=4), 
        program_mode="layer",
        size="big"
    )

    times = []
    for _ in range(100): 
        start = time.time()
        game_copy = game.copy()
        end = time.time()
        times.append(end - start)

    print('\nMean copy time:', sum(times) / len(times))


def new_hash_test(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=4), 
        program_mode="layer",
        game_mode="wormhole",
        size="big",
    )

    random.seed(42)

    move_count = 0
    while not game.is_finished() and move_count < 120:
        print("MOVE:", move_count)
        print("Current stored hash:", game.hash)
        print("Current correct hash:", game.hasher.compute_hash(game.board))
        
        turn = game.get_turn()
        game.next_turn()
        move_count += 1 

        print("Move made:", game.history[-1])

        print("New stored hash:", game.hash)
        print("New correct hash:", game.hasher.compute_hash(game.board))

        if game.hasher.compute_hash(game.board) != game.hash:
            print("Hash mismatch detected!")
            break

        print()

# test_hash()
# time_hash()
# copy_game()
# time_copy()
# new_hash_test()


# - - - - - - - - - - - - - - - - - - - - - - DRAWS - - - - - - - - - - - - - - - - - - - - - - - - 
def test_dead_positions(): 
    b = NormalBoard()
    p1 = Player(0)
    piece = King(b['a1'], p1)
    piece = Bishop(b['a2'], p1)

    p2 = Player(1)
    piece = King(b['h8'], p2)

    players = [p1, p2]
    game = Game(b, players)

    print(game.is_dead_position())


def test_repetition_draw(): 
    b = NormalBoard()
    p1 = Player(0)
    piece = King(b['a1'], p1)
    piece = Queen(b['a7'], p1)

    p2 = Player(1)
    piece = King(b['h8'], p2)

    players = [p1, p2]
    game = Game(b, players)

    moves = [(b['a1'], b['a2']), (b['h8'], b['h7']), (b['a2'], b['a1']), (b['h7'], b['h8'])]

    i = 0
    move_count = 0
    while not game.is_finished() and move_count < 15:
        game.make_move(moves[i])
        game.next_turn()
        i = (i + 1) % 4
        move_count += 1

        if game.is_draw_by_repetition():
            print(True)
            break


def test_50_move_rule(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_player_data(num_players=4), 
        program_mode="layer",
        size="big"
    )

    i = 0
    move_count = 0
    while not game.is_finished() and move_count < 120:
        if game.get_turn() == -1:
            game.next_turn()
            continue

        movements = game.get_movements()

        move = random.choice(movements)
        if len(movements) > 1:
            if all(m[1].piece is not None for m in movements):
                print("Test failed due to random moves leading to all movements capturing pieces")
                break
            while move[1].piece is not None:
                move = random.choice(movements)
        game.make_move(move)
        game.next_turn()

        move_count += 1

        if game.is_draw_by_50_moves(): 
            print(True)
            break

# test_dead_positions()
# test_repetition_draw()
# test_50_move_rule()



# - - - - - - - - - - - - - - - - - - - - - - GAME CREATION - - - - - - - - - - - - - - - - - - - - - - - - 
def create_board_with_factory(): 
    game = ChessFactory.create_game(
        player_data=ChessFactory.create_bot_data(num_bots=2), 
        program_mode="layer",
        game_mode="normal",
        size="big",
        # initial_positions='./engine/core/assets/4 pieces.json'
    )
    print(game.get_movements())
    game.next_turn()
    print(game.get_movements())

# create_board_with_factory()



def another_test(): 
    b = NormalBoard(size=(4, 4))
    p1 = Player(0)
    k1 = King(b['a1'], p1)
    q2 = Queen(b['b2'], p1)

    p2 = Player(1)
    k2 = King(b['c4'], p2)

    players = [p1, p2]
    game = Game(b, players, turn=0)

    print(game.get_movements())
    game.make_move((b['b2'], b['d2']))
    game.next_turn()
    print(game.get_movements())
    game.make_move((b['c4'], b['b3']))
    game.next_turn()
    print(game.get_movements())
    game.make_move((b['d2'], b['a2']))
    game.next_turn()
    print(game.get_movements())

# another_test()


# - - - - - - - - - - - - - - - - - - - - - - LAYER MATRIX BOARD - - - - - - - - - - - - - - - - - - - - 
print("\nLAYER MATRIX BOARD TESTING - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")

from engine.core_matrices.MatrixBoard import LayerMatrixBoard, Pieces, Teams

def test_layer_matrix_board(): 
    b = LayerMatrixBoard((8, 8), 'wormhole')
    # print(b.nodes)
    # print()
    # print(b.edges)
    # print()
    # print(b.node_edges)
    # print()
    print(b.check_size())
        
test_layer_matrix_board()