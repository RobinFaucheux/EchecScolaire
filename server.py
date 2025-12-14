import socket 
from src.model import *

class serveur:

    def __init__(self):
        self.counter=0

    def mainServer(self,port):
        sock= socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(10)
        try:
            while True:
                cli, addr = sock.accept()
                sess = Session(self,cli)
                sess.mainSession()
        except KeyboardInterrupt:
            print("Server interrupted by user, shutting down...")
        finally:
            try:
                sock.close()
            except Exception:
                pass

class Session:
    def __init__(self, serveur, sock):
        self.server=serveur
        self.socket=sock
        self.file= sock.makefile(mode="rw")
        self.game=Game("Player1","Player2")
        self.turn=1

    def mainSession(self):
        while True:
            line = self.file.readline().strip()
            if line == "quit":
                print("quit reçu")
                self.file.write("quit\n")
                self.file.flush()
                break
            line1 = self.game.board.translate(line[:2])
            print(line1)
            line2 = self.game.board.translate(line[2:4])
            print(line2)
            try:
                if self.game.board.in_board(line1) and self.game.board.in_board(line2):
                    self.file.write("Le coup a bien été reçu\n")
                    self.file.flush()
                    print(f"Le joueur {self.game.joueurs[(self.turn+1)%2]} a joué le coup {line}")
                    self.turn += 1
                else:
                    self.file.write(f"Le coup {line} n'est pas valide\n")
                    self.file.flush()
            except Exception as e:
                print("Erreur lors du traitement du coup:", e)
                try:
                    self.file.write(f"Erreur le coup {line} est invalide\n")
                    self.file.flush()
                except Exception:
                    pass
        
        try:
            self.file.close()
        except Exception:
            pass
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self.socket.close()
        except Exception:
            pass


serveur().mainServer(5555)