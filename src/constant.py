BACKGROUND_WHITE = "\033[47m"
BACKGROUND_BLUE = "\033[48;2;88;137;169m"
TEXTE_BLACK = "\033[30m"
RESET = "\033[0m"

WHITE_PAWN = "P"
WHITE_ROCK = "R"
WHITE_KNIGHT = "N"
WHITE_BISHOP = "B"
WHITE_QUEEN = "Q"
WHITE_KING = "K"

BLACK_PAWN = "p"
BLACK_ROCK = "r"
BLACK_KNIGHT = "n"
BLACK_BISHOP = "b"
BLACK_QUEEN = "q"
BLACK_KING = "k"

PIECE_SYMBOLS = {
    ("pawn", "WHITE"): WHITE_PAWN,
    ("pawn", "BLACK"): BLACK_PAWN,
    ("rock", "WHITE"): WHITE_ROCK,
    ("rock", "BLACK"): BLACK_ROCK,
    ("knight", "WHITE"): WHITE_KNIGHT,
    ("knight", "BLACK"): BLACK_KNIGHT,
    ("bishop", "WHITE"): WHITE_BISHOP,
    ("bishop", "BLACK"): BLACK_BISHOP,
    ("queen", "WHITE"): WHITE_QUEEN,
    ("queen", "BLACK"): BLACK_QUEEN,
    ("king", "WHITE"): WHITE_KING,
    ("king", "BLACK"): BLACK_KING
}