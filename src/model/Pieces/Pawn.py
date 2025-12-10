from .Piece import Piece
from .. import Color, Case

class Pawn(Piece):
    def __init__(self, color : Color, case : Case):
        name = "pawn"
        super().__init__(color, case, name)
        self._vectors = [(-1, -1), (-1, 0), (-1, 1)]