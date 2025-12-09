from .Piece import Piece
from .. import Color, Case

class Queen(Piece):
    def __init__(self, color : Color, case : Case):
        name = "queen"
        super().__init__(color, case, name)