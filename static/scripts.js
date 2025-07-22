function formatBotReply(reply) {
    return marked.parse(reply);
}

document.getElementById("chatForm").addEventListener("submit", function(event) {
  event.preventDefault(); // Prevent page reload
  // Call your send message function here
  sendMessage();
});

function sendMessage() {
    const userInput = document.getElementById("user_input").value;
    const sentBtn = document.getElementById("sendButton");
    const chatbox = document.getElementById("chatbox");

    sentBtn.disabled = true;
    sentBtn.textContent = "Sending";

    chatbox.innerHTML += `<div class="user">${userInput}</div>`;
    document.getElementById("user_input").value = "";

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        const formattedReply = formatBotReply(data.reply);
        chatbox.innerHTML += `<div class="bot">${formattedReply}</div>`;
        chatbox.scrollTop = chatbox.scrollHeight;
        sentBtn.disabled = false;
        sentBtn.textContent = "Send";
    })
    .catch(error => {
        chatbox.innerHTML += `<div class="bot">Error: ${error}</div>`;
        sentBtn.disabled = false;
        sentBtn.textContent = "Send";
    });
}
