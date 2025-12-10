from .Piece import Piece
from .. import Color, Case

class Bishop(Piece):
    def __init__(self, color : Color, case : Case):
        name = "bishop"
        super().__init__(color, case, name)
        self._vectors = []
        self.init_vectors()
    
    def init_vectors(self):
        for i in range (-7, 7):
            self._vectors.append((i, i))
            self._vectors.append((-i, i))