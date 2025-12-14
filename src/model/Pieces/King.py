from __future__ import annotations  # <--- Magic line
from ..Color import Color
from typing import TYPE_CHECKING
from .Piece import Piece

if TYPE_CHECKING:
    from ..Case import Case
class King(Piece):

    def __init__(self, color : Color, case : Case):
        name = "king"
        self._vectors = []
        self.init_vectors()
        super().__init__(color, case, name, self._vectors)
    

    def init_vectors(self) -> None:
        for i in range(-1, 2):
            for j in range (-1, 2):
                if (i != 0 and j != 0):
                    self._vectors.append((i,j))