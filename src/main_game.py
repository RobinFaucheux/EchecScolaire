from model import * 
import db.queries as queries
import sqlalchemy
from typing import Dict, Type, Union


def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02}:{seconds % 60:02}"


def play_turn(connexion: sqlalchemy.Connection, board: Board) -> Dict[str, Union[Type[Player], str]]:
    game = board.get_Game()
    player_color = game.current_color()
    if player_color == "WHITE":
        pos = 0
    else:
        pos = 1
    player = game.get_joueur(pos)

    if game.is_checkmate(player_color):
        print("\n" + TEXTE_RED + "CHECKMATE" + RESET)
        game.set_finish()
        looser = game.get_joueur(pos)
        if pos == 0:
            winner = game.get_joueur(1)
        else:
            winner = game.get_joueur(0)
        print("Player", winner.get_pseudo(), "won!")
        print("Player", looser.get_pseudo(), "lost!")
        return {"result": "checkmate", "winner": winner, "looser": looser}

    if game.is_stalemate(player_color):
        print("\n" + TEXTE_RED + "STALEMATE" + RESET)
        game.set_finish()
        print("Equality between the player", game.get_joueur(0), "and the player", game.get_joueur(1))
        return {"result": "stalemate", "white": game.get_joueur(0), "black": game.get_joueur(1)}

    print(f"\nTurn {game.get_turn()} - Player {player.get_pseudo()} - color : {player_color}")

    print(f"White time: {format_time(game.time_white)}")
    print(f"Black time: {format_time(game.time_black)}")

    board.plateau_terminal()
    while True:
        if (game.king_in_danger(player_color)) :
                print("Your king is in check")

        piece_to_be_moved = input("Enter the starting square (example: a2): ").lower()

        if len(piece_to_be_moved) < 2:
            print("Invalid input! Must be a letter followed by a number.")
            continue

        if not (piece_to_be_moved[0].isalpha() and piece_to_be_moved[1:].isdigit()):
            print("Invalid input! Must be a letter followed by a number.")
            continue

        start_piece_tuple = board.translate(piece_to_be_moved)
        if not board.in_board(start_piece_tuple):
            print("This case not is in the board!")
            continue

        start_case_piece = board.get_case(start_piece_tuple)
        if start_case_piece.get_piece() == None:
            print("No piece on this square!")
            continue
        
        if start_case_piece.get_piece().get_color().name != player_color:
            print("This is not your piece!")
            continue
        
        if start_case_piece.get_piece().accessible_spots() == []:
            print("This piece cant to move!")
            continue

        game.allowed_moves_graphic(piece_to_be_moved)
        while True:
        
            location_piece_to_be_moved = input("Enter the destination square (example: a4): ").lower()

            if len(location_piece_to_be_moved) < 2:
                print("Invalid input! Must be a letter followed by a number.")
                continue

            if not (location_piece_to_be_moved[0].isalpha() and location_piece_to_be_moved[1:].isdigit()):
                print("Invalid input! Must be a letter followed by a number.")
                continue

            end_piece_tuple = board.translate(location_piece_to_be_moved)
            if not board.in_board(end_piece_tuple):
                print("This case not is in the board!")
                continue

            end_case_piece = board.get_case(end_piece_tuple)

            final_start = board.roundtrip(start_case_piece.get_pos())
            final_end = board.roundtrip(end_case_piece.get_pos())

            save_start_case_piece = start_case_piece.get_piece()

            if game.king_in_check_after_move(start_case_piece.get_pos(), end_case_piece.get_pos(), player_color):
                print("Move would put your king in danger! Choose another piece.")
                board.plateau_terminal()
                break

            reussi = game.move(piece_to_be_moved, location_piece_to_be_moved)

            if not reussi:
                print("Movement not possible, please choose a green box.")
                continue

            game.update_clock()
            if game.get_time_black() == 0 or game.get_time_white() == 0:
                if game.get_time_black() == 0:
                    print("\n" + TEXTE_RED + "player", game.get_joueur(1).get_pseudo(), "time elapse" + RESET)
                    game.set_finish()
                    looser = game.get_joueur(1)
                    winner = game.get_joueur(0)
                elif game.get_time_white() == 0:
                    print("\n" + TEXTE_RED + "player", game.get_joueur(0).get_pseudo(), "time elapse" + RESET)
                    game.set_finish()
                    looser = game.get_joueur(0)
                    winner = game.get_joueur(1)

                print("Player", winner.get_pseudo(), "won!")
                print("Player", looser.get_pseudo(), "lost!")
                return {"result": "checkmate", "winner": winner, "looser": looser}

            print(f"{player.get_pseudo()} moved {save_start_case_piece.get_name()} from {final_start} to {final_end}")
            queries.save_coup(connexion, game.get_idG(), game.get_turn(), final_start, final_end)
            game.set_turn(game.get_turn() + 1)

            return