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
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
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
        str: A formatted string of the results, suitable for an LLM.
             Returns a message if no records are found or an error occurs.
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

        rows = connection.fetch_all(query, params)
        if not rows:
            return "Query executed successfully, but no records were found."

        # Get column names from the cursor description
        # Ensure connection.cursor is not None before accessing .description
        column_names = (
            [desc[0] for desc in connection.cursor.description]
            if connection.cursor and connection.cursor.description
            else []
        )
        total_rows = len(rows)  # type: ignore
        logging.info(f"Query returned {total_rows} rows.")

        # Serialize each row into a human-readable string
        formatted_rows = [
            ", ".join([f"{col}: {val}" for col, val in zip(column_names, row)])
            for row in rows  # type: ignore
        ]

        # Combine into a single text block
        full_output = "\n".join(formatted_rows)

        # Truncate if the output is too large for the LLM context
        max_output_length = 4000  # Characters
        if len(full_output) > max_output_length:
            truncated_output = full_output[:max_output_length]
            return f"{truncated_output}\n... (truncated, showing a subset of {total_rows} total rows)"

        return full_output

    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return f"Error during database query: {e}"

    finally:
        if connection and connection.is_connected():
            connection.disconnect_sql()
