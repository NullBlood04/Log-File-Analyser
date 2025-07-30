import mysql.connector
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ConnectDBase:

    def __init__(self, user, password, database) -> None:
        self.connection = None
        self.cursor = None
        try:
            self.connection = mysql.connector.connect(
                host="localhost", user=user, passwd=password, database=database
            )
            self.cursor = self.connection.cursor()
            logging.info(f"Successfully connected to the `{database}` database.")
        except mysql.connector.Error as e:
            logging.error(f"Could not connect to database: {e}")

    def is_connected(self) -> bool:
        """Check if the database connection is active."""
        return self.connection is not None and self.connection.is_connected()

    def disconnect_sql(self) -> None:
        if self.is_connected() and self.connection:
            # Check if cursor exists before closing
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            logging.info("Database connection closed.")

    def execute_query(self, query: str, params: tuple | None = None) -> bool:
        try:
            if self.is_connected() and self.cursor and self.connection:
                self.cursor.execute(query, params)  # type: ignore
                self.connection.commit()
                return True
            else:
                logging.warning("Query not executed: Database not connected.")
                return False
        except mysql.connector.Error as e:
            logging.error(f"Error executing query: {e}")
            if self.is_connected() and self.connection:
                self.connection.rollback()
            return False

    def execute_many(self, query: str, params_list: list[tuple]) -> bool:
        """Executes a query with a sequence of parameters (for batch inserts)."""
        try:
            if self.is_connected() and self.cursor:
                self.cursor.executemany(query, params_list)
                # Note: commit is not called here to allow for transactions
                return True
            else:
                logging.warning("Query not executed: Database not connected.")
                return False
        except mysql.connector.Error as e:
            logging.error(f"Error executing many: {e}")
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
    con = ConnectDBase(user, password, "log_analyzer")

    result = con.fetch_all("SELECT * FROM Application_logs LIMIT 10")
    print(result)

    con.disconnect_sql()
