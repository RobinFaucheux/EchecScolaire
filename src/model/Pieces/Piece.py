from __future__ import annotations  # <--- Magic line
from ..Color import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Case import Case
class Piece:
    def __init__(self, color : Color, case : Case, name: str, vectors = []):
        self.color =  color
        self.case = case
        self._vectors = vectors
        self.name = name
        print(self.accessible_spots())

    def process_vectors(self) -> list:
        l = []
        case = self.case
        current_pos = case.get_pos()
        for v in self._vectors:
            l.append((current_pos[0] + v[0], current_pos[1] + v[1]))
        return l

    def remove(self) -> None:
        self.case = None
    
    def spots_in_map(self):
        l = []
        for v in self.process_vectors():
            if self.get_case().get_board().in_board(v):
                l.append(v)
        return l

    def accessible_spots(self) -> list:
        l = []
        for v in self.spots_in_map():
            case = self.case.get_board().get_case(v)
            if case is not None:
                if case.get_color() != self.color:
                    l.append(case.get_pos())
            else:
                l.append(case.get_pos())
        return l

    def get_color(self) -> Color:
        return self.color
    
    def set_color(self, color : Color):
        self.color = color
    
    def get_case(self) -> Case:
        return self.case

    def set_case(self, case : Case):
        self.case = case

    def get_name(self) -> str:
        return self.name

    def move(self, case : Case) -> bool:
        if case.get_pos() is self.accessible_spots():    
            self.case.remove_piece()
            if case.get_piece!= None:
                if type(case.get_piece()) == King:
                    self.case.get_board().get_game().win()
                case.get_piece().remove() # A UPGRADE
            case.add_piece(self)
            self.case = case
            return True

    