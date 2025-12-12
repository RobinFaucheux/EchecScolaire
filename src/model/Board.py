from __future__ import annotations  # <--- Magic line

from .Color import Color
from .Pieces.Pawn import Pawn
from .Pieces.Rock import Rock
from .Pieces.Knight import Knight
from .Pieces.Bishop import Bishop
from .Pieces.Queen import Queen
from .Pieces.King import King
from .Case import Case
from .constant import * 


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Game import Game
    

class Board:
    def __init__(self, game : Game, width = 8, height = 8):
        self.width = width
        self.height = height
        self.game = game
        self.cases = []
        self.init_board()
    
    def init_board(self):
        for i in range(self.height):
            l = []
            for j in range(self.width):
                if (i%2 == 0):
                    if j%2==0:
                        l.append(Case((i, j), Color.BLACK, self))
                    else:
                        l.append(Case((i, j), Color.WHITE, self))
                else:
                    if j%2==1:
                        l.append(Case((i, j), Color.BLACK, self))
                    else:
                        l.append(Case((i, j), Color.WHITE, self))
            self.cases.append(l)

    def init_pieces(self):
        
        for i in range(self.width):
            case = self.get_case((1, i))
            pawn = Pawn(Color.WHITE, case)
            case.add_piece(pawn)

        for i in range(self.width):
            case = self.get_case((6, i))
            pawn = Pawn(Color.BLACK, case)
            case.add_piece(pawn)

        pieces = [
            (Rock, [
                (0, 0, Color.WHITE), 
                (0, self.width - 1, Color.WHITE),
                (self.height - 1, 0, Color.BLACK), 
                (self.height - 1, self.width - 1, Color.BLACK)
            ]),
            (Knight, [
                (0, 1, Color.WHITE), 
                (0, self.width - 2, Color.WHITE),
                (self.height - 1, 1, Color.BLACK), 
                (self.height - 1, self.width - 2, Color.BLACK)
            ]),
            (Bishop, [
                (0, 2, Color.WHITE), 
                (0, self.width - 3, Color.WHITE),
                (self.height - 1, 2, Color.BLACK), 
                (self.height - 1, self.width - 3, Color.BLACK)
            ]),
            (Queen, [
                (0, 3, Color.WHITE),
                (self.height - 1, 3, Color.BLACK)
            ]),
            (King, [
                (0, 4, Color.WHITE),
                (self.height - 1, 4, Color.BLACK)
            ])
        ]
        for clss, positions in pieces:
            for x, y, color in positions:
                case = self.get_case((x, y))
                piece = clss(color, case)
                case.add_piece(piece)

    def in_board(self, pos : tuple) -> bool:
        return 0 <= pos[0] < self.height and 0 <= pos[1] < self.width
    
    def case_in_board(self, case : Case) -> bool:
        return self.in_board(case.get_pos())
    
    def get_cases(self) -> list[Case]:
        return self.cases

    def get_case(self, pos : tuple) -> Case:
        return self.cases[pos[0]][pos[1]]

    def get_Game(self) -> Game:
        return self.game

    def translate(self, chain : str) -> tuple[int, int]:
        try:
            x = chain[0]
            y = int(chain[1:]) - 1
            letters = 'abcdefghijklmnopqrstuvwxyz'


            x = letters.index(x)
            # print(x, y)
            return y,x
        except:
            print("Wrong coordinates")
        
    def roundtrip(self, pos : tuple) -> str:
        try:
            y = pos[0] + 1
            x = pos[1]

            letters = 'abcdefghijklmnopqrstuvwxyz'

            x = letters[x]

            return str(x) + str(y)

        except:
            print("Wrong coordinates")

    def move(self, start : Case, end : Case) -> bool:
        return start.get_piece().move(end)
    
    def plateau_terminal(self, green_cases : list[tuple[int, int]] = []):
        cases = self.get_cases()
        draw = []
        for row in reversed(cases):
            for case in row:
                piece = " "
                if case.get_piece() is not None:
                    piece_obj = case.get_piece()
                    key = (piece_obj.get_name(), piece_obj.get_color().name)
                    piece = PIECE_SYMBOLS.get(key)
                if case.get_pos() in green_cases:
                    draw.append(BACKGROUND_GREEN + TEXTE_BLACK + " " + piece + " " + RESET)
                else:
                    if case.get_color().name == "WHITE":
                        draw.append(BACKGROUND_WHITE + TEXTE_BLACK + " " + piece + " " + RESET)
                    else:
                        draw.append(BACKGROUND_BLUE + TEXTE_BLACK + " " + piece + " " + RESET)
    
            draw.append("\n")
        print("".join(draw))