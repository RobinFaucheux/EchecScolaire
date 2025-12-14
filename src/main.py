from model import *
import db.init_db as db
import db.queries as queries
import model.constant as cons
import main_menu as menu
import main_game as game

from colorama import init
init()

p = Player(1, "a", 1, [])
p1 = p
g = Game(1, p, p1)

l = [p, p1]


def main():
    players = menu.main_menu(connexion)
    id_game = queries.save_game(connexion)
    g = Game(id_game, players[0], players[1])
    # g = Game(1, p, p1)
    input("Press enter to start the game")

    board = g.get_board()

    while not g.get_finish():
        dico = game.play_turn(connexion, board)

    board.plateau_terminal()

    input("Press to finish the game")
    if g.get_finish():
        print("Game over!")
        print(dico)

        if dico["result"] == "checkmate":
            old_elo_player_won = dico["winner"].get_elo()
            old_elo_player_lost = dico["looser"].get_elo()

            dico["winner"].calculate_elo(old_elo_player_lost, "won")
            dico["looser"].calculate_elo(old_elo_player_won, "loose")
            
            queries.save_final_game(connexion, g, id_game, dico["winner"], 'won')
            queries.save_final_game(connexion, g, id_game, dico["looser"], 'loose')
            print("Result of game saved!")

        elif dico["result"] == "stalemate":
            old_elo_player_black = dico["white"].get_elo()
            old_elo_player_white = dico["black"].get_elo()

            dico["white"].calculate_elo(old_elo_player_black, "equality")
            dico["black"].calculate_elo(old_elo_player_white, "equality")
            
            queries.save_final_game(connexion, g, id_game, dico["white"], 'equality')
            queries.save_final_game(connexion, g, id_game, dico["black"], 'equality')
            print("Result of game saved!")


if __name__ == "__main__":
    connexion = db.open_connexion()
    if not db.database_already_initialized(connexion):
        print("The database is empty, initialization...")
        db.create_database(connexion)
        print("Database initialized!")
    else:
        print("The database is already full")
    main()