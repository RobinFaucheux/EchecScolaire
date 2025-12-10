from __future__ import annotations  # <--- Magic line
from ..Color import Color
from .Piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case
class Pawn(Piece):
    def __init__(self, color : Color, case : Case):
        name = "pawn"
        self._vectors = [(-1, -1), (-1, 0), (-1, 1)]
        super().__init__(color, case, name, self._vectors)