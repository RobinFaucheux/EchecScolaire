import sqlalchemy  
# pour avoir sqlalchemy :
# sudo apt-get update 
# sudo apt-get install python3-sqlalchemy
# pip3 install mysql-connector-python

from dotenv import load_dotenv
import os
import platform

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

def open_connexion():
    """
    ouverture d'une connexion MySQL
    paramètres:
       user     (str) le login MySQL de l'utilsateur
       passwd   (str) le mot de passe MySQL de l'utilisateur
       host     (str) le nom ou l'adresse IP de la machine hébergeant le serveur MySQL
       database (str) le nom de la base de données à utiliser
    résultat: l'objet qui gère le connection MySQL si tout s'est bien passé
    """
    system = platform.system() 
    if system == 'Windows':
        driver = 'mysql+mysqlconnector'
    else:
        driver = 'mysql+pymysql'
    try:
        engine = sqlalchemy.create_engine(f'{driver}://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')
        cnx = engine.connect()
    except Exception as err:
        print(err)
        raise err
    print("connection successful")
    return cnx