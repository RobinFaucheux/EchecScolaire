from .Piece import Piece
from .. import Color, Case

class Rock(Piece):
    def __init__(self, color : Color, case : Case):
        name = "rock"
        super().__init__(color, case, name)
        self._vectors = []
        self.init_vectors()
    
    def init_vectors(self):
        for i in range (-7, 7):
            self._vectors.append((0, i))
            self._vectors.append((i, 0))