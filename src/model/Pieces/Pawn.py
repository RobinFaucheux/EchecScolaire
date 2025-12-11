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
            self._vectors = [(-1, -1), (-1, 0), (-1, 1)]
        else:
            self._vectors = [(1, -1), (1, 0), (1, 1)]
        super().__init__(color, case, name, self._vectors)
        # print(self.accessible_spots())
        # if len(self.accessible_spots()) > 0:
        #     self.move(self.case.get_board().get_case(self.accessible_spots()[0]))
        print(self.case)