from __future__ import annotations  # <--- Magic line
from ..Color import Color
from .Piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case
class Pawn(Piece):
    def __init__(self, color : Color, case : Case):
        name = "pawn"
        if color == Color.BLACK:
            self._vectors = [(-1, -1), (-1, 0), (-1, 1), (-2, 0)]
        else:
            self._vectors = [(1, -1), (1, 0), (1, 1), (2, 0)]
        super().__init__(color, case, name, self._vectors)
    
    def process_vectors(self) -> list[tuple[int, int]]:
        if self.color == Color.BLACK and self.case.get_pos()[0] != 6 and (-2, 0) in self._vectors:
            self._vectors.remove((-2, 0))
            
        if self.color == Color.WHITE and self.case.get_pos()[0] != 1 and (2, 0) in self._vectors:
            self._vectors.remove((2, 0))
        return super().process_vectors()