from __future__ import annotations  # <--- Magic line
from ..Color import Color
from .Piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case

class Queen(Piece):
    """
    Represents a queen chess piece.

    Attributes:
        color (Color): The color of the piece.
        case (Case): The board square where the queen is placed.
        _vectors (list[tuple[int, int]]): Possible movement vectors in all straight and diagonal directions.
    """

    def __init__(self, color : Color, case : Case):
        name = "queen"
        self._vectors = []
        self.init_vectors()
        super().__init__(color, case, name, self._vectors)


    def init_vectors(self) -> None:
        """
        Initializes the movement vectors for the queen.
        
        - Combines diagonal and straight line movements in all directions.
        - Excludes the (0, 0) vector to prevent no movement.
        """
        for i in range (-7, 7):
            if i != 0:
                self._vectors.append((i, i))
                self._vectors.append((0, i))
                self._vectors.append((i, 0))
                self._vectors.append((-i, i))