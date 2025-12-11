import db.queries as db
from model import *

def register_user(connexion):
    print("\n-- Register --")
    username = input("Enter your username: ").strip()
    while not username:
        print("Username cannot be empty.")
        username = input("Enter your username: ").strip()

    password = input("Enter your password: ").strip()
    while not password:
        print("Password cannot be empty.")
        password = input("Enter your password: ").strip()

    player_id = db.register_player(connexion, username, password)
    print(f"\nUser '{username}' successfully created, your ID is '{player_id}'")
    input()


def login_player(connexion, players):
    print("\n-- Log in --")

    id = input("Enter your ID: ").strip()
    id_other = (players[0].get_id() if players else "rien")
    while not id or id == str(id_other):
        print("id cannot be empty or same ID that player 1.")
        id = input("Enter your id: ").strip()

    player = db.collect_player(connexion, id)
    player_obj = None
    if player:
        print(f"\nWelcome back, {player[1]}! Your ELO: {player[3]}")
        player_obj = Player(player[0], player[1], player[2], [])
    else:
        print("\nInvalid ID\n")
    return player_obj


def main_menu(connexion):
    players = []
    print("======================================")
    print("       Welcome to ChessSchool")
    print("======================================\n")
    for i in range(1, 3):
        print(f"\n--- Player {i} ---")
        while True:
            print("1. Log in")
            print("2. Register")
            print("3. Quit\n")

            choice = input("Please choose an option (1-3): ").strip()
            while choice not in ["1", "2", "3"]:
                print("Invalid choice. Please try again.")
                choice = input("Please choose an option (1-3): ").strip()

            if choice == "1":
                player = login_player(connexion, players)
                if player:
                    players.append(player)        
                    input()
                    break
            elif choice == "2":
                register_user(connexion)
            else:
                print("Goodbye!")
                exit()
    
    print("\nBoth players are ready!")
    print(f"Player 1 : {players[0].get_pseudo()}, Player 2 : {players[1].get_pseudo()}")
    return players
