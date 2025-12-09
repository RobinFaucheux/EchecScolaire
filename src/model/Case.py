from . import Color, Board
from Pieces import Piece
class Case:
    def __init__(self, pos : tuple, color : Color, board = Board, piece = None):
        self.pos = pos
        self.color = color
        self.piece = piece
        self.board = board
    
    def get_piece(self) -> Piece:
        return self.piece 

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
