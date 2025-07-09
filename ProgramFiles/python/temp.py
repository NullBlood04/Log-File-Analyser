import mysql.connector


class ConnectDBase:
    def __init__(self, user, password, database) -> None:
        self.user = user
        self.password = password
        self.database = database

    def __enter__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user=self.user,
            passwd=self.password,
            database=self.database,
        )

        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.connection.close()
        if exc_type:
            print("Error:", exc_val)

        return True

    def execute_query(self, query: str, params: tuple | None = None) -> bool:
        try:
            if self.cursor:
                print("Query executed...")
                self.cursor.execute(query, params)  # type: ignore
                self.connection.commit()
                return True
            else:
                print("Query not executed")
                return False
        except Exception as e:
            print("Error:", e)
            self.connection.rollback()
            return False

    def fetch_all(self, query: str, params: tuple | None = None) -> bool | list:
        try:
            if self.cursor:
                print("Query Executed...")
                self.cursor.execute(query, params)  # type: ignore
                return self.cursor.fetchall()
            else:
                print("Database not connected")
                return False

        except Exception as e:
            print("Error:", e)
            self.connection.rollback()
            return False


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()

    password = os.getenv("MYSQL_PASSWORD")
    with ConnectDBase("root", password, "log") as c:
        result = c.fetch_all("SELECT * FROM application_errors")

    for rows in result:  # type: ignore
        print(rows)
