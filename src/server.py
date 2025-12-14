import socket
import sys
from model.game import Game
from model.player import Player
import db.init_db as db
from db import queries
from colorama import init

init()


class Serveur:
    """
    Represents a chess server.

    Attributes:
        counter (int): A counter for tracking connections or sessions (currently unused).
    """

    def __init__(self, connection):
        self.counter = 0
        self.connection = connection

    def main_server(self, port):
        """
        Starts the server and listens for incoming client connections.

        - Binds to the specified port and waits for a client to connect.
        - Creates a Session object for the connected client.
        - Handles exceptions and ensures the socket is closed on exit.
        """
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            sock.bind(("0.0.0.0", port))
            sock.listen(1)
            print(f"Server listening on port {port}...")
        except Exception as e:
            print(f"Error binding server: {e}")
            return

        try:
            print("Waiting for player...")
            cli, addr = sock.accept()
            print(f"New connection from {addr}")

            sess = Session(self, cli,self. connection)
            sess.main_session()

            print("Session finished.")

        except KeyboardInterrupt:
            print("Server interrupted by user.")
        except Exception as e:
            print(f"Server Error: {e}")
        finally:
            try:
                sock.close()
                print("Server socket closed. Exiting.")
            except Exception:
                pass
            sys.exit()


class Session:
    """
    Represents a single game session between the server and a client.

    Attributes:
        server (serveur): Reference to the parent server.
        socket (socket.socket): The socket connected to the client.
        file (TextIO): A file-like wrapper around the socket for reading/writing text.
        game (Game): The chess game being played in this session.
        board (Board): The game board for the current session.
    """

    def __init__(self, serveur, sock, connection):
        self.connection = connection
        self.server = serveur
        self.socket = sock
        self.file = sock.makefile(mode="rw", encoding="utf-8")

        player1 = Player(1, "player1", 1200, [])
        player2 = Player(2, "player2", 1200, [])

        try:
            id_game = queries.save_game(self.connexion)
        except Exception:
            id_game = 1

        self.game = Game(id_game, player1, player2)
        self.board = self.game.get_board()

    def format_time(self, seconds: float) -> str:
        """
        Converts a number of seconds into a MM:SS string format.

        Args:
            seconds (float): The number of seconds.

        Returns:
            str: The formatted time string as MM:SS.
        """
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02}:{seconds % 60:02}"

    def send(self, message):
        """
        Sends a message to the client through the socket.

        Args:
            message (str): The message to send.
        """
        try:
            self.file.write(message + "\n")
            self.file.flush()
        except Exception:
            pass

    def ask_input(self, prompt):
        """
        Sends a prompt to the client and reads their input.

        Args:
            prompt (str): The message to display to the client.

        Returns:
            str | None: The client's response, lowercased and stripped, or None if connection 
            is closed.
        """
        try:
            self.file.write(prompt + "\nEntree : \n")
            self.file.flush()

            response = self.file.readline()
            if not response:
                return None
            return response.strip().lower()
        except Exception:
            return None

    def main_session(self):
        """
        Main loop for a single game session with a client.

        - Alternates turns between players until the game ends.
        - Handles move input validation, checks for illegal moves, and updates the game board.
        - Updates player clocks and sends board and game status updates to the client.
        - Saves moves and final game results to the database.
        """
        game = self.game

        try:
            while not game.get_finish():
                player_color = game.current_color()
                pos = 0 if player_color == "WHITE" else 1
                player = game.get_joueur(pos)

                if game.time_white <= 0 or game.time_black <= 0:
                    self.send("Time is up! Game Over.")
                    break

                self.send("\n==========================================")
                self.send(
                    f"Turn {game.get_turn()} - {player.get_pseudo()} ({player_color})"
                )
                self.send(f"White time: {self.format_time(game.time_white)}")
                self.send(f"Black time: {self.format_time(game.time_black)}")
                self.send(self.board.plateau_terminal())

                piece_to_be_moved = ""
                start_case_piece = None

                while True:
                    piece_to_be_moved = self.ask_input(
                        "Enter the starting square (example: a2)")

                    if piece_to_be_moved is None:
                        return
                    if piece_to_be_moved == "quit":
                        return

                    if len(piece_to_be_moved) < 2 or not (
                            piece_to_be_moved[0].isalpha() and
                            piece_to_be_moved[1:].isdigit()):
                        self.send("Invalid input! Format: a2")
                        continue

                    start_piece_tuple = self.board.translate(piece_to_be_moved)
                    if not self.board.in_board(start_piece_tuple):
                        self.send("Square outside board!")
                        continue

                    start_case_piece = self.board.get_case(start_piece_tuple)
                    if start_case_piece.get_piece() is None:
                        self.send("No piece here!")
                        continue

                    if start_case_piece.get_piece().get_color(
                    ).name != player_color:
                        self.send("Not your piece!")
                        continue

                    if not start_case_piece.get_piece().accessible_spots():
                        self.send("Piece cannot move!")
                        continue

                    break

                self.send(game.allowed_moves_graphic(piece_to_be_moved))

                while True:
                    location_input = self.ask_input(
                        f"Enter destination for {piece_to_be_moved} (example: a4)"
                    )

                    if location_input is None:
                        return
                    if location_input == "quit":
                        return

                    if len(location_input) < 2:
                        self.send("Invalid input!")
                        continue

                    end_piece_tuple = self.board.translate(location_input)
                    if not self.board.in_board(end_piece_tuple):
                        self.send("Square outside board!")
                        continue

                    end_case_piece = self.board.get_case(end_piece_tuple)

                    save_start_case_piece = start_case_piece.get_piece()
                    final_start = self.board.roundtrip(
                        start_case_piece.get_pos())
                    final_end = self.board.roundtrip(end_case_piece.get_pos())

                    reussi = game.move(piece_to_be_moved, location_input)

                    if not reussi:
                        self.send("Illegal move! Choose a green box.")
                        continue

                    game.update_clock()
                    self.send(
                        f"> {player.get_pseudo()} moved {save_start_case_piece.get_name()} \
                        from {final_start} to {final_end}"
                    )

                    try:
                        queries.save_coup(self.connection, game.get_idG(),
                                          game.get_turn(), final_start,
                                          final_end)
                    except Exception:
                        pass

                    game.set_turn(game.get_turn() + 1)
                    break

            self.send("Game Over!")

            try:
                old_elo_player1 = game.get_joueur(0).get_elo()
                old_elo_player2 = game.get_joueur(1).get_elo()

                game.get_joueur(0).calculate_elo(old_elo_player2, "won")
                game.get_joueur(1).calculate_elo(old_elo_player1, "loose")

                queries.save_final_game(self.connexion, game, game.get_idG(),
                                        game.get_joueur(0), "won")
                queries.save_final_game(self.connexion, game, game.get_idG(),
                                        game.get_joueur(1), "loose")
            except Exception as e:
                print(f"Error saving game results: {e}")

        except Exception as e:
            print(f"Session Error: {e}")
        finally:
            try:
                self.file.close()
                self.socket.close()
            except Exception:
                pass


if __name__ == "__main__":
    connexion = db.open_connexion()
    if not db.database_already_initialized(connexion):
        print("Initializing database...")
        db.create_database(connexion)
    else:
        print("Database ready.")

    Serveur(connexion).main_server(5555)
