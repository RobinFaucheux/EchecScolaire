from model.Board import Board

def plateau_terminal(board: Board):
    WHITE = "\033[47m" + "\033[30m"
    BLACK = "\033[40m" + "\033[37m"
    RESET = "\033[0m"

    cases = board.get_cases()
    draw = []
    for row in reversed(cases):
        for case in row:
            if case.get_color().name == "WHITE":
                draw.append(WHITE + str(case.get_pos()) + RESET)
            else:
                draw.append(BLACK + str(case.get_pos()) + RESET)
        draw.append("\n")
    print("".join(draw))

def main():
    board = Board()

    plateau_terminal(board)

if __name__ == "__main__":
    main()
