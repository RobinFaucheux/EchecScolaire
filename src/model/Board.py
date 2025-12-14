from __future__ import annotations

from model.Pieces import Piece  # <--- Magic line

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
    def __init__(self, game : Game, width = WIDHT_BOARD, height = HEIGHT_BOARD):
        self.width = width
        self.height = height
        self.game = game
        self.cases = []
        self.init_board()
        self.white_king_piece = None
        self.black_king_piece = None
    
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

        pieces: list[tuple[type[Piece], list[tuple[int, int, Color]]]] = [
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
                name = piece.get_name()
                if name == "king":
                    if piece.get_color().name == "WHITE":
                        self.white_king_piece = piece
                    else:
                        self.black_king_piece = piece

                case.add_piece(piece)

    def in_board(self, pos : tuple) -> bool:
        return 0 <= pos[0] < self.height and 0 <= pos[1] < self.width
    
    def case_in_board(self, case : Case) -> bool:
        return self.in_board(case.get_pos())
    
    def get_cases(self) -> list[list[Case]]:
        return self.cases

    def get_case(self, pos : tuple) -> Case:
        if self.in_board(pos):
            return self.cases[pos[0]][pos[1]]
        return None
    
    def get_white_king(self) -> 'King': 
        return self.white_king_piece 
    
    def get_black_king(self) -> 'King': 
        return self.black_king_piece

    def get_Game(self) -> Game:
        return self.game

    def translate(self, chain : str) -> tuple[int, int]:
        try:
            x = chain[0]
            y = int(chain[1:]) - 1
            letters = 'abcdefghijklmnopqrstuvwxyz'


            x = letters.index(x)
            return y,x
        except:
            # return None to signal invalid coordinates to caller
            return None
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
        success = start.get_piece().move(end)
        if success:
            if end.get_piece().get_name() == "King":
                if end.get_piece().get_color().name == "WHITE":
                    self.white_king_piece = end.get_piece()
                else:
                    self.black_king_piece = end.get_piece()
        return success
    
    def plateau_terminal(self, piece : Piece = None):
        cases = self.get_cases()
        draw = []
        green_cases = []
        if piece != None:
            green_cases = piece.accessible_spots()
        draw.append("\n")
        cpt = self.height
        for row in reversed(cases):
            draw.append(" " + str(cpt) + " ")
            for case in row:
                display_piece = " "
                if case.get_piece() is not None:
                    piece_obj = case.get_piece()
                    key = (piece_obj.get_name(), piece_obj.get_color().name)
                    display_piece = PIECE_SYMBOLS.get(key)
                if case.get_pos() in green_cases:
                    draw.append(BACKGROUND_GREEN + TEXTE_BLACK + " " + display_piece + " " + RESET)
                elif piece != None and case.get_pos() == piece.get_case().get_pos():
                    draw.append(BACKGROUND_RED + TEXTE_BLACK + " " + display_piece + " " + RESET)
                else:
                    if case.get_color().name == "WHITE":
                        draw.append(BACKGROUND_WHITE + TEXTE_BLACK + " " + display_piece + " " + RESET)
                    else:
                        draw.append(BACKGROUND_BLUE + TEXTE_BLACK + " " + display_piece + " " + RESET)
            draw.append("\n")
            cpt -= 1
        draw.append("    a  b  c  d  e  f  g  h  ")
        draw.append("\n")
        print("".join(draw))