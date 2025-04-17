const apiKey = "AIzaSyCitsYctNp0B4eSz1xg-j80PrK9NnktvVY";
const apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

async function chatWithGemini(prompt) {
  const response = await fetch(`${apiUrl}?key=${apiKey}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      contents: [{
        parts: [{
          text: prompt
        }]
      }]
    })
  });

  if (response.ok) {
    const data = await response.json();
    return data.candidates[0].content.parts[0].text;
  } else {
    console.error("Error with API:", response.statusText);
    return "Sorry, there was an error with the API.";
  }
}

function sendMessage() {
  const userInput = document.getElementById("userInput").value;
  if (userInput.trim() === "") return;

  displayMessage(userInput, "user");
  document.getElementById("userInput").value = "";

  chatWithGemini(userInput).then(response => {
    displayMessage(response, "bot");
  });
}

function displayMessage(message, sender) {
  const chatBox = document.getElementById("chatBox");
  const messageElement = document.createElement("div");
  messageElement.classList.add("chat-message");
  messageElement.classList.add(sender === "user" ? "user-message" : "bot-message");
  messageElement.innerHTML = `<p>${message}</p>`;
  chatBox.appendChild(messageElement);

  chatBox.scrollTop = chatBox.scrollHeight;
}
