from flask import Flask, render_template, request, jsonify
import markdown2
from langchain_core.messages import AIMessage
from dependency import ChatBot

app = Flask(__name__, template_folder=r"..\..\templates", static_folder=r"..\..\static")

bot = ChatBot()

state = {"messages": []}


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]  # type: ignore

    # Process input via your existing function
    new_state = bot.stream_graph(user_input, state)  # type: ignore

    # Get last AI message from updated state
    ai_message = ""
    for msg in reversed(new_state["messages"]):
        if isinstance(msg, AIMessage):
            ai_message = msg.content
            break

    formated_aiMessage = markdown2.markdown(ai_message, extras=["fenced-code-blocks"])  # type: ignore
    return jsonify({"reply": formated_aiMessage})


if __name__ == "__main__":
    app.run(debug=True)
