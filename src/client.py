import socket
from model.color import Color
from model.game import Game

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

    def player_connexion(self):
        print()

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
                print("Connection effectuee avec succes")
                co_ok = True
                #TODO register, connexion
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

    def move(self, start):
        print("case d'arrivee ?")
        end = input()
        self.game.move(start, end)
        self.play_piece(start, end)

    def play(self):
        print("Que voulez vous jouer ? (quit pour quitter, leave pour abandonner )")
        command = input().strip()
        if command == "quit":
            self.send("leave")
            self.finish_game()
            self.send("quit")
            self.exit()
        if command == "leave":
            self.send('leave')
            self.finish_game()
        else:
            self.move(command)


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
