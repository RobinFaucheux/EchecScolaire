from __future__ import annotations  # <--- Magic line
from ..Color import Color
from .Piece import Piece
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case
class Knight(Piece):
    def __init__(self, color : Color, case : Case):
        name = "knight"
        self._vectors = [(-2 -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        super().__init__(color, case, name, self._vectors)