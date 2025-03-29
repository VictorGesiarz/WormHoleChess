import chess
import chess.engine

# Create a new chess board
board = chess.Board()

# Play until the game ends
while not board.is_game_over():
    print(board)  # Display the board
    move = input("Enter your move (e.g., e2e4): ")

    try:
        chess_move = chess.Move.from_uci(move)  # Convert input to a chess move
        if chess_move in board.legal_moves:
            board.push(chess_move)  # Make the move
        else:
            print("Illegal move, try again!")
    except ValueError:
        print("Invalid move format, use UCI notation (e.g., e2e4)")

# Game result
print("\nGame Over!")
print("Result:", board.result())  # "1-0", "0-1", or "1/2-1/2"
