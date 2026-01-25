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
import threading

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
        self.matchmaking_queue = []
        self.sock = None
        self.lst_thread_players = []
        self.verrou = threading.Lock()

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
            print(f"Serveur en écoute sur le port {port}...")
        except Exception as e:
            print(f"Erreur lors de la liaison au serveur : {e}")
            return
        
        try:
            while True:
                cli, addr = sock.accept()
                t = Thread(target=self.handle_lobby, args=(cli,))
                t.start()
                            
        except KeyboardInterrupt:
            print("Le serveur a été interrompu par un utilisateur")
        except Exception as e:
            print(f"Erreur serveur: {e}")
        finally:
            try:
                sock.close()
                print("Connexion serveur fermée. Arrêt")
            except Exception:
                pass
            sys.exit()
    
    def new(self, cli, player):
        try:
            real_pc = None
            with self.verrou:
                threads_to_test = list(self.lst_thread_players)
            for pc in threads_to_test:
                if pc.player.get_id() == player.get_id():
                    real_pc = pc
            with self.verrou:
                self.matchmaking_queue.append((cli, real_pc))
                print(f"Joueur {real_pc.player.get_pseudo()} en attente d'une partie")
            with self.verrou:
                if len(self.matchmaking_queue) >= 2:
                    p1_cli, p1_pc = self.matchmaking_queue.pop(0)
                    p2_cli, p2_pc = self.matchmaking_queue.pop(0)
                    servGame = ServerGame(self, p1_cli, p2_cli, self.connection, p1_pc.player, p2_pc.player)
                    t = Thread(target=servGame.mainGameServer)
                    t.start()
        except Exception as e:
            print(f"erreur : {e}")

    def handle_lobby(self, cli):
        pc = PlayerConnexion(cli, self.connection, self)
        with self.verrou:
            self.lst_thread_players.append(pc)
        while not pc.ready:
            pc.receive()
        if not pc.connected:
            return
        self.matchmaking_queue.append((cli, pc))
        print(f"Joueur {pc.player.get_pseudo()} en attente d'une partie")

        with self.verrou:
            if len(self.matchmaking_queue) >= 2:
                p1_cli, p1_pc = self.matchmaking_queue.pop(0)
                p2_cli, p2_pc = self.matchmaking_queue.pop(0)
                servGame = ServerGame(self, p1_cli, p2_cli, self.connection, p1_pc.player, p2_pc.player)
                t = Thread(target=servGame.mainGameServer)
                t.start()

    def remove_player_thread(self, player):
        with self.verrou:
            if player in self.lst_thread_players: 
                if player.player is not None:
                    pseudo = player.player.get_pseudo() 
                else:
                    pseudo = "Anonyme"
                print(f"Joueur {pseudo} déconnecté")
                self.lst_thread_players.remove(player)


class PlayerConnexion(Thread):
    def __init__(self, sock, connection, server):
        Thread.__init__(self)
        self.server = server
        self.sock = sock
        self.file = sock.makefile(mode="rw", encoding="utf-8")
        self.player = None
        self.connection = connection
        self.ready = False
        self.connected = True

    
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
        if row is not None:
            password = row[2]
            if password == passwd:
                self.player = Player(row[0], row[1], row[3], [])
                print(f"Joueur {self.player.get_pseudo()} connecté")
                self.send('OK')
            else:
                self.send("ERR")
        else:
            self.send("ERR")


    def register(self, name, passwd):
        id = queries.register_player(self.connection, name, passwd)
        if id is not None:
            row = queries.collect_player(self.connection, id)
            self.player = Player(row[0], row[1], row[3], [])
            self.send('OK')
        else:
            self.send("ERR")


    def get_historical(self, player: Player):
        id = player.get_id()
        player = queries.collect_player(self.connection, id)
        player_obj = None
        if player:
            player_obj = Player(player[0], player[1], player[3])
            player_obj.set_historical(queries.collect_historic_game_of_player(self.connection, player_obj))   
            historicals = player_obj.get_historical()
            json_data = json.dumps(historicals)
            return "list_games " + json_data
        return "ERR"


    def get_list_players(self):
        list_players = []
        for player in self.server.lst_thread_players:
            if player.player is not None:
                list_players.append(player.player.get_pseudo())
        json_data = json.dumps(list_players)
        return json_data


    def receive(self):
        try:
            line = self.file.readline()
        except ConnectionResetError:
            line = ""
            
        if not line:
            self.server.remove_player_thread(self)
            self.connected = False
            self.ready = True
            return
            
        rep = line.strip().split(' ')
        response = rep[0]
        args = rep[1:]

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

            case "list_games":
                try:
                    if self.player is not None:
                        historicals = self.get_historical(self.player)
                        self.send(historicals)
                    else:
                        self.send("ERR")
                except:
                    self.send('ERR')

            case "players":
                try:
                    self.send("players " + self.get_list_players())
                except:
                    self.send('ERR')

            case "new":
                try:
                    self.ready = True
                    self.send('OK')
                except:
                    self.send('ERR')
            
            case "quit":
                try:
                    self.send('OK')
                except:
                    self.send('ERR')
                
            case _:
                self.send('ERR')



class ServerGame:
    def __init__(self, serveur : Serveur, sock1, sock2, connection, player1, player2):
        self.serveur = serveur
        self.socket1 = sock1
        self.socket2 = sock2
        self.connection = connection
        self.piece_played = False
        self.replay_count = [] 
        self.player1 = player1
        self.player2 = player2
        try:
            id_game = queries.save_game(self.connection)
        except Exception:
            id_game = 1

        self.sess1 = Session(self.serveur, self.socket1, self.connection, id_game, player1, player2, Color.WHITE, self)
        self.sess2 = Session(self.serveur, self.socket2, self.connection, id_game, player2, player1, Color.BLACK, self)
        self.current_player = self.sess1
        self.current_color = Color.WHITE
        self.promotable_piece = None
        self.game = Game(id_game, player1, player2)


    def new(self, player):
        if player.get_id() == self.player1.get_id():
            self.serveur.new(self.socket1, self.player1)
        else:
            self.serveur.new(self.socket2, self.player2)

    def promote(self, type) -> bool:
        if self.game.get_board().get_case(self.game.get_board().translate(self.promotable_piece)).get_piece().get_color() == Color.WHITE:
            self.sess2.promote(type)
        else:
            self.sess1.promote(type)
        return self.game.promote(self.promotable_piece, type)

    def movePiece(self, start, end, color):
        if self.game.current_color() == color.name:
            if self.game.move(start, end):
                if color == Color.WHITE:
                    self.sess2.send_adversary_move(start, end)
                else:
                    self.sess1.send_adversary_move(start, end)
                self.piece_played = True
            if self.game.get_board().get_case(self.game.get_board().translate(end)).get_piece().can_be_promoted():
                self.promotable_piece = end
                self.current_player.receive()
            try:
                queries.save_coup(self.connection, self.game.get_id_g(),
                                    self.game.get_turn(), start,
                                    end)
            except Exception:
                pass


    def abandon(self, color):
        self.game.set_finish()
        if color == Color.WHITE:
            self.sess2.win()
            self.sess1.loose()
            self.end_game('loose', 'won')

        else:
            self.sess1.win()
            self.sess2.loose()
            self.end_game('won', 'loose')


    def replay(self, color):
        print(f"Demande de replay reçue de {color}")
        if color not in self.replay_count:
            self.replay_count.append(color)

        if color == Color.WHITE:
                self.current_player = self.sess2
        else:
                self.current_player = self.sess1
        
        if len(self.replay_count) == 2:
            p1 = self.game.get_joueur(0)
            p2 = self.game.get_joueur(1)
            try:
                new_id = queries.save_game(self.connection)
            except:
                new_id = self.game.get_id_g() + 1

            self.game = Game(new_id, p1, p2)
            self.game.set_turn(1)
            self.replay_count = []
            self.current_player = self.sess1
            self.current_color = Color.WHITE
            self.mainGameServer()


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

            queries.save_final_game(self.connection, self.game, self.game.get_id_g(),
                                    self.game.get_joueur(0), status_player_1)
            queries.save_final_game(self.connection, self.game, self.game.get_id_g(),
                                    self.game.get_joueur(1), status_player_2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des résultats de jeu: {e}")


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
        self.sess1.game = self.game
        self.sess1.board = self.game.get_board()
        self.sess2.game = self.game
        self.sess2.board = self.game.get_board()
        while self.sess1.opened and self.sess2.opened:
            result = self.current_player.receive()
            if not result:
                break
            if not self.game.get_finish():
                if self.piece_played:
                    self.next_turn()
                    self.piece_played = False


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
        self.player1 = player
        self.player2 = adversary
        self.serverGame = serverGame
        self.game = Game(id_game, self.player1, self.player2)
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

    def promote(self, type):
        self.send(f'promote {type}')

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
        try:
            line = self.file.readline()
        except ConnectionResetError:
            line = ""
            
        if not line:
            self.server.remove_player_thread(self)
            self.connected = False
            self.ready = True
            return
            
        rep = line.strip().split(' ')
        response = rep[0]
        args = rep[1:]
        print(rep)

        match response:
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
                    return True
                except:
                    self.send('ERR')
                    return True
            case "quit":
                try :
                    self.send('OK')
                    self.disconnect()
                except:
                    self.send('ERR')
            case "replay":
                try:
                    self.serverGame.replay(self.color)
                    return True
                except:
                    self.send('ERR')
            case "new":
                try:
                    self.send('OK')
                    self.serverGame.new(self.player1)
                    return False
                except:
                    self.send("ERR")
                    return False
            case "promote":
                try:
                    r = self.serverGame.promote(args[0])
                    if r:
                        self.send('OK')
                    else:
                        self.send('ERR')
                except:
                    pass
            case _:
                self.send('ERR')
        return True

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

if __name__ == "__main__":
    connection = db.open_connexion()
    if not db.database_already_initialized(connection):
        print("Initialisation de la base de données...")
        db.create_database(connection)
    else:
        print("Base de données prête")

    Serveur(connection).main_server(5555)
