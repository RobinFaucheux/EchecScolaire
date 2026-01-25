import socket
from model.color import Color
from model.game import Game
from model.constant import REPLAY_TIMEOUT
from colorama import init
import json
import select

init()

HOST = "127.0.0.1"
PORT = 5555

class Client:
    def __init__(self, host = "127.0.0.1", port = 5555):
        self.HOST = host
        self.port = port
        self.sock = socket.socket()
        self.file = None
        self.quit = False
        self.game = None
        self.player_co = False
        self.promotable_piece = None
        self.start()
        self.lobby()
        if not self.quit:
            self.receive()
            self.main_client()

    def start(self):
        print(
        "======================\n"
        "     EchecScolaire    \n"
        "======================")

    def connection_to_server(self):
        print("Entrez l'ip du serveur (defaut : serveur local)")
        host = str(input(""))
        if host == "":
            host = "localhost"
        self.host = host
        print("Entrez le port du serveur (defaut : 5555)")
        port = input("")
        if port == "":
            port = 5555
            self.port = port
        else:
            port = int(port)
            self.port = port       
        self.sock.connect((self.host, self.port))
        self.file = self.sock.makefile(mode="rw")
        print("Connection au serveur effectuee avec succes")

    def connection_player(self):
        print("1. Se connecter \n" \
              "2. S'inscrire \n" \
              "3. Quitter")
        commande = input().strip()
        match commande:
            case "1":
                try :
                    name = ''
                    mdp = ''
                    while (name == '' or mdp == ''):    
                        name  = input ("nom :")
                        mdp = input("mot de passe : ")
                        self.send(f'connect {name} {mdp}')
                        rep = self.file.readline().strip()
                        if rep == "OK":
                            self.player_co = True
                        else :
                            print('Erreur de connexion')
                except :
                    print("Erreur")
            case "2":
                try :
                    name = ''
                    mdp = ''
                    while (name == '' or mdp == ''):
                        name  = input ("nom :")
                        mdp = input("mot de passe : ")
                        self.send(f'register {name} {mdp}')
                        rep = self.file.readline().strip()
                        if rep == "OK":
                            self.player_co = True
                        else:
                            print("Erreur d'inscription")
                except:
                    print("Erreur")
            case "3":
                try :
                    self.send("quit")
                    rep = self.file.readline().strip()
                    if rep == "OK":
                        self.exit()
                        return None
                except:
                    print("Erreur")
            case _:
                print("Veuillez entrer un nom/mdp correct")
    
    def menu_before_game(self):
        ready = False
        print("" \
        "1. Voir son historique \n"
        "2. Voir la liste des joueurs\n"
        "3. Chercher une game \n"
        "4. Se déconnecter")
        commande = input().strip()
        match commande:
            case "1":
                self.send("list_games")
                self.receive()
            case "2":
                self.send("players")
                self.receive()
            case "3":
                self.send("new")  
                rep = self.file.readline().strip()
                if rep == "OK":
                    ready = True
                    print("En attente de joueurs")
            case "4":
                self.send("quit")
                rep = self.file.readline().strip()
                if rep == "OK":
                    self.exit()
                    return True
                pass
            case _:
                print('Veuillez entrer une commande correcte')
        return ready

    def lobby(self):
        ready = False
        while not ready and not self.quit:
            try :
                if self.file == None: 
                    self.connection_to_server()

                if not self.player_co:
                    while self.player_co is False and not self.quit:
                        self.connection_player()
                    if self.quit:
                        return
                if self.player_co is not None:
                    print("Connexion réussie\nBienvenue !")
                    ready = self.menu_before_game()
                else : 
                    ready = True
            except:
                print("Veuillez entrer des valeurs correcte")

    def end_prompt(self):
        rep_ok = False
        while not rep_ok:
            try :
                print("Que voulez vous faire ?")
                print("1. relancer contre une nouvelle personne \n" \
                "2. Retourner au menu d'accueil \n"
                "3. Quitter")
                rep = input().strip()
                match rep:
                    case "1":                 
                        rep_ok = True
                        self.replay_other()
                    case "2":                    
                        rep_ok = True
                        self.lobby()
                    case "3":
                        rep_ok = True
                        self.send("quit")
                        rep = self.file.readline().strip()
                        if rep == "OK":
                            self.exit()
            except Exception as e:
                print(f"Erreur : {e}")

    def replay_other(self):
        self.send("new")
        print("En attente d'un autre joueur")
        self.receive()

    

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
    
    def finish_game(self, win, rematch):
        if win == "win":
            print('Victoire')
        elif win == "loose":
            print('Defaite')
        else:
            print('Egalite')
        self.game = None
        if rematch:
            self.demander_rematch()

    def exit(self):
        self.quit = True
        self.player_co = False
        self.file.close()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    def receive(self):
        rep = self.file.readline().strip().split(' ')
        response = rep[0]
        args = rep[1:]
        
        match response:
            case "play_ad":
                try :
                    start = args[0]
                    end = args[1]
                    self.game.move(start, end)
                    if self.game.get_board().get_case(self.game.get_board().translate(end)).get_piece().can_be_promoted():
                        self.promotable_piece = end
                        self.receive()
                except:
                    print("ERR")
            case "win":
                try:
                    self.finish_game('win', True)
                    return
                except:
                    print("ERR")
            case "loose":
                try:
                    self.finish_game('loose', True)
                    return
                except:
                    print("ERR")
            case "draw":
                try:
                    self.finish_game('draw', True)
                    return
                except:
                    print('ERR')
            case 'exit':
                try:
                    self.exit()
                except:
                    print("ERR")
            case 'start':
                try :
                    color = args[0]
                    if color == 'w':
                        self.color = Color.WHITE
                    else:
                        self.color = Color.BLACK
                    self.game = Game(0, None, None)
                except:
                    print("ERR")
            case 'list_games':
                json_str = " ".join(args)
                self.get_historicals(json_str)
            case 'players':
                json_str = " ".join(args)
                self.get_players(json_str)
            case 'OK':
                print("Succes")
            case 'ERR':
                print('ERREUR SERVEUR')
            case 'promote':
                try :
                    if self.promotable_piece is not None:
                        self.game.promote(self.promotable_piece, args[0])
                except:
                    print('err')

    def play_piece(self, start, end):
        self.send(f"play {start} {end}")

    def send_rematch(self):
        self.send("replay")
        print("En attente de l'autre joueur")
        ready = select.select([self.sock], [], [], REPLAY_TIMEOUT)
        if ready[0]:
            self.receive()
        else:
            print("Replay refuse ou expire")
            self.end_prompt()

    def send_ask_to_do_after_game(self):
        print("" \
        "1. Relancer une nouvelle partie \n"
        "2. Revenir au menu principal\n"
        "3. Se déconnecter")

    def demander_rematch(self):
        rep = ""
        while rep not in ["y", "n"]:
            rep = input(f"Rematch ({REPLAY_TIMEOUT}s)? (y/n)")
        if rep.upper() == 'Y':
            self.send_rematch()
        else:
            self.end_prompt()
            

    def get_historicals(self, json_str):
        historicals = json.loads(json_str)
        if not historicals:
            print("Vous n'avez aucune partie enregistrée dans votre historique")
            return
        print("======================")
        print("      HISTORIQUE      ")
        print("======================")
        print("")
        for game in historicals:
            adversaire = game.get("pseudo_joueur", "Inconnu")
            resultat = game.get("result", "En cours")
            print(f"adversaire : {adversaire} | {resultat}")  
        print("-" * 22)

    def get_players(self, json_str):
        players = json.loads(json_str)
        if not players:
            print("Aucun joueur disponible")
            return
        chaine = "Liste des joueurs connectés : " + " / ".join(players)
        print(chaine)


    def ask_end_piece(self, start):
        self.game.allowed_moves_graphic(start)
        print("Où voulez vous la déplacer ? (cancel pour annuler le coup)")
        start_piece_tuple = self.game.get_board().translate(start)
        start_case_piece = self.game.get_board().get_case(start_piece_tuple)

        while True:
            end = input().strip().lower()

            if end == "cancel":
                self.game.get_board().plateau_terminal()
                self.play()
                break

            if len(end) < 2:
                print("Rentrez une lettre suivie d'un chiffre")
                continue

            if not (end[0].isalpha() and
                    end[1:].isdigit()):
                print("Rentrez une lettre suivie d'un chiffre")
                continue

            end_piece_tuple = self.game.get_board().translate(end)
            if not self.game.get_board().in_board(end_piece_tuple):
                print("Cette case n'est pas sur le plateau")
                continue
            
            end_case_piece = self.game.get_board().get_case(end_piece_tuple)
            if self.game.king_in_check_after_move(start_case_piece.get_pos(),
                                             end_case_piece.get_pos(),
                                             self.game.current_color()):
                print(
                    "Votre mouvement met votre roi en echec, choisissez une autre piece")
                self.game.get_board().plateau_terminal()
                self.play()
                break

            else :
                reussi = self.game.move(start, end)

                if not reussi:
                    print("Mouvement impossible, veuillez choisir une case verte")
                    continue
                self.play_piece(start, end)
                if self.game.get_board().get_case(self.game.get_board().translate(end)).get_piece().can_be_promoted():
                    t = self.ask_promote()
                    self.game.promote(end, t)

                break

    def ask_promote(self) -> str:
        available_promotions = ['q', 'r', 'b', 'k']
        res = ''
        while res not in available_promotions:
            print("Entrez la piece en laquelle vous voulez qu'elle se transforme (q, r, b, k)")
            res = input()
        self.send(f'promote {res}')
        self.receive()
        return res


    def play(self):
        print("Quelle piece voulez vous déplacer ? (quit pour quitter, leave pour abandonner)")

        while True:
            command = input().strip().lower()

            if command == "quit":
                self.send("leave") 
                self.send("quit")
                while True:
                    line = self.file.readline().strip()
                    if line == "OK" or not line:
                        break
                self.finish_game("loose", False)
                self.exit()
                break

            if command == "leave":
                self.send('leave')
                self.receive()
                break

            if self.game.king_in_danger(self.game.current_color()):
                print("Vous êtes en echec")

            if len(command) < 2:
                print("Rentrez une lettre suivie d'un chiffre")
                continue

            if not (command[0].isalpha() and command[1:].isdigit()):
                print("Rentrez une lettre suivie d'un chiffre")
                continue

            start_piece_tuple = self.game.get_board().translate(command)
            if not self.game.get_board().in_board(start_piece_tuple):
                print("Cette case n'est pas sur le plateau")
                continue

            start_case_piece = self.game.get_board().get_case(start_piece_tuple)
            if start_case_piece.get_piece() is None:
                print("Pas de piece sur cette case")
                continue

            if start_case_piece.get_piece().get_color().name != self.game.current_color():
                print("Ce n'est pas votre pièce")
                continue

            if start_case_piece.get_piece().accessible_spots() == []:
                print("Cette pièce ne peut pas bouger")
                continue

            else:
                self.ask_end_piece(command)
                break


    def next_turn(self):
        self.game.get_board().plateau_terminal()
        if self.game.current_color() == self.color.name:
            self.play()
            if self.game is None:
                return
            self.receive()
        else:
            self.receive()
        if self.game is None:
            return
        self.game.set_turn(self.game.get_turn() + 1)
        self.game.update_clock()
        if self.color == Color.WHITE:
            print(f"Temps restant : {self.game.get_time_black()}")
            print(f"Temps restant de l'adversaire : {self.game.get_time_white()}")
        else:
            print(f"Temps restant : {self.game.get_time_white()}")
            print(f"Temps restant de l'adversaire : {self.game.get_time_black()}")

    def main_client(self):
        self.quit = False
        while not self.quit:
            if self.game is None:
                self.receive()
            else:
                self.next_turn()


if __name__ == "__main__":
    cl = Client()
