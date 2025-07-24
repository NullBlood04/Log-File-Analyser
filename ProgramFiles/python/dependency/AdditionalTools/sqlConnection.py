import mysql.connector
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ConnectDBase:

    def __init__(self, user, password, database) -> None:
        self.connect_dbase = None
        self.cursor = None
        try:
            self.connect_dbase = mysql.connector.connect(
                host="localhost", user=user, passwd=password, database=database
            )
            self.cursor = self.connect_dbase.cursor()
            logging.info("Successfully connected to the database.")
        except mysql.connector.Error as e:
            logging.error(f"Could not connect to database: {e}")

    def is_connected(self) -> bool:
        """Check if the database connection is active."""
        return self.connect_dbase is not None and self.connect_dbase.is_connected()

    def disconnect_sql(self) -> None:
        if self.is_connected() and self.connect_dbase:
            # Check if cursor exists before closing
            if self.cursor:
                self.cursor.close()
            self.connect_dbase.close()
            logging.info("Database connection closed.")

    def execute_query(self, query: str, params: tuple | None = None) -> bool:
        try:
            if self.is_connected() and self.cursor and self.connect_dbase:
                self.cursor.execute(query, params)  # type: ignore
                self.connect_dbase.commit()
                return True
            else:
                logging.warning("Query not executed: Database not connected.")
                return False
        except mysql.connector.Error as e:
            logging.error(f"Error executing query: {e}")
            if self.is_connected() and self.connect_dbase:
                self.connect_dbase.rollback()
            return False

    def fetch_all(self, query: str, params: tuple | None = None) -> bool | list:
        try:
            if self.is_connected() and self.cursor:
                self.cursor.execute(query, params)  # type: ignore
                return self.cursor.fetchall()
            else:
                logging.warning("Cannot fetch: Database not connected.")
                return False
        except mysql.connector.Error as e:
            logging.error(f"Error fetching data: {e}")
            return False


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()

    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    con = ConnectDBase(user, password, "log")

    result = con.fetch_all("SELECT * FROM application_errors")
    print(result)

    con.disconnect_sql()
