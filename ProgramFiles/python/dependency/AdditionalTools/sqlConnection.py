import mysql.connector


class ConnectDBase:

    def __init__(self, user, password, database) -> None:
        try:
            self.connect_dbase = mysql.connector.connect(
                host="localhost", user=user, passwd=password, database=database
            )
            self.cursor = self.connect_dbase.cursor()
        except Exception as e:
            print("Could not connect:", e)

    def disconnect_sql(self) -> None:
        if self.connect_dbase and self.connect_dbase.is_connected():
            self.connect_dbase.close()
            self.cursor.close()

    def execute_query(self, query: str, params: tuple | None = None) -> bool:
        try:
            if self.cursor:
                print("Query executed...")
                self.cursor.execute(query, params)  # type: ignore
                self.connect_dbase.commit()
                return True
            else:
                print("Query not executed")
                return False
        except Exception as e:
            print("Error:", e)
            self.connect_dbase.rollback()
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
            self.connect_dbase.rollback()
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
