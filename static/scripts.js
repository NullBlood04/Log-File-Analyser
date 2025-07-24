// Global controller to abort fetch requests. Also serves as a state flag.
let abortController = null;

function formatBotReply(reply) {
    return marked.parse(reply);
}

// Main form submission handler
document.getElementById("chatForm").addEventListener("submit", function(event) {
  event.preventDefault(); // Prevent page reload
  // If a request is already in progress, the submit event should do nothing.
  // The button's own click handler will manage stopping.
  if (abortController) {
      return;
  }
  sendMessage();
});

// Add a click listener to the button to handle the "Stop" action
document.getElementById("sendButton").addEventListener("click", function(event) {
    // If a request is in flight, this click should stop it.
    if (abortController) {
        event.preventDefault(); // Prevent the form from submitting again
        abortController.abort();
    }
    // If no request is in flight, this click will trigger the form's "submit" event,
    // which is what we want.
});


function sendMessage() {
    const userInputField = document.getElementById("user_input");
    const userInput = userInputField.value.trim();
    const sendButton = document.getElementById("sendButton");
    const chatbox = document.getElementById("chatbox");

    // Don't send empty messages
    if (!userInput) {
        return;
    }

    // Set up the AbortController for this request
    abortController = new AbortController();

    // Update UI to show "in progress" state
    sendButton.textContent = "Abort";

    // Display user message securely
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'user';
    userMessageDiv.textContent = userInput; // Use textContent to prevent XSS
    chatbox.appendChild(userMessageDiv);
    chatbox.scrollTop = chatbox.scrollHeight;

    userInputField.value = ""; // Clear input field

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput }),
        signal: abortController.signal // Link the request to the controller
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const formattedReply = formatBotReply(data.reply);
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'bot';
        botMessageDiv.innerHTML = formattedReply; // Assuming marked.parse() is safe
        chatbox.appendChild(botMessageDiv);
    })
    .catch(error => {
        // Don't show an error if the user intentionally aborted the request
        if (error.name === 'AbortError') {
            console.log('Fetch aborted by user.');
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'bot';
            botMessageDiv.textContent = 'Generation stopped.';
            chatbox.appendChild(botMessageDiv);
        } else {
            console.error('Fetch error:', error);
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'bot';
            botMessageDiv.textContent = `Error: ${error.message}`;
            chatbox.appendChild(botMessageDiv);
        }
    })
    .finally(() => {
        // This block runs whether the fetch succeeded, failed, or was aborted.
        chatbox.scrollTop = chatbox.scrollHeight;
        sendButton.disabled = false;
        sendButton.textContent = "Send";
        abortController = null; // Reset the controller
    });
}
