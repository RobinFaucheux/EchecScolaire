from __future__ import annotations  # <--- Magic line
from ..Color import Color
from .Piece import Piece
from .Queen import Queen
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case
class Pawn(Piece):
    def __init__(self, color : Color, case : Case):
        name = "pawn"
        if color == Color.BLACK:
            self._vectors = [(-1, -1), (-1, 0), (-1, 1), (-2, 0)]
        else:
            self._vectors = [(1, -1), (1, 0), (1, 1), (2, 0)]
        super().__init__(color, case, name, self._vectors)
    
    def process_vectors(self) -> list[tuple[int, int]]:
        if self.color == Color.BLACK and self.case.get_pos()[0] != 6 and (-2, 0) in self._vectors:
            self._vectors.remove((-2, 0))
            
        if self.color == Color.WHITE and self.case.get_pos()[0] != 1 and (2, 0) in self._vectors:
            self._vectors.remove((2, 0))
        return super().process_vectors()
    
    def remove_lines_after_piece(self):
        l = super().remove_lines_after_piece()

        res = []

        d_vectors = {}
        pos = self.case.get_pos()
        for co in l:
            vector = (co[0] - pos[0], co[1] - pos[1])
            d_vectors[vector] = co
        
        if self.color == Color.BLACK:
            for vector, co in d_vectors.items():
                piece = self.case.get_board().get_case(co).get_piece()
                match vector:
                    case (-1, -1):
                        if piece != None and piece.get_color != self.color:
                            res.append(co)
                        continue
                    case (-1, 0):
                        if piece == None:
                            res.append(co)
                        continue
                    case (-2, 0):
                        if piece == None:
                            res.append(co)
                        continue
                    case (-1, 1):
                        if piece != None and piece.get_color != self.color:
                            res.append(co)
                        continue
        else:
            for vector, co in d_vectors.items():
                piece = self.case.get_board().get_case(co).get_piece()
                match vector:
                    case (1, -1):
                        if piece != None and piece.get_color != self.color:
                            res.append(co)
                        continue
                    case (1, 0):
                        if piece == None:
                            res.append(co)
                        continue
                    case (2, 0):
                        if piece == None:
                            res.append(co)
                        continue
                    case (1, 1):
                        if piece != None and piece.get_color != self.color:
                            res.append(co)
                        continue
        return res
    
    def move(self, case : Case) -> bool:
        if case.get_pos() in self.accessible_spots():

            if self.color == Color.BLACK and case.get_pos()[0] == 0:
                if case.get_piece() != None:
                    if case.get_piece().get_name() == "king":
                        case.get_board().get_Game().win()
                    case.get_piece().remove() # A UPGRADE
                self.case.remove_piece()
                self.remove()
                case.add_piece(Queen(Color.BLACK, case))
                return True
            if self.color == Color.WHITE and case.get_pos()[0] == self.case.get_board().height-1:
                if case.get_piece() != None:
                    if case.get_piece().get_name() == "king":
                        case.get_board().get_Game().win()
                    case.get_piece().remove() # A UPGRADE
                self.case.remove_piece()
                self.remove()
                case.add_piece(Queen(Color.WHITE, case))
                return True

            self.case.remove_piece()
            if case.get_piece() != None:
                if case.get_piece().get_name() == "king":
                    case.get_board().get_Game().win()
                case.get_piece().remove() # A UPGRADE
            case.add_piece(self)
            self.case = case
            return True
        return False