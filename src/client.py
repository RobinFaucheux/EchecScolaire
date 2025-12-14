import socket
import sys

HOST = "127.0.0.1"
PORT = 5555


def main_client():
    """
    A simple TCP client that connects to a server at a specified host and port.

    Features:
    - Connects to the server using a socket.
    - Reads and prints messages from the server.
    - Sends user input to the server.
    - Handles server disconnection and keyboard interruption gracefully.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Server is not running.")
        return

    f = sock.makefile(mode='rw', encoding='utf-8')

    try:
        while True:
            line = f.readline()

            if not line:
                print("Server closed connection.")
                break

            print(line, end="")

            if "Entree : " in line:
                user_input = input()
                f.write(user_input + "\n")
                f.flush()

                if user_input.lower() == "quit":
                    break

    except KeyboardInterrupt:
        print("\nClient exiting...")
    finally:
        sock.close()


if __name__ == "__main__":
    main_client()
