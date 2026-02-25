class ChatApp {
  constructor() {
    this.chatMessages = document.getElementById("chatMessages");
    this.messageInput = document.getElementById("messageInput");
    this.sendButton = document.getElementById("sendButton");
    this.processLogs = document.getElementById("processLogs");
    this.skillsList = document.getElementById("skillsList");
    this.customerList = document.getElementById("customerList");
    this.shortMemoryContent = document.getElementById("shortMemoryContent");
    this.longMemoryContent = document.getElementById("longMemoryContent");
    this.memoryUpdatedAt = document.getElementById("memoryUpdatedAt");
    this.memoryRefreshBtn = document.getElementById("memoryRefreshBtn");
    this.threadId = "";
    this.history = [];
    this.isSending = false;
    this.abortController = null;
    this.memoryVersion = "";
    this.memoryPollTimer = null;
    this.isLoadingMemories = false;
    this.init();
  }

  init() {
    this.sendButton.addEventListener("click", () => this.sendMessage());
    this.messageInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        this.sendMessage();
      }
    });

    this.loadCustomers();
    this.loadSkills();
    this.loadMemories({ force: true });
    this.startMemoryMonitor();

    if (this.memoryRefreshBtn) {
      this.memoryRefreshBtn.addEventListener("click", () => {
        this.loadMemories({ force: true });
      });
    }

    window.addEventListener("beforeunload", () => {
      if (this.memoryPollTimer) {
        clearInterval(this.memoryPollTimer);
      }
    });
  }

  startMemoryMonitor() {
    if (this.memoryPollTimer) {
      clearInterval(this.memoryPollTimer);
    }

    this.memoryPollTimer = setInterval(() => {
      this.loadMemories({ silent: true });
    }, 4000);
  }

  async loadMemories(options = {}) {
    const { force = false, silent = false } = options;
    if (!this.shortMemoryContent || !this.longMemoryContent) {
      return;
    }

    if (this.isLoadingMemories) {
      return;
    }

    this.isLoadingMemories = true;
    if (this.memoryRefreshBtn) {
      this.memoryRefreshBtn.disabled = true;
    }

    try {
      const response = await fetch(`/api/memories?ts=${Date.now()}`);
      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }

      const payload = await response.json();
      const nextVersion =
        typeof payload.version === "string" || typeof payload.version === "number"
          ? String(payload.version)
          : "";

      if (!force && nextVersion && this.memoryVersion && nextVersion === this.memoryVersion) {
        return;
      }

      this.memoryVersion = nextVersion || this.memoryVersion;
      const shortTerm = Array.isArray(payload.short_term) ? payload.short_term : [];
      const longTerm = payload.long_term && typeof payload.long_term === "object" ? payload.long_term : {};

      this.renderShortMemories(shortTerm);
      this.renderLongMemory(longTerm);
      this.updateMemoryUpdatedAt(nextVersion);
    } catch (error) {
      if (silent) {
        return;
      }
      const reason = error instanceof Error ? error.message : String(error);
      this.shortMemoryContent.innerHTML = `<div class="memory-empty">短期记忆加载失败: ${this.escapeHtml(reason)}</div>`;
      this.longMemoryContent.innerHTML = `<div class="memory-empty">长期记忆加载失败: ${this.escapeHtml(reason)}</div>`;
      if (this.memoryUpdatedAt) {
        this.memoryUpdatedAt.textContent = "更新时间: 刷新失败";
      }
    } finally {
      this.isLoadingMemories = false;
      if (this.memoryRefreshBtn) {
        this.memoryRefreshBtn.disabled = false;
      }
    }
  }

  updateMemoryUpdatedAt(version) {
    if (!this.memoryUpdatedAt) {
      return;
    }

    const seconds = Number(version);
    if (Number.isFinite(seconds) && seconds > 0) {
      const updated = new Date(seconds * 1000);
      this.memoryUpdatedAt.textContent = `更新时间: ${this.formatDateTime(updated)}`;
      return;
    }

    this.memoryUpdatedAt.textContent = `更新时间: ${this.formatDateTime(new Date())}`;
  }

  renderShortMemories(items) {
    if (!this.shortMemoryContent) {
      return;
    }

    this.shortMemoryContent.innerHTML = "";
    if (!items.length) {
      this.shortMemoryContent.innerHTML = '<div class="memory-empty">暂无短期记忆</div>';
      return;
    }

    for (const item of items) {
      const wrapper = document.createElement("div");
      wrapper.className = "memory-doc";

      const header = document.createElement("div");
      header.className = "memory-doc-header";
      header.textContent =
        typeof item.date === "string" && item.date ? item.date : "unknown-date";
      wrapper.appendChild(header);

      const body = document.createElement("div");
      body.className = "memory-md";
      const content = typeof item.content === "string" ? item.content : "";
      body.innerHTML = this.renderMarkdownToHtml(content || "(空内容)");
      wrapper.appendChild(body);

      this.shortMemoryContent.appendChild(wrapper);
    }
  }

  renderLongMemory(item) {
    if (!this.longMemoryContent) {
      return;
    }

    const content = item && typeof item.content === "string" ? item.content : "";
    if (!content.trim()) {
      this.longMemoryContent.innerHTML = '<div class="memory-empty">暂无长期记忆</div>';
      return;
    }

    this.longMemoryContent.innerHTML = `<div class="memory-md">${this.renderMarkdownToHtml(content)}</div>`;
  }

  renderMarkdownToHtml(markdown) {
    const input = typeof markdown === "string" ? markdown : "";
    const escaped = this.escapeHtml(input);

    const codeBlocks = [];
    const withPlaceholders = escaped.replace(/```([\s\S]*?)```/g, (_, code) => {
      const index = codeBlocks.length;
      codeBlocks.push(`<pre><code>${code}</code></pre>`);
      return `@@CODEBLOCK_${index}@@`;
    });

    const lines = withPlaceholders.split("\n");
    const html = [];
    let inList = false;

    const closeList = () => {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
    };

    for (const rawLine of lines) {
      const line = rawLine.trimEnd();
      const tokenMatch = line.match(/^@@CODEBLOCK_(\d+)@@$/);
      if (tokenMatch) {
        closeList();
        html.push(`@@CODEBLOCK_${tokenMatch[1]}@@`);
        continue;
      }

      if (!line.trim()) {
        closeList();
        continue;
      }

      const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
      if (headingMatch) {
        closeList();
        const level = headingMatch[1].length;
        html.push(`<h${level}>${this.formatMarkdownInline(headingMatch[2])}</h${level}>`);
        continue;
      }

      const listMatch = line.match(/^[-*]\s+(.*)$/);
      if (listMatch) {
        if (!inList) {
          html.push("<ul>");
          inList = true;
        }
        html.push(`<li>${this.formatMarkdownInline(listMatch[1])}</li>`);
        continue;
      }

      closeList();
      html.push(`<p>${this.formatMarkdownInline(line)}</p>`);
    }

    closeList();
    let rendered = html.join("");
    rendered = rendered.replace(/@@CODEBLOCK_(\d+)@@/g, (_, idx) => codeBlocks[Number(idx)] || "");
    return rendered;
  }

  formatMarkdownInline(text) {
    return text
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/==([^=]+)==/g, "<mark>$1</mark>");
  }

  async loadSkills() {
    if (!this.skillsList) {
      return;
    }

    try {
      const response = await fetch("/api/skills");
      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }

      const payload = await response.json();
      const skills = Array.isArray(payload.skills) ? payload.skills : [];
      this.renderSkills(skills);
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      this.skillsList.innerHTML = "";
      const item = document.createElement("div");
      item.className = "skill-item muted";
      item.textContent = `技能包加载失败: ${reason}`;
      this.skillsList.appendChild(item);
    }
  }

  async loadCustomers() {
    if (!this.customerList) {
      return;
    }

    try {
      const response = await fetch("/api/customers");
      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }

      const payload = await response.json();
      const customers = Array.isArray(payload.customers) ? payload.customers : [];
      this.renderCustomers(customers);
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      this.customerList.innerHTML = "";
      const item = document.createElement("div");
      item.className = "customer-card muted";
      item.textContent = `客户信息加载失败: ${reason}`;
      this.customerList.appendChild(item);
    }
  }

  renderCustomers(customers) {
    if (!this.customerList) {
      return;
    }

    this.customerList.innerHTML = "";
    if (!customers.length) {
      const item = document.createElement("div");
      item.className = "customer-card muted";
      item.textContent = "暂无客户信息";
      this.customerList.appendChild(item);
      return;
    }

    for (const customer of customers) {
      const card = document.createElement("div");
      card.className = "customer-card";

      const name =
        typeof customer.name === "string" && customer.name ? customer.name : "未知客户";
      const age = typeof customer.age === "string" && customer.age ? customer.age : "--";
      const gender =
        typeof customer.gender === "string" && customer.gender ? customer.gender : "--";
      const behavior =
        typeof customer.behavior === "string" && customer.behavior ? customer.behavior : "--";

      card.innerHTML =
        `<div class="customer-name">${this.escapeHtml(name)}</div>` +
        `<div class="customer-field"><span>年龄</span><strong>${this.escapeHtml(age)}</strong></div>` +
        `<div class="customer-field"><span>性别</span><strong>${this.escapeHtml(gender)}</strong></div>` +
        `<div class="customer-field behavior"><span>行为</span><strong>${this.escapeHtml(behavior)}</strong></div>`;

      this.customerList.appendChild(card);
    }
  }

  renderSkills(skills) {
    if (!this.skillsList) {
      return;
    }

    this.skillsList.innerHTML = "";
    if (!skills.length) {
      const item = document.createElement("div");
      item.className = "skill-item muted";
      item.textContent = "未发现技能包";
      this.skillsList.appendChild(item);
      return;
    }

    for (const skill of skills) {
      const item = document.createElement("div");
      item.className = "skill-item";

      const nameEl = document.createElement("div");
      nameEl.className = "skill-name";
      nameEl.textContent =
        typeof skill.name === "string" && skill.name ? skill.name : "unknown";
      item.appendChild(nameEl);

      if (typeof skill.path === "string" && skill.path) {
        const pathEl = document.createElement("div");
        pathEl.className = "skill-path";
        pathEl.textContent = skill.path;
        item.appendChild(pathEl);
      }

      this.skillsList.appendChild(item);
    }
  }

  stopGeneration() {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }

  async sendMessage() {
    if (this.isSending) {
      this.stopGeneration();
      return;
    }

    const message = this.messageInput.value.trim();
    if (!message) {
      return;
    }

    this.addUserMessage(message);
    const botMessageEl = this.addBotMessage("");
    this.resetProcessLogs();
    this.messageInput.value = "";
    this.setSending(true);

    try {
      this.abortController = new AbortController();
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
        signal: this.abortController.signal,
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
          } else if (payload.event === "replace") {
            fullReply = payload.text || "";
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
      if (error.name === "AbortError") {
        this.addProcessLine("用户停止生成", true);
        return;
      }
      const reason = error instanceof Error ? error.message : String(error);
      this.updateBotMessage(botMessageEl, `请求失败: ${reason}`);
      this.addProcessLine(`请求失败: ${reason}`, true);
    } finally {
      this.abortController = null;
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
    if (sending) {
      this.sendButton.disabled = false;
      this.sendButton.textContent = "停止";
      this.sendButton.classList.add("stop-mode");
    } else {
      this.sendButton.disabled = false;
      this.sendButton.textContent = "发送";
      this.sendButton.classList.remove("stop-mode");
    }
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

    const contentWrap = document.createElement("div");
    contentWrap.className = "message-content";
    const p = document.createElement("p");
    p.textContent = content;
    contentWrap.appendChild(p);

    const time = document.createElement("div");
    time.className = "message-time";
    time.textContent = this.formatNow();

    messageDiv.appendChild(contentWrap);
    messageDiv.appendChild(time);
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
    return messageDiv;
  }

  updateBotMessage(messageDiv, content) {
    const p = messageDiv.querySelector(".message-content p");
    if (p) {
      p.textContent = content;
    }
    this.scrollToBottom();
  }

  formatNow() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, "0");
    const minutes = now.getMinutes().toString().padStart(2, "0");
    return `${hours}:${minutes}`;
  }

  formatDateTime(dt) {
    const y = dt.getFullYear();
    const m = String(dt.getMonth() + 1).padStart(2, "0");
    const d = String(dt.getDate()).padStart(2, "0");
    const h = String(dt.getHours()).padStart(2, "0");
    const min = String(dt.getMinutes()).padStart(2, "0");
    const sec = String(dt.getSeconds()).padStart(2, "0");
    return `${y}-${m}-${d} ${h}:${min}:${sec}`;
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
