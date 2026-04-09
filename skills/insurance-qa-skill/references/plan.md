# 计划模块：问题拆分与工具选择

## 目标
将用户复杂问题拆解为可独立执行的子问题序列，确保每个子问题：
- 单一职责（只问一件事）
- 工具明确（知道用哪个工具）
- 可验证（有明确的成功标准）

## 问题拆分策略

### 1.1 需要拆分的情况

当用户问题符合以下特征时，必须进行拆分：

| 特征类型 | 具体表现 | 示例 |
|---------|---------|------|
| 多产品查询 | 包含多个产品名称 | "A产品和B产品哪个好" |
| 多维度询问 | 询问同一产品的多个方面 | "XX重疾险的等待期和保额上限是多少" |
| 对比类问题 | 包含"对比"、"比较"、"vs"等词 | "平安福和国寿福有什么区别" |
| 多子问题 | 用"和"、"以及"、"分别"连接 | "A产品保什么，B产品怎么理赔" |
| 混合信息 | 同时需要内部资料和外部信息 | "XX产品的条款和最新监管政策" |

### 1.2 拆分执行流程

```
接收问题
    ↓
识别问题类型（单产品/多产品/对比/混合）
    ↓
提取关键实体（产品名称、属性、时间等）
    ↓
拆分为独立子问题
    ↓
为每个子问题分配工具
    ↓
确定执行顺序（并行/串行）
    ↓
生成执行计划
```

### 1.3 子问题定义规范

每个子问题必须包含以下要素：

```yaml
sub_problem:
  id: "SP001"                    # 子问题编号
  type: "product_query"          # 问题类型：product_query/attribute_query/tool_query/web_query
  question: "查询XX产品的等待期"  # 具体问题描述
  tool: "product_attribute_detail" # 推荐工具
  parameters:                    # 工具参数
    productName: "XX重疾险"
    attributeType: "产品投保规则"
  dependencies: []               # 依赖的其他子问题ID
  parallelizable: true           # 是否可并行执行
```

### 1.4 问题类型识别矩阵

| 问题关键词 | 问题类型 | 推荐工具 | 参数要点 |
|-----------|---------|---------|---------|
| "保什么"、"保障"、"责任" | 内容检索 | product_content_search | contentType=产品险种列表 |
| "条款"、"说明书" | 内容检索 | product_content_search | contentType=产品说明书 |
| "投保规则"、"年龄"、"健康告知" | 属性查询 | product_attribute_detail | attributeType=产品投保规则 |
| "费率"、"多少钱"、"保费" | 属性查询 | product_attribute_detail | attributeType=产品基本信息 |
| "责任详情"、"具体责任" | 工具接口 | product_tool_interface | mktProdCode + requestFields |
| "竞品"、"对比"、"市场" | 外部搜索 | web_search | --question |

## 工具选择决策树

```
用户问题
    ↓
是否涉及具体产品？
    ├─ 否 → 是否需要分类浏览？
    │          ├─ 是 → product_content_search (contentType=产品险种列表)
    │          └─ 否 → uncertain.md (反问模块)
    ↓
是
    ↓
是否知道产品编码？
    ├─ 是 → product_tool_interface (查责任详情)
    └─ 否 → 需要查询什么信息？
               ├─ 产品基本信息 → product_attribute_detail (attributeType=产品基本信息)
               ├─ 投保规则 → product_attribute_detail (attributeType=产品投保规则)
               ├─ 产品说明书 → product_content_search (contentType=产品说明书)
               ├─ 险种列表 → product_content_search (contentType=产品险种列表)
               └─ 责任详情 → 先product_attribute_detail获取productCode，再product_tool_interface
```

## 特殊场景处理

### 3.1 对比类问题拆分

**场景**：用户询问"A产品和B产品哪个更好"

**拆分方案**：

```yaml
sub_problems:
  - id: "SP001"
    type: "product_query"
    question: "查询A产品的基本信息和保障责任"
    tool: "product_attribute_detail"
    parameters:
      productName: "A产品"
      attributeType: "产品基本信息,产品险种列表"
  
  - id: "SP002"
    type: "product_query"
    question: "查询B产品的基本信息和保障责任"
    tool: "product_attribute_detail"
    parameters:
      productName: "B产品"
      attributeType: "产品基本信息,产品险种列表"
  
  - id: "SP003"
    type: "comparison"
    question: "基于SP001和SP002的结果进行对比分析"
    tool: "analysis"
    dependencies: ["SP001", "SP002"]
```

**执行顺序**：SP001和SP002并行执行 → SP003串行执行

### 3.2 混合信息问题拆分

**场景**：用户询问"XX重疾险的最新条款和当前市场评价"

**拆分方案**：

```yaml
sub_problems:
  - id: "SP001"
    type: "product_query"
    question: "查询XX重疾险的产品说明书"
    tool: "product_content_search"
    parameters:
      productName: "XX重疾险"
      contentType: "产品说明书"
    parallelizable: true
  
  - id: "SP002"
    type: "web_query"
    question: "搜索XX重疾险的市场评价和口碑"
    tool: "web_search"
    parameters:
      question: "XX重疾险 市场评价 口碑 测评"
    parallelizable: true
  
  - id: "SP003"
    type: "synthesis"
    question: "整合内部条款和外部评价"
    tool: "analysis"
    dependencies: ["SP001", "SP002"]
```

**执行顺序**：SP001和SP002并行执行 → SP003串行执行

### 3.3 条件依赖问题

**场景**：需要先查询A产品信息，再根据结果查询B产品

**处理原则**：
- 明确标识依赖关系
- 串行执行依赖链
- 前置问题失败时，终止后续执行

```yaml
sub_problems:
  - id: "SP001"
    type: "product_query"
    question: "查询A产品的升级版本"
    tool: "product_attribute_detail"
  
  - id: "SP002"
    type: "product_query"
    question: "查询A产品升级版的详细责任"
    tool: "product_tool_interface"
    dependencies: ["SP001"]  # 依赖SP001的结果
```

## 执行计划生成模板

```yaml
plan:
  version: "1.0"
  original_question: "用户原始问题"
  analysis:
    intent: "用户意图"
    entities:
      - type: "product"
        value: "产品名称"
      - type: "attribute"
        value: "属性类型"
  sub_problems:
    - id: "SP001"
      type: "..."
      question: "..."
      tool: "..."
      parameters: {...}
      dependencies: []
      parallelizable: true/false
  execution_order:
    - phase: 1
      tasks: ["SP001", "SP002"]
      mode: "parallel"
    - phase: 2
      tasks: ["SP003"]
      mode: "sequential"
  fallback_strategy:
    - condition: "工具返回空结果"
      action: "调整参数重试"
    - condition: "信息不足"
      action: "调用web_search补充"
```

## 常见错误避免

### 5.1 过度拆分

**错误示例**：将"XX产品的等待期和免赔额是多少"拆分为两个子问题

**正确处理**：这是同一产品的不同属性，可以一次查询product_attribute_detail的多个attributeType

### 5.2 遗漏依赖

**错误示例**：对比两个产品时，未识别需要分别查询两个产品信息

**正确处理**：对比类问题必须拆分为至少两个独立的产品查询子问题

### 5.3 工具选择错误

**错误示例**：查询责任详情时直接使用product_attribute_detail

**正确处理**：责任详情需要通过product_tool_interface查询，需要mktProdCode

### 5.4 参数遗漏

**错误示例**：查询产品内容时未指定contentType

**正确处理**：必须根据问题类型选择合适的contentType，否则可能返回不相关信息
