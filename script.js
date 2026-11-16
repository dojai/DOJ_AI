
const API_URL = "https://YOUR-BACKEND-DOMAIN.com/api/chat";

const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const statusBox = document.getElementById("status");
const clearBtn = document.getElementById("clearBtn");

let messages = [];

function addMessage(text, role) {
  const message = document.createElement("div");
  message.className = `message ${role}`;
  message.textContent = text;
  chatBox.appendChild(message);
  chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = userInput.value.trim();

  if (!question || sendBtn.disabled) return;

  chatBox.querySelector(".welcome")?.remove();

  addMessage(question, "user");

  messages.push({
    role: "user",
    content: question
  });

  userInput.value = "";
  sendBtn.disabled = true;
  statusBox.textContent = "AI is thinking...";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        messages: messages.slice(-12)
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Request failed.");
    }

    addMessage(data.reply, "assistant");

    messages.push({
      role: "assistant",
      content: data.reply
    });

    messages = messages.slice(-12);

    statusBox.textContent = "";

  } catch (error) {
    addMessage(
      "Sorry, something went wrong. Please try again.",
      "assistant"
    );

    messages.pop();
    statusBox.textContent = error.message;

  } finally {
    sendBtn.disabled = false;
    userInput.focus();
  }
});

clearBtn.addEventListener("click", () => {
  messages = [];
  chatBox.innerHTML = `
    <div class="welcome">
      <h1>How can I help you?</h1>
      <p>Ask me anything. I'm ready to assist!</p>
    </div>
  `;
  statusBox.textContent = "";
});
