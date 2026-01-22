import socket
import sys
import json
from model.game import Game
from model.color import Color
from model.player import Player
from model.constant import TEXTE_RED, RESET
import db.init_db as db
from db import queries
from colorama import init
from threading import Thread

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
        lstThread = []

        try:
            sock.bind(("0.0.0.0", port))
            sock.listen(1)
            print(f"Server listening on port {port}...")
        except Exception as e:
            print(f"Error binding server: {e}")
            return
        
        try:
            while True:
                    nb_joueur = 0
                    duel = []
                    
                    while nb_joueur < 2:

                        print("Waiting for player...")
                        cli, addr = sock.accept()
                        print(f"New connection from {addr}")

                        print(f"Waiting for player log in")
                        pc = PlayerConnexion(cli, self.connection)
                        while pc.player is None:
                            pc.receive()

                        duel.append((cli, pc))
                        nb_joueur += 1

                    servGame = ServerGame(self, duel[0][0], duel[1][0], self.connection, duel[0][1].player, duel[1][1].player)
                    t = Thread(target=servGame.mainGameServer)
                    t.start()
                    
                    lstThread.append(t)
                    print(f"Partie lancée ! Nombre de threads actifs : {len(lstThread)}")
                            
            

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

class PlayerConnexion(Thread):
    def __init__(self, sock, connexion):
        self.sock = sock
        self.file = sock.makefile(mode="rw", encoding="utf-8")
        self.player = None
        self.connexion = connexion

    def connect(self, name, passwd):
        row = queries.connect_player(self.connexion, name)
        if row is not None:
            password = row[2]
            if password == passwd:
                self.player = Player(row[0], row[1], row[3], [])
                self.send('OK')
            else:
                self.send("ERR")
        else:
            self.send("ERR")

    def register(self, name, passwd):
        id = queries.register_player(self.connexion, name, passwd)
        if id is not None:
            row = queries.collect_player(self.connexion, id)
            self.player = Player(row[0], row[1], row[3], [])
            self.send('OK')
        else:
            self.send("ERR")
    


    def receive(self):
        rep = self.file.readline().strip().split(' ')
        response = rep[0]
        args = rep[1:]

        match response:
            case "register":
                nomJ = args[0]
                mdpJ = args[1]
                self.register(nomJ, mdpJ)

            case "connect":
                nomJ = args[0]
                mdpJ = args[1]
                self.connect(nomJ, mdpJ)
         
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
    
    
        

class ServerGame:
    def __init__(self, serveur, sock1, sock2, connection, player1, player2 ):
        self.serveur = serveur
        self.socket1 = sock1
        self.socket2 = sock2
        self.connexion = connection

        self.replay_count = []

        
        try:
            id_game = queries.save_game(self.connexion)
        except Exception:
            id_game = 1

        self.sess1 = Session(self.serveur, self.socket1, connexion, id_game, player1, player2, Color.WHITE, self)
        self.sess2 = Session(self.serveur, self.socket2, connexion, id_game, player2, player1, Color.BLACK, self) # Session2.wav go stream



        self.current_player = self.sess1
        self.current_color = Color.WHITE

        self.game = Game(id_game, player1, player2)


    def movePiece(self, start, end, color):
        if self.game.current_color() == color.name:
            self.game.move(start, end)
            if color == Color.WHITE:
                self.sess2.send_adversary_move(start, end)
            else:
                self.sess1.send_adversary_move(start, end)
        try:
            queries.save_coup(self.connection, self.game.get_id_g(),
                                self.game.get_turn(), start,
                                end)
        except Exception:
            pass

    

    def abandon(self, color):
        if color == Color.WHITE:
            self.sess2.win()
            self.sess1.loose()
            self.end_game('loose', 'won')

        else:
            self.sess1.win()
            self.sess2.loose()
            self.end_game('won', 'loose')



    def replay(self, color):
        if color not in self.replay_count:
            self.replay_count.append(self.color)
        
        if len(self.replay_count == 2):
            self = ServerGame(self.serveur, self.socket1, self.socket2, self.connexion)

    
    def get_historical(self, color):
        if color == Color.WHITE:
            player = self.game.get_joueur(0)
        else:
            player = self.game.get_joueur(1)
        
        id = player.get_id()
        player = queries.collect_player(self.connexion, id)
        player_obj = None
        if player:
            player_obj = Player(player[0], player[1], player[3])
            player_obj.set_historical(queries.collect_historic_game_of_player(connexion, player_obj))   
            historicals = player_obj.get_historical()
            json_data = json.dumps(historicals)
            print(json_data)
            return "list_games " + json_data
        return "ERR"


    def next(self):
        if self.current_color == Color.WHITE:
            self.current_player = self.sess2
            self.current_color = Color.BLACK
        else:
            self.current_player = self.sess1
            self.current_color = Color.WHITE



    def end_game(self, status_player_1 : str, status_player_2 : str):
        try:
            old_elo_player1 = self.game.get_joueur(0).get_elo()
            old_elo_player2 = self.game.get_joueur(1).get_elo()

            self.game.get_joueur(0).calculate_elo(old_elo_player2, status_player_1)
            self.game.get_joueur(1).calculate_elo(old_elo_player1, status_player_2)

            queries.save_final_game(self.connexion, self.game, self.game.get_id_g(),
                                    self.game.get_joueur(0), status_player_1)
            queries.save_final_game(self.connexion, self.game, self.game.get_id_g(),
                                    self.game.get_joueur(1), status_player_2)
        except Exception as e:
            print(f"Error saving game results: {e}")


    def next_turn(self):
        self.next()
        if self.game.time_white <= 0 or self.game.time_black <= 0:
            self.game.set_finish()

        if self.game.is_checkmate(self.current_color.name):
            self.game.set_finish()
            if self.current_color == Color.BLACK:
                self.sess2.loose()
                self.sess1.win()
                self.end_game("won", "loose")
            else:
                self.sess2.win()
                self.sess1.loose()
                self.end_game("loose", "won")
                

        if self.game.is_stalemate(self.current_color.name):
            self.game.set_finish()
            self.sess1.draw()
            self.sess2.draw()
            self.end_game("equality", "equality")
        
        self.game.update_clock()
        
        

        self.game.set_turn(self.game.get_turn() + 1)

    def set_player(self, color : Color, player : Player):
        if color == Color.BLACK:
            self.game.set_joueur(player, 1)
        else:
            self.game.set_joueur(player, 2)
        

    def mainGameServer(self):
        self.sess1.start('w')
        self.sess2.start('b')
        while self.sess1.opened and self.sess2.opened:
            self.current_player.receive()
            self.next_turn()
            
        
        

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

    def __init__(self, serveur, sock, connection, id_game, player : Player, adversary, color : Color, serverGame : ServerGame):
        self.connection = connection
        self.server = serveur
        self.socket = sock
        self.file = sock.makefile(mode="rw", encoding="utf-8")

        player1 = player
        player2 = adversary

        self.serverGame = serverGame

        try:
            id_game = queries.save_game(self.connexion)
        except Exception:
            id_game = 1

        self.game = Game(id_game, player1, player2)
        self.board = self.game.get_board()

        self.opened = True

        self.color = color


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
    
    def connect(self, name, passwd):
        row = queries.connect_player(self.connection, name)
        password = row[2]
        if password == passwd:
            p = Player(row[0], row.pseudo[1], row.elo[3], [])
            self.send('OK')
            self.serverGame.set_player(self.color, p) 
        else:
            self.send("ERR")
    
    def register(self, name, passwd):
        id = queries.register_player(self.connection, name, passwd)
        if id is not None:
            self.send('OK')
            row = queries.connect_player(self.connection, name)
            p = Player(row[0], row.pseudo[1], row.elo[3], [])
            self.serverGame.set_player(self.color, p) 
        else:
            self.send("ERR")

    def start(self, color):
        self.send(f'start {color}')

    def send_adversary_move(self, start, end):
        self.send("play_ad "+start+" "+end)

    def win(self):
        self.send("win")
    
    def loose(self):
        self.send("loose")
    
    def draw(self):
        self.send("draw")
    
    def exit(self):
        self.send("exit")

    def receive(self):
        rep = self.file.readline().strip().split(' ')
        response = rep[0]
        args = rep[1:]
        print(rep)

        match response:
            case "register":
                try:
                    nomJ = args[0]
                    mdpJ = args[1]
                    self.register(nomJ, mdpJ)
                except:
                    self.send('ERR')
            case "connect":
                try:
                    nomJ = args[0]
                    mdpJ = args[1]
                    self.connect(nomJ, mdpJ)
                except:
                    self.send('ERR')
            case "play":
                try:
                    dep = args[0]
                    arr = args[1]
                    self.serverGame.movePiece(dep, arr, self.color)
                    self.send('OK')
                except:
                    self.send('ERR')
            case "leave":
                try :
                    self.serverGame.abandon(self.color)
                    self.send('OK')
                except:
                    self.send('ERR')
            case "quit":
                try :
                    self.serverGame.abandon(self.color)
                    self.send('OK')
                    self.disconnect()
                except:
                    self.send('ERR')
            case "replay":
                try:
                    self.serverGame.replay(self.color)
                    self.send('OK')
                except:
                    self.send('ERR')
            case "new":
                try:
                    #TODO
                    pass
                except:
                    pass
            case "list_games":
                try:
                    print("nigger")
                    historicals = self.serverGame.get_historical(self.color)
                    print(historicals)
                    self.send(historicals)
                except:
                    self.send('ERR')
            case _:
                self.send('ERR')



    def disconnect(self):
        self.file.close()
        self.socket.close()
        self.opened = False

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



    # def main_session(self):
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

                if game.is_checkmate(player_color):
                    self.send("\n" + TEXTE_RED + "CHECKMATE" + RESET)
                    game.set_finish()
                    looser = game.get_joueur(pos)
                    if pos == 0:
                        winner = game.get_joueur(1)
                    else:
                        winner = game.get_joueur(0)
                    self.send("Player" + winner.get_pseudo() + "won!")
                    self.send("Player" + looser.get_pseudo() + "lost!")
                    return {
                        "result": "checkmate",
                        "winner": winner,
                        "looser": looser
                    }

                if game.is_stalemate(player_color):
                    self.send("\n" + TEXTE_RED + "STALEMATE" + RESET)
                    game.set_finish()
                    self.send("Equality between the player" + game.get_joueur(0) +
                              "and the player" + game.get_joueur(1))
                    return {
                        "result": "stalemate",
                        "white": game.get_joueur(0),
                        "black": game.get_joueur(1)
                    }
                   






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
                    if game.king_in_danger(player_color):
                        self.send("Your king is in check")
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

                    if game.king_in_check_after_move(start_case_piece.get_pos(),
                                                     end_case_piece.get_pos(),
                                                     player_color):
                        self.send(
                            "Move would put your king in danger! Choose another piece."
                        )
                        self.send(self.board.plateau_terminal())
                        break

                    if not reussi:
                        self.send("Illegal move! Choose a green box.")
                        continue

                    game.update_clock()
                    if game.get_time_black() == 0 or game.get_time_white() == 0:
                        if game.get_time_black() == 0:
                            self.send("\n" + TEXTE_RED + "player" +
                                      game.get_joueur(1).get_pseudo() +
                                      "time elapse" + RESET)
                            game.set_finish()
                            looser = game.get_joueur(1)
                            winner = game.get_joueur(0)
                        elif game.get_time_white() == 0:
                            self.send("\n" + TEXTE_RED + "player" +
                                      game.get_joueur(0).get_pseudo() +
                                      "time elapse" + RESET)
                            game.set_finish()
                            looser = game.get_joueur(0)
                            winner = game.get_joueur(1)

                        self.send("Player" + winner.get_pseudo() + "won!")
                        self.send("Player" + looser.get_pseudo() + "lost!")
                        return {
                            "result": "checkmate",
                            "winner": winner,
                            "looser": looser
                        }

                    self.send(
                        f"> {player.get_pseudo()} moved {save_start_case_piece.get_name()} \
                        from {final_start} to {final_end}"
                    )

                    try:
                        queries.save_coup(self.connection, game.get_id_g(),
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

                queries.save_final_game(self.connexion, game, game.get_id_g(),
                                        game.get_joueur(0), "won")
                queries.save_final_game(self.connexion, game, game.get_id_g(),
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
