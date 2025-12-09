from .Piece import Piece
from .. import Color, Case

class Knight(Piece):
    def __init__(self, color : Color, case : Case):
        name = "knight"
        super().__init__(color, case, name)