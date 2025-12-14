from __future__ import annotations
from ..color import Color
from .piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..case import Case


class Bishop(Piece):
    """
    Represents a bishop chess piece.

    Attributes:
        color (Color): The color of the piece.
        case (Case): The board square where the bishop is placed.
        _vectors (list[tuple[int, int]]): Possible diagonal movement vectors.
    """

    def __init__(self, color: Color, case: Case):
        name = "bishop"
        self._vectors = []
        self.init_vectors()
        super().__init__(color, case, name, self._vectors)

    def init_vectors(self) -> None:
        """
        Initializes the bishop's diagonal movement vectors.
        """
        for i in range(-7, 7):
            if i != 0:
                self._vectors.append((i, i))
                self._vectors.append((-i, i))
