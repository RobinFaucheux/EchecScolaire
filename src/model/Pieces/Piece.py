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
        
        # Create the vector map
        l_vect = {}
        for coo in l_origin:
            vect = (coo[0] - coords[0], coo[1] - coords[1])
            l_vect[coo] = vect

        l_coords = l_origin.copy()
        
        # Iterate through every possible spot to see if there is a piece there
        for coo_blocker, vect_blocker in l_vect.items():
            # Get the piece at this spot (the potential blocker)
            piece = self.case.get_board().get_case(coo_blocker).get_piece()
            
            # If there is a piece here, it might block spots behind it
            if piece is not None:
                # We must calculate its distance to know what is "behind" it
                # (Squared distance is faster and safer than sqrt)
                dist_blocker_sq = vect_blocker[0]**2 + vect_blocker[1]**2
                
                # Check all OTHER spots to see if they are shadowed by this blocker
                for coo_target, vect_target in l_vect.items():
                    
                    # Skip if we are looking at the blocker itself or if already removed
                    if coo_blocker == coo_target or coo_target not in l_coords:
                        continue
                    
                    # 1. STRICT COLLINEARITY CHECK (Cross Product)
                    # (x1 * y2) must equal (y1 * x2) for them to be on the same line
                    is_collinear = (vect_blocker[0] * vect_target[1] == vect_blocker[1] * vect_target[0])
                    
                    # 2. SAME DIRECTION CHECK
                    # Their coordinates must have matching signs
                    same_direction = (vect_blocker[0] * vect_target[0] >= 0) and \
                                    (vect_blocker[1] * vect_target[1] >= 0)

                    if is_collinear and same_direction:
                        dist_target_sq = vect_target[0]**2 + vect_target[1]**2
                        
                        # If the target is strictly further away than the blocker, remove it
                        if dist_target_sq > dist_blocker_sq:
                            l_coords.remove(coo_target)
        for coo in l_coords:
            print(self.case.get_board().roundtrip(coo), end=', ')
        print()
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
                    case.get_board().get_Game().win()
                case.get_piece().remove() # A UPGRADE
            case.add_piece(self)
            self.case = case
            return True
        return False