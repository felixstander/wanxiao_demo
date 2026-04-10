# 工具调用规范（Tool Specification）

## 目标
明确4个核心脚本的调用方式、参数格式、输出解析和错误处理，确保 Agent 能正确执行工具调用并处理返回结果。

---

## 工具概览

| 工具名称 | 脚本路径 | 核心功能 | 优先级 |
|---------|---------|---------|--------|
| 保险产品内容检索 | `scripts/product_content_search.py` | 根据内容类型检索产品列表 | 高 |
| 保险产品属性详情 | `scripts/product_attribute_detail.py` | 查询产品具体属性信息 | 高 |
| 网页搜索 | `scripts/web_search.py` | 补充外部产品信息 | 低（仅内部资料不足时使用）|

---

## 工具 1：保险产品内容检索

### 基本信息
- **脚本路径**：`scripts/product_content_search.py`
- **功能**：根据产品内容检索保险产品，支持按内容类型、状态、类别筛选
- **适用场景**：
  - 用户询问某类产品（意外险、医疗险、财产险可以保什么责任）
  - 根据疾病关键词查找可保产品（肺结节可以有什么保险能保）
  - 根据职业类型查找可保产品（电焊工、运动员有什么保险能保）

### 调用方式

```bash
python scripts/product_content_search.py \
  --productContent "搜索关键词" \
  --contentType "内容类型1" "内容类型2" \
  --topK 10
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|-----|------|------|------|------|
| `--productContent` | str | **是** | 从客户问题中提取的搜索关键词 | `"意外险"`、`"肺结节"`、`"电焊工"` |
| `--contentType` | list | 否 | 内容类型，默认为空（全部类型），支持多个 | `"产品说明书" "产品险种列表"` |
| `--productCategory` | str | 否 | 产品目录/知识库目录 | `"健康险"` |
| `--topK` | int | 否 | 返回产品个数，默认10 | `10` |

**productContent 提取指南**：
- 产品大类关键词：`意外险`、`医疗险`、`财产险`、`重疾险`、`寿险` 等
- 疾病关键词：`肺结节`、`糖尿病`、`高血压`、`癌症` 等
- 职业关键词：`电焊工`、`运动员`、`高空作业`、`矿工` 等
- 通用需求词：`住院`、`门诊`、`报销`、`津贴` 等

**contentType可选值**：
- `产品基本信息` - 查询产品基本资料
- `产品投保规则` - 查询投保条件、年龄限制等
- `产品说明书` - 查询完整产品条款
- `产品险种列表` - 查询产品包含的险种
- `产品套餐列表` - 查询套餐组合信息

### 输出格式

**成功返回示例**：
```json
[
  {
    "productCode": "MP18021166",
    "productName": "平安肺常爱肺结节专病恶性肿瘤保险(福利版)",
    "productContent": [
      {
        "recallSimilarity": 20.016516,
        "recallType": "productContentText",
        "contentId": "1821437331530481695",
        "rankScore": 2.84375,
        "label": "平安肺常爱肺结节专病恶性肿瘤保险(福利版)的产品险种责任列表",
        "knowledgeType": "产品险种列表",
        "content": "平安肺常爱肺结节专病恶性肿瘤保险(福利版)的险种包括\\n1.PL180J070平安法定传染病身故保险：它是主险，它的责任有传染病身故\\n2.PL180J684平安..."
      },
      {
        "recallSimilarity": 32.4864,
        "recallType": "productContentText",
        "contentId": "1821437331173965910",
        "rankScore": 0.45166015625,
        "label": "平安肺常爱肺结节专病恶性肿瘤保险(福利版)的基本信息",
        "knowledgeType": "产品基本信息",
        "content": "平安肺常爱肺结节专病恶性肿瘤保险(福利版)的市场产品编码是MP18021166，平安肺常爱肺结节专病恶性肿瘤保险(福利版)的产品版本是1.03..."
      }
    ],
    "productInfo": {
      "effectiveState": "生效",
      "productType": "标准产品",
      "productCategory": "健康险"
    }
  }
]
```

**输出字段说明**：
- `productCode`: 产品编码
- `productName`: 产品名称
- `productContent`: 产品相关内容数组（按相关度排序）
  - `recallSimilarity`: 召回相似度分数
  - `recallType`: 召回类型
  - `contentId`: 内容唯一标识
  - `rankScore`: 排序分数
  - `label`: 内容标签/标题
  - `knowledgeType`: 知识类型（如产品险种列表、产品基本信息等）
  - `content`: 具体内容文本
- `productInfo`: 产品基本信息
  - `effectiveState`: 生效状态（生效/失效）
  - `productType`: 产品类型
  - `productCategory`: 产品目录分类

### 使用场景示例

**场景1：用户问肺结节可以保什么保险**
```bash
python scripts/product_content_search.py \
  --productContent "肺结节" \
  --contentType "产品险种列表" \
  --effectiveState "生效" \
  --topK 10
```

**场景2：用户问意外险保什么责任**
```bash
python scripts/product_content_search.py \
  --productContent "意外险" \
  --contentType "产品说明书" "产品险种列表" \
  --effectiveState "生效" \
  --topK 10
```

**场景3：查询电焊工可以投保的产品**
```bash
python scripts/product_content_search.py \
  --productContent "电焊工" \
  --contentType "产品投保规则" \
  --effectiveState "生效" \
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
  --attributeType "属性类型1" "属性类型2"
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|-----|------|------|------|------|
| `--productName` | str | 否 | 产品名称，支持模糊搜索 | `"平安福"` |
| `--productCode` | str | 否 | 产品编码，精准匹配 | `"PA0001"` |
| `--attributeType` | list | 否 | 属性类型，支持多个值 | `"产品基本信息" "产品投保规则"` |

**attributeType可选值**（与contentType相同）：
- `产品基本信息` - 产品名称、编码、类别、状态等
- `产品投保规则` - 投保年龄、健康告知、保额限制等
- `产品说明书` - 完整条款内容
- `产品险种列表` - 包含的险种及责任
- `产品套餐列表` - 套餐组合及价格

**注意**：`productName`和`productCode`至少填一个

### 输出格式

**成功返回示例**：
```json
{
  "prodBchrPO": {
    "cpttProdCmp": null,
    "ivldTm": null,
    "prodSpcl": "风险多保障，施工再无忧",
    "clmServ": null,
    "effTm": "2024-12-26 08:50:39",
    "updtBy": "HUANGFAN493",
    "updtTm": "2025-11-19 09:58:51",
    "servProd": null,
    "insrPrt": "施工过程中的财损、三者人伤及施工人员意外",
    "tgtCust": "适用客户：地方施工企业、小型工程公司、城投公司、地方投资公司、个人业主",
    "idProdInfo": "DDAPDF2F25E6259E8BE0536003581E6926",
    "crtBy": "ZHANGKE701",
    "feeRateRng": null,
    "crtTm": "2024-12-26 08:50:39",
    "scrtScp": "施工物损、三者、意外人伤都可保",
    "stdTgtCust": "",
    "idProdInstr": "2A0EBBB9D7F760AFE0636003581E9BFE"
  },
  "mktProductAuthDeptList": [
    "江苏分公司",
    "青岛分公司",
    "厦门分公司",
    "四川分公司",
    "青海分公司",
    "宁夏分公司",
    "宁波分公司",
    "西藏分公司",
    "佛山分公司",
    "温州分公司"
  ],
  "mktProdApplyRulePO": {
    "jntInsrMaxNum": null,
    "endSalePerd": null,
    "shrtEffTm": "1",
    "nameAply": "否",
    "maxNum": "1",
    "suitCust": null,
    "minInsrAge": null,
    "crtTm": "2025-11-19 09:58:50"
  }
}
```

**输出字段说明**：
- `prodBchrPO`: 产品基本信息对象
  - `prodSpcl`: 产品特色描述
  - `effTm`: 生效时间
  - `insrPrt`: 投保须知/说明
  - `tgtCust`: 目标客户群体
  - `scrtScp`: 保障范围描述
  - `crtBy`: 创建人
  - `crtTm`: 创建时间
  - `updtBy`: 更新人
  - `updtTm`: 更新时间
- `mktProductAuthDeptList`: 授权销售的分公司列表（数组）
- `mktProdApplyRulePO`: 产品投保规则对象
  - `shrtEffTm`: 短期生效时间（天数）
  - `nameAply`: 是否记名投保
  - `maxNum`: 最大投保份数
  - `minInsrAge`: 最小投保年龄
  - `jntInsrMaxNum`: 联合投保最大人数
  - `endSalePerd`: 销售截止日期
  - `crtTm`: 规则创建时间

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
  --attributeType "产品基本信息" "产品投保规则" "产品险种列表"
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
  "Modelmetrics": {...},
  "web_detail": [
    {
      "summary": "中国海油1月2日宣布，我国海上最大气田'深海一号'近期完成投产以来的第100船原油外输工作，2025年气田油气总产量突破450万吨油当量...",
      "date": "2026-04-10 00:00:00",
      "title": "时事一点通",
      "url": "https://m.ssydt.com/",
      "content": "时事日报 更多\n2026年4月10日时政考点\n全军高级干部培训班4月8日上午在国防大学开班\n...",
      "timestamp": 1775750400,
      "status": 200
    },
    {
      "summary": "...",
      "date": "2026-04-09 00:00:00",
      "title": "另一篇文章标题",
      "url": "https://example.com/article2",
      "content": "...",
      "timestamp": 1775664000,
      "status": 200
    }
  ],
  "answer": "基于搜索结果的总结：中国海油'深海一号'气田近期完成第100船原油外输工作，2025年产量突破450万吨油当量..."
}
```

**输出字段说明**：
- `Modelmetrics`: 模型性能指标对象
- `web_detail`: 网页搜索结果数组（按相关度排序）
  - `summary`: 网页内容摘要（AI生成的总结）
  - `date`: 文章发布日期
  - `title`: 网页标题
  - `url`: 网页链接地址
  - `content`: 网页原始内容（或正文提取）
  - `timestamp`: 时间戳（Unix时间戳格式）
  - `status`: HTTP状态码（200表示正常）
- `answer`: 基于所有搜索结果的综合性总结回答

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
# 步骤1：查询产品险种列表（使用产品名称作为关键词）
python scripts/product_content_search.py \
  --productContent "平安福" \
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
  --attributeType "产品基本信息" "产品险种列表"

# 步骤2：查询国寿福详细信息（并行）
python scripts/product_attribute_detail.py \
  --productName "国寿福" \
  --attributeType "产品基本信息" "产品险种列表"

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

6. **多值参数格式错误**
   - 陷阱：使用逗号分隔多个contentType或attributeType（如`"类型1,类型2"`）
   - 正确：使用空格分隔多个值（如`"类型1" "类型2"`），因为脚本使用`nargs="*"`接收参数
