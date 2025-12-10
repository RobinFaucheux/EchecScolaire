from __future__ import annotations  # <--- Magic line
from ..Color import Color
from .Piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case
class Rock(Piece):
    def __init__(self, color : Color, case : Case):
        name = "rock"
        self._vectors = []
        self.init_vectors()
        super().__init__(color, case, name, self._vectors)
    
    def init_vectors(self):
        for i in range (-7, 7):
            self._vectors.append((0, i))
            self._vectors.append((i, 0))