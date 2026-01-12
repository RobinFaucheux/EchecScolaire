from model.game import Game
import db.init_db as db
from db import queries
import main_menu as menu
import main_game as game
from colorama import init

init()


def main(connexion):
    """
    Main entry point for the Chess game application.

    - Calls the main menu to log in or register two players.
    - Initializes a new game and the board.
    - Runs the game loop until the game finishes.
    - Updates and saves ELO ratings for players based on the game result.
    - Displays the final board and messages about the game's outcome.
    """
    players = menu.main_menu(connexion)
    id_game = queries.save_game(connexion)
    g = Game(id_game, players[0], players[1])
    input("Press enter to start the game")

    board = g.get_board()

    g.move(("g1"), ("h3"))
    g.move(("e2"), ("e4"))
    g.move(("f2"), ("f4"))
    g.move(("f1"), ("c4"))
    g.move(("d2"), ("d4"))
    board.plateau_terminal()
    
    while not g.get_finish():
        dico = game.play_turn(connexion, board)

    board.plateau_terminal()

    input("Press to finish the game")
    if g.get_finish():
        print("Game over!")

        if dico["result"] == "checkmate":
            old_elo_player_won = dico["winner"].get_elo()
            old_elo_player_lost = dico["looser"].get_elo()

            dico["winner"].calculate_elo(old_elo_player_lost, "won")
            dico["looser"].calculate_elo(old_elo_player_won, "loose")

            queries.save_final_game(connexion, g, id_game, dico["winner"],
                                    "won")
            queries.save_final_game(connexion, g, id_game, dico["looser"],
                                    "loose")
            print("Result of game saved!")

        elif dico["result"] == "stalemate":
            old_elo_player_black = dico["white"].get_elo()
            old_elo_player_white = dico["black"].get_elo()

            dico["white"].calculate_elo(old_elo_player_black, "equality")
            dico["black"].calculate_elo(old_elo_player_white, "equality")

            queries.save_final_game(connexion, g, id_game, dico["white"],
                                    "equality")
            queries.save_final_game(connexion, g, id_game, dico["black"],
                                    "equality")
            print("Result of the game saved!")


if __name__ == "__main__":
    db_conn = db.open_connexion()
    if not db.database_already_initialized(db_conn):
        print("The database is empty, initialization...")
        db.create_database(db_conn)
        print("Database initialized!")
    else:
        print("The database is already full")
    main(db_conn)
