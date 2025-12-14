import socket
import sys

HOST = "127.0.0.1"
PORT = 5555

def main_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Server is not running.")
        return

    # Use makefile for easier reading/writing of lines
    # 'rw' means read/write, 'utf-8' handles characters properly
    f = sock.makefile(mode='rw', encoding='utf-8')

    try:
        while True:
            # We read line by line from the server
            line = f.readline()
            
            if not line:
                # If server closes connection, readline returns empty string
                print("Server closed connection.")
                break
            
            print(line, end="")

            # LOGIC: If the server asks for input (contains ": "), we let the user type
            # We check specific keywords that indicate the server is waiting
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