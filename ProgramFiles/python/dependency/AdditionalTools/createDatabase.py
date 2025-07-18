from dotenv import load_dotenv
import os

# Local imports
from .sqlConnection import ConnectDBase


load_dotenv()

""" 
Database Schema:
        Database: log
        Table: application_errors
            - EventID (INT, PRIMARY KEY, NOT NULL)
            - Level (VARCHAR(8))
            - Source (VARCHAR(70))
            - TimeCreated (DATETIME, PRIMARY KEY, NOT NULL)
            - Message (TEXT)
 """

RECORD_PATH = os.getenv("RECORD_PATH")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")

query = """
CREATE DATABASE IF NOT EXISTS log;
USE log;
CREATE TABLE IF NOT EXISTS application_errors (
    EventID INT PRIMARY KEY NOT NULL,
    Level VARCHAR(8),
    Source VARCHAR(70),
    TimeCreated DATETIME PRIMARY KEY NOT NULL,
    Message TEXT
);
"""


def create_errorDbase() -> None:

    if not os.path.exists(os.path.abspath(str(RECORD_PATH))):
        con = ConnectDBase(user, password, None)
        con.execute_query(query)
        con.disconnect_sql()

    else:
        print("Database already exists")


if __name__ == "__main__":
    create_errorDbase()
