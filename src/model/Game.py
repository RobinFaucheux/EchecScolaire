from .Player import Player
from .Board import Board

class Game:
    def __init__(self, idG: int, player1: Player, player2: Player):
        self.idG = idG
        self.finish = False
        self.turn = 1
        self.board = Board(self)
        self.board.init_pieces()
        self.joueurs = [player1, player2]

    def get_joueur(self, pos: int) -> Player:
        return self.joueurs[pos]

    def get_idG(self) -> int:
        return self.idG  
    
    def get_finish(self) -> bool:
        return self.finish
    
    def get_board(self) -> Board:
        return self.board

    def set_finish(self):
        self.finish = True

    def get_turn(self) -> int:
        return self.turn
    
    def set_turn(self, new_turn: int) -> None:
        self.turn = new_turn

    def init_game(self) -> None:
        self.board.init_board()
    
    def win(self) -> None:
        self.victory = True
    
    def allowed_moves(self, position : str) -> list[str]:
        c = self.board.get_case(self.board.translate(position))
        piece = c.get_piece()
        if piece is not None:
            l = piece.accessible_spots()
            coords = []
            for v in l:
                coords.append(self.board.roundtrip(v))
            return coords
        return None
    
    def allowed_moves_graphic(self, position : str):
        c = self.board.get_case(self.board.translate(position))
        piece = c.get_piece()
        if piece is not None:
            l = piece.accessible_spots()
            coords = []
            for v in l:
                coords.append(v)
            self.board.plateau_terminal(coords)
        
    

    def move(self, start : str, end : str) -> bool:
        cstart = self.board.get_case(self.board.translate(start))
        cend = self.board.get_case(self.board.translate(end))

        boolean = self.board.move(cstart, cend)
        return boolean