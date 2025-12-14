import sqlalchemy
from datetime import date
from model import *
from typing import List, Dict, Union

def register_player(connexion : sqlalchemy.Connection, username : str, password : str) -> int:
    stmt = sqlalchemy.text("insert into PLAYER(pseudo, passwd) VALUES (:pseudo, :passwd) returning idP")
    res = connexion.execute(stmt, {"pseudo": username, "passwd": password})
    connexion.commit()
    row = res.fetchone()
    return row[0] if row else None

def collect_player(connexion : sqlalchemy.Connection, id : int):
    stmt = sqlalchemy.text("select idP, pseudo, passwd, elo from PLAYER where idP = :id")
    res = connexion.execute(stmt, {"id": id})
    row = res.fetchone()
    return row if row else None

def save_game(connexion : sqlalchemy.Connection) -> int:
    today = date.today()
    stmt = sqlalchemy.text("insert into GAME(dateG, stateG) VALUES (:dateG, :stateG) returning idG")
    res = connexion.execute(stmt, {"dateG": today, "stateG": "in progress"})
    connexion.commit()
    row = res.fetchone()
    return row[0] if row else None

def save_final_game(connexion : sqlalchemy.Connection, game: Game, idG: int, player: Player, won: str):
    final_duration = ((constant.TIMER * constant.ONE_MINUTE_IN_SECONDS - game.get_time_white()) + (constant.TIMER * constant.ONE_MINUTE_IN_SECONDS - game.get_time_black()))
    if game.get_joueur(0).get_id() == player.get_id():
        player_color = "WHITE"
    else:
        player_color = "BLACK"
    
    stmt1 = sqlalchemy.text("insert into PLAY(idG, idP, won, color) VALUES (:idG, :idP, :won, :color)")
    connexion.execute(stmt1, {"idG": idG, "idP": player.get_id(), "won": won, "color": player_color})
    connexion.commit()
    stmt2 = sqlalchemy.text("update GAME set stateG = :stateG, duration = :duration  where idG = :idG")
    connexion.execute(stmt2, {"stateG": "finished", "idG": idG, "duration": final_duration})
    connexion.commit()
    
    stmt3 = sqlalchemy.text("update PLAYER set elo = :elo where idP = :idP")
    connexion.execute(stmt3, {"elo": player.get_elo(),"idP": player.get_id()})
    connexion.commit()

def save_coup(connexion : sqlalchemy.Connection, idG: int, turn: int, start_piece: str, end_piece: str):
    coup = start_piece + "/" + end_piece + "\n"
    stmt1 = sqlalchemy.text("insert into COUP(idG, turn, coup) VALUES (:idG, :turn, :coup)")
    connexion.execute(stmt1, {"idG": idG, "turn": turn, "coup": coup})
    connexion.commit()

def collect_historic_game_of_player(connexion: sqlalchemy.Connection, player: Player) -> List[Dict[str, Union[int, str]]]:
    historic = []
    stmt1 = sqlalchemy.text("select idG from PLAY where idP = :idP")
    res1 = connexion.execute(stmt1, {"idP": player.get_id()})
    rows1 = res1.fetchall()

    for elem in rows1:
        stmt2 = sqlalchemy.text("select pseudo, won from PLAY natural join PLAYER where idG = :idG and idP != :idP")
        res2 = connexion.execute(stmt2, {"idG": elem[0], "idP": player.get_id()})
        row2 = res2.fetchone()

        if row2 is not None:
            dico = {"id_game": elem[0], "pseudo_joueur": row2[0], "result": row2[1]}
            historic.append(dico)

    return historic