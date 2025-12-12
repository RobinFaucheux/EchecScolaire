from model import *
import db.init_db as db
import db.queries as queries
import constant as cons
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

def main():
    players = menu.main_menu(connexion)
    id_game = queries.save_game(connexion)
    g = Game(id_game, players[0], players[1])
    # g = Game(1, p, p1)
    input("Press enter to start the game")
    board = Board(g)
    board.init_pieces()

    # print(board.translate('a2'))

    # board.get_case(board.translate('a2')).get_piece().move(board.get_case(board.translate('a3')))
    
    # board.get_case(board.translate('b2')).get_piece().move(board.get_case(board.translate('b3')))

    # for coord in board.get_case(board.translate('b2')).get_piece().accessible_spots():
    #     print(board.roundtrip(coord))
    
    plateau_terminal(board)

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