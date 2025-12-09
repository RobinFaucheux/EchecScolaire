from .Case import Case
from .Color import Color
from .Pieces.Pawn import Pawn
from .Pieces.Rock import Rock
from .Pieces.Knight import Knight
from .Pieces.Bishop import Bishop
from .Pieces.Queen import Queen
from .Pieces.King import King

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
                        l.append(Case((i, j), Color.BLACK))
                    else:
                        l.append(Case((i, j), Color.WHITE))
                else:
                    if j%2==1:
                        l.append(Case((i, j), Color.BLACK))
                    else:
                        l.append(Case((i, j), Color.WHITE))
            self.cases.append(l)

    def init_pieces(self):
        # Pawns
        for i in range(self.width):
            case = self.get_Case((1, i))
            pawn = Pawn(Color.WHITE, case)
            case.add_piece(pawn)

        for i in range(self.width):
            case = self.get_Case((6, i))
            pawn = Pawn(Color.BLACK, case)
            case.add_piece(pawn)

        # Rock
        tours = [
            ((0, 0), Color.WHITE),
            ((0, self.width - 1), Color.WHITE),
            ((self.height - 1, 0), Color.BLACK),
            ((self.height - 1, self.width - 1), Color.BLACK)
        ]
        for pos, color in tours:
            case = self.get_Case(pos)
            rock = Rock(color, case)
            case.add_piece(rock)

        # Knight
        tours = [
            ((0, 1), Color.WHITE),
            ((0, self.width - 2), Color.WHITE),
            ((self.height - 1, 1), Color.BLACK),
            ((self.height - 1, self.width - 2), Color.BLACK)
        ]
        for pos, color in tours:
            case = self.get_Case(pos)
            knight = Knight(color, case)
            case.add_piece(knight)

        # Bishop
        tours = [
            ((0, 2), Color.WHITE),
            ((0, self.width - 3), Color.WHITE),
            ((self.height - 1, 2), Color.BLACK),
            ((self.height - 1, self.width - 3), Color.BLACK)
        ]
        for pos, color in tours:
            case = self.get_Case(pos)
            bishop = Bishop(color, case)
            case.add_piece(bishop)

        # Queen
        tours = [
            ((0, 3), Color.WHITE),
            ((self.height - 1, self.width - 5), Color.BLACK),
        ]
        for pos, color in tours:
            case = self.get_Case(pos)
            queen = Queen(color, case)
            case.add_piece(queen)
        
        # King
        tours = [
            ((0, 4), Color.WHITE),
            ((self.height - 1, self.width - 4), Color.BLACK),
        ]
        for pos, color in tours:
            case = self.get_Case(pos)
            king = King(color, case)
            case.add_piece(king)



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