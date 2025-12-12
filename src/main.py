from model import *
import db.init_db as db
import db.queries as queries
import model.constant as cons
import menu

def plateau_terminal(board: Board):
    cases = board.get_cases()
    draw = []
    for row in reversed(cases):
        for case in row:
            piece = " "
            if case.get_piece() is not None:
                piece_obj = case.get_piece()
                key = (piece_obj.get_name(), piece_obj.get_color().name)
                piece = cons.PIECE_SYMBOLS.get(key)

            if case.get_color().name == "WHITE":
                draw.append(cons.BACKGROUND_WHITE + cons.TEXTE_BLACK + " " + piece + " " + cons.RESET)
            else:
                draw.append(cons.BACKGROUND_BLUE + cons.TEXTE_BLACK + " " + piece + " " + cons.RESET)
   
        draw.append("\n")
    print("".join(draw))

p = Player(1, "a", 1, [])
p1 = p
g = Game(1, p, p1)

l = [p, p1]


def main():
    # players = menu.main_menu(connexion)
    # id_game = queries.save_game(connexion)
    # g = Game(id_game, players[0], players[1])
    g = Game(1, p, p1)
    input("Press enter to start the game")
    board = Board(g)
    board.init_pieces()

    g.move('a2', 'a4')
    g.move('b2', 'b3')
    g.move('c1', 'a3')
    
    g.move('a3', 'e7')

    print(g.allowed_moves_graphic('e7'))

    plateau_terminal(g.get_board())

    # input("appuie pour terminer la partie")
    # g.set_finish()
    if g.get_finish():
        # queries.save_final_game(connexion, id_game, players[0].get_id(), False)
        #queries.save_final_game(connexion, id_game, players[1].get_id(), True)
        print("Partie terminé ")



if __name__ == "__main__":
    connexion = db.open_connexion()
    if not db.database_already_initialized(connexion):
        print("The database is empty, initialization...")
        db.create_database(connexion)
        print("Database initialized!")
    else:
        print("The database is already full")
    main()