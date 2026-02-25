# 前端UI改进计划：加载动画与布局调整

## TL;DR

> **目标**：改进AI对话平台前端的两个用户体验问题
> 
> **改进1**：添加AI响应等待期间的加载动画（三个点动画），避免用户看到空白内容
> **改进2**：将右侧边栏的思考过程窗口和skills区域从1:1比例调整为2:3比例
> 
> **涉及文件**：
> - `frontend/script.js` - 加载动画逻辑
> - `frontend/style.css` - 加载动画样式和布局比例
> 
> **预计工作量**：Quick (15-30分钟)

---

## Context

### 当前问题分析

**问题1 - 缺失加载动画：**
在 `script.js` 的 `sendMessage()` 方法中：
1. 用户发送消息后调用 `addBotMessage("")` 创建空的AI消息占位符
2. 在等待 `fetch("/api/chat/stream")` 响应期间（通常1-3秒），聊天区域显示空白内容
3. 用户无法感知系统正在工作，体验不佳

**问题2 - 布局比例不当：**
在 `style.css` 的 `.side-column` 中：
- `.process-panel` 设置 `flex: 1`（自适应高度）
- `.skills-section` 设置 `min-height: 210px`（固定最小高度）
- 实际视觉比例接近1:1，但用户希望思考过程窗口更大一些，比例为2:3

### 技术栈

- 前端：原生 HTML + CSS + JavaScript
- 后端：FastAPI + DeepAgents
- 构建：无需构建，静态文件直接服务

---

## Work Objectives

### Core Objective
实现两个前端UI改进：加载动画和布局比例调整

### Concrete Deliverables
- [ ] 添加加载动画HTML结构和CSS样式
- [ ] 修改 `addBotMessage()` 方法支持加载状态
- [ ] 修改 `updateBotMessage()` 方法移除加载状态
- [ ] 调整 `.side-column` flex布局比例为2:3

### Definition of Done
- [ ] 发送消息后，AI消息区域显示三个点加载动画
- [ ] 收到首个响应字节后，加载动画消失，显示实际内容
- [ ] 思考过程窗口和skills区域比例为2:3
- [ ] 所有改动在浏览器中正常显示，无CSS破坏

### Must Have
- [x] 加载动画在AI响应期间可见
- [x] 布局比例调整为2:3

### Must NOT Have (Guardrails)
- [ ] 不要改变现有主题颜色
- [ ] 不要破坏移动端响应式布局
- [ ] 不要添加新的依赖库

---

## Verification Strategy

### QA Policy
所有任务通过浏览器手动验证，使用 `/start-work` 启动后打开 `http://localhost:7860` 进行测试。

---

## Execution Strategy

### Parallel Execution Waves

这是一个快速UI调整任务，只有1个Wave，2个顺序任务（存在依赖关系）：

```
Wave 1 (顺序执行):
├── Task 1: 添加加载动画功能 [quick]
│   └── 依赖: 无
│   └── 包含: HTML结构 + CSS动画 + JS逻辑
│   └── 输出: 加载动画在AI响应等待期间可见
└── Task 2: 调整右侧边栏布局比例 [quick]
    └── 依赖: 无（与Task 1独立）
    └── 包含: CSS修改
    └── 输出: 思考过程窗口:skills = 2:3

可并行度: 高 (Task 1和Task 2可以并行执行，互不影响)
```

---

## TODOs

- [ ] 1. 添加AI响应加载动画

  **What to do**:
  1. 在 `style.css` 中添加加载动画CSS（三个点弹跳动画）
  2. 修改 `script.js` 中的 `addBotMessage()` 方法，添加加载动画元素
  3. 修改 `updateBotMessage()` 方法，在第一次更新内容时移除加载动画

  **Must NOT do**:
  - 不要使用外部CSS框架
  - 不要改变现有动画timing函数

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Reason**: 前端UI调整，需要CSS动画技能
  - **Skills**: `frontend-ui-ux`

  **Parallelization**:
  - **Can Run In Parallel**: YES (与Task 2独立)
  - **Blocks**: 无
  - **Blocked By**: 无

  **References** (CRITICAL):

  **Pattern References**:
  - `frontend/script.js:516-534` - `addBotMessage()` 方法，需要添加加载动画
  - `frontend/script.js:537-543` - `updateBotMessage()` 方法，需要移除加载动画

  **Style References**:
  - `frontend/style.css:506-515` - 现有 `@keyframes fadeIn` 动画参考

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: 加载动画显示 - 用户发送消息后
    Tool: Playwright
    Preconditions: 页面已加载，后端服务运行中
    Steps:
      1. 在输入框中输入"你好"
      2. 点击"发送"按钮
      3. 等待500ms
    Expected Result: AI消息区域显示三个点动画，不是空白
    Evidence: .sisyphus/evidence/task-1-loading-visible.png

  Scenario: 加载动画消失 - 收到AI响应
    Tool: Playwright
    Preconditions: 已发送消息，加载动画显示中
    Steps:
      1. 观察AI消息区域
      2. 等待AI响应到达（通常1-3秒）
      3. 验证第一个响应字节到达后动画消失
    Expected Result: 加载动画消失，显示AI实际回复内容
    Evidence: .sisyphus/evidence/task-1-loading-gone.png
  ```

  **Evidence to Capture**:
  - [ ] 截图：加载动画显示状态
  - [ ] 截图：加载动画消失后显示内容

  **Commit**: YES
  - Message: `feat(frontend): add loading animation during AI response`
  - Files: `frontend/script.js`, `frontend/style.css`

---

- [ ] 2. 调整右侧边栏布局比例为2:3

  **What to do**:
  1. 修改 `style.css` 中的 `.side-column`，设置为 `flex-direction: column`（已有）
  2. 修改 `.process-panel` 的 `flex` 属性为 `flex: 2`
  3. 修改 `.skills-section` 的 `flex` 属性为 `flex: 1`

  **Must NOT do**:
  - 不要修改 `.side-column` 的宽度（保持 `min(320px, 28vw)`）
  - 不要删除 `min-height` 约束

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Reason**: CSS布局调整
  - **Skills**: `frontend-ui-ux`

  **Parallelization**:
  - **Can Run In Parallel**: YES (与Task 1独立)
  - **Blocks**: 无
  - **Blocked By**: 无

  **References** (CRITICAL):

  **Pattern References**:
  - `frontend/style.css:98-106` - `.side-column` 容器定义
  - `frontend/style.css:108-117` - `.process-panel` 思考过程面板
  - `frontend/style.css:207-216` - `.skills-section` skills区域

  **Acceptance Criteria**:

  **QA Scenarios:**

  ```
  Scenario: 布局比例验证 - 思考过程窗口占2/3
    Tool: Playwright
    Preconditions: 页面已加载，浏览器窗口宽度 > 768px
    Steps:
      1. 打开浏览器开发者工具
      2. 检查 `.process-panel` 元素高度
      3. 检查 `.skills-section` 元素高度
      4. 验证比例为 2:1（思考过程是skills的两倍高度）
    Expected Result: 思考过程窗口高度是skills区域的约2倍
    Evidence: .sisyphus/evidence/task-2-layout-ratio.png

  Scenario: 移动端响应式 - 比例在移动端不生效
    Tool: Playwright
    Preconditions: 浏览器窗口宽度 < 768px（模拟移动端）
    Steps:
      1. 设置视口宽度为 375px
      2. 刷新页面
      3. 检查 `.side-column` 布局
    Expected Result: 移动端下两个面板堆叠，高度自适应
    Evidence: .sisyphus/evidence/task-2-mobile-layout.png
  ```

  **Evidence to Capture**:
  - [ ] 截图：桌面端2:3比例布局
  - [ ] 截图：移动端响应式布局

  **Commit**: YES
  - Message: `style(frontend): adjust right sidebar ratio to 2:3`
  - Files: `frontend/style.css`

---

## Final Verification Wave

这是一个小型UI调整，不需要专门的最终验证，QA场景已覆盖需求。

---

## Success Criteria

### Verification Commands
```bash
# 启动服务
cd /Users/felixcxr/code/wanxiao_demo && uv run python main.py

# 打开浏览器验证
# http://localhost:7860
```

### Final Checklist
- [ ] 发送消息后，聊天区域显示三个点加载动画
- [ ] 加载动画在AI响应到达后消失，显示实际内容
- [ ] 思考过程窗口和skills区域比例为2:3
- [ ] 移动端布局正常响应
