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

    def process_vectors(self) -> list[tuple[int, int]]:
        l = []
        case = self.case
        current_pos = case.get_pos()
        for v in self._vectors:
            l.append((current_pos[0] + v[0], current_pos[1] + v[1]))
        return l

    def remove(self) -> None:
        self.case = None
    
    def spots_in_map(self) -> list[tuple[int, int]]:
        l = []
        for v in self.process_vectors():
            if self.get_case().get_board().in_board(v):
                l.append(v)
        return l

    def remove_lines_after_piece(self):
        l_origin = self.spots_in_map()

        coords = self.case.get_pos()
        
        l_vect = {}
        for coo in l_origin:
            vect = (coo[0] - coords[0], coo[1] - coords[1])
            l_vect[coo] = vect

        
        print(l_vect)
        l_coords = l_origin.copy()
        for coo, vect in l_vect.items():
            piece = self.case.get_board().get_case(coo).get_piece()
            if piece is not None:
                pos = piece.get_case().get_pos()
                for c, ve in l_vect.items():
                    if vect[0] * ve[0] >=0 and vect[1] * ve[1] >=0 and c in l_coords:
                        dist_v = (abs(vect[0]),abs(vect[1]))
                        dist_ve = (abs(ve[0]), abs(ve[1]))
                        if (dist_v[0] <= dist_ve[0] and dist_v[1] <= dist_ve[1] and vect != ve):
                            l_coords.remove(c)
        print(l_coords)
        return l_coords 

    def accessible_spots(self) -> list[tuple[int, int]]:
        l = []
        spots = self.remove_lines_after_piece()
        for v in spots:
            piece = self.case.get_board().get_case(v).get_piece()
            if piece is not None:
                if piece.get_color() != self.color:
                    l.append(v)
            else:
                l.append(v)
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
        if case.get_pos() in self.accessible_spots():  
            self.case.remove_piece()
            if case.get_piece() != None:
                if case.get_piece().get_name() == "king":
                    case.get_board().get_game().win()
                case.get_piece().remove() # A UPGRADE
            case.add_piece(self)
            return True
        return False