import socket

HOST = "127.0.0.1"
PORT = 5555


def main_client():
    sock = socket.socket()
    sock.connect((HOST, PORT))
    f = sock.makefile(mode="rw")
    quit = True
    while quit:
        rep = input("commande : ") 
        if rep == "quit": 
            quit = False
        rep+="\n"
        f.write(rep)
        f.flush()
        print(f.readline())
    
    f.write("quit\n")
    f.flush()
    print(f.readline(),end="")
    f.close()
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


if __name__ == "__main__":
    main_client()
