import sqlalchemy
from datetime import date

def register_player(connexion, username, password):
    stmt = sqlalchemy.text("insert into PLAYER(pseudo, passwd) VALUES (:pseudo, :passwd) returning idP")
    res = connexion.execute(stmt, {"pseudo": username, "passwd": password})
    connexion.commit()
    row = res.fetchone()
    return row[0] if row else None

def collect_player(connexion, id):
    stmt = sqlalchemy.text("select idP, pseudo, passwd, elo from PLAYER WHERE idP = :id")
    res = connexion.execute(stmt, {"id": id})
    row = res.fetchone() 
    return row if row else None

def save_game(connexion):
    today = date.today()
    stmt = sqlalchemy.text("insert into GAME(dateG, stateG) VALUES (:dateG, :stateG) returning idG")
    res = connexion.execute(stmt, {"dateG": today, "stateG": "in progress"})
    connexion.commit()
    row = res.fetchone()
    return row[0] if row else None

def save_final_game(connexion, idG: int, idP: int, won: bool):
    stmt1 = sqlalchemy.text("insert into PLAY(idG, idP, won) VALUES (:idG, :idP, :won)")
    connexion.execute(stmt1, {"idG": idG, "idP": idP, "won": won})
    connexion.commit()
    stmt2 = sqlalchemy.text("update GAME set stateG = :stateG where idG = :idG")
    connexion.execute(stmt2, {"stateG": "finished", "idG": idG})
    connexion.commit()