from __future__ import annotations
from ..color import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..case import Case


class Piece:
    """
    Represents a generic chess piece on the board.

    Attributes:
        color (Color): The color of the piece (WHITE or BLACK).
        case (Case): The square on which the piece is currently located.
        name (str): The name of the piece (e.g., "bishop", "pawn").
        _vectors (list[tuple[int, int]]): Movement directions relative to the current position.
    """

    def __init__(self, color: Color, case: Case, name: str, vectors = None):
        if vectors is None:
            vectors = []
        self.color = color
        self.case = case
        self._vectors = vectors
        self.name = name

    def get_color(self) -> Color:
        """
        Returns the color of the piece.
        
        Returns:
            Color: The color of the piece.
        """
        return self.color

    def set_color(self, color: Color) -> None:
        """
        Sets the color of the piece.
        
        Args:
            color (Color): The new color for the piece.
        """
        self.color = color

    def get_case(self) -> Case:
        """
        Returns the current square (Case) of the piece.
        
        Returns:
            Case: The square where the piece is located.
        """
        return self.case

    def set_case(self, case: Case) -> None:
        """
        Sets the piece's current square.
        
        Args:
            case (Case): The new square for the piece.
        """
        self.case = case

    def get_name(self) -> str:
        """
        Returns the name of the piece.
        
        Returns:
            str: The name of the piece.
        """
        return self.name

    def process_vectors(self) -> list[tuple[int, int]]:
        """
        Calculates potential board coordinates based on the piece's movement vectors.
        
        - Adds each vector to the current position of the piece to get possible coordinates.
        
        Returns:
            list[tuple[int, int]]: The list of potential coordinates.
        """
        l = []
        case = self.case
        current_pos = case.get_pos()
        for v in self._vectors:
            l.append((current_pos[0] + v[0], current_pos[1] + v[1]))
        return l

    def remove(self) -> None:
        """
        Removes the piece from the board.
        
        - Sets the piece's current square to None.
        """
        self.case = None

    def spots_in_map(self) -> list[tuple[int, int]]:
        """
        Filters the coordinates from process_vectors to keep only those inside the board.
        
        Returns:
            list[tuple[int, int]]: Coordinates that are within the board limits.
        """
        l = []
        for v in self.process_vectors():
            if self.get_case().get_board().in_board(v):
                l.append(v)
        return l

    def remove_lines_after_piece(self) -> None:
        """
        Removes moves that are blocked by other pieces in a straight line from the piece.
        
        - Keeps only coordinates reachable without jumping over friendly or enemy pieces.
        
        Returns:
            list[tuple[int, int]]: Filtered list of coordinates.
        """
        l_origin = self.spots_in_map()
        coords = self.case.get_pos()
        l_vect = {}
        for coo in l_origin:
            vect = (coo[0] - coords[0], coo[1] - coords[1])
            l_vect[coo] = vect

        l_coords = l_origin.copy()

        for coo_blocker, vect_blocker in l_vect.items():
            piece = self.case.get_board().get_case(coo_blocker).get_piece()
            if piece is not None:
                dist_blocker_sq = vect_blocker[0]**2 + vect_blocker[1]**2

                for coo_target, vect_target in l_vect.items():
                    if coo_blocker == coo_target or coo_target not in l_coords:
                        continue

                    is_collinear = (vect_blocker[0] *
                                    vect_target[1] == vect_blocker[1] *
                                    vect_target[0])
                    same_direction = (vect_blocker[0] * vect_target[0] >= 0) and \
                                    (vect_blocker[1] * vect_target[1] >= 0)

                    if is_collinear and same_direction:
                        dist_target_sq = vect_target[0]**2 + vect_target[1]**2

                        if dist_target_sq > dist_blocker_sq:
                            l_coords.remove(coo_target)
        return l_coords

    def accessible_spots(self) -> list[tuple[int, int]]:
        """
        Calculates legal moves for the piece.
        
        - Includes capturing moves on opponent pieces.
        - Uses remove_lines_after_piece to filter blocked moves.
        
        Returns:
            list[tuple[int, int]]: Legal move coordinates.
        """
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

    def move(self, case: Case) -> bool:
        """
        Moves the piece to the given square if the move is legal.
        
        - Captures any opponent piece on the target square.
        - Updates the piece's current square.
        
        Args:
            case (Case): The destination square.
        
        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if case.get_pos() in self.accessible_spots():

            self.case.remove_piece()
            if case.get_piece() is not None:

                if case.get_piece().get_name() == "king":
                    case.get_board().get_game().win()

                case.get_piece().remove()
            case.add_piece(self)
            self.case = case
            return True
        return False
