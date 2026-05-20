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
    this.activeCountdowns = new Map(); // task_id -> {timer, script}
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
    this.loadNegotiationState({ force: true });
    this.startMemoryMonitor();

    if (this.memoryRefreshBtn) {
      this.memoryRefreshBtn.addEventListener("click", () => {
        this.loadNegotiationState({ force: true });
      });
    }

    // 中间件开关
    this.middlewareToggle = document.getElementById("middlewareToggle");
    if (this.middlewareToggle) {
      this.middlewareToggle.addEventListener("change", () => {
        const enabled = this.middlewareToggle.checked;
        this.addSystemMessage(`中间件已${enabled ? "启用" : "禁用"}`);
      });
    }

    window.addEventListener("beforeunload", () => {
      if (this.memoryPollTimer) {
        clearInterval(this.memoryPollTimer);
      }
    });
  }

  addSystemMessage(text) {
    const el = document.createElement("div");
    el.className = "message system-message";
    el.innerHTML = `<div class="message-content"><p><em>${this.escapeHtml(text)}</em></p></div>`;
    this.chatMessages.appendChild(el);
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  startMemoryMonitor() {
    if (this.memoryPollTimer) {
      clearInterval(this.memoryPollTimer);
    }

    this.memoryPollTimer = setInterval(() => {
      this.loadNegotiationState({ silent: true });
    }, 4000);
  }

  async loadNegotiationState(options = {}) {
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
      const userId = "web-user";
      // 并行获取事实和策略
      const [stateRes, strategyRes] = await Promise.all([
        fetch(`/api/negotiation_state?user_id=${userId}&ts=${Date.now()}`),
        fetch(`/api/strategy`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, current_input: "" }),
        }),
      ]);

      if (!stateRes.ok) throw new Error(`State API failed (${stateRes.status})`);
      if (!strategyRes.ok) throw new Error(`Strategy API failed (${strategyRes.status})`);

      const statePayload = await stateRes.json();
      const strategyPayload = await strategyRes.json();

      const facts = statePayload.facts || {};
      const strategy = strategyPayload.strategy || {};

      this.renderFacts(facts);
      this.renderStrategy(strategy, facts);

      if (this.memoryUpdatedAt) {
        this.memoryUpdatedAt.textContent = `更新时间: ${this.formatDateTime(new Date())}`;
      }
    } catch (error) {
      if (silent) return;
      const reason = error instanceof Error ? error.message : String(error);
      this.shortMemoryContent.innerHTML = `<div class="memory-empty">事实加载失败: ${this.escapeHtml(reason)}</div>`;
      this.longMemoryContent.innerHTML = `<div class="memory-empty">策略加载失败: ${this.escapeHtml(reason)}</div>`;
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

  renderFacts(facts) {
    if (!this.shortMemoryContent) {
      return;
    }

    this.shortMemoryContent.innerHTML = "";

    // 构建事实展示 HTML
    const roundCount = facts.round_count || 0;
    const stage = facts.stage || "初始";
    const priceTrajectory = facts.price_trajectory || [];
    const budget = facts.budget || { "值": null, "依据": "" };
    const deletedCoverages = facts["已删险种"] || [];
    const currentCoverages = facts["当前险种"] || [];
    const recentStrategy = facts["最近策略"] || {};
    const coreConcern = facts["核心顾虑"] || "";

    const html = `
      <div class="fact-card">
        <div class="fact-row">
          <span class="fact-label">轮次:</span>
          <span class="fact-value">${roundCount}</span>
        </div>
        <div class="fact-row">
          <span class="fact-label">阶段:</span>
          <span class="fact-value fact-stage">${stage}</span>
        </div>
        <div class="fact-row">
          <span class="fact-label">价格轨迹:</span>
          <span class="fact-value">${priceTrajectory.length ? priceTrajectory.join(" → ") : "—"}</span>
        </div>
        <div class="fact-row">
          <span class="fact-label">预算:</span>
          <span class="fact-value">${budget["值"] !== null ? budget["值"] + "元" : "未提及"}</span>
        </div>
        <div class="fact-row">
          <span class="fact-label">当前险种:</span>
          <span class="fact-value">${currentCoverages.length ? currentCoverages.join(", ") : "—"}</span>
        </div>
        ${deletedCoverages.length ? `
        <div class="fact-row">
          <span class="fact-label">已删险种:</span>
          <span class="fact-value fact-deleted">${deletedCoverages.join(", ")}</span>
        </div>
        ` : ""}
        <div class="fact-row">
          <span class="fact-label">最近策略:</span>
          <span class="fact-value">${recentStrategy["编码"] || "—"}</span>
        </div>
        <div class="fact-row">
          <span class="fact-label">客户反应:</span>
          <span class="fact-value">${recentStrategy["客户反应"] || "—"}</span>
        </div>
        <div class="fact-row">
          <span class="fact-label">结果:</span>
          <span class="fact-value fact-result-${recentStrategy["结果"] === "成功" ? "success" : recentStrategy["结果"] === "失败" ? "fail" : "unknown"}">${recentStrategy["结果"] || "—"}</span>
        </div>
        ${coreConcern ? `
        <div class="fact-row">
          <span class="fact-label">核心顾虑:</span>
          <span class="fact-value fact-concern">${coreConcern}</span>
        </div>
        ` : ""}
      </div>
    `;

    this.shortMemoryContent.innerHTML = html;
  }

  renderStrategy(strategy, facts) {
    if (!this.longMemoryContent) {
      return;
    }

    const analysis = strategy["局势分析"] || "";
    const mainStrategy = strategy["主策略"] || {};

    if (!mainStrategy["编码"]) {
      this.longMemoryContent.innerHTML = '<div class="memory-empty">暂无策略推荐</div>';
      return;
    }

    const html = `
      <div class="strategy-card">
        <div class="strategy-section">
          <div class="strategy-section-title">局势分析</div>
          <div class="strategy-analysis">${this.escapeHtml(analysis)}</div>
        </div>
        <div class="strategy-section">
          <div class="strategy-section-title">主策略</div>
          <div class="strategy-main">
            <div class="strategy-code">${mainStrategy["编码"] || ""}</div>
            <div class="strategy-name">${this.escapeHtml(mainStrategy["名称"] || "")}</div>
            <div class="strategy-module">模块: ${mainStrategy["模块"] || ""}</div>
            <div class="strategy-action">动作: ${this.escapeHtml(mainStrategy["动作"] || "")}</div>
            <div class="strategy-reason">理由: ${this.escapeHtml(mainStrategy["理由"] || "")}</div>
          </div>
        </div>
        ${facts["核心顾虑"] ? `
        <div class="strategy-section">
          <div class="strategy-section-title">核心顾虑</div>
          <div class="strategy-concern">${this.escapeHtml(facts["核心顾虑"])}</div>
        </div>
        ` : ""}
      </div>
    `;

    this.longMemoryContent.innerHTML = html;
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
    let inTable = false;
    let tableRows = [];

    const closeList = () => {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
    };

    const closeTable = () => {
      if (inTable && tableRows.length > 1) { // 至少需要表头+一行数据
        // 第一行是表头
        const headerRow = tableRows[0];
        // 找到分隔符行的位置
        let separatorIndex = -1;
        for (let i = 1; i < tableRows.length; i++) {
          if (tableRows[i].length === 0) {
            separatorIndex = i;
            break;
          }
        }
        // 数据行在分隔符之后
        const bodyRows = separatorIndex > 0 ? tableRows.slice(separatorIndex + 1) : tableRows.slice(1);

        let tableHtml = "<table><thead><tr>";
        headerRow.forEach((cell) => {
          tableHtml += `<th>${this.formatMarkdownInline(cell)}</th>`;
        });
        tableHtml += "</tr></thead><tbody>";

        bodyRows.forEach((row) => {
          if (row.length > 0) {
            tableHtml += "<tr>";
            row.forEach((cell) => {
              tableHtml += `<td>${this.formatMarkdownInline(cell)}</td>`;
            });
            tableHtml += "</tr>";
          }
        });
        tableHtml += "</tbody></table>";

        html.push(tableHtml);
      }
      inTable = false;
      tableRows = [];
    };

    for (const rawLine of lines) {
      const line = rawLine.trimEnd();
      const tokenMatch = line.match(/^@@CODEBLOCK_(\d+)@@$/);
      if (tokenMatch) {
        closeList();
        closeTable();
        html.push(`@@CODEBLOCK_${tokenMatch[1]}@@`);
        continue;
      }

      // 如果是空行，检查是否在表格中
      if (!line.trim()) {
        // 如果在表格中，跳过空行（允许表格行之间有空行）
        if (inTable) {
          continue;
        }
        closeList();
        continue;
      }
      // 检测表格行: | cell1 | cell2 | cell3 |
      const tableMatch = line.match(/^\|(.+)\|$/);
      if (tableMatch) {
        // 解析单元格（按 | 分割，去除首尾空格）
        const cells = tableMatch[1]
          .split("|")
          .map((cell) => cell.trim())
          .filter((cell) => cell.length > 0);

        if (cells.length > 0) {
          // 检测是否为分隔符行 (|---|---|---|)
          const isSeparator = cells.every((cell) => /^[-:]+[-\s:|]*$/.test(cell));

          if (!isSeparator) {
            closeList();
            inTable = true;
            tableRows.push(cells);
          } else if (inTable) {
            // 这是分隔符行，记录但不输出
            tableRows.push([]); // 占位符
          }
          continue;
        }
      }

      // 如果不是表格行但有正在构建的表格，先关闭表格
      if (inTable) {
        closeTable();
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
    closeTable();

    let rendered = html.join("");
    rendered = rendered.replace(/@@CODEBLOCK_(\d+)@@/g, (_, idx) => codeBlocks[Number(idx)] || "");
    return rendered;
  }
  formatMarkdownInline(text) {
    return text
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/==([^=]+)==/g, "<mark>$1</mark>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .replace(/~~([^~]+)~~/g, "<del>$1</del>")
      .replace(/__([^_]+)__/g, "<strong>$1</strong>");
  }

  isMarkdown(text) {
    if (typeof text !== "string" || !text) return false;
    // 检测常见的 Markdown 语法特征
    const markdownPatterns = [
      /^#{1,6}\s+/m,           // 标题 # ## ###
      /^[-*+]\s+/m,            // 无序列表 - * +
      /^\d+\.\s+/m,            // 有序列表 1. 2.
      /\*\*[^*]+\*\*/,         // 粗体 **text**
      /\*[^*]+\*/,             // 斜体 *text*
      /`[^`]+`/,               // 行内代码 `code`
      /```[\s\S]*?```/,        // 代码块
      /\[[^\]]+\]\([^)]+\)/,  // 链接 [text](url)
      /!\[[^\]]*\]\([^)]+\)/, // 图片 ![alt](url)
      /^>\s+/m,                // 引用 >
      /~~[^~]+~~/,             // 删除线 ~~text~~
      /==[^=]+==/,             // 高亮 ==text==
      /^\|.*\|$/m,             // 表格 | col1 | col2 |
      /^-{3,}$/m,              // 水平线 ---
      /^\*\*\*+$/m,            // 水平线 ***
    ];
    return markdownPatterns.some((pattern) => pattern.test(text));
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

    // 用户发送新消息时，取消所有活跃倒计时（视为"点击/交互"）
    this.cancelAllCountdowns();

    this.addUserMessage(message);
    const botMessageEl = this.addBotMessage("", true);
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
          use_middleware: this.middlewareToggle ? this.middlewareToggle.checked : true,
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
          } else if (payload.event === "countdown_started") {
            // 收到倒计时启动事件，开始轮询
            const taskId = payload.task_id;
            const countdownSeconds = payload.countdown_seconds || 10;
            this.addProcessLine(`倒计时启动: ${taskId} (${countdownSeconds}s)`);
            this.startCountdown(taskId);
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

  addBotMessage(content, isLoading = false) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message";

    const contentWrap = document.createElement("div");
    contentWrap.className = "message-content";
    if (isLoading) {
      const loadingDots = document.createElement("div");
      loadingDots.className = "loading-dots";
      loadingDots.innerHTML = "<span></span><span></span><span></span>";
      contentWrap.appendChild(loadingDots);
    } else {
      const p = document.createElement("p");
      p.textContent = content;
      contentWrap.appendChild(p);
    }

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
    const contentWrap = messageDiv.querySelector(".message-content");
    if (!contentWrap) {
      return;
    }

    const loadingDots = contentWrap.querySelector(".loading-dots");
    if (loadingDots) {
      loadingDots.remove();
    }

    // 检测是否为 Markdown 格式
    const isMarkdownContent = this.isMarkdown(content);

    if (isMarkdownContent) {
      // Markdown 内容：使用 innerHTML 渲染富文本
      contentWrap.innerHTML = `<div class="markdown-content">${this.renderMarkdownToHtml(content)}</div>`;
    } else {
      // 非 Markdown 内容：使用 textContent 保持纯文本
      let p = contentWrap.querySelector("p");
      if (!p) {
        p = document.createElement("p");
        contentWrap.appendChild(p);
      }
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

  // ========== 倒计时相关方法 ==========

  /**
   * 启动倒计时轮询
   * @param {string} taskId - 倒计时任务ID
   */
  startCountdown(taskId) {
    // 如果已存在同 taskId 的倒计时，先取消
    if (this.activeCountdowns.has(taskId)) {
      clearInterval(this.activeCountdowns.get(taskId).timer);
    }

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/countdown/${taskId}`);
        if (!response.ok) {
          if (response.status === 404) {
            clearInterval(interval);
            this.activeCountdowns.delete(taskId);
          }
          return;
        }

        const data = await response.json();

        if (data.status === "completed") {
          clearInterval(interval);
          this.activeCountdowns.delete(taskId);
          this.showTimeoutScript(data.timeout_script);
        } else if (data.status === "not_found") {
          clearInterval(interval);
          this.activeCountdowns.delete(taskId);
        } else if (data.status === "error") {
          console.error("Countdown query error:", data.message);
          clearInterval(interval);
          this.activeCountdowns.delete(taskId);
        }
        // running 状态继续轮询
      } catch (error) {
        console.error("Countdown poll error:", error);
        clearInterval(interval);
        this.activeCountdowns.delete(taskId);
      }
    }, 1000); // 每秒轮询一次

    this.activeCountdowns.set(taskId, { timer: interval });
  }

  /**
   * 取消所有活跃的倒计时
   */
  cancelAllCountdowns() {
    for (const [taskId, { timer }] of this.activeCountdowns) {
      clearInterval(timer);
    }
    this.activeCountdowns.clear();
  }

  /**
   * 展示倒计时结束后的话术
   * @param {string} script - 话术内容
   */
  showTimeoutScript(script) {
    if (!script || typeof script !== "string") {
      return;
    }

    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message countdown-script";

    const contentWrap = document.createElement("div");
    contentWrap.className = "message-content";
    const p = document.createElement("p");
    p.textContent = script;
    contentWrap.appendChild(p);

    const time = document.createElement("div");
    time.className = "message-time";
    time.textContent = this.formatNow();

    messageDiv.appendChild(contentWrap);
    messageDiv.appendChild(time);
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();

    this.addProcessLine("倒计时结束，话术已展示");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  new ChatApp();
});
