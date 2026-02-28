# 修复：Agents 重复初始化问题

## 问题诊断

**根本原因**：`init_agents()` 在代码中被调用了 **3 次**：

1. **`main()` 函数**（第 1499 行）- 用户运行 `python main.py` 时执行
2. **`create_app()` 函数**（第 1395 行）- Uvicorn 导入 `main:app` 时执行  
3. **`create_app()` 函数**（第 1395 行）- Worker 进程导入时再次执行

从日志可以清楚看到三次初始化：
- "所有 Agents 预加载完成！(7.8s)" - main() 触发
- "所有 Agents 预加载完成！(8.0s)" - create_app() 第一次触发
- "所有 Agents 预加载完成！(6.9s)" - create_app() 第二次触发

## 修复方案

### 步骤 1：注释掉 create_app() 中的 init_agents() 调用

**文件**：`main.py`
**行号**：1395

**当前代码**：
```python
    # 注意：只在 main() 中调用 init_agents()，避免模块导入时重复初始化
    # init_agents()  # 已移至 main() 函数中统一调用
    init_agents()  # ← 注释掉这一行
```

**修复后**：
```python
    # 注意：只在 main() 中调用 init_agents()，避免模块导入时重复初始化
    # init_agents()  # 已移至 main() 中统一调用，避免重复初始化
```

### 步骤 2：清理残留锁文件（启动前执行）

```bash
rm -f /Users/felixcxr/code/wanxiao_demo/.agents_init.lock
```

### 步骤 3：重新启动服务

```bash
uv run python main.py
```

## 预期结果

- 应该只看到 **1 次** "所有 Agents 预加载完成！" 输出
- Uvicorn Worker 进程不会重复初始化
- 前端请求可以正常使用 Agents

## 如果仍有问题

如果 Worker 进程中 `AGENT` 为 `None`，需要实现**懒加载机制**：

1. 在 `create_app()` 中添加 `_ensure_agents_initialized()` 调用
2. 实现 `_ensure_agents_initialized()` 函数，使用文件锁确保只有一个进程初始化
3. 其他进程等待初始化完成后共享结果

---

**执行命令**：

```bash
# 1. 先停止当前服务
# 2. 清理锁文件
rm -f /Users/felixcxr/code/wanxiao_demo/.agents_init.lock

# 3. 注释掉 main.py 第 1395 行的 init_agents()
# 手动编辑或使用 sed:
sed -i '' 's/^    init_agents()$/    # init_agents()  # 已移至 main() 中统一调用，避免重复初始化/' main.py

# 4. 重新启动
uv run python main.py
```
