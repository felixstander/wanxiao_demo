class ChatApp {
  constructor() {
    this.chatMessages = document.getElementById("chatMessages");
    this.messageInput = document.getElementById("messageInput");
    this.sendButton = document.getElementById("sendButton");
    this.processLogs = document.getElementById("processLogs");
    this.threadId = "";
    this.history = [];
    this.isSending = false;
    this.init();
  }

  init() {
    this.sendButton.addEventListener("click", () => this.sendMessage());
    this.messageInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        this.sendMessage();
      }
    });

    const suggestedButtons = document.querySelectorAll(".suggested-btn");
    suggestedButtons.forEach((btn) => {
      btn.addEventListener("click", (event) => {
        const question = event.currentTarget.dataset.question || "";
        this.messageInput.value = question;
        this.sendMessage();
      });
    });
  }

  async sendMessage() {
    const message = this.messageInput.value.trim();
    if (!message || this.isSending) {
      return;
    }

    this.addUserMessage(message);
    const botMessageEl = this.addBotMessage("");
    this.resetProcessLogs();
    this.messageInput.value = "";
    this.setSending(true);

    try {
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          history: this.history,
          thread_id: this.threadId || null,
        }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed (${response.status})`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let fullReply = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const block of parts) {
          const line = block
            .split("\n")
            .find((l) => l.startsWith("data: "));
          if (!line) {
            continue;
          }

          const payload = JSON.parse(line.slice(6));
          if (payload.event === "start") {
            this.threadId = payload.thread_id || this.threadId;
            this.addProcessLine(`会话开始: ${this.threadId}`);
          } else if (payload.event === "delta") {
            fullReply += payload.text || "";
            this.updateBotMessage(botMessageEl, fullReply);
          } else if (payload.event === "process") {
            this.addProcessLine(payload.text || "(空过程信息)");
          } else if (payload.event === "done") {
            this.threadId = payload.thread_id || this.threadId;
            this.history = Array.isArray(payload.history) ? payload.history : this.history;
            this.addProcessLine("完成");
          } else if (payload.event === "error") {
            fullReply += `\n\n[流式中断] ${payload.detail || "unknown error"}`;
            this.updateBotMessage(botMessageEl, fullReply);
            this.addProcessLine(payload.detail || "stream error", true);
          }
        }
      }

      if (!fullReply) {
        this.updateBotMessage(botMessageEl, "(空回复)");
      }
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      this.updateBotMessage(botMessageEl, `请求失败: ${reason}`);
      this.addProcessLine(`请求失败: ${reason}`, true);
    } finally {
      this.setSending(false);
    }
  }

  resetProcessLogs() {
    if (!this.processLogs) {
      return;
    }
    this.processLogs.innerHTML = "";
  }

  addProcessLine(text, isError = false) {
    if (!this.processLogs) {
      return;
    }
    const line = document.createElement("div");
    line.className = isError ? "process-line error" : "process-line";
    line.textContent = text;
    this.processLogs.appendChild(line);
    this.processLogs.scrollTop = this.processLogs.scrollHeight;
  }

  setSending(sending) {
    this.isSending = sending;
    this.sendButton.disabled = sending;
    this.sendButton.textContent = sending ? "发送中..." : "发送";
  }

  addUserMessage(content) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message user-message";
    messageDiv.innerHTML =
      '<div class="message-content"><p>' +
      this.escapeHtml(content) +
      "</p></div>" +
      `<div class="message-time">${this.formatNow()}</div>`;
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
  }

  addBotMessage(content) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message";
    let formattedContent = this.escapeHtml(content);
    formattedContent = formattedContent.replace(
      /```([\s\S]*?)```/g,
      "<pre><code>$1</code></pre>",
    );

    messageDiv.innerHTML =
      '<div class="message-content"><p>' +
      formattedContent +
      "</p></div>" +
      `<div class="message-time">${this.formatNow()}</div>`;
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
    return messageDiv;
  }

  updateBotMessage(messageDiv, content) {
    let formattedContent = this.escapeHtml(content);
    formattedContent = formattedContent.replace(
      /```([\s\S]*?)```/g,
      "<pre><code>$1</code></pre>",
    );

    const p = messageDiv.querySelector(".message-content p");
    if (p) {
      p.innerHTML = formattedContent;
    }
    this.scrollToBottom();
  }

  formatNow() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, "0");
    const minutes = now.getMinutes().toString().padStart(2, "0");
    return `${hours}:${minutes}`;
  }

  scrollToBottom() {
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  escapeHtml(text) {
    if (typeof text !== "string") {
      return "";
    }
    const map = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  new ChatApp();
});
