from .Case import Case
from .Color import Color

class Board:
    def __init__(self, width = 8, height = 8):
        self.width = width
        self.height = height
        self.cases = []
        self.init_board()
    
    def init_board(self):
        for i in range(self.height):
            l = []
            for j in range(self.width):
                if (i%2 == 0):
                    if j%2==0:
                        l.append(Case((i, j), Color.WHITE))
                    else:
                        l.append(Case((i, j), Color.BLACK))
                else:
                    if j%2==1:
                        l.append(Case((i, j), Color.WHITE))
                    else:
                        l.append(Case((i, j), Color.BLACK))
            self.cases.append(l)

    def in_board(self, pos : tuple) -> bool:
        return 0 < pos[0] < self.height and 0 < pos[1] < self.width
    
    def case_in_board(self, case : Case):
        return self.in_board(case.get_pos())
    
    def get_cases(self) -> list:
        return self.cases

    def get_Case(self, pos : tuple):
        return self.cases[pos[0]][pos[1]]

    def move(self, start : Case, end : Case) -> bool:
        return start.get_piece().move(end)