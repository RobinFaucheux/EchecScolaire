from __future__ import annotations  # <--- Magic line
from ..Color import Color
from .Piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case

class Rock(Piece):
    """
    Represents a rook chess piece.

    Attributes:
        color (Color): The color of the piece.
        case (Case): The board square where the rook is placed.
        _vectors (list[tuple[int, int]]): Possible movement vectors along rows and columns.
    """

    def __init__(self, color : Color, case : Case):
        name = "rock"
        self._vectors = []
        self.init_vectors()
        super().__init__(color, case, name, self._vectors)
    

    def init_vectors(self) -> None:
        """
        Initializes the rook's movement vectors.

        The rook can move any number of squares vertically or horizontally.
        This method generates all possible direction vectors for those moves.
        """
        for i in range (-7, 7):
            if i!=0:
                self._vectors.append((0, i))
                self._vectors.append((i, 0))