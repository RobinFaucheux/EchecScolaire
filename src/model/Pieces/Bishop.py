from .Piece import Piece
from .. import Color, Case

class Bishop(Piece):
    def __init__(self, color : Color, case : Case):
        name = "bishop"
        super().__init__(color, case, name)