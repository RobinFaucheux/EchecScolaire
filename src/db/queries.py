import sqlalchemy
from datetime import date
from model.player import Player
from model.game import Game
from model.constant import TIMER, ONE_MINUTE_IN_SECONDS
from typing import List, Dict, Union
from sqlalchemy.engine import Row


def register_player(connexion: sqlalchemy.Connection, username: str,
                    password: str) -> int:
    """
    Registers a new player in the database.

    Args:
        connexion (sqlalchemy.Connection): Database connection object.
        username (str): The username of the new player.
        password (str): The password of the new player.

    Returns:
        int: The ID of the newly created player.
    """
    stmt = sqlalchemy.text(
        "insert into PLAYER(pseudo, passwd) VALUES (:pseudo, :passwd) returning idP"
    )
    res = connexion.execute(stmt, {"pseudo": username, "passwd": password})
    connexion.commit()
    row = res.fetchone()
    return row[0] if row else None


def connect_player(connexion: sqlalchemy.Connection, nom: str) -> Row:
    """
    Retrieves a player's data from the database by ID.

    Args:
        connexion (sqlalchemy.Connection): Database connection object.
        id (int): The ID of the player to retrieve.

    Returns:
        Row: The database row containing player data, or None if not found.
    """
    stmt = sqlalchemy.text(
        "select idP, pseudo, passwd, elo from PLAYER where pseudo = :nom")
    res = connexion.execute(stmt, {"nom": nom})
    row = res.fetchone()
    return row if row else None


def collect_player(connexion: sqlalchemy.Connection, id: int) -> Row:
    """
    Retrieves a player's data from the database by ID.

    Args:
        connexion (sqlalchemy.Connection): Database connection object.
        id (int): The ID of the player to retrieve.

    Returns:
        Row: The database row containing player data, or None if not found.
    """
    stmt = sqlalchemy.text(
        "select idP, pseudo, passwd, elo from PLAYER where idP = :id")
    res = connexion.execute(stmt, {"id": id})
    row = res.fetchone()
    return row if row else None


def save_game(connexion: sqlalchemy.Connection) -> int:
    """
    Saves a new game entry in the database with the current date.

    Args:
        connexion (sqlalchemy.Connection): Database connection object.

    Returns:
        int: The ID of the newly created game.
    """
    today = date.today()
    stmt = sqlalchemy.text(
        "insert into GAME(dateG, stateG) VALUES (:dateG, :stateG) returning idG"
    )
    res = connexion.execute(stmt, {"dateG": today, "stateG": "in progress"})
    connexion.commit()
    row = res.fetchone()
    return row[0] if row else None


def save_final_game(connexion: sqlalchemy.Connection, game: Game, id_g: int,
                    player: Player, won: str) -> None:
    """
    Saves the final result of a game, updates player ELO and game state.

    Args:
        connexion (sqlalchemy.Connection): Database connection object.
        game (Game): The game object being saved.
        idG (int): The ID of the game.
        player (Player): The player whose result is being saved.
        won (str): The result for this player ('won', 'loose', 'equality').
    """
    final_duration = ((TIMER * ONE_MINUTE_IN_SECONDS - game.get_time_white()) +
                      (TIMER * ONE_MINUTE_IN_SECONDS - game.get_time_black()))
    if game.get_joueur(0).get_id() == player.get_id():
        player_color = "WHITE"
    else:
        player_color = "BLACK"

    stmt1 = sqlalchemy.text(
        "insert into PLAY(idG, idP, won, color) VALUES (:idG, :idP, :won, :color)"
    )
    connexion.execute(stmt1, {
        "idG": id_g,
        "idP": player.get_id(),
        "won": won,
        "color": player_color
    })
    connexion.commit()
    stmt2 = sqlalchemy.text(
        "update GAME set stateG = :stateG, duration = :duration  where idG = :idG"
    )
    connexion.execute(stmt2, {
        "stateG": "finished",
        "idG": id_g,
        "duration": final_duration
    })
    connexion.commit()

    stmt3 = sqlalchemy.text("update PLAYER set elo = :elo where idP = :idP")
    connexion.execute(stmt3, {"elo": player.get_elo(), "idP": player.get_id()})
    connexion.commit()


def save_coup(connexion: sqlalchemy.Connection, id_g: int, turn: int,
              start_piece: str, end_piece: str) -> None:
    """
    Saves a move made in a game to the database.

    Args:
        connexion (sqlalchemy.Connection): Database connection object.
        idG (int): The ID of the game.
        turn (int): The turn number.
        start_piece (str): The starting square of the piece.
        end_piece (str): The ending square of the piece.
    """
    coup = start_piece + "/" + end_piece + "\n"
    stmt1 = sqlalchemy.text(
        "insert into COUP(idG, turn, coup) VALUES (:idG, :turn, :coup)")
    connexion.execute(stmt1, {"idG": id_g, "turn": turn, "coup": coup})
    connexion.commit()


def collect_historic_game_of_player(
        connexion: sqlalchemy.Connection,
        player: Player) -> List[Dict[str, Union[int, str]]]:
    """
    Retrieves the historical games of a specific player.

    Args:
        connexion (sqlalchemy.Connection): Database connection object.
        player (Player): The player whose history is being retrieved.

    Returns:
        List[Dict[str, Union[int, str]]]: A list of dictionaries containing game ID, opponent's 
        pseudo, and result.
    """
    historic = []
    stmt1 = sqlalchemy.text("select idG from PLAY where idP = :idP")
    res1 = connexion.execute(stmt1, {"idP": player.get_id()})
    rows1 = res1.fetchall()

    for elem in rows1:
        stmt2 = sqlalchemy.text(
            "select pseudo, won from PLAY natural join PLAYER where idG = :idG and idP != :idP"
        )
        res2 = connexion.execute(stmt2, {
            "idG": elem[0],
            "idP": player.get_id()
        })
        row2 = res2.fetchone()

        if row2 is not None:
            dico = {
                "id_game": elem[0],
                "pseudo_joueur": row2[0],
                "result": row2[1]
            }
            historic.append(dico)

    return historic
