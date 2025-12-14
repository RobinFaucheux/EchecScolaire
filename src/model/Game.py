from .Player import Player
from .Board import Board
from .Case import Case
import time
from .constant import *
from copy import deepcopy

class Game:
    def __init__(self, idG: int, player1: Player, player2: Player):
        self.idG = idG
        self.finish = False
        self.turn = 1
        self.board = Board(self)
        self.board.init_pieces()
        self.joueurs = [player1, player2]
        self.time_white = TIMER * ONE_MINUTE_IN_SECONDS
        self.time_black = TIMER * ONE_MINUTE_IN_SECONDS
        self.turn_start_time = time.time()


    def get_joueur(self, pos: int) -> Player:
        return self.joueurs[pos]


    def get_idG(self) -> int:
        return self.idG


    def get_time_white(self) -> int:
        return self.time_white


    def get_time_black(self) -> int:
        return self.time_black


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


    def get_joueurs(self):
        return self.joueurs


    def init_game(self) -> None:
        self.board.init_board()
    

    def win(self) -> None:
        self.finish = True


    def current_color(self) -> str:
        if self.turn % 2 == 1:
            return "WHITE" 
        else:
            return "BLACK"


    def update_clock(self) -> None:
        now = time.time()
        elapsed = now - self.turn_start_time

        if self.current_color() == "WHITE":
            self.time_white = max(0, self.time_white - elapsed)    

        else:
            self.time_black = max(0, self.time_black - elapsed)
        self.turn_start_time = now

        if self.time_white <= 0:
            self.finish = True
            print("White ran out of time. Black wins.")

        if self.time_black <= 0:
            self.finish = True
            print("Black ran out of time. White wins.")
    

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
            return self.board.plateau_terminal(piece)
        

    def move(self, start : str, end : str) -> bool:
        cstart = self.board.get_case(self.board.translate(start))
        cend = self.board.get_case(self.board.translate(end))

        boolean = self.board.move(cstart, cend)
        return boolean


    def king_in_danger(self, color: str) -> bool:
        if color == "WHITE":
            king_piece = self.board.get_white_king()
        else:
            king_piece = self.board.get_black_king()
        pos = king_piece.get_case().get_pos()

        for row in (self.board.get_cases()):
            for other_case in row:
                if other_case.get_piece() != None:
                    if other_case.get_piece().get_color().name != color:

                        other_list_accessible_spots = other_case.get_piece().accessible_spots()
                        for other_accessible_spot in other_list_accessible_spots:
                           if other_accessible_spot == pos:
                                return True
        return False


    def king_in_check_after_move(self, start_pos: tuple, end_pos: tuple, player_color: str) -> bool:
        board_copy = deepcopy(self.board)
        game_copy = board_copy.get_Game()

        start_case = board_copy.get_case(start_pos)
        end_case = board_copy.get_case(end_pos)
        moving_piece = start_case.get_piece()

        start_case.set_piece(None)
        end_case.set_piece(moving_piece)
        moving_piece.set_case(end_case)
        
        if moving_piece.get_name() == "King":
            if moving_piece.get_color().name == "WHITE":
                board_copy.white_king_piece = moving_piece
            else:
                board_copy.black_king_piece = moving_piece

        danger = game_copy.king_in_danger(player_color)
        return danger


    def has_legal_move(self, player_color: str) -> bool:
        for row in self.board.get_cases():
            for case in row:
                piece = case.get_piece()
                if piece != None:
                    if piece.get_color().name == player_color:

                        for end_pos in piece.accessible_spots():
                            if not self.king_in_check_after_move(case.get_pos(), end_pos, player_color):
                                return True
        return False


    def is_checkmate(self, player_color: str) -> bool:
        if  self.king_in_danger(player_color) and not self.has_legal_move(player_color):
            return True
        return False


    def is_stalemate(self, player_color: str) -> bool:
        if not self.king_in_danger(player_color) and not self.has_legal_move(player_color):
            return True
        return False