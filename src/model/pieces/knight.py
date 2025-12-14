from __future__ import annotations
from ..color import Color
from .piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..case import Case


class Knight(Piece):
    """
    Represents a knight chess piece.

    Attributes:
        color (Color): The color of the knight.
        case (Case): The board square where the knight is placed.
        _vectors (list[tuple[int, int]]): Possible movement vectors in 'L' shapes.
    """

    def __init__(self, color: Color, case: Case):
        name = "knight"
        self._vectors = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2),
                         (2, -1), (2, 1)]
        super().__init__(color, case, name, self._vectors)
