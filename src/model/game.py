from .player import Player
from .board import Board
from .case import Case
from .pieces.piece import Piece
import time
from .constant import TIMER, ONE_MINUTE_IN_SECONDS
from copy import deepcopy


class Game:
    """
    Represents a chess game, managing players, board state, turns, clocks, and game rules.

    Attributes:
        id_g (int): Unique game identifier.
        finish (bool): Whether the game is finished.
        turn (int): Current turn number.
        board (Board): The chess board with pieces.
        joueurs (list[Player]): List of two players.
        time_white (float): Remaining time for White in seconds.
        time_black (float): Remaining time for Black in seconds.
        turn_start_time (float): Timestamp for the start of the current turn.
    """

    def __init__(self, id_g: int, player1: Player, player2: Player):
        self.id_g = id_g
        self.finish = False
        self.turn = 1
        self.board = Board(self)
        self.board.init_pieces()
        self.joueurs = [player1, player2]
        self.time_white = TIMER * ONE_MINUTE_IN_SECONDS
        self.time_black = TIMER * ONE_MINUTE_IN_SECONDS
        self.turn_start_time = time.time()

    def get_joueur(self, pos: int) -> Player:
        """
        Returns the player at the specified position.

        Returns:
            Player: The player object at index pos.
        """
        return self.joueurs[pos]

    def get_id_g(self) -> int:
        """
        Returns the game ID.

        Returns:
            int: The ID of the game.
        """
        return self.id_g

    def get_time_white(self) -> int:
        """
        Returns the remaining time for the white player.

        Returns:
            int: Time in seconds.
        """
        return self.time_white

    def get_time_black(self) -> int:
        """
        Returns the remaining time for the black player.

        Returns:
            int: Time in seconds.
        """
        return self.time_black

    def get_finish(self) -> bool:
        """
        Checks if the game has finished.

        Returns:
            bool: True if the game is finished, False otherwise.
        """
        return self.finish

    def get_board(self) -> Board:
        """
        Returns the game board.

        Returns:
            Board: The board object.
        """
        return self.board

    def set_finish(self) -> None:
        """
        Sets the game as finished.
        """
        self.finish = True

    def get_turn(self) -> int:
        """
        Returns the current turn number.

        Returns:
            int: The current turn.
        """
        return self.turn

    def set_turn(self, new_turn: int) -> None:
        """
        Sets the current turn number.

        Args:
            new_turn (int): The new turn number.
        """
        self.turn = new_turn

    def get_joueurs(self) -> list[Player, Player]:
        """
        Returns the list of players.

        Returns:
            list[Player, Player]: The two players.
        """
        return self.joueurs

    def init_game(self) -> None:
        """
        Initializes the board for a new game.
        """
        self.board.init_board()

    def win(self) -> None:
        """
        Marks the game as won and finished.
        """
        self.finish = True

    def current_color(self) -> str:
        """
        Returns the color of the current player.

        Returns:
            str: "WHITE" or "BLACK".
        """
        if self.turn % 2 == 1:
            return "WHITE"
        else:
            return "BLACK"

    def update_clock(self) -> None:
        """
        Updates the timer for the current player and checks if time ran out.
        """
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

    def allowed_moves(self, position: str) -> list[str]:
        """
        Returns all accessible moves for the piece at the given position.

        Args:
            position (str): The square in algebraic notation (e.g., "e2").

        Returns:
            list[str]: List of squares the piece can move to.
        """
        c = self.board.get_case(self.board.translate(position))
        piece = c.get_piece()

        if piece is not None:
            l = piece.accessible_spots()
            coords = []

            for v in l:
                coords.append(self.board.roundtrip(v))
            return coords
        return None

    def allowed_moves_graphic(self, position: str):
        """
        Displays the board highlighting allowed moves for the piece at the given position.

        Args:
            position (str): The square in algebraic notation (e.g., "e2").
        """
        c = self.board.get_case(self.board.translate(position))
        piece = c.get_piece()

        if piece is not None:
            l = piece.accessible_spots()
            coords = []

            for v in l:
                coords.append(v)
            return self.board.plateau_terminal(piece)

    def move(self, start: str, end: str) -> bool:
        """
        Moves a piece from the start square to the end square.

        Args:
            start (str): Starting square (e.g., "e2").
            end (str): Destination square (e.g., "e4").

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        cstart = self.board.get_case(self.board.translate(start))
        cend = self.board.get_case(self.board.translate(end))

        boolean = self.board.move(cstart, cend)
        return boolean

    def king_in_danger(self, color: str) -> bool:
        """
        Checks if the king of the given color is in danger.

        Args:
            color (str): "WHITE" or "BLACK".

        Returns:
            bool: True if the king is in check, False otherwise.
        """
        if color == "WHITE":
            king_piece = self.board.get_white_king()
        else:
            king_piece = self.board.get_black_king()
        pos = king_piece.get_case().get_pos()

        for row in (self.board.get_cases()):
            for other_case in row:
                if other_case.get_piece() is not None:
                    if other_case.get_piece().get_color().name != color:

                        other_list_accessible_spots = other_case.get_piece(
                        ).accessible_spots()
                        for other_accessible_spot in other_list_accessible_spots:
                            if other_accessible_spot == pos:
                                return True
        return False

    def king_in_check_after_move(self, start_pos: tuple, end_pos: tuple,
                                 player_color: str) -> bool:
        """
        Simulates a move and checks if the king would be in danger afterward.

        Args:
            start_pos (tuple): Starting position coordinates.
            end_pos (tuple): Destination position coordinates.
            player_color (str): The player's color.

        Returns:
            bool: True if the move would leave the king in check.
        """
        board_copy = deepcopy(self.board)
        game_copy = board_copy.get_game()

        start_case = board_copy.get_case(start_pos)
        end_case = board_copy.get_case(end_pos)

        if start_case.get_piece().get_name() == "king":
            ligne, col = start_case.get_pos()
            reussi = None

            if (ligne, col + 2) == end_case.get_pos():
                reussi = self.can_castle(start_case.get_piece(), "left")

            elif (ligne, col - 2) == end_case.get_pos():
                reussi = self.can_castle(start_case.get_piece(), "right")

            if reussi != None:
                print("rock ", reussi)
                return not reussi
                

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
        """
        Checks if the player has any legal move.

        Args:
            player_color (str): "WHITE" or "BLACK".

        Returns:
            bool: True if at least one legal move exists.
        """
        for row in self.board.get_cases():
            for case in row:
                piece = case.get_piece()
                if piece is not None:
                    if piece.get_color().name == player_color:

                        for end_pos in piece.accessible_spots():
                            if not self.king_in_check_after_move(
                                    case.get_pos(), end_pos, player_color):
                                return True
        return False

    def is_checkmate(self, player_color: str) -> bool:
        """
        Determines if the player is in checkmate.

        Args:
            player_color (str): "WHITE" or "BLACK".

        Returns:
            bool: True if the player is checkmated.
        """
        if self.king_in_danger(
                player_color) and not self.has_legal_move(player_color):
            return True
        return False

    def is_stalemate(self, player_color: str) -> bool:
        """
        Determines if the player is in stalemate.

        Args:
            player_color (str): "WHITE" or "BLACK".

        Returns:
            bool: True if the player is stalemated.
        """
        if not self.king_in_danger(player_color) and not self.has_legal_move(
                player_color):
            return True
        return False

    def can_castle(self, king_piece: Piece, direction) -> bool:
        color = king_piece.get_color()
        rock_case = None
        king_pos = king_piece.get_case().get_pos()

        if direction == "left":
            rock_case = self.board.get_case((king_pos[0], 7))
        else:
            rock_case = self.board.get_case((king_pos[0], 0))

        if rock_case.contains_piece():
            if not rock_case.get_piece().get_already_moved():
                if not king_piece.get_already_moved():
                    self.to_castle(king_piece, king_pos, rock_case)
                    return True
        return False
                            
    def to_castle(self, king_piece: Piece, king_pos: tuple[int, int], rock_case: Case):
        self.board.move(king_piece.get_case(), self.board.get_case((king_pos[0], 6)))
        self.board.move(rock_case, self.board.get_case((king_pos[0], 5)))
