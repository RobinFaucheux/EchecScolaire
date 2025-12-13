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

    # while not g.set_finish():
    #     game.play_turn(board)

    board.plateau_terminal()

    input("Press to finish the game")
    g.set_finish()
    if g.get_finish():
        old_elo_player1 = g.get_joueur(0).get_elo()
        old_elo_player2 = g.get_joueur(1).get_elo()
        g.get_joueur(0).calculate_elo(old_elo_player2, 'won')
        g.get_joueur(1).calculate_elo(old_elo_player1, 'loose')
        queries.save_final_game(connexion, id_game, g.get_joueur(0), 'won')
        queries.save_final_game(connexion, id_game, g.get_joueur(1), 'loose')
        print("Game over!")

if __name__ == "__main__":
    connexion = db.open_connexion()
    if not db.database_already_initialized(connexion):
        print("The database is empty, initialization...")
        db.create_database(connexion)
        print("Database initialized!")
    else:
        print("The database is already full")
    main()