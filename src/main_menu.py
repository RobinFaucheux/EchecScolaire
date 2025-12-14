import db.queries as db
from model import *
import sqlalchemy


def register_user(connexion: sqlalchemy.Connection) -> None:
    """
    Registers a new player in the system.

    - Prompts the user for a username and password.
    - Validates that the inputs are not empty.
    - Saves the player in the database.
    - Displays a success message with the assigned player ID.

    Args:
        connexion (sqlalchemy.Connection): Database connection used to register the player.
    """
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


def login_player(connexion: sqlalchemy.Connection, players: list[Player, Player]) -> Player:
    """
    Logs in an existing player.

    - Prompts the user for their player ID.
    - Ensures the ID is not empty and not already used by the other player.
    - Retrieves player data from the database.
    - Initializes a Player object with historical game data.
    - Displays a welcome message and game history if available.

    Args:
        connexion (sqlalchemy.Connection): Database connection used to retrieve player info.
        players (list[Player, Player]): List of already logged-in players to avoid duplicate IDs.

    Returns:
        Player: The logged-in Player object, or None if the ID was invalid.
    """
    print("\n-- Log in --")

    id = input("Enter your ID: ").strip()
    id_other = (players[0].get_id() if players else "rien")
    while not id or id == str(id_other):
        print("id cannot be empty or same ID that player 1.")
        id = input("Enter your id: ").strip()

    player = db.collect_player(connexion, id)
    player_obj = None
    if player:
        player_obj = Player(player[0], player[1], player[3])
        player_obj.set_historical(db.collect_historic_game_of_player(connexion, player_obj))
        print(f"\nWelcome back, {player[1]}! Your ELO: {player[3]}")
        historicals = player_obj.get_historical()
        if historicals != []:
            print("Your game historicals : ")
            for game in player_obj.get_historical():
                print("game :", game["id_game"], "/ opponent :",  game["pseudo_joueur"], "/ result of the game :",  game["result"], "\n", end="")
    else:
        print("\nInvalid ID\n")
    return player_obj


def main_menu(connexion: sqlalchemy.Connection) -> list[Player]:
    """
    Displays the main menu for player selection.

    - Welcomes players to the game.
    - For each of the two players, allows them to either log in or register.
    - Ensures valid menu choices are made.
    - Returns a list containing both Player objects once both have joined.

    Args:
        connexion (sqlalchemy.Connection): Database connection used for logging in or registering players.

    Returns:
        list[Player]: List containing the two Player objects ready to play.
    """
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