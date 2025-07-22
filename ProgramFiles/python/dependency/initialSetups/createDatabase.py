from dotenv import load_dotenv
import os
import logging

# Local imports
from .sqlConnection import ConnectDBase

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

""" 
Database Schema:
        Database: log
        Table: application_errors
            - RecordId (BIGINT, PRIMARY KEY)
            - EventID (INT)
            - Level (VARCHAR(8))
            - Source (VARCHAR(70))
            - TimeCreated (DATETIME)
 """
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))


user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")

# Split the multi-statement query into individual commands
create_db_query = "CREATE DATABASE IF NOT EXISTS log;"
use_db_query = "USE log;"
create_table_query = """
CREATE TABLE IF NOT EXISTS application_errors (
    RecordId BIGINT PRIMARY KEY NOT NULL,
    EventID INT,
    Level VARCHAR(8),
    Source VARCHAR(70),
    TimeCreated DATETIME
);
"""


def create_errorDbase() -> None:
    """Creates the database and table if they don't exist."""
    con = None  # Initialize con to None
    try:
        con = ConnectDBase(user, password, None)
        if con.is_connected():
            con.execute_query(create_db_query)
            con.execute_query(use_db_query)
            con.execute_query(create_table_query)
            logging.info("Database and table checked/created successfully.")
    except Exception as e:
        logging.error(f"Failed to create database: {e}")
    finally:
        if con and con.is_connected():
            con.disconnect_sql()


if __name__ == "__main__":
    create_errorDbase()
