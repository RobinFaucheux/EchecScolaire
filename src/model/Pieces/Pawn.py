from . import Piece
from .. import Color, Case

class Pawn(Piece):
    def __init__(self, color : Color, case : Case ):
        super(color, case)
        self.vectors = [(-1, -1), (-1, 0), (-1, 1)]
    
    def process_vectors(self) -> list:
        l = []
        case = self.case
        current_pos = case.get_pos()
        for v in self.vectors:
            l.append((current_pos[0] + v[0], current_pos[1] + v[1]))
        return v
    
    def move(self, case : Case):
        if case.get_pos() in self.process_vectors() and case.get_board.case_in_board(case):
            super.move(self.case, case)