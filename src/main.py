from model.Board import Board
from db.db import open_connexion
import constant as cons

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

def main():
    board = Board()
    board.init_pieces()
    
    plateau_terminal(board)

if __name__ == "__main__":
    connexion=open_connexion()
    main()