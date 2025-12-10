import sqlalchemy

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
    