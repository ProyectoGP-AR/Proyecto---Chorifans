document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chori-bot-form");
  const input = document.getElementById("chori-bot-input");
  const messages = document.getElementById("chori-bot-messages");

  if (!form || !input || !messages) {
    return;
  }

  const context = window.CHORI_BOT_CONTEXT || {};

  function getCsrfToken() {
    const cookieValue = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="));

    return cookieValue ? cookieValue.split("=")[1] : "";
  }

  function scrollMessagesToBottom() {
    messages.scrollTop = messages.scrollHeight;
  }

  function isSafeUrl(url) {
    if (!url || typeof url !== "string") {
      return false;
    }

    return (
      url.startsWith("/") ||
      url.startsWith("http://") ||
      url.startsWith("https://")
    );
  }

  function createStyledLink(label, url) {
    const link = document.createElement("a");
    link.href = url;
    link.textContent = label;
    link.target = url.startsWith("http") ? "_blank" : "_self";
    link.rel = url.startsWith("http") ? "noopener noreferrer" : "";
    link.style.color = "#ffd27a";
    link.style.textDecoration = "underline";
    link.style.fontWeight = "700";
    return link;
  }

  function appendRichText(container, text) {
    const lines = String(text || "").split("\n");
    const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;

    lines.forEach((line, lineIndex) => {
      let lastIndex = 0;
      let match;

      while ((match = markdownLinkRegex.exec(line)) !== null) {
        const [fullMatch, label, url] = match;
        const matchIndex = match.index;

        if (matchIndex > lastIndex) {
          container.appendChild(
            document.createTextNode(line.slice(lastIndex, matchIndex))
          );
        }

        if (isSafeUrl(url)) {
          container.appendChild(createStyledLink(label, url));
        } else {
          container.appendChild(document.createTextNode(fullMatch));
        }

        lastIndex = matchIndex + fullMatch.length;
      }

      if (lastIndex < line.length) {
        container.appendChild(document.createTextNode(line.slice(lastIndex)));
      }

      if (lineIndex < lines.length - 1) {
        container.appendChild(document.createElement("br"));
      }
    });
  }

  function createMessageElement(content, type = "bot", isLoading = false) {
    const message = document.createElement("div");
    message.className = `chori-bot-message chori-bot-message--${type}`;

    if (type === "bot") {
      message.style.cssText = `
        max-width: 84%;
        align-self: flex-start;
        background: #3b2507;
        color: #fff3df;
        border: 1px solid rgba(255, 152, 0, 0.45);
        border-radius: 18px;
        border-bottom-left-radius: 6px;
        padding: 11px 14px;
        line-height: 1.42;
        font-size: 0.96rem;
        word-break: break-word;
        white-space: normal;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.22);
        margin-bottom: 6px;
      `;
    } else {
      message.style.cssText = `
        max-width: 84%;
        align-self: flex-end;
        background: linear-gradient(180deg, #ffb52d, #ff9800);
        color: #181818;
        border: 1px solid rgba(255, 193, 7, 0.65);
        border-radius: 18px;
        border-bottom-right-radius: 6px;
        padding: 11px 14px;
        line-height: 1.42;
        font-size: 0.96rem;
        font-weight: 500;
        word-break: break-word;
        white-space: pre-line;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.22);
        margin-bottom: 6px;
      `;
    }

    if (isLoading) {
      message.style.opacity = "0.8";
      message.style.fontStyle = "italic";
    }

    if (type === "bot") {
      appendRichText(message, content);
    } else {
      message.textContent = String(content || "");
    }

    return message;
  }

  function appendMessage(content, type = "bot", isLoading = false) {
    const message = createMessageElement(content, type, isLoading);
    messages.appendChild(message);
    scrollMessagesToBottom();
    return message;
  }

  async function sendMessageToBot(userMessage) {
    const loadingMessage = appendMessage("Pensando...", "bot", true);

    try {
      const response = await fetch("/api/chatbot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          message: userMessage,
          context: {
            currentPath: context.currentPath || window.location.pathname,
            currentView: context.currentView || "",
            isAuthenticated: context.isAuthenticated || false,
            username: context.username || "",
            pageTitle: document.title,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Error HTTP ${response.status}`);
      }

      const data = await response.json();

      loadingMessage.remove();

      const botReply =
        data.reply ||
        data.response ||
        data.message ||
        "Perdón, no pude responder en este momento.";

      appendMessage(botReply, "bot");
    } catch (error) {
      console.error("Error al consultar Chori Bot:", error);
      loadingMessage.remove();

      appendMessage(
        "Uy, en este momento no me pude conectar. Probá de nuevo en unos segundos.",
        "bot"
      );
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const userMessage = input.value.trim();

    if (!userMessage) {
      return;
    }

    appendMessage(userMessage, "user");
    input.value = "";
    input.focus();

    await sendMessageToBot(userMessage);
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  scrollMessagesToBottom();
});