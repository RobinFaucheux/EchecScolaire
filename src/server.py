import os
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

import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


init()


class Serveur:
    """
    Manages the main chess server logic, player connections, and matchmaking.

    Attributes:
        counter (int): Counter to track sessions or connections.
        connection: The database or network connection object.
        matchmaking_queue (list): List of players waiting to start a game.
        sock: The main server socket for listening to new clients.
        lst_thread_players (list): List of active player threads.
        verrou (Lock): A threading lock to prevent data conflicts.
    """

    def __init__(self, connection):
        self.counter = 0
        self.connection = connection
        self.matchmaking_queue = []
        self.sock = None
        self.lst_thread_players = []
        self.pub_key = ''
        self.priv_key = ''
        self.verrou = threading.Lock()
        self.encoded_pub = ''

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
            self.priv_key = ec.generate_private_key(ec.SECP256R1())
            self.pub_key = self.priv_key.public_key()

            pub_bytes = self.pub_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Base64 encode the key for the string message
            self.encoded_pub = base64.b64encode(pub_bytes).decode()
        except Exception as e:
            print(f'Erreur lors de la generation des cles : {e}')

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
                servGame = ServerGame(self, p1_cli, p2_cli, self.connection, p1_pc.player, p2_pc.player, p1_pc.final_key, p2_pc.final_key)
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
    """
    Manages a single player's connection and communication in a separate thread.
    
    Attributes:
        server: The main server instance.
        sock: The client's socket.
        file: A file-like object for reading and writing data (UTF-8).
        player: The player data associated with this connection.
        connection: The database or network connection object.
        ready: Boolean to track if the player is ready to play.
        connected: Boolean to track if the player is currently online.
    """
    def __init__(self, sock, connection, server):
        Thread.__init__(self)
        self.server = server
        self.sock = sock
        self.file = sock.makefile(mode="rw", encoding="utf-8")
        self.player = None
        self.connection = connection
        self.ready = False
        self.connected = True
        self.connected = True
        self.final_key = ''
        self.send(f'sync#{self.server.encoded_pub}', False)
        self.receive_key()

    
    def send(self, message, encrypted=True):
        try:
            if encrypted and self.final_key:
                payload = self.encrypt(message)
                self.file.write(payload + '\n')
            else:
                self.file.write(message + "\n")
            self.file.flush()
        except Exception as e:
            print(f"Send error: {e}")


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
        """
        Checks if the provided name and password already exist in the database. 
        Returns an error if they do; otherwise, creates the new player in the 
        database and initializes the player object
        """
        id = queries.register_player(self.connection, name, passwd)
        if id is not None:
            row = queries.collect_player(self.connection, id)
            self.player = Player(row[0], row[1], row[3], [])
            self.send('OK')
        else:
            self.send("ERR")


    def get_historical(self, player: Player):
        """
        Retrieves the player's match history from the database and converts it into JSON format.
        """
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


    def receive_key(self):
        try:
            line = self.file.readline().strip()
        except Exception:
            line = ""
            
        if not line:
            self.server.remove_player_thread(self)
            self.connected = False
            self.ready = True
            return

        parts = line.split('#', 1)
        if len(parts) < 2:
            return

        response, arg = parts[0], parts[1]
        
        if response == 'sync':
            try:
                client_pub_bytes = base64.b64decode(arg)
                
                peer_pub_key = serialization.load_pem_public_key(client_pub_bytes)
                
                shared_secret = self.server.priv_key.exchange(ec.ECDH(), peer_pub_key)

                self.final_key = HKDF(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=None,
                    info=b'session'
                ).derive(shared_secret)
                
                print(f"Encryption established with a new client.")
            except Exception as e:
                print(f"Server Key Exchange Error: {e}")

    def encrypt(self, msg_str):
        if not self.final_key:
            return msg_str
            
        aesgcm = AESGCM(self.final_key)
        nonce = os.urandom(12)  
        ciphertext = aesgcm.encrypt(nonce, msg_str.encode(), None)
        
        return base64.b64encode(nonce + ciphertext).decode()

    def decrypt_msg(self, msg_str):
        if not self.final_key or not msg_str:
            return msg_str
        
        try:
            combined_bytes = base64.b64decode(msg_str)
            
            aesgcm = AESGCM(self.final_key)
            nonce = combined_bytes[:12]
            ciphertext = combined_bytes[12:]
            
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            print(decrypted_bytes.decode())

            return decrypted_bytes.decode()
        except Exception as e:
            if "sync" in msg_str: return msg_str 
            return f"Error decryption: {e}"

    def receive(self):
        try:
            line = self.decrypt_msg(self.file.readline().strip())
        except ConnectionResetError:
            line = ""
            
        if not line:
            self.server.remove_player_thread(self)
            self.connected = False
            self.ready = True
            return
            
        rep = line.strip().split('#')
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
                    self.send("players#" + self.get_list_players())
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
    """
    Manages a live chess match between two players.

    This class synchronizes the game logic, the two player sessions (sockets), 
    and the database storage.

    Attributes:
        serveur: Reference to the main Server instance.
        socket1 / socket2: Communication sockets for both players.
        connection: Database connection to save match results.
        player1 / player2: Player data objects.
        game: The core chess logic instance (rules, board state).
        sess1 / sess2: Individual session handlers for each player.
        current_player: The session of the player whose turn it is.
        current_color: The color (White/Black) currently moving.
        replay_count (list): Tracks votes to restart the game.
    """
    def __init__(self, serveur : Serveur, sock1, sock2, connection, player1, player2, final_key_1, final_key_2):
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

        self.sess1 = Session(self.serveur, self.socket1, self.connection, id_game, player1, player2, Color.WHITE, self, final_key_1)
        self.sess2 = Session(self.serveur, self.socket2, self.connection, id_game, player2, player1, Color.BLACK, self, final_key_2) # session2.wav go stream
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
        """
        Executes a move if it's the player's turn and the move is valid.Sends the move to the opponent.
        Checks if a pawn can be promoted at the destination. Saves the move to the database.
        """
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
        """
        Ends the game immediately when a player forfeits.
        """
        if color == Color.WHITE:
            self.sess2.win()
            self.sess1.loose()
            self.end_game('loose', 'won')

        else:
            self.sess1.win()
            self.sess2.loose()
            self.end_game('won', 'loose')


    def replay(self, color):
        """
        Registers a replay request from a player.
        """
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
        """
        Switches the turn to the next player.
        """
        if self.current_color == Color.WHITE:
            self.current_player = self.sess2
            self.current_color = Color.BLACK
        else:
            self.current_player = self.sess1
            self.current_color = Color.WHITE


    def end_game(self, status_player_1 : str, status_player_2 : str):
        """
        Finalizes the game results. Calculates the new Elo ratings for both players and saves 
        the final match data to the database.
        """
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
            print(f"Erreur lors de la sauvegarde des résultats de jeu: {e}")


    def next_turn(self):
        """
        Processes the transition to the next turn. Checks for timeout, checkmate, or stalemate.
        If the game is over, it triggers the end_game sequence and notifies players.
        """
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
        """
        Assigns a player object to a specific color (Black or White) inside the game logic.
        """
        if color == Color.BLACK:
            self.game.set_joueur(player, 1)
        else:
            self.game.set_joueur(player, 2)
        

    def mainGameServer(self):
        """
        Initializes player sessions, shares the board state, and continuously listens for client moves 
        until the game ends or a player disconnects.
        """
        self.sess1.start('w')
        self.sess2.start('b')
        self.sess1.game = self.game
        self.sess1.board = self.game.get_board()
        self.sess2.game = self.game
        self.sess2.board = self.game.get_board()
        while self.sess1.opened and self.sess2.opened:
            result = self.current_player.receive()
            if not result:
                break #Maybe cette ligne casse la deconnexion
            if not self.game.get_finish():
                if self.piece_played:
                    self.next_turn()
                    self.piece_played = False


class Session:
    """
    Represents an active communication bridge between a player and the game server.

    Attributes:
        connection: Database connection for queries.
        server: Reference to the main Server instance.
        socket: The network socket for this client.
        file: Text stream wrapper for easy reading and writing.
        player1: The player object associated with this session.
        player2: The opponent player object.
        serverGame: Reference to the ServerGame controller managing the match.
        game: The chess logic instance.
        board: The current state of the chess board.
        opened (bool): True if the connection is still active.
        color (Color): The piece color assigned to this player (White/Black).
    """

    def __init__(self, serveur, sock, connection, id_game, player : Player, adversary, color : Color, serverGame : ServerGame, final_key):
        self.connection = connection
        self.server = serveur
        self.socket = sock
        self.file = sock.makefile(mode="rw", encoding="utf-8")
        self.player1 = player
        self.final_key = final_key
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

    def encrypt(self, msg_str):
        if not self.final_key:
            return msg_str
            
        aesgcm = AESGCM(self.final_key)
        nonce = os.urandom(12)  
        ciphertext = aesgcm.encrypt(nonce, msg_str.encode(), None)
        
        return base64.b64encode(nonce + ciphertext).decode()

    def decrypt_msg(self, msg_str):
        if not self.final_key or not msg_str:
            return msg_str
        
        try:
            combined_bytes = base64.b64decode(msg_str)
            
            aesgcm = AESGCM(self.final_key)
            nonce = combined_bytes[:12]
            ciphertext = combined_bytes[12:]
            
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            print(decrypted_bytes.decode())
            return decrypted_bytes.decode()
        except Exception as e:
            if "sync" in msg_str: return msg_str 
            return f"Error decryption: {e}"


    def send(self, message, encrypted=True):
        try:
            if encrypted and self.final_key:
                payload = self.encrypt(message)
                self.file.write(payload + '\n')
            else:
                self.file.write(message + "\n")
            self.file.flush()
        except Exception as e:
            print(f"Send error: {e}")
    
    def connect(self, name, passwd):
        """
        Authenticates a player using their name and password.
        """
        row = queries.connect_player(self.connection, name)
        password = row[2]
        if password == passwd:
            p = Player(row[0], row.pseudo[1], row.elo[3], [])
            self.send('OK')
            self.serverGame.set_player(self.color, p) 
        else:
            self.send("ERR")
    
    def register(self, name, passwd):
        """
        Registers a new player in the database.
        """
        id = queries.register_player(self.connection, name, passwd)
        if id is not None:
            self.send('OK')
            row = queries.connect_player(self.connection, name)
            p = Player(row[0], row.pseudo[1], row.elo[3], [])
            self.serverGame.set_player(self.color, p) 
        else:
            self.send("ERR")

    def promote(self, type):
        self.send(f'promote#{type}')

    def start(self, color):
        self.send(f'start#{color}')

    def send_adversary_move(self, start, end):
        self.send("play_ad#"+start+"#"+end)

    def win(self):
        self.send("win")
    
    def loose(self):
        self.send("loose")
    
    def draw(self):
        self.send("draw")
    
    def exit(self):
        self.send("exit")

    def receive(self):
        """
        Receives messages from the client and redirects them to the correct functions 
        based on the message content.
        """
        try:
            line = self.decrypt_msg(self.file.readline().strip())
        except ConnectionResetError:
            line = ""
            
        if not line:
            self.server.remove_player_thread(self)
            self.connected = False
            self.ready = True
            return
            
        rep = line.strip().split('#')
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
        """
        Safely closes the communication stream and the network socket.
        """
        self.file.close()
        self.socket.close()
        self.opened = False


if __name__ == "__main__":
    connection = db.open_connexion()
    if not db.database_already_initialized(connection):
        print("Initialisation de la base de données...")
        db.create_database(connection)
    else:
        print("Base de données prête")

    Serveur(connection).main_server(5555)
