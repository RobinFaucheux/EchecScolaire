from .Player import Player
from .Board import Board

class Game:
    def __init__(self, player1: Player, player2: Player):
        self.victory = False
        self.turn = 1
        self.board = Board(self)
        self.joueurs = [player1, player2]
        
    def get_victory(self) -> bool:
        return self.victory

    def get_turn(self) -> int:
        return self.turn
    
    def set_turn(self, new_turn: int) -> None:
        self.turn = new_turn

    def init_game(self) -> None:
        self.board.init_board()
    
    def win(self) -> None:
        self.victory = True