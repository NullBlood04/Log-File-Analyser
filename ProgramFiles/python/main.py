from flask import Flask, render_template, request, jsonify
from langchain_core.messages import HumanMessage, AIMessage
from dependency import ChatBot

app = Flask(__name__)

bot = ChatBot()

state = {"messages": []}


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]

    # Process input via your existing function
    new_state = bot.stream_graph(user_input, state)

    # Get last AI message from updated state
    ai_message = ""
    for msg in reversed(new_state["messages"]):
        if isinstance(msg, AIMessage):
            ai_message = msg.content
            break

    return jsonify({"reply": ai_message})


if __name__ == "__main__":
    app.run(debug=True)
