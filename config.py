import os


# Enable debug mode.

# Connect to the database
class DatabaseURI:
    SECRET_KEY = os.urandom(32)
    # Grabs the folder where the script runs.
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Just change the names of your database and crendtials and all to connect to your local system
    DATABASE_NAME = "fyurr"
    username = 'postgres'
    password = 'arthur'
    url = 'localhost:5432'
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)
    
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

