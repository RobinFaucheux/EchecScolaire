import socket
from src.model import *


HOST = "127.0.0.1"
PORT = 5555

move = input("Entrez le coup à jouer ou quit: ")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
f=sock.makefile(mode='rw')
ok = move != "quit"
move+="\n"
while ok:
    f.write(move)
    f.flush()
    print(f.readline(), end="")
    move = input("Entrez le coup à jouer ou quit: ")
    ok = move != "quit"
    move+="\n"
reply = sock.recv(1024).decode()
print("Réponse du serveur :", reply)

sock.close()
