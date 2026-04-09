# 工具调用规范（Tool Specification）

## 目标
明确4个核心脚本的调用方式、参数格式、输出解析和错误处理，确保 Agent 能正确执行工具调用并处理返回结果。

---

## 工具概览

| 工具名称 | 脚本路径 | 核心功能 | 优先级 |
|---------|---------|---------|--------|
| 保险产品内容检索 | `scripts/product_content_search.py` | 根据内容类型检索产品列表 | 高 |
| 保险产品属性详情 | `scripts/product_attribute_detail.py` | 查询产品具体属性信息 | 高 |
| 产品工具接口 | `scripts/product_tool_interface.py` | 通过MP_CODE查询责任详情 | 高 |
| 网页搜索 | `scripts/web_search.py` | 补充外部产品信息 | 低（仅内部资料不足时使用）|

---

## 工具 1：保险产品内容检索

### 基本信息
- **脚本路径**：`scripts/product_content_search.py`
- **功能**：根据产品内容检索保险产品，支持按内容类型、状态、类别筛选
- **适用场景**：查找产品列表、了解产品分类、查询产品说明书/险种列表

### 调用方式

```bash
python scripts/product_content_search.py \
  --productContent "产品内容" \
  --contentType "内容类型" \
  --effectiveState "生效/失效" \
  --productCategory "产品目录" \
  --productType "产品类别" \
  --topK 3
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|-----|------|------|------|------|
| `--productContent` | str | 否 | 产品内容关键词 | `"重疾险"` |
| `--contentType` | str | 否 | 内容类型，默认空（全部类型） | `"产品说明书"` |
| `--effectiveState` | str | 否 | 产品状态：生效/失效 | `"生效"` |
| `--productCategory` | str | 否 | 产品目录/知识库目录 | `"健康险"` |
| `--productType` | str | 否 | 产品类别：标准产品/自选产品/不可销售产品 | `"标准产品"` |
| `--productName` | str | 否 | 产品名称，支持模糊搜索 | `"平安福"` |
| `--productCode` | str | 否 | 产品编码，精准匹配 | `"PA0001"` |
| `--topK` | int | 否 | 返回产品个数，默认3 | `5` |

**contentType可选值**：
- `产品基本信息` - 查询产品基本资料
- `产品投保规则` - 查询投保条件、年龄限制等
- `产品说明书` - 查询完整产品条款
- `产品险种列表` - 查询产品包含的险种
- `产品套餐列表` - 查询套餐组合信息
- `渠道授权列表` - 查询销售渠道授权
- `APP授权列表` - 查询APP销售授权
- `机构授权列表` - 查询机构销售授权

### 输出格式

**成功返回示例**：
```json
{
  "products": [
    {
      "productCode": "PA0001",
      "productName": "平安福重疾险",
      "productCategory": "健康险",
      "effectiveState": "生效",
      "contentType": "产品说明书",
      "content": "产品说明书内容摘要..."
    }
  ],
  "total": 1
}
```

### 使用场景示例

**场景1：查询某产品的说明书**
```bash
python scripts/product_content_search.py \
  --productName "平安福" \
  --contentType "产品说明书" \
  --effectiveState "生效"
```

**场景2：浏览某类产品列表**
```bash
python scripts/product_content_search.py \
  --productCategory "健康险" \
  --contentType "产品险种列表" \
  --topK 10
```

---

## 工具 2：保险产品属性详情

### 基本信息
- **脚本路径**：`scripts/product_attribute_detail.py`
- **功能**：根据产品编码或产品名称，返回产品基础信息、投保规则、产品说明书、险种列表等
- **适用场景**：查询特定产品的详细信息、投保条件、费率等

### 调用方式

```bash
python scripts/product_attribute_detail.py \
  --productName "产品名称" \
  --productCode "产品编码" \
  --attributeType "属性类型"
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|-----|------|------|------|------|
| `--productName` | str | 否 | 产品名称，支持模糊搜索 | `"平安福"` |
| `--productCode` | str | 否 | 产品编码，精准匹配，支持单个或多个 | `"PA0001"` |
| `--attributeType` | str | 否 | 属性类型，支持多个用逗号分隔 | `"产品基本信息,产品投保规则"` |

**attributeType可选值**（与contentType相同）：
- `产品基本信息` - 产品名称、编码、类别、状态等
- `产品投保规则` - 投保年龄、健康告知、保额限制等
- `产品说明书` - 完整条款内容
- `产品险种列表` - 包含的险种及责任
- `产品套餐列表` - 套餐组合及价格
- `APP授权列表` - 线上销售渠道授权
- `机构授权列表` - 线下机构销售授权
- `渠道授权列表` - 全渠道授权信息

**注意**：`productName`和`productCode`至少填一个

### 输出格式

**成功返回示例**：
```json
{
  "productCode": "PA0001",
  "productName": "平安福重疾险",
  "attributes": {
    "产品基本信息": {
      "产品类别": "健康险",
      "投保年龄": "18-55周岁",
      "保障期限": "终身",
      "缴费方式": "年缴/趸交"
    },
    "产品投保规则": {
      "最低保额": "10万元",
      "最高保额": "100万元",
      "等待期": "90天",
      "健康告知": "需如实告知"
    }
  }
}
```

### 使用场景示例

**场景1：查询产品投保规则**
```bash
python scripts/product_attribute_detail.py \
  --productName "平安福" \
  --attributeType "产品投保规则"
```

**场景2：同时查询多个属性**
```bash
python scripts/product_attribute_detail.py \
  --productCode "PA0001" \
  --attributeType "产品基本信息,产品投保规则,产品险种列表"
```

---

## 工具 3：产品工具接口

### 基本信息
- **脚本路径**：`scripts/product_tool_interface.py`
- **功能**：通过MP_CODE查询关于责任更详细的信息，支持指定查询字段
- **适用场景**：需要查询产品责任详情、特定字段信息时

### 调用方式

```bash
python scripts/product_tool_interface.py \
  --mktProdCode "产品编码" \
  --requestFields "查询字段"
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|-----|------|------|------|------|
| `--mktProdCode` | str | 是 | 产品编码（MP_CODE） | `"PA0001"` |
| `--requestFields` | str | 否 | 查询的表格和字段，多个用逗号分隔 | `"责任详情,费率表"` |

### 输出格式

**成功返回示例**：
```json
{
  "mktProdCode": "PA0001",
  "productName": "平安福重疾险",
  "responsibilities": [
    {
      "责任代码": "RESP001",
      "责任名称": "重大疾病保险金",
      "责任描述": "被保险人初次发生合同约定的重大疾病...",
      "赔付比例": "100%",
      "等待期": "90天"
    }
  ],
  "fields": {
    "费率表": {...},
    "免责条款": {...}
  }
}
```

### 使用场景示例

**场景：查询产品责任详情**
```bash
python scripts/product_tool_interface.py \
  --mktProdCode "PA0001" \
  --requestFields "责任详情,费率表,免责条款"
```

---

## 工具 4：网页搜索（外部补充）

### 基本信息
- **脚本路径**：`scripts/web_search.py`
- **功能**：执行网络搜索，获取外部产品信息、市场评价、竞品对比等
- **适用场景**：内部资料不足时补充外部信息，或查询竞品信息

### 调用方式

```bash
python scripts/web_search.py --question "搜索问题"
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|-----|------|------|------|------|
| `--question` | str | 是 | 搜索查询词 | `"平安福重疾险 市场评价"` |

### 输出格式

**成功返回示例**：
```json
{
  "web_detail": [
    {
      "title": "网页标题",
      "url": "https://example.com/article",
      "content": "网页内容摘要..."
    }
  ],
  "web_sumn": "搜索结果总结...",
  "sources": ["https://example.com/article"]
}
```

### 使用约束

1. **仅作为补充**：外部搜索仅用于内部资料不足时的补充，不用于通用问答
2. **来源标注**：使用外部信息时必须标注来源URL
3. **可信度评估**：优先采信官方渠道（保险公司官网、监管网站），谨慎使用论坛、自媒体信息

---

## 工具选择决策流程

```
用户问题
    ↓
是否涉及具体产品？
    ├─ 否 → 使用product_content_search浏览产品分类
    ↓
是
    ↓
需要查询什么信息？
    ├─ 产品列表/分类浏览 → product_content_search
    ├─ 产品基本信息/投保规则/险种列表 → product_attribute_detail
    ├─ 责任详情/特定字段 → product_tool_interface
    └─ 外部评价/竞品信息 → web_search（内部资料不足时）
```

---

## 工具调用组合示例

### 示例1：查询产品保障责任

**用户问题**："平安福重疾险保什么？"

**执行流程**：
```bash
# 步骤1：查询产品险种列表
python scripts/product_content_search.py \
  --productName "平安福" \
  --contentType "产品险种列表"

# 步骤2：如有需要，查询详细责任
python scripts/product_tool_interface.py \
  --mktProdCode "PA0001" \
  --requestFields "责任详情"
```

### 示例2：对比两款产品

**用户问题**："平安福和国寿福有什么区别？"

**执行流程**：
```bash
# 步骤1：查询平安福详细信息（并行）
python scripts/product_attribute_detail.py \
  --productName "平安福" \
  --attributeType "产品基本信息,产品险种列表"

# 步骤2：查询国寿福详细信息（并行）
python scripts/product_attribute_detail.py \
  --productName "国寿福" \
  --attributeType "产品基本信息,产品险种列表"

# 步骤3：整合对比（Agent分析）
```

### 示例3：内部资料不足时补充外部信息

**用户问题**："平安福的市场评价如何？"

**执行流程**：
```bash
# 步骤1：先查询内部产品信息
python scripts/product_attribute_detail.py \
  --productName "平安福" \
  --attributeType "产品基本信息"

# 步骤2：补充外部市场评价
python scripts/web_search.py \
  --question "平安福重疾险 市场评价 用户反馈"
```

---

## 错误处理规范

### 常见错误及处理

| 错误类型 | 错误标识 | 处理建议 |
|---------|---------|---------|
| 参数错误 | `[ERROR] 参数异常` | 检查必填参数，修正后重试 |
| 产品不存在 | `未找到相关产品` | 尝试模糊搜索或询问用户确认产品名称 |
| 编码错误 | `[ERROR] 产品编码不存在` | 先通过productName查询productCode |
| 服务超时 | `[ERROR] 服务超时` | 重试1次，仍失败则提示用户稍后重试 |
| 外部搜索失败 | `搜索服务异常` | 重试1次或告知无法获取外部信息 |

### 重试策略

1. **参数错误**：立即修正，不重试
2. **服务超时**：等待2秒后重试1次
3. **空结果**：尝试调整参数（如模糊搜索）后重试
4. **连续失败**：转入error.md处理流程

---

## Gotchas（工具调用陷阱）

1. **混淆contentType和attributeType**
   - 陷阱：两个参数可选值相同，但使用场景不同
   - 正确：contentType用于product_content_search，attributeType用于product_attribute_detail

2. **忽视effectiveState**
   - 陷阱：查询时未指定生效状态，返回已停售产品
   - 正确：查询在售产品时务必指定`--effectiveState "生效"`

3. **productCode和productName混淆**
   - 陷阱：将产品名称当作productCode传入
   - 正确：productCode是编码（如PA0001），productName是名称（如平安福）

4. **web_search过度使用**
   - 陷阱：优先使用web_search而非内部工具
   - 正确：必须先尝试内部工具，外部搜索仅作为补充

5. **未指定产品时的默认行为**
   - 陷阱：用户未指定产品时随机返回结果
   - 正确：未指定产品时默认优先查询平安保险产品
