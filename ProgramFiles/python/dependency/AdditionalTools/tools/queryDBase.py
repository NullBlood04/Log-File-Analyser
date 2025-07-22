from langchain.tools import tool
from ..sqlConnection import ConnectDBase
from dotenv import load_dotenv
import os
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)

load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

USR = os.getenv("MYSQL_USER")
PWD = os.getenv("MYSQL_PASSWORD")


@tool(parse_docstring=True)
def database_tool(query: str, params: tuple | None = None):
    """
    Executes a read-only SQL SELECT query on the 'log' database and returns the results.
    This tool is for data retrieval only. Operations like INSERT, UPDATE, or DELETE are not allowed.
    Use '%s' as the placeholder for parameters in the query.

    Database Schema:
        Table: application_errors
            - RecordId (BIGINT, PRIMARY KEY, NOT NULL)
            - EventID (INT)
            - Level (VARCHAR(8))
            - Source (VARCHAR(70))
            - TimeCreated (DATETIME)

    Args:
        query (str): The SELECT SQL query string. Must start with "SELECT".
        params (tuple, optional): A tuple of parameters to be safely substituted into the query.

    Returns:
        list[tuple] | str: A list of rows for a successful query, or an error message string.
                           Returns an empty list if no records are found.
    """
    logging.info(f"Executing SQL query: {query} with params: {params}")

    # Security: Enforce read-only operations
    if not query.strip().upper().startswith("SELECT"):
        logging.warning(f"Blocked non-SELECT query: {query}")
        return "Error: Only SELECT queries are allowed."

    connection = None
    try:
        connection = ConnectDBase(user=USR, password=PWD, database="log")
        if not connection.is_connected():
            raise ConnectionError(
                "Failed to establish a connection to the SQL database."
            )

        results = connection.fetch_all(query, params)
        if isinstance(results, list):
            logging.info(f"Query returned {len(results)} rows.")
        else:
            logging.info("Query did not return a list of results.")
        return results

    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return f"Error during database query: {e}"

    finally:
        if connection and connection.is_connected():
            connection.disconnect_sql()
