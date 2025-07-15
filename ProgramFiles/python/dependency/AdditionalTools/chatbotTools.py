from langchain.tools import tool
from subprocess import run
from dotenv import load_dotenv
import os
import re
import logging

from ..AdditionalTools.sqlConnection import ConnectDBase
from ..Agents.frequencyAgent import ErrorFrequencyAgent
from ..Agents.resultAgent import ResultAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

USR = os.getenv("MYSQL_USER")
PWD = os.getenv("MYSQL_PASSWORD")


@tool(parse_docstring=True)
def database_tool(operation: str, query: str, params: tuple | None = None):
    """
    Performs a database operation on the "log" database (execute or fetch) and returns the result.


    Database Schema:
        Table: application_errors
            - EventID (INT, PRIMARY KEY, NOT NULL)
            - Level (VARCHAR(8))
            - Source (VARCHAR(70))
            - TimeCreated (DATETIME, PRIMARY KEY, NOT NULL)
            - Message (TEXT)

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


@tool(parse_docstring=True)
def errorFrequencyAgent_prompt_node(timestamps: str):
    """
    Summarises error frequency from given timestamps using AI.

    Args:
        timestamps (str): Stringified list of error timestamps.

    Returns:
        str: One-line AI summary of error frequency.
    """
    frequencyAgent = ErrorFrequencyAgent()
    response = frequencyAgent.frequency_prompt(timestamps)
    return response


@tool(parse_docstring=True)
def resultAgent_prompt_node(analyse_content: str):
    """
    Analyses error content using ResultAgent AI to provide explanations.

    Args:
        analyse_content (str): Error text to analyse.

    Returns:
        str: AI-generated explanation and solution.
    """
    resultAgent = ResultAgent()
    response = resultAgent.prompt(analyse_content)
    return response


@tool(parse_docstring=True)
def probe_system(script: str) -> str:
    """
    Executes a validated PowerShell script and returns its output.
    allowed_commands = {
            "Test-Path": r'Test-Path -Path "[^"]+"',
            "Get-WinEvent": r'Get-WinEvent -LogName Application -MaxEvents \\d+ -FilterScript \\{ \\$\\_.ProviderName -eq "[^"]+" -and \\$\\_.ID -eq \\d+ \\}',
            "Get-Service": r'Get-Service -Name "[^"]+"',
            "Get-Process": r'Get-Process -Name "[^"]+"',
            "Get-ComputerInfo": r"Get-ComputerInfo \\| Select-Object (OsName|OsVersion|WindowsVersion)",
        }

    Args:
        script (str): Whitelisted PowerShell command to execute.

    Returns:
        str: Output from the executed script or an error message.
    """
    try:
        # Input Validation (Whitelist approach)
        allowed_commands = {
            "Test-Path": r'Test-Path -Path "[^"]+"',
            "Get-WinEvent": r'Get-WinEvent -LogName Application -MaxEvents \d+ -FilterScript \{ \$\_.ProviderName -eq "[^"]+" -and \$\_.ID -eq \d+ \}',
            "Get-Service": r'Get-Service -Name "[^"]+"',
            "Get-Process": r'Get-Process -Name "[^"]+"',
            "Get-ComputerInfo": r"Get-ComputerInfo \| Select-Object (OsName|OsVersion|WindowsVersion)",
        }

        command_found = False
        for command, pattern in allowed_commands.items():
            if re.match(pattern, script):
                command_found = True
                break

        if not command_found:
            raise ValueError("Script contains disallowed commands or invalid syntax.")

        result = run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=30,  # Timeout in seconds
        )

        output = result.stdout

        # Output Length Limiting
        max_output_length = 1024  # Example: Limit to 1024 characters
        if len(output) > max_output_length:
            output = output[:max_output_length] + "... (truncated)"

        if output:
            return output
        return "recieved no output from command"

    except Exception as e:
        logging.error(f"Error executing script: {e}")
        return f"Error: {str(e)}"


tools = [
    resultAgent_prompt_node,
    errorFrequencyAgent_prompt_node,
    database_tool,
    probe_system,
]
