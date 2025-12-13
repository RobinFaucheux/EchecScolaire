from model import * 
import db.queries as queries
import sqlalchemy

def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02}:{seconds % 60:02}"

def play_turn(connexion: sqlalchemy.Connection, board: Board):
    game = board.get_Game()
    player_color = game.current_color()
    if player_color == "WHITE":
        pos = 0
    else:
        pos = 1
    player = game.get_joueur(pos)
    print(f"\nTurn {game.get_turn()} - Player {player.get_pseudo()}")

    print(f"White time: {format_time(game.time_white)}")
    print(f"Black time: {format_time(game.time_black)}")

    board.plateau_terminal()
    while True:
        piece_to_be_moved = input("Enter the starting square (example: a2): ").lower()

        if len(piece_to_be_moved) < 2:
            print("Invalid input! Must be a letter followed by a number.")
            continue

        if not (piece_to_be_moved[0].isalpha() and piece_to_be_moved[1:].isdigit()):
            print("Invalid input! Must be a letter followed by a number.")
            continue

        start_piece_tuple = board.translate(piece_to_be_moved)
        start_case_piece = board.get_case(start_piece_tuple)

        if not board.case_in_board(start_case_piece):
            print("This case not is in the board!")
            continue

        if start_case_piece.get_piece() == None:
            print("No piece on this square!")
            continue
        
        if start_case_piece.get_piece().get_color().name != player_color:
            print("This is not your piece!")
            continue

        print(game.allowed_moves_graphic(piece_to_be_moved))
        while True:
        
            location_piece_to_be_moved = input("Enter the destination square (example: a4): ").lower()

            if len(location_piece_to_be_moved) < 2:
                print("Invalid input! Must be a letter followed by a number.")
                continue

            if not (location_piece_to_be_moved[0].isalpha() and location_piece_to_be_moved[1:].isdigit()):
                print("Invalid input! Must be a letter followed by a number.")
                continue

            end_piece_tuple = board.translate(location_piece_to_be_moved)
            end_case_piece = board.get_case(end_piece_tuple)

            final_start = board.roundtrip(start_case_piece.get_pos())
            final_end = board.roundtrip(end_case_piece.get_pos())

            save_start_case_piece = start_case_piece.get_piece()

            reussi = game.move(piece_to_be_moved, location_piece_to_be_moved)
            if not reussi:
                print("Movement not possible, please choose a green box.")
                continue
            game.update_clock()
            if game.get_time_black() == 0 or game.get_time_white() == 0:
                break

            print(f"{player.get_pseudo()} moved {save_start_case_piece.get_name()} from {final_start} to {final_end}")
            queries.save_coup(connexion, game.get_idG(), game.get_turn(), final_start, final_end)
            game.set_turn(game.get_turn() + 1)

            board.plateau_terminal()
            break
        break