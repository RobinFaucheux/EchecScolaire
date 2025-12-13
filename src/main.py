from model import *
import db.init_db as db
import db.queries as queries
import model.constant as cons
import menu

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


    g.move('a2', 'a4')
    g.move('b2', 'b3')
    g.move('c1', 'a3')
    
    g.move('a3', 'e7')

    print(g.allowed_moves_graphic('e7'))

    board.pla


    print(g.get_board().plateau_terminal(green_cases=g.get_board().get_case(g.get_board().translate('e7')).get_piece().remove_lines_after_piece()))

    input("Press to finish the game")
    g.set_finish()
    if g.get_finish():
        old_elo_player1 = players[0].get_elo()
        old_elo_player2 = players[1].get_elo()
        print("type de elo : ", type(old_elo_player1))
        players[0].calculate_elo(old_elo_player2, 'won')
        players[1].calculate_elo(old_elo_player1, 'loose')
        queries.save_final_game(connexion, id_game, players[0], 'won')
        queries.save_final_game(connexion, id_game, players[1], 'loose')
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