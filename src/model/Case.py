from __future__ import annotations  # <--- Magic line

from .Color import Color
from .Pieces import Piece


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Board import Board
class Case:

    def __init__(self, pos : tuple, color : Color, board : Board, piece = None):
        self.pos = pos
        self.color = color
        self.piece = piece
        self.board = board


    def get_piece(self) -> Piece:
        return self.piece


    def set_piece(self, new_piece: Piece) -> Piece:
        self.piece = new_piece


    def remove_piece(self) -> bool:
        self.piece = None
        return True


    def add_piece(self, piece : Piece) -> bool:
        self.piece = piece
        return True


    def get_pos(self) -> tuple:
        return self.pos


    def get_board(self) -> Board:
        return self.board


    def get_color(self) -> Color:
        return self.color


    def contains_piece(self) -> bool:
        return self.piece is not None