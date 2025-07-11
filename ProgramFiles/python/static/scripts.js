function formatBotReply(reply) {
    return marked.parse(reply);
}

function sendMessage() {
    const userInput = document.getElementById("user_input").value;
    const chatbox = document.getElementById("chatbox");

    chatbox.innerHTML += `<div class="user"><strong>You:</strong> ${userInput}</div>`;
    document.getElementById("user_input").value = "";

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        const formattedReply = formatBotReply(data.reply);
        chatbox.innerHTML += `<div class="bot"><strong>Bot:</strong> ${formattedReply}</div>`;
        chatbox.scrollTop = chatbox.scrollHeight;
    })
    .catch(error => {
        chatbox.innerHTML += `<div class="bot"><strong>Bot:</strong> Error: ${error}</div>`;
    });
}
