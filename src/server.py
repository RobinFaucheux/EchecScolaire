import socket
import sys
import json
import struct
import crypto_utils
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
        self.matchmaking_queue = []
        self.sock = None
        self.lstThread = []


    def handshake(self, sock):
        """Performs ECDH handshake and returns session key."""
        try:
            priv, pub = crypto_utils.generer_cles_ecdh()
            pub_pem = crypto_utils.serialiser_cle_publique(pub)
            sock.sendall(struct.pack('!I', len(pub_pem)) + pub_pem)
            len_data = sock.recv(4)
            if not len_data: return None
            pub_len = struct.unpack('!I', len_data)[0]
            client_pub_pem = sock.recv(pub_len)
            client_pub = crypto_utils.charger_cle_publique(client_pub_pem)
            shared_secret = crypto_utils.calculer_secret_partage(priv, client_pub)
            return crypto_utils.deriver_cle_session(shared_secret)
        except Exception as e:
            print(f"Handshake error: {e}")
            return None    

    def main_server(self, port):
        """
        Starts the server and listens for incoming client connections.
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
            while True:
                cli, addr = sock.accept()
                print(f"New connection from {addr}")
                t = Thread(target=self.handle_lobby, args=(cli,))
                t.start()

                            
        except KeyboardInterrupt:
            print("Server interrupted by user.")
        except Exception as e:
            print(f"Server Error: {e}")
        finally:
            try:
                self.sock.close()
                print("Server socket closed. Exiting.")
            except Exception:
                pass
            sys.exit()
    
    def new(self, cli1):
        print("Waiting for player...")
        cli, addr = self.sock.accept()
        print(f"New connection from {addr}")

        # Handshake
        session_key = self.handshake(cli)
        if not session_key:
            cli.close()
            return

        print(f"Waiting for player log in")
        pc = PlayerConnexion(cli, self.connection, session_key)
        while pc.player is None:
            pc.receive()
        
        servGame = ServerGame(self, cli1.socket, cli, self.connection, cli1.player1, pc.player)
        t = Thread(target=servGame.mainGameServer)
        t.start()
        
        self.lstThread.append(t)



    def handle_lobby(self, cli):
        print(">>> handle_lobby called!")
        sys.stdout.flush()
        # Handshake d'abord
        print(">>> Calling handshake...")
        sys.stdout.flush()
        session_key = self.handshake(cli)
        print(f">>> handshake returned: {session_key is not None}")
        sys.stdout.flush()
        if not session_key:
            print("Handshake failed, closing connection")
            cli.close()
            return
        
        print("Handshake successful")
        
        pc = PlayerConnexion(cli, self.connection, session_key)
        while not pc.ready:
            if not pc.receive():
                print("Client disconnected")
                cli.close()
                return
        self.matchmaking_queue.append((cli, pc))
        print(f"Joueur {pc.player.get_pseudo()} en attente.")
        if len(self.matchmaking_queue) >= 2:
            p1_cli, p1_pc = self.matchmaking_queue.pop(0)
            p2_cli, p2_pc = self.matchmaking_queue.pop(0)
            servGame = ServerGame(self, p1_pc, p2_pc, self.connection, p1_pc.player, p2_pc.player)
            t = Thread(target=servGame.mainGameServer)
            t.start()



class PlayerConnexion(Thread):
    def __init__(self, sock, connexion, session_key=None):
        self.sock = sock
        if session_key:
            self.file = crypto_utils.SocketSecurise(sock, session_key)
        else:
            self.file = sock.makefile(mode="rw", encoding="utf-8")
        self.player = None
        self.connexion = connexion
        self.ready = False

    
    def send(self, message):
        """
        Sends a message to the client through the socket.
        """
        try:
            self.file.write(message + "\n")
            self.file.flush()
        except Exception:
            pass


    def connect(self, name, passwd):
        row = queries.connect_player(self.connexion, name)
        if row is not None:
            hashed_stored = row[2]
            # Vérifie le mot de passe hashé
            if crypto_utils.verifier_mdp(hashed_stored, passwd):
                self.player = Player(row[0], row[1], row[3], [])
                self.send('OK')
            else:
                self.send("ERR")
        else:
            self.send("ERR")


    def register(self, name, passwd):
        # Hasher le mot de passe avant stockage
        hashed = crypto_utils.hacher_mdp(passwd)
        id = queries.register_player(self.connexion, name, hashed)
        if id is not None:
            row = queries.collect_player(self.connexion, id)
            self.player = Player(row[0], row[1], row[3], [])
            self.send('OK')
        else:
            self.send("ERR")


    def get_historical(self, player: Player):
        id = player.get_id()
        player = queries.collect_player(self.connexion, id)
        player_obj = None
        if player:
            player_obj = Player(player[0], player[1], player[3])
            player_obj.set_historical(queries.collect_historic_game_of_player(self.connexion, player_obj))   
            historicals = player_obj.get_historical()
            json_data = json.dumps(historicals)
            return "list_games " + json_data
        return "ERR"
    

    def receive(self):
        try:
            line = self.file.readline()
            if not line:
                return False  # Connexion fermée
            rep = line.strip().split(' ')
            response = rep[0]
            args = rep[1:]
        except Exception as e:
            print(f"Receive error: {e}")
            return False

        # Tant que le joueur n'est pas en partie, n'accepter que register, connect, list_games, new
        if not hasattr(self, 'serverGame') or self.serverGame is None:
            if response not in ["register", "connect", "list_games", "new"]:
                self.send("ERR Pas encore en partie")
                return True

        match response:
            case "register":
                if len(args) < 2:
                    self.send("ERR Usage: register nomJoueur motDePasse")
                    return True
                nomJ = args[0]
                mdpJ = args[1]
                if not (3 <= len(nomJ) <= 10) or ' ' in nomJ:
                    self.send("ERR Nom joueur invalide")
                    return True
                if len(mdpJ) < 6:
                    self.send("ERR Mot de passe trop court")
                    return True
                self.register(nomJ, mdpJ)

            case "connect":
                if len(args) < 2:
                    self.send("ERR Usage: connect nomJoueur motDePasse")
                    return True
                nomJ = args[0]
                mdpJ = args[1]
                self.connect(nomJ, mdpJ)

            case "list_games":
                try:
                    if self.player is not None:
                        historicals = self.get_historical(self.player)
                        self.send(historicals)
                    else:
                        self.send("ERR")
                except:
                    self.send('ERR')
            case "new":
                self.ready = True
                self.send("OK")
            # Les autres commandes ne sont traitées que si self.serverGame existe
            case _:
                if not hasattr(self, 'serverGame') or self.serverGame is None:
                    self.send('ERR Pas encore en partie')
                else:
                    return False  # Laisser la session de jeu prendre le relais
        return True  # Continuer à recevoir



class ServerGame:
    def __init__(self, serveur : Serveur, pc1, pc2, connection, player1, player2):
        self.serveur = serveur
        self.pc1 = pc1  # PlayerConnexion avec SocketSecurise
        self.pc2 = pc2
        self.connexion = connection

        self.replay_count = []

        
        try:
            id_game = queries.save_game(self.connexion)
        except Exception:
            id_game = 1

        self.sess1 = Session(self.serveur, pc1, connection, id_game, player1, player2, Color.WHITE, self)
        self.sess2 = Session(self.serveur, pc2, connection, id_game, player2, player1, Color.BLACK, self)



        self.current_player = self.sess1
        self.current_color = Color.WHITE

        self.game = Game(id_game, player1, player2)


    def new(self, session):
        self.serveur.new(session)

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
    """

    def __init__(self, serveur, pc, connection, id_game, player : Player, adversary, color : Color, serverGame : ServerGame):
        self.connection = connection
        self.server = serveur
        self.socket = pc.sock
        self.file = pc.file  # Utilise le SocketSecurise du PlayerConnexion

        player1 = player
        player2 = adversary

        self.serverGame = serverGame

        self.game = Game(id_game, player1, player2)
        self.board = self.game.get_board()

        self.opened = True

        self.color = color


    def format_time(self, seconds: float) -> str:
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02}:{seconds % 60:02}"

    def send(self, message):
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
        try:
            line = self.file.readline()
            if not line:
                return False  # Connexion fermée
            rep = line.strip().split(' ')
            response = rep[0]
            args = rep[1:]
        except Exception as e:
            print(f"Receive error: {e}")
            return False

        # Tant que le joueur n'est pas en partie, n'accepter que register, connect, list_games, new
        if not hasattr(self, 'serverGame') or self.serverGame is None:
            if response not in ["register", "connect", "list_games", "new"]:
                self.send("ERR Pas encore en partie")
                return True

        match response:
            case "register":
                if len(args) < 2:
                    self.send("ERR Usage: register nomJoueur motDePasse")
                    return True
                nomJ = args[0]
                mdpJ = args[1]
                if not (3 <= len(nomJ) <= 10) or ' ' in nomJ:
                    self.send("ERR Nom joueur invalide")
                    return True
                if len(mdpJ) < 6:
                    self.send("ERR Mot de passe trop court")
                    return True
                self.register(nomJ, mdpJ)

            case "connect":
                if len(args) < 2:
                    self.send("ERR Usage: connect nomJoueur motDePasse")
                    return True
                nomJ = args[0]
                mdpJ = args[1]
                self.connect(nomJ, mdpJ)

            case "list_games":
                try:
                    if self.player is not None:
                        historicals = self.get_historical(self.player)
                        self.send(historicals)
                    else:
                        self.send("ERR")
                except:
                    self.send('ERR')
            case "new":
                self.ready = True
                self.send("OK")

            case "play":
                if len(args) == 2:
                    start = args[0]
                    end = args[1]
                    self.serverGame.movePiece(start, end, self.color)
                else:
                    self.send("ERR")

            # Les autres commandes ne sont traitées que si self.serverGame existe
            case _:
                if not hasattr(self, 'serverGame') or self.serverGame is None:
                    self.send('ERR Pas encore en partie')
                else:
                    return False  # Laisser la session de jeu prendre le relais
        return True  # Continuer à recevoir

    def disconnect(self):
        self.file.close()
        self.socket.close()
        self.opened = False

    def ask_input(self, prompt):
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
    connexion = db.open_connexion()
    if not db.database_already_initialized(connexion):
        print("Initializing database...")
        db.create_database(connexion)
    else:
        print("Database ready.")

    Serveur(connexion).main_server(5555)