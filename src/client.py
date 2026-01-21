import socket
from model.color import Color
from model.game import Game
from colorama import init

init()

HOST = "127.0.0.1"
PORT = 5555

class Client:
    def __init__(self, host = "127.0.0.1", port = 5555):
        self.HOST = host
        self.port = port
        self.sock = socket.socket()
        self.start()
        self.file = None
        self.connect()
        self.game = None
        self.receive()

    def start(self):
        print(
        "======================\n"
        "     EchecScolaire    \n"
        "======================")
    
    def connexion_menu(self):
        print("" \
        "1. Se connecter \n"
        "2. S'enregistrer")

    def player_connexion(self):
        print()

    def replay_prompt(self):
        rep_ok = False
        while not rep_ok:
            try :
                print("Voulez-vous rejouer contre la meme personne ?")
                print("1. relancer contre la meme personne \n" \
                "2. relancer contre une autre personne \n"
                "3. Quitter")
                rep = input().strip()

                match rep:
                    case "1":
                        self.replay_same()
                    case "2":
                        self.replay_other()
                    case _:
                        self.exit()
            except:
                pass

    def replay_other(self):
        self.send("new")
        print("En attente d'un autre joueur")
        self.receive()
    def replay_same(self):
        self.send("replay")
        print("En attente de l'autre joueur")
        self.receive()
    

    def connect(self):
        co_ok = False
        while not co_ok:
            try :
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
                co_ok = True
                player_co = False
                while not player_co:
                    self.connexion_menu()
                    commande = input().strip()
                    match commande:
                        case "1":
                            name  = input ("nom :")
                            mdp = input("mot de passe : ")
                            self.send(f'connect {name} {mdp}')
                            rep = self.file.readline().strip()
                            print(rep)
                            if rep == "OK":
                                player_co = True
                        case "2":
                            name  = input ("nom :")
                            mdp = input("mot de passe : ")
                            self.send(f'register {name} {mdp}')
                            rep = self.file.readline().strip()
                            print(rep)
                            if rep == "OK":
                                player_co = True
                        case "quit":
                            self.exit()
                        case _:
                            print("Veuillez entrer un nom/mdp correct")
                print("Connexion a votre compte effectuee avec succes")
                print("Attente d'un autre joueur")
                
            except:
                print("Veuillez entrer des valeurs correctes")

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
    
    def finish_game(self, win):
        if win == "win":
            print('Victoire')
        elif win == "loose":
            print('Defaite')
        else:
            print('Egalite')
        self.demander_rematch()
        

    def exit(self):
        self.file.close()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.quit = True
    
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

                except:
                    print("ERR")
            case "win":
                try:
                    self.finish_game('win')
                except:
                    print("ERR")
            case "loose":
                try:
                    self.finish_game('loose')
                except:
                    print("ERR")
            case "draw":
                try:
                    self.finish_game('draw')
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
                    self.main_client()
                except:
                    print("ERR")
            case 'OK':
                print("Succes")
            case 'ERR':
                print('ERREUR SERVEUR')

    def play_piece(self, start, end):
        self.send(f"play {start} {end}")

    def send_rematch(self):
        self.send("replay")

    def demander_rematch(self):
        print("Remarch ? (y/n)")
        rep = input()
        if rep.upper() == 'Y':
            self.send_rematch()

    def ask_end_piece(self, start):
        self.game.allowed_moves_graphic(start)
        print("Ou voulez vous la déplacer ? (cancel pour annuler le coup)")
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
                break

    def play(self):
        print("Qu'elle piece voulez vous déplacer ? (quit pour quitter, leave pour abandonner )")

        while True:
            command = input().strip().lower()

            if command == "quit":
                self.send("leave")
                self.finish_game()
                self.send("quit")
                self.exit()
                break

            if command == "leave":
                self.send('leave')
                self.finish_game()
                break

            if self.game.king_in_danger(self.game.current_color()):
                print("Vous êtes en echec")

            if len(command) < 2:
                print("c")
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
            self.receive()
        else:
            self.receive()
        self.game.set_turn(self.game.get_turn() + 1)


    def main_client(self):
        self.quit = False
        while not self.quit:
            self.next_turn()


if __name__ == "__main__":
    cl = Client()
