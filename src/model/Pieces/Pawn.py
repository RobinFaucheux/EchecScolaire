from .Piece import Piece
from .. import Color, Case

class Pawn(Piece):
    def __init__(self, color : Color, case : Case):
        name = "pawn"
        super().__init__(color, case, name)
        self.vectors = [(-1, -1), (-1, 0), (-1, 1)]
    
    
    
    def move(self, case : Case):
        if case.get_pos() in self.process_vectors() and case.get_board.case_in_board(case):
            super.move(self.case, case)