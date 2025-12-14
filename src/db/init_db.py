import sqlalchemy
from sqlalchemy import inspect, text
from dotenv import load_dotenv
import os
import platform

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER")


def open_connexion():
    """
    Opens a connection to the MySQL database using environment variables.

    Returns:
        sqlalchemy.Connection: The connection object for interacting with the database.
    """
    try:
        engine = sqlalchemy.create_engine(
            f'{DB_DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')
        connexion = engine.connect()
    except Exception as err:
        print(err)
        raise err
    print("connection successful")
    return connexion


def database_already_initialized(connexion: sqlalchemy.Connection) -> bool:
    """
    Checks if the database already contains tables.

    Args:
        connexion (sqlalchemy.Connection): The database connection to inspect.

    Returns:
        bool: True if the database contains any tables, False otherwise.
    """
    inspector = inspect(connexion)
    tables = inspector.get_table_names()
    return not (len(tables) == 0)


def create_database(connexion: sqlalchemy.Connection) -> None:
    """
    Initializes the database by executing the SQL statements in 'db/creation.sql'.

    Args:
        connexion (sqlalchemy.Connection): The database connection to use for executing the statements.
    """
    path = "db/creation.sql"
    with open(path, "r", encoding="utf8") as f:
        sql = f.read()

    statements = sql.split(";")
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            connexion.execute(text(stmt))
