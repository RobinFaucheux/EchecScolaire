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
    
    def remove_lines_after_piece(self):
        l = super().remove_lines_after_piece()
        res = [l[1]]
        piece_1 = self.case.get_board().get_case(l[0]).get_piece()
        if piece_1 is not None and piece_1.get_color() != self.color:
            res.append(l[0])
        
        piece_2 = self.case.get_board().get_case(l[2]).get_piece()
        if piece_2 is not None and piece_2.get_color() != self.color:
            res.append(l[2])
        
        if (len(l) >3):
            res.append(l[-1])
        return res
