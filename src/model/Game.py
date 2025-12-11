from .Player import Player
from .Board import Board

class Game:
    def __init__(self, idG: int, player1: Player, player2: Player):
        self.idG = idG
        self.finish = False
        self.turn = 1
        self.board = Board(self)
        self.joueurs = [player1, player2]

    def get_idG(self) -> int:
        return self.idG  
    
    def get_finish(self) -> bool:
        return self.finish
    
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