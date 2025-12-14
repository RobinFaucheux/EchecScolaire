from __future__ import annotations

from model.Pieces import Piece
from .Color import Color
from .Pieces.Pawn import Pawn
from .Pieces.Rock import Rock
from .Pieces.Knight import Knight
from .Pieces.Bishop import Bishop
from .Pieces.Queen import Queen
from .Pieces.King import King
from .Case import Case
from .constant import * 

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Game import Game

class Board:
    """
    Represents a chessboard with all squares and pieces.

    Attributes:
        width (int): The number of columns on the board.
        height (int): The number of rows on the board.
        game (Game): The game instance this board belongs to.
        cases (list[list[Case]]): 2D grid of board squares.
        white_king_piece (King | None): Reference to the white king piece.
        black_king_piece (King | None): Reference to the black king piece.
    """

    def __init__(self, game : Game, width = WIDHT_BOARD, height = HEIGHT_BOARD):
        self.width = width
        self.height = height
        self.game = game
        self.cases = []
        self.init_board()
        self.white_king_piece = None
        self.black_king_piece = None


    def init_board(self) -> None:
        """
        Initializes the chessboard with alternating colored squares.

        Creates all `Case` instances for the board and arranges them in a 2D grid.
        """
        for i in range(self.height):
            l = []
            for j in range(self.width):
                if (i%2 == 0):
                    if j%2==0:
                        l.append(Case((i, j), Color.BLACK, self))
                    else:
                        l.append(Case((i, j), Color.WHITE, self))
                else:
                    if j%2==1:
                        l.append(Case((i, j), Color.BLACK, self))
                    else:
                        l.append(Case((i, j), Color.WHITE, self))
            self.cases.append(l)


    def init_pieces(self) -> None:
        """
        Places all chess pieces in their starting positions on the board.

        - Pawns are placed on the second and seventh ranks.
        - Rooks, Knights, Bishops, Queen, and King are placed on the first and last ranks.
        - Updates references to the white and black kings.
        """
        for i in range(self.width):
            case = self.get_case((1, i))
            pawn = Pawn(Color.WHITE, case)
            case.add_piece(pawn)

        for i in range(self.width):
            case = self.get_case((6, i))
            pawn = Pawn(Color.BLACK, case)
            case.add_piece(pawn)

        pieces: list[tuple[type[Piece], list[tuple[int, int, Color]]]] = [
            (Rock, [
                (0, 0, Color.WHITE), 
                (0, self.width - 1, Color.WHITE),
                (self.height - 1, 0, Color.BLACK), 
                (self.height - 1, self.width - 1, Color.BLACK)
            ]),
            (Knight, [
                (0, 1, Color.WHITE), 
                (0, self.width - 2, Color.WHITE),
                (self.height - 1, 1, Color.BLACK), 
                (self.height - 1, self.width - 2, Color.BLACK)
            ]),
            (Bishop, [
                (0, 2, Color.WHITE), 
                (0, self.width - 3, Color.WHITE),
                (self.height - 1, 2, Color.BLACK), 
                (self.height - 1, self.width - 3, Color.BLACK)
            ]),
            (Queen, [
                (0, 3, Color.WHITE),
                (self.height - 1, 3, Color.BLACK)
            ]),
            (King, [
                (0, 4, Color.WHITE),
                (self.height - 1, 4, Color.BLACK)
            ])
        ]
        for clss, positions in pieces:
            for x, y, color in positions:
                case = self.get_case((x, y))
                piece = clss(color, case)
                name = piece.get_name()
                if name == "king":
                    if piece.get_color().name == "WHITE":
                        self.white_king_piece = piece
                    else:
                        self.black_king_piece = piece

                case.add_piece(piece)


    def in_board(self, pos : tuple) -> bool:
        """
        Checks if a given position is within the board boundaries.

        Args:
            pos (tuple[int, int]): The coordinates to check.

        Returns:
            bool: True if the position is inside the board, False otherwise.
        """
        return 0 <= pos[0] < self.height and 0 <= pos[1] < self.width


    def case_in_board(self, case : Case) -> bool:
        """
        Checks if a given board square (Case) is within the board boundaries.

        Args:
            case (Case): The square to check.

        Returns:
            bool: True if the square is inside the board, False otherwise.
        """
        return self.in_board(case.get_pos())


    def get_cases(self) -> list[list[Case]]:
        """
        Returns the full 2D grid of board squares.

        Returns:
            list[list[Case]]: All cases on the board.
        """
        return self.cases


    def get_case(self, pos : tuple) -> Case:
        """
        Retrieves the Case object at the specified coordinates.

        Args:
            pos (tuple[int, int]): Coordinates of the square.

        Returns:
            Case | None: The square at the position, or None if out of bounds.
        """
        if self.in_board(pos):
            return self.cases[pos[0]][pos[1]]
        return None


    def get_white_king(self) -> 'King': 
        """
        Returns the white king piece.

        Returns:
            King | None: Reference to the white king on the board.
        """
        return self.white_king_piece 


    def get_black_king(self) -> 'King':
        """
        Returns the black king piece.

        Returns:
            King | None: Reference to the black king on the board.
        """
        return self.black_king_piece


    def get_Game(self) -> Game:
        """
        Returns the game instance this board belongs to.

        Returns:
            Game: The parent game object.
        """
        return self.game


    def translate(self, chain : str) -> tuple[int, int]:
        """
        Converts a board coordinate string (e.g., 'a2') to numeric indices.

        Args:
            chain (str): The board position in algebraic notation.

        Returns:
            tuple[int, int] | None: Corresponding (row, column) indices, or None if invalid.
        """
        try:
            x = chain[0]
            y = int(chain[1:]) - 1
            letters = 'abcdefghijklmnopqrstuvwxyz'

            x = letters.index(x)
            return y,x
        
        except:
            return None


    def roundtrip(self, pos : tuple) -> str:
        """
        Converts numeric board indices back to algebraic notation (e.g., (1,0) -> 'a2').

        Args:
            pos (tuple[int, int]): The numeric position.

        Returns:
            str: The position in algebraic notation.
        """
        try:
            y = pos[0] + 1
            x = pos[1]

            letters = 'abcdefghijklmnopqrstuvwxyz'
            x = letters[x]
            return str(x) + str(y)

        except:
            print("Wrong coordinates")


    def move(self, start : Case, end : Case) -> bool:
        """
        Moves a piece from the start Case to the end Case.

        Updates the board's reference if a king is moved.

        Args:
            start (Case): The starting square.
            end (Case): The target square.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        success = start.get_piece().move(end)

        if success:
            if end.get_piece().get_name() == "King":

                if end.get_piece().get_color().name == "WHITE":
                    self.white_king_piece = end.get_piece()
                else:
                    self.black_king_piece = end.get_piece()
        return success


    def plateau_terminal(self, piece : Piece = None):
        """
        Displays the current board state in the terminal.

        Highlights:
            - The selected piece in red.
            - Accessible squares for the selected piece in green.

        Args:
            piece (Piece | None): Optional piece to highlight moves for.

        Returns:
            str: The string representation of the board.
        """
        cases = self.get_cases()
        draw = []
        green_cases = []

        if piece != None:
            green_cases = piece.accessible_spots()

        draw.append("\n")
        cpt = self.height
        for row in reversed(cases):
            draw.append(" " + str(cpt) + " ")

            for case in row:
                display_piece = " "

                if case.get_piece() is not None:
                    piece_obj = case.get_piece()
                    key = (piece_obj.get_name(), piece_obj.get_color().name)
                    display_piece = PIECE_SYMBOLS.get(key)

                if case.get_pos() in green_cases:
                    draw.append(BACKGROUND_GREEN + TEXTE_BLACK + " " + display_piece + " " + RESET)

                elif piece != None and case.get_pos() == piece.get_case().get_pos():
                    draw.append(BACKGROUND_RED + TEXTE_BLACK + " " + display_piece + " " + RESET)

                else:
                    if case.get_color().name == "WHITE":
                        draw.append(BACKGROUND_WHITE + TEXTE_BLACK + " " + display_piece + " " + RESET)
                    else:
                        draw.append(BACKGROUND_BLUE + TEXTE_BLACK + " " + display_piece + " " + RESET)

            draw.append("\n")
            cpt -= 1

        draw.append("    a  b  c  d  e  f  g  h  ")
        draw.append("\n")
        print("".join(draw))
        return "".join(draw)