from langchain.tools import tool
from ..sqlConnection import ConnectDBase
from dotenv import load_dotenv
import os
import re


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)

load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

USR = os.getenv("MYSQL_USER")
PWD = os.getenv("MYSQL_PASSWORD")


@tool(parse_docstring=True)
def database_tool(operation: str, query: str, params: tuple | None = None):
    """
    Performs a database operation on the "log" database (execute or fetch) and returns the result.

    Database Schema:
        Table: application_errors
            - RecordId (BIGINT, PRIMARY KEY, NOT NULL)
            - EventID (INT)
            - Level (VARCHAR(8))
            - Source (VARCHAR(70))
            - TimeCreated (DATETIME)

    Args:
        operation (str): The type of database operation to perform. Accepts:
                        - "execute" for modifying queries (INSERT, UPDATE, DELETE)
                        - "fetch" for retrieval queries (SELECT).
        query (str): The SQL query string.
        params (tuple, optional): Query parameters.

    Returns:
        Any: The result of the database operation.
             For "execute" operations, returns True if successful.
             For "fetch" operations, returns fetched data as a list of rows.

    Raises:
        ConnectionError: If the database connection or operation fails.
        ValueError: If an invalid operation type is provided.
    """
    print("___________________database_tool used______________________")
    clean_query = re.sub(r"\?", "%s", query)
    connection = ConnectDBase(user=USR, password=PWD, database="log")

    try:
        if operation == "execute":

            isExecuted = connection.execute_query(clean_query, params)
            if isExecuted:
                print(clean_query, params)
                return isExecuted

            else:
                print(clean_query, params)
                raise ConnectionError(
                    "Connection may not be established, please check whether sql is connected"
                )

        elif operation == "fetch":
            isFetched = connection.fetch_all(clean_query, params)

            if isFetched:
                print(clean_query, params)
                return isFetched

            else:
                print(clean_query, params)
                raise ConnectionError(
                    "Connection may not be established, please check whether sql is connected"
                )

        else:
            raise ValueError("Invalid operation type. Use 'execute' or 'fetch'.")

    except Exception as e:
        connection.disconnect_sql()

    finally:
        connection.disconnect_sql()
