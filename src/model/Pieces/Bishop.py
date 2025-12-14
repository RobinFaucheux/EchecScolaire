from __future__ import annotations  # <--- Magic line
from ..Color import Color
from .Piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case

class Bishop(Piece):
    def __init__(self, color : Color, case : Case):
        name = "bishop"
        self._vectors = []
        self.init_vectors()
        super().__init__(color, case, name, self._vectors)
    
    def init_vectors(self) -> None:
        for i in range (-7, 7):
            if i!=0:
                self._vectors.append((i, i))
                self._vectors.append((-i, i))