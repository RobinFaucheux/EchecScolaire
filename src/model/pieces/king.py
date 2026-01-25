from __future__ import annotations
from ..color import Color
from typing import TYPE_CHECKING
from .piece import Piece

if TYPE_CHECKING:
    from ..case import Case


class King(Piece):
    """
    Represents a king chess piece.

    Attributes:
        color (Color): The color of the king.
        case (Case): The board square where the king is placed.
        _vectors (list[tuple[int, int]]): Possible movement vectors (one square in any direction).
    """

    def __init__(self, color: Color, case: Case):
        name = "king"
        self.already_moved = False
        self._vectors = []
        self.init_vectors()
        super().__init__(color, case, name, self._vectors)

    def init_vectors(self) -> None:
        """
        Initializes the king's movement vectors (one square in all directions).
        """
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i != 0 or j != 0):
                    self._vectors.append((i, j))
        self._vectors.append((0, -2))
        self._vectors.append((0, 2))
    
    def king_moved(self):
        self.already_moved = True
        self._vectors.pop()
        self._vectors.pop()


    def get_already_moved(self):
        return self.already_moved
