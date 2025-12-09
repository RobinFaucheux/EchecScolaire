from model.Board import Board

def plateau_terminal(board: Board):
    BACKGROUND_WHITE = "\033[47m"
    BACKGROUND_BLACK = "\033[40m"
    RESET = "\033[0m"

    WHITE_PAWN = "○"
    BLACK_PAWN = "●"

    cases = board.get_cases()
    draw = []
    for row in reversed(cases):
        for case in row:

            piece = " "
            if case.get_piece() != None:
                if case.get_piece().get_name() == "pawn":
                    if case.get_piece().get_color().name == "WHITE":
                        piece = WHITE_PAWN
                    else:
                        piece = BLACK_PAWN

        
            if case.get_color().name == "WHITE":
                draw.append(BACKGROUND_WHITE + " " + piece + " " + RESET)
            else:
                draw.append(BACKGROUND_BLACK + " " + piece + " " + RESET)

            
        draw.append("\n")
    print("".join(draw))

def main():
    board = Board()
    board.init_pieces()
    
    plateau_terminal(board)

if __name__ == "__main__":
    main()



