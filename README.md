# EchecScolaire

install modules : 
` pip install -r requirements.txt`

The code was made by us, with a few small sections where we used AI to help fix some issues. 
The docstring were mostly translated using AI to fit the style of the project where all commits and code were written in english.

To launch echecScolaire, create a .env file in the project root directory with the following:

` DB_USER=morain `
` DB_PASS=morain `
` DB_HOST=servinfo-maria `
` DB_NAME=DBmorain `

# Driver SQLAlchemy to use
# For MySQL : mysql+mysqlconnector
# For MariaDB : mysql+pymysql
` DB_DRIVER=mysql+pymysql `

To launch the server, simply type `python src/server.py`
To launch a client, type `python src/client.py`