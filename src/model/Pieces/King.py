from .Piece import Piece
from .. import Color, Case

class King(Piece):
    def __init__(self, color : Color, case : Case):
        name = "king"
        super().__init__(color, case, name)