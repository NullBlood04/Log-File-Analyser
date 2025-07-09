from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing_extensions import TypedDict
from typing import Annotated, Match

# from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import json
import os

# Local imports
from summaryAgent import SummaryAgent
from inputHandler import HandleInput
from literals import chat_system_prompt


load_dotenv()

AZURE_RESOURCE_NAME = os.getenv("AZURE_RESOURCE_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
GPT_MODEL = os.getenv("AZURE_DEPLOYMENT_NAME")
USER = os.getenv("MYSQL_USER")
PASSWD = os.getenv("MYSQL_PASSWORD")

# API Connection
chat = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,  # type: ignore
    azure_endpoint=f"https://{AZURE_RESOURCE_NAME}.openai.azure.com/",
    api_version=AZURE_API_VERSION,
    model=GPT_MODEL,
    temperature=0.2,
)

memory = ConversationBufferMemory(return_messages=True)

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

conversation = (
    RunnablePassthrough.assign(
        history=lambda x: memory.load_memory_variables({})["history"]
    )
    | prompt
    | chat
)


# State definition
class State(TypedDict):
    messages: list
    error_content: str | list | bool | Match[str] | None
    ai_response: str | list | dict


# Handles inputs
def input_handler_tool(state: State) -> State:
    message = state["messages"]
    inp_handle = HandleInput()
    response_data = inp_handle.prompt(message)  # type: ignore
    state["error_content"] = response_data
    print("Input Handler")
    return state


# Uses tools and integrates answers to give human understandable summary
def give_summary(state: State) -> State:
    message = state["error_content"]
    summary_agent = SummaryAgent()
    summary = summary_agent.prompt(message)
    state["error_content"] = summary
    print("summary agent")
    return state


# Chatbot node
def chatbot(state: State):
    last_message = state["messages"][-1]  # Assuming last item is HumanMessage

    if isinstance(last_message, dict):
        user_input = last_message["content"]
    else:
        user_input = last_message.content

    response = conversation.invoke({"input": user_input}).content

    state["messages"].append({"role": "assistant", "content": response})
    memory.save_context({"input": user_input}, {"output": str(response)})

    return state


""" 
def route_tools(state: State):
    '''Use in the conditional_edge to route to the ToolNode if the last message
    has tools calls. Otherwise, route to the chatbot.'''

    if isinstance(state, list):
        ai_message = state[-1]  # type: ignore

    elif messages := state.get("messages", []):
        ai_message = messages[-1]

    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")

    if (
        hasattr(ai_message, "tool_calls")
        and len(ai_message.tool_calls) > 0  # type: ignore
    ):
        return "tools"
    return END """


def condition_parse(state: State):
    json_file = state["error_content"]

    if not json_file:
        print("Warning: No content to parse.")
        return END

    try:
        check_json = json.loads(json_file)  # type: ignore
    except json.JSONDecodeError:
        print("Warning: Invalid JSON received:", json_file)
        return END

    if "original_input" in check_json:
        print("going to chatbot")
        return END
    print("using summary Agent")
    return "summaryAgent"


# Adding and conneting nodes
build = StateGraph(State)

build.add_node("Chatbot", chatbot)
build.add_node("inputHandler", input_handler_tool)
build.add_node("summaryAgent", give_summary)

build.add_edge(START, "Chatbot")
build.add_edge("Chatbot", "inputHandler")
build.add_conditional_edges("inputHandler", condition_parse, [END, "summaryAgent"])

graph = build.compile()

# Initial context for AI


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

                    # Handle dict vs message object
                    content = (
                        last_message["content"]
                        if isinstance(last_message, dict)
                        else last_message.content
                    )
                    print("Bot:", content)

                    state["messages"].append(last_message)

        return state

    def mainbot(self) -> None:
        state = {"messages": []}  # initialize fresh state

        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            state = self.stream_graph(user_input, state)  # type: ignore | update state each loop
            log_register.append(state.copy())  # store copy for logs

        print(log_register)


if __name__ == "__main__":
    c = ChatBot()
    c.mainbot()
