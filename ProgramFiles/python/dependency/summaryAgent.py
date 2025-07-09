from parent_aiConnector import Connect_AI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.tools import tool
from dotenv import load_dotenv
import os

from frequencyAgent import ErrorFrequencyAgent
from resultAgent import ResultAgent
from sqlConnection import ConnectDBase
from literals import summaryAgent_system_prompt

load_dotenv()
USR = os.getenv("MYSQL_USER")
PWD = os.getenv("MYSQL_PASSWORD")


@tool(parse_docstring=True)
def database_tool(operation: str, query: str, params: tuple | None = None):
    """
    Performs a database operation on the "log" database (execute or fetch) and returns the result.

    Use this tool when the structured error data containing the following is recieved:
    error_type, error_message, application_name, source, time_generated, and additional_details

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
        query (str): The SQL query string to execute.
        params (tuple, optional): A tuple of arguments for parameterised queries. Defaults to None.

    Returns:
        Any: The result of the database operation.
             For "execute" operations, returns True if successful.
             For "fetch" operations, returns fetched data as a list of rows.

    Raises:
        ConnectionError: If the database connection or operation fails.
        ValueError: If an invalid operation type is provided.
    """
    connection = ConnectDBase(user=USR, password=PWD, database="log")

    try:
        if operation == "execute":

            isExecuted = connection.execute_query(query, params)
            if isExecuted:
                print(query, params)
                return isExecuted

            else:
                print(query, params)
                raise ConnectionError(
                    "Connection may not be established, please check whether sql is connected"
                )

        elif operation == "fetch":
            isFetched = connection.fetch_all(query, params)

            if isFetched:
                print(query, params)
                return isFetched

            else:
                print(query, params)
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
    Processes a list of timestamps retrieved from SQL queries to generate a concise summary of error frequency.

    Args:
        timestamps (str): A stringified list of timestamps representing error occurrences fetched from the database.

    Returns:
        str: A one-line AI-generated summary describing the frequency and distribution of the provided timestamps.

    Behavior:
        - Accepts a string input containing a list of timestamps.
        - Uses the ErrorFrequencyAgent class to invoke an AI model with the timestamps and a predefined system prompt.
        - Returns the AI-generated frequency summary as a string for downstream nodes to access.

    Dependencies:
        - Utilises the ErrorFrequencyAgent class, which inherits from Connect_AI and uses the system prompt 'errorFrequencyAgent_system_prompt' to process the input.
        - The ErrorFrequencyAgent.frequency_prompt() method constructs messages with the system prompt and user input, calls the AI model, and returns the content.

    Example:
        >>> errorFrequencyAgent_prompt_node("[2025-07-08T10:00:00Z, 2025-07-08T12:00:00Z, ...]")
        "2 errors on 8 July 2025"

        >>> errorFrequencyAgent_prompt_node("[2025-07-08T10:00:00Z, 2025-07-09T11:30:00Z, ...]")
        "1 error on 8 July 2025, 1 error on 9 July 2025"
    """
    frequencyAgent = ErrorFrequencyAgent()
    response = frequencyAgent.frequency_prompt(timestamps)
    return response


@tool(parse_docstring=True)
def resultAgent_prompt_node(analyse_content: str):
    """
    Uses the ResultAgent AI model to analyse provided error content and returns the AI-generated analysis.

    Args:
        analyse_content (str): The error content string to be analysed by the AI model.

    Returns:
        str: The AI-generated analysis based on the provided error content.

    Behaviour:
        - Accepts error content as input.
        - Passes the content to the ResultAgent's `prompt` method for AI-based analysis.
        - Returns the AI-generated analysis as a string for downstream processing.

    Dependencies:
        - Utilises the ResultAgent class, which inherits from Connect_AI and uses a predefined system prompt to analyse error data.
        - The ResultAgent.prompt() method constructs messages with the system prompt and input, calls the AI model, and returns the content.

    Example:
        >>> resultAgent_prompt_node("Application Error: Faulting module example.dll")
        "The error indicates that example.dll caused the application to crash due to invalid memory access."
    """
    resultAgent = ResultAgent()
    response = resultAgent.prompt(analyse_content)
    return response


tools = [
    resultAgent_prompt_node,
    errorFrequencyAgent_prompt_node,
    database_tool,
]


class SummaryAgent(Connect_AI):

    system_prompt = summaryAgent_system_prompt

    def __init__(self):
        self.tool_binded_chat = self.chat.bind_tools(tools)

    def prompt(self, error_content):  # type: ignore

        try:
            message = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=error_content),
            ]
            self.content = self.tool_binded_chat.invoke(message).content
            return self.content
        except Exception as e:
            return f"Something went Wrong: {e}"
