from .Piece import Piece
from .. import Color, Case

class Rock(Piece):
    def __init__(self, color : Color, case : Case):
        name = "rock"
        super().__init__(color, case, name)