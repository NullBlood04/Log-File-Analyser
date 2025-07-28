from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables import RunnablePassthrough
from langgraph.prebuilt import ToolNode
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing_extensions import TypedDict
from dotenv import load_dotenv
import os

from ..AdditionalTools import CHAT_SYSTEM_PROMPT, TOOLS
from . import PROJECT_ROOT

load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

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

memory = ConversationBufferWindowMemory(return_messages=True, k=4)

initial_state = {
    "messages": [],
    "memory": memory,
}

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CHAT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)


# State definition
class State(TypedDict):
    messages: list


tool_binded_chat = chat.bind_tools(TOOLS)

conversation = (
    RunnablePassthrough.assign(
        history=lambda x: memory.load_memory_variables({})["history"]
    )
    | prompt
    | tool_binded_chat
)


tool_node = ToolNode(TOOLS)


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
    memory.save_context({"input": user_input}, {"output": str(response.content)})

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
# build.add_edge("Chatbot", END)

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
