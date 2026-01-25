from __future__ import annotations
from ..color import Color
from .piece import Piece
from .queen import Queen
from .bishop import Bishop
from .knight import Knight
from .rock import Rock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..case import Case


class Pawn(Piece):
    """
    Represents a pawn chess piece.

    Attributes:
        color (Color): The color of the pawn (WHITE or BLACK).
        case (Case): The board square where the pawn is placed.
        _vectors (list[tuple[int, int]]): Possible movement vectors including standard moves, 
        captures, and double advance on first move.
    """

    def __init__(self, color: Color, case: Case):
        name = "pawn"
        if color == Color.BLACK:
            self._vectors = [(-1, -1), (-1, 0), (-1, 1), (-2, 0)]
        else:
            self._vectors = [(1, -1), (1, 0), (1, 1), (2, 0)]
        super().__init__(color, case, name, self._vectors)

    def process_vectors(self) -> list[tuple[int, int]]:
        """
        Adjusts the pawn's movement vectors based on its current position.
        
        - Removes the two-square forward move if the pawn is not on its starting rank.
        - Calls the parent class to process other vector rules.
        
        Returns:
            list[tuple[int, int]]: The list of adjusted movement vectors.
        """
        if self.color == Color.BLACK and self.case.get_pos()[0] != 6 and (
                -2, 0) in self._vectors:
            self._vectors.remove((-2, 0))

        if self.color == Color.WHITE and self.case.get_pos()[0] != 1 and (
                2, 0) in self._vectors:
            self._vectors.remove((2, 0))
        return super().process_vectors()

    def remove_lines_after_piece(self) -> list:
        """
        Filters potential moves according to pawn-specific rules.
        
        - Handles diagonal captures only if an opponent piece is present.
        - Ensures forward moves are allowed only if the square is empty.
        
        Returns:
            list: List of board coordinates (tuples) where the pawn can legally move.
        """
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
                        if piece is not None and piece.get_color() != self.color:
                            res.append(co)
                        continue
                    case (-1, 0):
                        if piece is None:
                            res.append(co)
                        continue
                    case (-2, 0):
                        if piece is None:
                            res.append(co)
                        continue
                    case (-1, 1):
                        if piece is not None and piece.get_color() != self.color:
                            res.append(co)
                        continue
        else:
            for vector, co in d_vectors.items():
                piece = self.case.get_board().get_case(co).get_piece()
                match vector:
                    case (1, -1):
                        if piece is not None and piece.get_color() != self.color:
                            res.append(co)
                        continue
                    case (1, 0):
                        if piece is None:
                            res.append(co)
                        continue
                    case (2, 0):
                        if piece is None:
                            res.append(co)
                        continue
                    case (1, 1):
                        if piece is not None and piece.get_color() != self.color:
                            res.append(co)
                        continue
        return res
    
    def can_be_promoted(self):
        target_row = 0 if self.color == Color.BLACK else self.case.get_board().height - 1
        return self.case.get_pos()[0] == target_row
    
    def promote(self, type : str):
        self.case.remove_piece()
        match type:
            case "q":
                self.case.add_piece(Queen(self.color, self.case))
            case "r":
                self.case.add_piece(Rock(self.color, self.case))
            case "b":
                self.case.add_piece(Bishop(self.color, self.case))
            case "k":
                self.case.add_piece(Knight(self.color, self.case))
        self.remove()
        return True


    def move(self, case: Case) -> bool:
        """
        Attempts to move the pawn to a given square.
        
        - Handles normal forward moves, diagonal captures, and promotion to a Queen.
        - Removes captured pieces if present.
        - Updates the pawn's current square.
        
        Args:
            case (Case): The target square to move to.
        
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
