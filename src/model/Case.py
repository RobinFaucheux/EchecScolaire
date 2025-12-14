from __future__ import annotations

from .color import Color
from .pieces import Piece

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .board import Board


class Case:
    """
    Represents a single square on the chessboard.

    Attributes:
        pos (tuple[int, int]): Coordinates of the square on the board.
        color (Color): The color of the square (black or white).
        piece (Piece | None): The chess piece currently on this square, if any.
        board (Board): Reference to the board this square belongs to.
    """

    def __init__(self, pos: tuple, color: Color, board: Board, piece=None):
        self.pos = pos
        self.color = color
        self.piece = piece
        self.board = board

    def get_piece(self) -> Piece:
        """
        Returns the piece currently on this square.

        Returns:
            Piece | None: The piece on the square, or None if empty.
        """
        return self.piece

    def set_piece(self, new_piece: Piece) -> Piece:
        """
        Sets or replaces the piece on this square.

        Args:
            new_piece (Piece): The piece to place on the square.

        Returns:
            None
        """
        self.piece = new_piece

    def remove_piece(self) -> bool:
        """
        Removes any piece from this square.

        Returns:
            bool: Always True to indicate the piece was removed.
        """
        self.piece = None
        return True

    def add_piece(self, piece: Piece) -> bool:
        """
        Places a piece on this square, replacing any existing piece.

        Args:
            piece (Piece): The piece to place on the square.

        Returns:
            bool: Always True to indicate the piece was added.
        """
        self.piece = piece
        return True

    def get_pos(self) -> tuple:
        """
        Returns the coordinates of this square on the board.

        Returns:
            tuple[int, int]: The (row, column) position of the square.
        """
        return self.pos

    def get_board(self) -> Board:
        """
        Returns the board this square belongs to.

        Returns:
            Board: The parent board instance.
        """
        return self.board

    def get_color(self) -> Color:
        """
        Returns the color of the square.

        Returns:
            Color: The square's color (black or white).
        """
        return self.color

    def contains_piece(self) -> bool:
        """
        Checks if the square currently contains a piece.

        Returns:
            bool: True if a piece is on the square, False otherwise.
        """
        return self.piece is not None
