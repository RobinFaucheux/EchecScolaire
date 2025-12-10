from .Piece import Piece
from .. import Color, Case

class King(Piece):
    def __init__(self, color : Color, case : Case):
        name = "king"
        super().__init__(color, case, name)
        self._vectors = []
        self.init_vectors()
    
    def init_vectors(self):
        for i in range(-1, 2):
            for j in range (-1, 2):
                if (i != 0 and j != 0):
                    self._vectors.append((i,j))