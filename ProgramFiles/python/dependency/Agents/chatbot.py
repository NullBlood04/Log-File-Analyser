from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables import RunnablePassthrough
from langgraph.prebuilt import ToolNode
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing_extensions import TypedDict
from dotenv import load_dotenv
import os

# Local imports
from .frequencyAgent import ErrorFrequencyAgent
from .resultAgent import ResultAgent
from ..AdditionalTools.sqlConnection import ConnectDBase
from ..AdditionalTools.literals import chat_system_prompt


load_dotenv()

AZURE_RESOURCE_NAME = os.getenv("AZURE_RESOURCE_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
GPT_MODEL = os.getenv("AZURE_DEPLOYMENT_NAME")
USER = os.getenv("MYSQL_USER")
PASSWD = os.getenv("MYSQL_PASSWORD")

USR = os.getenv("MYSQL_USER")
PWD = os.getenv("MYSQL_PASSWORD")

# API Connection
chat = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,  # type: ignore
    azure_endpoint=f"https://{AZURE_RESOURCE_NAME}.openai.azure.com/",
    api_version=AZURE_API_VERSION,
    model=GPT_MODEL,
    temperature=0.2,
)

memory = ConversationBufferWindowMemory(return_messages=True, k=5)

initial_state = {
    "messages": [],
    "memory": memory,
}

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", chat_system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)


# State definition
class State(TypedDict):
    messages: list


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

    Use this tool if you want one line answer on how frequent an error occured

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
    Uses the ResultAgent AI model to analyse provided error content use to explain and returns the AI-generated analysis.

    Use this tool to explain each error in and their practical solutions.

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


tool_binded_chat = chat.bind_tools(tools)

conversation = (
    RunnablePassthrough.assign(
        history=lambda x: memory.load_memory_variables({})["history"]
    )
    | prompt
    | tool_binded_chat
)


tool_node = ToolNode(tools)


# Chatbot node
def chatbot(state: State):

    if not state["messages"]:
        # Handle initial empty state: ask user for input or skip
        print("No messages yet. Awaiting user input.")
        return state

    last_message = state["messages"][-1]  # Assuming last item is HumanMessage

    if isinstance(last_message, dict):
        user_input = last_message["content"]
    else:
        user_input = last_message.content

    response = conversation.invoke({"input": user_input})

    state["messages"].append(response)
    memory.save_context({"input": user_input}, {"output": str(response)})

    return state


def check_toolcalls(state: State):
    # Get last message
    if not state["messages"]:
        return "END"

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage):
        if getattr(last_message, "tool_calls", None):
            return "tools"

    return "END"


# Adding and conneting nodes
build = StateGraph(State)

build.add_node("Chatbot", chatbot)
build.add_node("tools", tool_node)

build.add_edge(START, "Chatbot")
build.add_conditional_edges("Chatbot", check_toolcalls, {"tools": "tools", "END": END})
build.add_edge("tools", "Chatbot")
build.add_edge("Chatbot", END)

graph = build.compile()

# Stores the last ai message

log_register = list()


# Driver program loop
class ChatBot:

    def stream_graph(self, user_input: str, state: State) -> State:
        state["messages"].append(HumanMessage(content=user_input))

        for event in graph.stream(state):
            for value in event.values():
                if value and value["messages"]:
                    last_message = value["messages"][-1]

                    # Append all messages to state for correct flow
                    state["messages"].append(last_message)

                    # Print only final LLM messages with no tool calls
                    if isinstance(last_message, AIMessage):
                        if not getattr(last_message, "tool_calls", None):
                            content = last_message.content
                            print("Bot:", content)

        return state

    def mainbot(self) -> None:
        state = {
            "messages": [],
        }

        # Initial user input before streaming the graph
        user_input = input("You: ")
        state["messages"].append(HumanMessage(content=user_input))

        while True:
            if user_input.lower() == "exit":
                break
            state = self.stream_graph(user_input, state)  # type: ignore # update state each loop
            log_register.append(state.copy())  # store copy for logs

            user_input = input("You: ")  # prompt again for next loop

        print(log_register)


if __name__ == "__main__":
    c = ChatBot()
    c.mainbot()
