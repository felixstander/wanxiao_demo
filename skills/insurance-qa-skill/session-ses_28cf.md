# 平安保险产品问答Skill架构设计

**Session ID:** ses_28cfcff25ffepRX4dPSJD9Syf4
**Created:** 4/10/2026, 12:11:09 AM
**Updated:** 4/10/2026, 12:53:47 AM

---

## User

[search-mode]
MAXIMIZE SEARCH EFFORT. Launch multiple background agents IN PARALLEL:
- explore agents (codebase patterns, file structures, ast-grep)
- librarian agents (remote repos, official docs, GitHub examples)
Plus direct tools: Grep, ripgrep (rg), ast-grep (sg)
NEVER stop at first result - be exhaustive.

[analyze-mode]
ANALYSIS MODE. Gather context before diving deep:
CONTEXT GATHERING (parallel):
- 1-2 explore agents (codebase patterns, implementations)
- 1-2 librarian agents (if external library involved)
- Direct tools: Grep, AST-grep, LSP for targeted searches

IF COMPLEX - DO NOT STRUGGLE ALONE. Consult specialists:
- **Oracle**: Conventional problems (architecture, debugging, complex logic)
- **Artistry**: Non-conventional problems (different approach needed)

SYNTHESIZE findings before proceeding.
---
MANDATORY delegate_task params: ALWAYS include load_skills=[] and run_in_background when calling delegate_task.
Example: delegate_task(subagent_type="explore", prompt="...", run_in_background=true, load_skills=[])

---

我是中国平安的员工，我现在正在设计一个 Skill技能包，这个技能包需要覆盖用户的所有保险产品问答相关的能力（比如知识答疑、销售话术生成、内外部产品对比等）。我现在只有四个工具，3 个内部保险产品问答工具，一个网页搜索工具，理论上这四个工具就应该能覆盖所有的问答。我现在需要对这个 Skill设计一套机制，该 skill可以帮助用户得到满意的答案。这个主 Skill.md应该包括触发条件，任务目标，硬规则（比如判断用户问题是否需要拆分多个子问题等），然后接下来，都有每个模块的子 Skill去做接下来的事情，1、计划模块：确定问题如何拆分多个子问题进行不同工具的调用（@references/plan.md) ，2、工具调用模块：我现在有 4个 python脚本，其中三个脚本的作用和入参，如图片中所示[Image 1] ，另外一个脚本叫做web_search.py，入参是--question "用户问题"(@references/tool.md),3、报错/冲突模块：工具报错/ 信息有冲突之后，如何调整工具/处理冲突(@references/error.md),4、反问模块：当用户问题主体不明确时（比如说问题里没有提及保险产品大类（，只说了帮我查下保险可以保什么）（@refences/uncertain.md),5、输出规范模块：当内容涉及多款到保险产品时，需要以表格形式输出；当回答用户问题时（比如说 xxx产品可以保肺结核吗），输出应该先简明扼要回答用户问题，再详细展开），但涉及外部网页搜索信息时，需要以 markdown格式对生成内容加上网址引用（@assets/format.md)。现在请你从主 Skill.md和多个不同子 Skill.md需要做的事情这个角度出发，去帮我书写每个模块可以如何去做的详细内容。我这里有篇文章，你可以进行参考https://mp.weixin.qq.com/s/c42XqFaEeNEhh6DtQgajFw。该 skill请创建在@skills/ 目录下

---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 95.9s)

_Thinking:_

 用户是中国平安的员工，需要设计一个保险产品问答相关的Skill技能包。让我先分析用户的需求：

1. **目标**：创建一个保险产品问答Skill，覆盖知识答疑、销售话术生成、内外部产品对比等能力
2. **工具**：4个工具 - 3个内部保险产品问答工具 + 1个网页搜索工具
3. **模块结构**：
   - 主Skill.md：触发条件、任务目标、硬规则
   - 子Skill模块：
     1. plan.md：问题拆分、工具调用计划
     2. tool.md：工具调用（3个内部脚本 + web_search.py）
     3. error.md：报错/冲突处理
     4. uncertain.md：反问模块（问题不明确时）
     5. format.md：输出规范

4. **特殊要求**：
   - 参考文章：https://mp.weixin.qq.com/s/c42XqFaEeNEhh6DtQgajFw
   - 创建在skills/目录下

从图片中我能看到三个内部工具的详细信息：
1. 保险产品内容检索
2. 保险产品属性详情
3. 产品工具接口

以及TODO部分：
1. 外部网页搜索工具作为产品问答的补充，不用于通用问答的回答
2. 去除调内部资料/网络信息标识的输出，用引用的方式标识外部信息
3. 未指定产品的时候，默认先走平安产品


4. 去除脚本调用的思考过程生成

我将制定一个全面的实施计划。需要深入分析现有技能目录结构，仔细研究参考文章，确保技能包设计符合公司具体要求。设计过程将注重模块化和灵活性，确保能够覆盖各种保险产品问答场景。

 我来帮您设计这个保险产品问答Skill技能包。首先让我创建任务列表并开始分析参考文章和现有技能结构。

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "分析参考文章和现有技能目录结构",
      "priority": "high",
      "status": "in_progress"
    },
    {
      "content": "设计主Skill.md（触发条件、任务目标、硬规则）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - plan.md（问题拆分与工具调用计划）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - tool.md（工具调用执行）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - error.md（报错与冲突处理）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - uncertain.md（反问模块）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - format.md（输出规范）",
      "priority": "high",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "分析参考文章和现有技能目录结构",
    "priority": "high",
    "status": "in_progress"
  },
  {
    "content": "设计主Skill.md（触发条件、任务目标、硬规则）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - plan.md（问题拆分与工具调用计划）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - tool.md（工具调用执行）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - error.md（报错与冲突处理）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - uncertain.md（反问模块）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - format.md（输出规范）",
    "priority": "high",
    "status": "pending"
  }
]
```



**Tool: webfetch**

**Input:**
```json
{
  "url": "https://mp.weixin.qq.com/s/c42XqFaEeNEhh6DtQgajFw",
  "format": "markdown"
}
```

**Output:**
```
                                                                                                                                                                                      

   

![cover_image](https://mmbiz.qpic.cn/mmbiz_jpg/Fnx2G2wYdEIsBXQUWhB95JhHBnVkrQjibnUasdBf3DbicVWWfxaMCwkPkk6UHkCiaPlOYBFCJHIpMedDhOYYWYHqUBniaxbM58IFtXOvCVLJnicY/0?wx_fmt=jpeg)

# Anthropic 如何使用 Skills：团队经验如何才能被 Agent 稳定复用

Original 若飞 若飞 [架构师](javascript:void\(0\);)

在小说阅读器中沉浸阅读

架构师（JiaGouX）

我们都是架构师！  
架构未来，你来不来？

  

  

#   

---

这两天，Anthropic 工程师 Thariq Shihipar 又发了一篇长文，分享了他们内部做 Skills 的实战经验。熟悉这个名字的读者应该还记得，他之前写的《[Seeing like an Agent](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408480&idx=1&sn=5821c745dd33c781530ab273ab44cdce&scene=21#wechat_redirect)》和《[Prompt Caching Is Everything](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408819&idx=1&sn=f0c65045a197c9a3a6ca5b19faeae4da&scene=21#wechat_redirect)》我们都做过梳理——这次是他"Lessons from Building Claude Code"系列的第三篇。

我把原文和周边讨论都过了一遍，最后留下来的感受其实很简单：

Anthropic 这篇文章值得读，不是因为里面提到了“内部已经有几百个 Skill”，也不只是因为它列出了 9 种 Skill 类型。更有意思的是，它把很多团队已经在摸索、但还没有完全说透的一件事讲明白了。

**Skill 当然可以写成一段提示词，但它更像一个给 Agent 用的工作单元。**

它可以有说明文档，也可以有脚本、模板、数据、hooks 和历史记录。模型不是只来“读一段字”，而是在进入一个提前整理过的小工作区，知道该看什么、该调什么、哪些地方最容易出错。

我觉得这正是 Anthropic 这篇文章和很多“Skill 教程”不太一样的地方。

它没有把重点放在“提示词该怎么写得更花”，而是放在一个更工程化的问题上：**团队经验到底怎样才能被 Agent 稳定复用。**

如果你之前读过我们写的《[Claude Code 最佳实践](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408788&idx=1&sn=ffed2fec07f79e5a64029a02fff0f600&scene=21#wechat_redirect)》，可能还记得里面提到 Skills 是控制面六层架构中的“工作流层”。当时那个判断更多是我们根据网络上的资料梳理。而 Thariq 这个系列刚好在一步步印证这件事：第一篇讲工具怎么设计（动作空间），第二篇讲缓存怎么决定架构取舍（上下文税），这次第三篇终于讲到 Skills 本身——团队经验到底怎么沉淀成 Agent 能稳定复用的工作单元。

下面这篇，不是逐段翻译，也不是简单转述。我把原文中真正有信息增量的部分拎出来，重新梳理了一遍，再放回工程团队日常会遇到的语境里做了批注。

---

## 太长不看版（6 条）

-   • Skill 可以从一段说明开始，但真正拉开差距的，往往是脚本、参考资料、hooks 和日志这些外围结构。
    
-   • Anthropic 给出的 9 类 Skill，更像一张团队能力清单，适合拿来盘点缺口。
    
-   • 如果只记住一个点，我会记 Gotchas。很多 Skill 最有用的部分，恰好是那些踩过坑以后补进去的经验。
    
-   • 把文件系统当成上下文的一部分，比把所有信息都塞进主文件里更稳。
    
-   • 验证类 Skill 的价值通常被低估。生成只是第一步，能不能验对，才决定它能不能进真实流程。
    
-   • 团队分发 Skill 这件事，通常是先在仓库里跑通，再慢慢长成市场，而不是反过来。
    

---

## Skill 为什么不只是提示词

很多人第一次接触 Skill，都会先把它理解成一段专用提示词。这种理解不算错，只是有点窄。

文章里反复强调的一点是，**Skill 是文件夹，不是单个 Markdown 文件。**

这句话看起来像是在讲形态，实际讲的是能力边界。因为一旦 Skill 是文件夹，它能承载的东西就完全不一样了。除了说明文档，它还可以放：

-   • 参考资料，例如 API 用法、约定、模板、例子
    
-   • 可执行脚本，把确定性的事情交给程序处理
    
-   • 配置和状态，让 Skill 在多次运行之间保留连续性
    
-   • hooks，在特定场景里临时加上一层行为约束
    

这样一来，Skill 解决的问题就不只是“告诉模型怎么做”，还包括“把模型带到一个更适合做事的环境里”。

这个差别看着有点抽象，落到实际其实很具体。

如果你把 Skill 当提示词写，重点通常会落在措辞、结构、覆盖面，最后得到的是一份说明书。说明书当然有用，但它很容易越写越长，也很容易把真正关键的东西埋进去。

如果你把 Skill 当工作单元来做，思路就会变成另一套：入口文件只放触发条件和关键规则，细节拆到 `references/`，脚本拆到 `scripts/`，模板放到 `assets/`，需要保留的状态写进日志或配置里。

到这里，Skill 的味道就已经不太像“提示词工程”了，更接近一种轻量的上下文工程。

图 1：一个更像“工作单元”的 Skill，大致会怎么组织

---

## 9 类 Skill，更像一张能力地图

Anthropic 把内部活跃使用的 Skills 大致归成了 9 类。这部分我觉得很有用，因为它回答的不是“Skill 能做什么”，而是“团队一般会把哪些东西沉淀成 Skill”。

简单归一下，大概包括这几类：

类别

更像什么

解决的问题

库与 API 参考

面向 Agent 的内部文档

某个库、CLI、SDK 怎么用才不出错

产品验证

自动化验收脚本

代码写完以后，怎么确认真的跑通

数据获取与分析

带路线图的数据助手

指标去哪查、怎么 join、看哪块仪表盘

流程自动化

团队版快捷命令

站会、周报、建单、同步这些重复动作

脚手架与模板

规范化生成器

新建 migration、workflow、服务骨架

代码质量与评审

组织经验的执行层

代码风格、测试要求、评审视角

拉取、推送与部署

发布流程封装

PR 跟踪、部署、回滚、cherry-pick

排障与调查

值班手册的可执行版本

告警来了之后从哪查起、怎么串工具

运维与例行维护

带护栏的操作流程

清理资源、排查成本、做依赖治理

这个分类本身没有神秘感，但很适合做盘点。

很多团队一说要做 Skill，第一反应是“要不要先做一个很强的大 Skill”。读完这篇文章，我反而会更自然地先问三个问题：

1.  1\. 团队里哪些高频动作已经重复得足够多？
    
2.  2\. 哪些地方模型明明快做对了，但总差最后那一下？
    
3.  3\. 哪些知识现在还掌握在少数人手里，别人不太容易复用？
    

顺着这三个问题往下走，优先级通常就比较清楚了。

如果团队刚开始做，我自己会先看三类：内部库参考、验证、流程自动化。它们的边界清楚，收益也最容易被看见。

---

## 很多 Skill 最有用的地方，恰好是坑点

整篇文章里我印象最深的一句是：**Skill 里信息密度最高的，通常是 Gotchas。**

这句话很像经验之谈。

很多人写 Skill，会先花力气把背景讲完整、概念讲清楚、结构铺漂亮。结果文档是完整了，模型真正容易犯错的地方却没有被单独拎出来。

而 Gotchas 刚好相反。它不追求全面，只盯着那些反复出问题的点。

比如：

-   • 某个 CLI 子命令表面很像，实际参数语义不一样
    
-   • 某个迁移脚本在生产前必须先做只读检查
    
-   • 某个验证流程不能只看页面提示，要连后端状态一起核对
    
-   • 某个 UI 组件在特定布局下会退化，模型很容易照着默认写法踩进去
    

这些内容写在普通文档里，常常只是边角信息。但放到 Skill 里，它们反而应该占最显眼的位置。

因为 Skill 不是百科条目，它更像一份“少走弯路”的压缩包。

我自己读到这里时，脑子里冒出来的不是“怎样写出一个完整 Skill”，而是另外一个更实际的问题：**团队最近三个月，模型反复撞到的坑，到底有没有地方认真记下来。**

如果答案是没有，那 Skill 往往还只做了一半。

Gotchas 的价值也在这里。它不是为了让文档更完整，而是把失败经验变成下一次的默认保护。

从这个角度看，Skill 很像代码库里的测试。很多时候，真正让它变得可靠的，并不是第一版写得多好，而是后来每撞一次墙，就补上一条边界。

---

## 文件怎么组织，会直接影响 Skill 好不好用

文章里还有一个特别值得留意的点：Skill 既然是文件夹，那文件系统本身就是上下文设计的一部分。

这听起来像一句偏理论的话，但实际特别落地。

很多 Skill 的主文件都写得太满。背景、规范、API、示例、FAQ，全都堆在一起。模型不是不能读，只是进入成本会越来越高，真正关键的东西反而不容易被看见。

更顺手的组织方式，通常是这种结构：

-   • `SKILL.md` 只保留触发条件、任务目标、硬规则
    
-   • `references/` 放详细说明和案例
    
-   • `scripts/` 放脚本、辅助函数、检查程序
    
-   • `assets/` 放模板和固定格式
    
-   • `examples/` 放好结果的样子，让模型有参照
    

这样做有个很直接的好处：入口会比较轻。

模型先知道“什么时候该用我、核心规则是什么”，需要细节再下钻；执行时如果有脚本可用，也不用每次都从头组织一遍。

这就是文中说的“渐进式披露”。不是把所有信息一股脑塞进去，而是把信息按用途分层，等真正需要时再读。

放到工程语境里，这其实很好理解。主链路应该轻，复杂信息往下沉。Skill 的组织方式也是一样。

这个思路在 OpenClaw 的 Skills 机制里也能看到类似的设计。系统提示词只注入一份紧凑的 Skills 列表（名称 + 描述 + 位置），Skill 的完整指令默认不加载，模型只在需要时才去读取 `SKILL.md`。这正是渐进式披露在系统层面的体现：列表是索引，文件夹是仓库，模型按需下钻。

---

## Hooks、日志和验证，把 Skill 从好用拉到可靠

前面聊的都是“Skill 怎么写得更清楚”，接下来要聊的，其实是更关键的问题：“Skill 怎样才能更稳”。

这里有三样东西特别值得留意。

第一是 hooks。

文中提到一种按需激活的 hooks，只在某个 Skill 被调用时才生效，会话结束就关掉。这个设计很实用——很多约束你并不想一直开着，但到了特定场景又非常有价值。

比如动生产环境时，拦住危险命令；比如只允许模型修改某个目录，避免调试时顺手动了别的地方。

第二是日志和状态。

举个例子，standup-post 这类 Skill 可以把以前发过的内容存起来，下次运行时直接比较变化，只输出增量。听起来简单，但意义不小——它让 Skill 不再只是一次性任务，而是开始带上连续性。

第三是验证。

这部分读完印象很深。文中甚至建议，验证类 Skill 值得让工程师专门花一周时间打磨。仔细想想确实合理。生成本身越来越便宜，真正稀缺的，反而是确认结果是否正确、过程是否可信。

所以很多时候，验证 Skill 才是那个让 Agent 真正能进入日常工作流的分水岭。

没有验证，Agent 更像一个写得很快的助手。

验证补上以后，它才开始接近一个能交付结果的系统。

我们之前在《[Claude Code 最佳实践](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408788&idx=1&sn=ffed2fec07f79e5a64029a02fff0f600&scene=21#wechat_redirect)》里也聊过类似的判断：**生成越来越便宜，验证才是真正的分水岭。** 当 AI 开始吞掉实现环节，人的价值自然会往验证、观测、约束、回滚这条线上走。验证类 Skill 正是这条线上的一个关键节点。

---

## 团队里怎么分发和治理，也值得一起看

分发和治理这部分，没有前面那么“新”，但很有现实感。

Anthropic 的做法并不激进：小团队、少仓库时，Skill 直接放进仓库里就够用；规模上来以后，再考虑搭建插件市场做更正式的分发。

这个节奏挺合理的。

因为 Skill 的问题往往不是“发不出去”，而是“发出去以后是不是有很多重复、低质量、没人维护的东西”。如果这些基础问题还没解决，市场只会把混乱放大。

还有一个容易被忽略的提醒：仓库里的每个 Skill，都会给模型的上下文增加一点负担。

这句话挺值得记一下。它意味着 Skill 也不是越多越好。团队真正需要的，其实是一套筛选机制，知道哪些 Skill 在被反复使用，哪些只是短暂试验，哪些已经可以清理掉了。

从这个角度看，Skill 的治理和内部脚手架、组件库、平台能力的治理很像。都需要 owner，需要边界，需要审核，也需要淘汰。

只是这一次，被治理的对象不再只是代码，还包括一部分“Agent 能力”。

顺带一提，OpenClaw 在 Skills 的分发治理上已经走出了一个可参考的路径：内置 Skills 随安装包发布，团队共享 Skills 放在 `~/.openclaw/skills`，项目级 Skills 放在工作区的 `skills/` 目录里，三层优先级清晰。再往上，ClawHub 作为公共 Skills 注册表，提供安装、更新和同步能力。

这套分层和 Anthropic 文中描述的“先入库、再市场”的路径是一致的，只是 OpenClaw 已经把它落到了工具链里。

---

## 如果放到团队里，我会先看这几件事

读完 Anthropic 这篇文章，我脑子里比较自然地留下了 7 个观察点。它们都不大，但很适合拿来判断一个团队是不是已经开始把 Skill 当工程资产来维护。

1.  1\. 起点通常是高频返工点，不是最酷的想法。
    
2.  2\. 一个 Skill 先解决一个明确问题，边界窄一点反而更容易站住。
    
3.  3\. 主文件通常会比较短，细节和工具往外拆。
    
4.  4\. 真实踩过的坑，最好单独沉淀下来，再慢慢补厚。
    
5.  5\. 能用脚本兜底的地方，单靠自然语言提醒通常不太够。
    
6.  6\. 验证往往要补得更早，不然后面会越来越贵。
    
7.  7\. 哪些 Skill 值得留下，最后还是要回到日志和实际使用情况上来看。
    

这几条看起来都不复杂，但它们拼在一起，方向就很清楚了。

Skill 这件事，更像一类持续整理和维护的工程活。它不太依赖灵光一现，更依赖团队能不能把已有经验拆清楚，再一点点补稳。

---

## 写在最后

这篇文章之所以值得认真读，是因为它没有把 Skills 讲成一种新鲜概念，而是把它放回了工程实践里。

读完之后再回头看，会发现很多事情其实都不陌生：文档怎么拆，脚本怎么配，坑点怎么记，验证怎么补，资产怎么治理。这些原本就是工程团队一直在做的事。

变化只在于，现在这些经验不再只是给人看，也开始需要给 Agent 用。

所以如果要用一句更平实的话来概括这篇文章，我大概会写成这样：

**Skill 的价值，不在于把提示词写长，而在于把团队已经跑通的经验，整理成 Agent 也能稳定接住的工作方式。**

这件事一旦做好，模型带来的效率提升才比较容易留下来。否则很多高光时刻都只是偶发，换个任务、换个上下文，效果就掉回去了。

而 Anthropic 这篇文章最值得参考的，也正是它把这条路讲得很具体。

如果你今天只做一件事，我建议做个小练习：

-   • **列出团队最近一个月 Agent 反复踩到的 3 个坑**（具体到命令、参数或流程步骤）
    
-   • 对每个坑，写两行：
    

-   • **现状：** 每次怎么发现的？修了几次？
    
-   • **沉淀：** 能不能变成一条 Gotcha，放进对应的 Skill 里？
    

-   • **选一个，本周就动手做成一个最小 Skill**，哪怕只有 SKILL.md + 一个 Gotchas 章节
    

从一个坑开始，比从一个完美蓝图开始，更容易真正跑起来。

---

## 把前几篇放到一起看

如果你有兴趣把最近这几篇连起来看，会发现它们其实在讲同一条线：

篇目

核心关键词

和这篇的关系

[《Claude Code 最佳实践：架构、治理与工程实践》](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408788&idx=1&sn=ffed2fec07f79e5a64029a02fff0f600&scene=21#wechat_redirect)

**控制面分层**

Skills 是六层架构中的工作流层，这篇展开讲它怎么做

[《Skills 详解：Anthropic和OpenAI的路线差异》](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408639&idx=1&sn=ad325d5fa3dd0e112d62b0e34ea3c48a&scene=21#wechat_redirect)

**工作流沉淀**

上次讲路线差异，这次 Anthropic 自己把内部做法公开了

[《深入解析 OpenClaw 上下文窗口压缩》](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408774&idx=1&sn=2cba06288b0f507bb630f83fd04038bf&scene=21#wechat_redirect)

**长会话治理**

Skill 的文件组织和渐进式披露，本质上也是上下文治理的一部分

[《2026 AI Memory 综述：从4W分类到系统落地》](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408756&idx=1&sn=03188bfa5d034a1b5ca0347c72b673fd&scene=21#wechat_redirect)

**记忆分层**

Skill 的日志和状态存储，和情景记忆、工作记忆的设计异曲同工

《[CC核心开发者分享 | 构建 Claude Code 的经验教训：像 Agent 一样看世界](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408480&idx=1&sn=5821c745dd33c781530ab273ab44cdce&scene=21#wechat_redirect)》

**动作空间**

Thariq 系列第一篇，工具设计的方法论也适用于 Skill 怎么拆和组织

《[别把 Prompt Cache 只当优化技巧](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408819&idx=1&sn=f0c65045a197c9a3a6ca5b19faeae4da&scene=21#wechat_redirect)》

**缓存纪律**

Thariq 系列第二篇，Skill 的上下文开销直接受缓存架构影响

[《OpenAI 工程师不写代码了？拆开 Harness Engineering》](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408765&idx=1&sn=62bc37d9672262334fa3aa5d7c77d8f4&scene=21#wechat_redirect)

**反馈回路**

验证类 Skill 正是 Harness Engineering 里反馈回路的具体落地

放在一起看就会更清楚：**Skill 不是一个孤立的功能特性，它是整套 Agent 工程化体系里的一个关键节点。** 怎么组织文件、怎么沉淀坑点、怎么做验证、怎么治理资产——每一个问题都能在这些文章里找到对应的工程思路。

##   

---

## 参考资料

1.  1\. Thariq Shihipar, 《Lessons from Building Claude Code: How We Use Skills》  
      https://x.com/trq212/status/2033949937936085378
    

1.  2\. Claude Code Skills 文档  
      https://docs.anthropic.com/en/docs/claude-code/skills
    
2.  3\. AgentSkills 规范  
      https://agentskills.io
    

如喜欢本文，请点击右上角，把文章分享到朋友圈  
如有想了解学习的技术点，请留言给若飞安排分享

**因公众号更改推送规则，请点“在看”并加“星标”第一时间获取精彩技术分享**

**·END·**  

**相关阅读：**

-   [Claude Skills 入门：把“会用 AI”变成“可复制的工程能力”](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408200&idx=1&sn=2f2cce7dfcbdb0766eac3590f777a17b&scene=21#wechat_redirect)
    
-   [一套可复制的 Claude Code 配置方案：CLAUDE.md、Rules、Commands、Hooks](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408189&idx=1&sn=7d4f7a442a22af37f95c46ff1048a3df&scene=21#wechat_redirect)  
    
-   [Claude Code 最佳实践：把上下文变成生产力（团队可落地版）](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408183&idx=1&sn=0b6f1437465d3a61118db688cc889b17&scene=21#wechat_redirect)
    
-   [把 AI 当成新同事：Agent Coding 的上下文与验证体系](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408169&idx=1&sn=7bba1377a31ffa0ce68932935c8d923a&scene=21#wechat_redirect)
    
-   [一周写百万行的背后：Cursor长时间运行 Agent 的工程方法论](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408161&idx=1&sn=85aaff6f2f779e53b6ae9c5e1f003269&scene=21#wechat_redirect)
    
-   [2026年生活重启指南](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408141&idx=1&sn=e1e64ad73d25414957aa5206ca969fc3&scene=21#wechat_redirect)
    
-   [我真不敢相信，AI 先加速的是工程师。](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408153&idx=1&sn=d33b48464de93a2573a0a0cb025ada9e&scene=21#wechat_redirect)
    
-   [扒一扒 Claude Cowork 系统提示词：Anthropic 如何打造数字同事](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408128&idx=1&sn=1b6c640de61986d1364847bffb2cd28f&scene=21#wechat_redirect)
    
-   [Cowork 安全架构深度解析：从 Claude Code 到 Cowork，Anthropic 如何把“可控”做成产品](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408114&idx=1&sn=29a754281cd07c16b6191c6d146c5837&scene=21#wechat_redirect)  
    
-   [Anthropic官方万字长文：AI Agent评估的系统化方法论](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408107&idx=1&sn=905552d68f5b174fd9548360bdea4448&scene=21#wechat_redirect)
    
-   [银弹还是枷锁？Claude Agent SDK 的架构真相](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408084&idx=1&sn=82f274ba084f9c289e2d141aad0c088b&scene=21#wechat_redirect)
    
-   [Claude Code创始人亲授13条使用技巧](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408076&idx=1&sn=f139e90d699b528e80e79c558eed42ee&scene=21#wechat_redirect)
    
-   [Claude Code 内部工具开源 code-simplifier：终结 AI 屎山代码的终极方案](https://mp.weixin.qq.com/s?__biz=MzAwNjQwNzU2NQ==&mid=2650408028&idx=1&sn=3a8571a9fa0bd5d7e59cd66fc6187b3e&scene=21#wechat_redirect)
    

> 版权申明：内容来源网络，仅供学习研究，版权归原创者所有。如有侵权烦请告知，我们会立即删除并表示歉意。谢谢!

**架构师**

我们都是架构师！

  

  

****关注**架构师(JiaGouX)，添加“星标”**

**获取每天技术干货，一起成为牛逼架构师**  

**技术群请****加若飞：****1321113940** **进架构师群**

投稿、合作、版权等邮箱：**admin@137x.com**

  

预览时标签不可点

Scan to Follow

继续滑动看下一个

轻触阅读原文

![](http://mmbiz.qpic.cn/mmbiz_png/sXiaukvjR0RCNb3RYsCgx02T4J55ia2SnemY7uJHsDChxq6jAibbATlIKDgzLxz0zekXWjblzCDcL86AjbMNp02Tg/0?wx_fmt=png)

架构师

向上滑动看下一个

[Got It](javascript:;)

 

 Scan with Weixin to  
use this Mini Program

[Cancel](javascript:void\(0\);) [Allow](javascript:void\(0\);)

[Cancel](javascript:void\(0\);) [Allow](javascript:void\(0\);)

[Cancel](javascript:void\(0\);) [Allow](javascript:void\(0\);)

× 分析

![作者头像](http://mmbiz.qpic.cn/mmbiz_png/sXiaukvjR0RCNb3RYsCgx02T4J55ia2SnemY7uJHsDChxq6jAibbATlIKDgzLxz0zekXWjblzCDcL86AjbMNp02Tg/0?wx_fmt=png)

微信扫一扫可打开此内容，  
使用完整服务

 : ， ， ， ， ， ， ， ， ， ， ， ， .   Video Mini Program Like ，轻点两下取消赞 Wow ，轻点两下取消在看 Share Comment Favorite 听过
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for Z")

// Then continue your work while they run in background
// System will notify you when each completes
```

WHY:
- Agents can perform deeper, more thorough searches
- Background tasks run in parallel, saving time
- Specialized agents have domain expertise
- Reduces context window usage in main session

ALWAYS prefer: Multiple parallel task calls > Direct tool calls

```



**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/skill-creator/SKILL.md"
}
```

**Output:**
```
<path>/Users/felixcxr/code/wanxiao_demo/skills/skill-creator/SKILL.md</path>
<type>file</type>
<content>1: ---
2: name: skill-creator
3: description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
4: license: Complete terms in LICENSE.txt
5: ---
6: 
7: # Skill Creator
8: 
9: This skill provides guidance for creating effective skills.
10: 
11: ## About Skills
12: 
13: Skills are modular, self-contained packages that extend Claude's capabilities by providing
14: specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
15: domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
16: equipped with procedural knowledge that no model can fully possess.
17: 
18: ### What Skills Provide
19: 
20: 1. Specialized workflows - Multi-step procedures for specific domains
21: 2. Tool integrations - Instructions for working with specific file formats or APIs
22: 3. Domain expertise - Company-specific knowledge, schemas, business logic
23: 4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks
24: 
25: ## Core Principles
26: 
27: ### Concise is Key
28: 
29: The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.
30: 
31: **Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"
32: 
33: Prefer concise examples over verbose explanations.
34: 
35: ### Set Appropriate Degrees of Freedom
36: 
37: Match the level of specificity to the task's fragility and variability:
38: 
39: **High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.
40: 
41: **Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.
42: 
43: **Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.
44: 
45: Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).
46: 
47: ### Anatomy of a Skill
48: 
49: Every skill consists of a required SKILL.md file and optional bundled resources:
50: 
51: ```
52: skill-name/
53: ├── SKILL.md (required)
54: │   ├── YAML frontmatter metadata (required)
55: │   │   ├── name: (required)
56: │   │   └── description: (required)
57: │   └── Markdown instructions (required)
58: └── Bundled Resources (optional)
59:     ├── scripts/          - Executable code (Python/Bash/etc.)
60:     ├── references/       - Documentation intended to be loaded into context as needed
61:     └── assets/           - Files used in output (templates, icons, fonts, etc.)
62: ```
63: 
64: #### SKILL.md (required)
65: 
66: Every SKILL.md consists of:
67: 
68: - **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
69: - **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).
70: 
71: #### Bundled Resources (optional)
72: 
73: ##### Scripts (`scripts/`)
74: 
75: Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.
76: 
77: - **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
78: - **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
79: - **Benefits**: Token efficient, deterministic, may be executed without loading into context
80: - **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments
81: 
82: ##### References (`references/`)
83: 
84: Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.
85: 
86: - **When to include**: For documentation that Claude should reference while working
87: - **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
88: - **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
89: - **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
90: - **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
91: - **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.
92: 
93: ##### Assets (`assets/`)
94: 
95: Files not intended to be loaded into context, but rather used within the output Claude produces.
96: 
97: - **When to include**: When the skill needs files that will be used in the final output
98: - **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
99: - **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
100: - **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context
101: 
102: #### What to Not Include in a Skill
103: 
104: A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:
105: 
106: - README.md
107: - INSTALLATION_GUIDE.md
108: - QUICK_REFERENCE.md
109: - CHANGELOG.md
110: - etc.
111: 
112: The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxilary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.
113: 
114: ### Progressive Disclosure Design Principle
115: 
116: Skills use a three-level loading system to manage context efficiently:
117: 
118: 1. **Metadata (name + description)** - Always in context (~100 words)
119: 2. **SKILL.md body** - When skill triggers (<5k words)
120: 3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)
121: 
122: #### Progressive Disclosure Patterns
123: 
124: Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.
125: 
126: **Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.
127: 
128: **Pattern 1: High-level guide with references**
129: 
130: ```markdown
131: # PDF Processing
132: 
133: ## Quick start
134: 
135: Extract text with pdfplumber:
136: [code example]
137: 
138: ## Advanced features
139: 
140: - **Form filling**: See [FORMS.md](FORMS.md) for complete guide
141: - **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
142: - **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
143: ```
144: 
145: Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.
146: 
147: **Pattern 2: Domain-specific organization**
148: 
149: For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:
150: 
151: ```
152: bigquery-skill/
153: ├── SKILL.md (overview and navigation)
154: └── reference/
155:     ├── finance.md (revenue, billing metrics)
156:     ├── sales.md (opportunities, pipeline)
157:     ├── product.md (API usage, features)
158:     └── marketing.md (campaigns, attribution)
159: ```
160: 
161: When a user asks about sales metrics, Claude only reads sales.md.
162: 
163: Similarly, for skills supporting multiple frameworks or variants, organize by variant:
164: 
165: ```
166: cloud-deploy/
167: ├── SKILL.md (workflow + provider selection)
168: └── references/
169:     ├── aws.md (AWS deployment patterns)
170:     ├── gcp.md (GCP deployment patterns)
171:     └── azure.md (Azure deployment patterns)
172: ```
173: 
174: When the user chooses AWS, Claude only reads aws.md.
175: 
176: **Pattern 3: Conditional details**
177: 
178: Show basic content, link to advanced content:
179: 
180: ```markdown
181: # DOCX Processing
182: 
183: ## Creating documents
184: 
185: Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).
186: 
187: ## Editing documents
188: 
189: For simple edits, modify the XML directly.
190: 
191: **For tracked changes**: See [REDLINING.md](REDLINING.md)
192: **For OOXML details**: See [OOXML.md](OOXML.md)
193: ```
194: 
195: Claude reads REDLINING.md or OOXML.md only when the user needs those features.
196: 
197: **Important guidelines:**
198: 
199: - **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
200: - **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Claude can see the full scope when previewing.
201: 
202: ## Skill Creation Process
203: 
204: Skill creation involves these steps:
205: 
206: 1. Understand the skill with concrete examples
207: 2. Plan reusable skill contents (scripts, references, assets)
208: 3. Initialize the skill (run init_skill.py)
209: 4. Edit the skill (implement resources and write SKILL.md)
210: 5. Package the skill (run package_skill.py)
211: 6. Iterate based on real usage
212: 
213: Follow these steps in order, skipping only if there is a clear reason why they are not applicable.
214: 
215: ### Step 1: Understanding the Skill with Concrete Examples
216: 
217: Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.
218: 
219: To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.
220: 
221: For example, when building an image-editor skill, relevant questions include:
222: 
223: - "What functionality should the image-editor skill support? Editing, rotating, anything else?"
224: - "Can you give some examples of how this skill would be used?"
225: - "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
226: - "What would a user say that should trigger this skill?"
227: 
228: To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.
229: 
230: Conclude this step when there is a clear sense of the functionality the skill should support.
231: 
232: ### Step 2: Planning the Reusable Skill Contents
233: 
234: To turn concrete examples into an effective skill, analyze each example by:
235: 
236: 1. Considering how to execute on the example from scratch
237: 2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly
238: 
239: Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:
240: 
241: 1. Rotating a PDF requires re-writing the same code each time
242: 2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill
243: 
244: Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:
245: 
246: 1. Writing a frontend webapp requires the same boilerplate HTML/React each time
247: 2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill
248: 
249: Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:
250: 
251: 1. Querying BigQuery requires re-discovering the table schemas and relationships each time
252: 2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill
253: 
254: To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.
255: 
256: ### Step 3: Initializing the Skill
257: 
258: At this point, it is time to actually create the skill.
259: 
260: Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.
261: 
262: When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.
263: 
264: Usage:
265: 
266: ```bash
267: scripts/init_skill.py <skill-name> --path <output-directory>
268: ```
269: 
270: The script:
271: 
272: - Creates the skill directory at the specified path
273: - Generates a SKILL.md template with proper frontmatter and TODO placeholders
274: - Creates example resource directories: `scripts/`, `references/`, and `assets/`
275: - Adds example files in each directory that can be customized or deleted
276: 
277: After initialization, customize or remove the generated SKILL.md and example files as needed.
278: 
279: ### Step 4: Edit the Skill
280: 
281: When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.
282: 
283: #### Learn Proven Design Patterns
284: 
285: Consult these helpful guides based on your skill's needs:
286: 
287: - **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
288: - **Specific output formats or quality standards**: See references/output-patterns.md for template and example patterns
289: 
290: These files contain established best practices for effective skill design.
291: 
292: #### Start with Reusable Skill Contents
293: 
294: To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.
295: 
296: Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.
297: 
298: Any example files and directories not needed for the skill should be deleted. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.
299: 
300: #### Update SKILL.md
301: 
302: **Writing Guidelines:** Always use imperative/infinitive form.
303: 
304: ##### Frontmatter
305: 
306: Write the YAML frontmatter with `name` and `description`:
307: 
308: - `name`: The skill name
309: - `description`: This is the primary triggering mechanism for your skill, and helps Claude understand when to use the skill.
310:   - Include both what the Skill does and specific triggers/contexts for when to use it.
311:   - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to Claude.
312:   - Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"
313: 
314: Do not include any other fields in YAML frontmatter.
315: 
316: ##### Body
317: 
318: Write instructions for using the skill and its bundled resources.
319: 
320: ### Step 5: Packaging a Skill
321: 
322: Once development of the skill is complete, it must be packaged into a distributable .skill file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:
323: 
324: ```bash
325: scripts/package_skill.py <path/to/skill-folder>
326: ```
327: 
328: Optional output directory specification:
329: 
330: ```bash
331: scripts/package_skill.py <path/to/skill-folder> ./dist
332: ```
333: 
334: The packaging script will:
335: 
336: 1. **Validate** the skill automatically, checking:
337: 
338:    - YAML frontmatter format and required fields
339:    - Skill naming conventions and directory structure
340:    - Description completeness and quality
341:    - File organization and resource references
342: 
343: 2. **Package** the skill if validation passes, creating a .skill file named after the skill (e.g., `my-skill.skill`) that includes all files and maintains the proper directory structure for distribution. The .skill file is a zip file with a .skill extension.
344: 
345: If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.
346: 
347: ### Step 6: Iterate
348: 
349: After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.
350: 
351: **Iteration workflow:**
352: 
353: 1. Use the skill on real tasks
354: 2. Notice struggles or inefficiencies
355: 3. Identify how SKILL.md or bundled resources should be updated
356: 4. Implement changes and test again

(End of file - total 356 lines)
</content>

[Project README: /Users/felixcxr/code/wanxiao_demo/README.md]
# TODO LIST

1. - [ ] skills 仍未成功加载
2. - [ ] 记忆模块完善
    1. - [ ] Milvus Lite 记忆检索脚本尝试
    2. - [x] 记忆子Agent从主 Agent解耦出来
    3. - [ ] 画记忆模块的架构图
    4. - [ ] 长期记忆的提示词需要进行解耦，要记录的内容现在太杂太多，应该解耦成用户偏好/代理人偏好/已咨询保险等
    5. - [x] 系统提示词里 memory.md 需要修改，不应该让他再去 read file的，因为记忆已经自动载入到<agent_memory> 里，这样会浪费一次大模型的调用。可以指明 edit file 的记忆路径


# DeepAgents + OpenRouter + 原生前端 Demo

## 功能说明

- 使用 LangChain DeepAgents（`create_deep_agent`）作为核心 Agent 运行时。
- 通过 `langchain-openai` 接入 OpenRouter 模型（默认 `z-ai/glm-4.7-flash`）。
- 从 `~/.deepagents/agent/skills` 加载技能文件，并映射到 `/skills/*`。
- 使用本地文件系统后端，记忆数据存储在项目内的 `memories/` 目录。
- 前端使用原生 `HTML + CSS + JavaScript`。
- 后端使用 FastAPI 提供静态页面与接口（如 `/api/chat`、`/api/chat/stream`）。
- 前端通过 `/api/chat/stream` 消费流式输出。
- 界面右侧提供“思考过程”面板，展示 LangGraph 事件、工具调用与阶段信息。

## 环境准备

1. 安装依赖：

```bash
uv sync
```

2. 创建环境变量文件：

```bash
cp .env.example .env
```

3. 编辑 `.env`：

```env
OPENROUTER_API_KEY="your-openrouter-key"
OPENROUTER_MODEL="z-ai/glm-4.5-flash"
OPENROUTER_MEMORY_MODEL="z-ai/glm-4.7-flash"
MEMORY_AGENT_ENABLED="1"
OUTPUT_SANITIZE_ENABLED="1"
```

## 启动项目

```bash
uv run python main.py
```

浏览器访问：`http://localhost:7860`

默认开启自动重载（代码变更后进程自动重启）。

如果要关闭自动重载：

```bash
AUTO_RELOAD=0 uv run python main.py
```

## 运行测试

```bash
uv run python -m unittest tests/test_main.py
```

或运行全部测试：

```bash
uv run python -m unittest discover -s tests
```

## 前端目录结构

```text
frontend/
├── index.html
├── style.css
└── script.js
```

- `index.html`：聊天页面结构（头部、消息区、技能区、输入区）
- `style.css`：页面布局、动画、响应式样式
- `script.js`：前端交互逻辑与接口调用

## 技能目录说明

应用会递归读取以下目录中的技能文本文件：

`~/.deepagents/agent/skills`

这些文件会被映射为 DeepAgents 可访问的虚拟路径 `/skills/...`，供 Agent 按需加载。

## 记忆目录说明（双层记忆）

记忆以 Markdown 形式保存在项目根目录下：

```text
memories/
├── MEMORY.md
└── daily/
    └── YYYY-MM-DD.md
```

- `memories/daily/YYYY-MM-DD.md`：短期记忆（按天记录的追加日志）
- `memories/MEMORY.md`：长期记忆（用户偏好、关键决策、联系人、项目事实）

系统提示会引导 Agent：

1. 会话开始时读取长期记忆与最近日记。
2. 将短期信息按 `## HH:MM - 标题` 写入当日日志。
3. 将跨天稳定信息去重后沉淀到 `MEMORY.md`。

## Prompt 配置化

- 所有主/子 Agent 提示词已从 `main.py` 抽离到配置与模板文件：

```text
config/prompts.yaml
prompts/main_system/SOUL.md
prompts/main_system/INDENTITY.md
prompts/main_system/MEMORY.md
prompts/memory_agent.md
```

- `config/prompts.yaml` 负责：
  - prompt 文件路由
  - 主模型与 memory_agent 模型配置（含 env 键与默认值）

## Memory Agent（异步记忆提炼）

- 新增 `memory_agent` 子 Agent：每轮用户-助手对话结束后异步执行，不阻塞主回复。
- 模型默认使用 `z-ai/glm-4.7-flash`（可通过 `OPENROUTER_MEMORY_MODEL` 覆盖）。
- 输出为结构化 JSON，自动落盘到：
  - 每日短期记忆：`memories/daily/YYYY-MM-DD.md`
  - 长期记忆：`memories/MEMORY.md`
- 可通过 `MEMORY_AGENT_ENABLED=0` 关闭该异步记忆提炼流程。

## 输出净化规则配置

- 配置文件：`config/output_sanitize.yaml`
- 可配置项：
  - `enabled`：是否启用净化
  - `literals`：命中即过滤的关键词
  - `regex`：正则过滤规则
- 运行时总开关：`OUTPUT_SANITIZE_ENABLED=0/1`

## 文件自动同步（Daytona 沙箱）
应用支持将本地 `skills/`、`data/`、`memories/` 文件夹的变更**自动同步**到 Daytona 沙箱，无需重启应用。

### 工作原理

- **自动监听**：应用启动后，使用 `watchdog` 库监视三个文件夹的变更
- **防抖机制**：变更发生后等待 2 秒（可配置），期间如有新变更则重置计时器
- **增量同步**：只上传变更的文件，保留沙箱中其他文件
- **自动清理**：应用退出时自动停止监听器

### 环境变量配置

```bash
# 禁用文件监听（默认启用）
FILE_WATCH_ENABLED=0 uv run python main.py

# 调整防抖时间（默认 2.0 秒）
FILE_WATCH_DEBOUNCE=5.0 uv run python main.py
```

### 手动同步 API

如需手动触发同步（例如临时禁用自动监听时）：

```bash
# 触发同步
curl -X POST http://localhost:7860/api/sync

# 返回示例
{
  "status": "success",
  "message": "文件夹同步完成",
  "synced_folders": ["skills", "data", "memories"]
}
```

### 工作流程

```
修改本地文件（skills/data/memories）
           ↓
    文件监听器检测到变更
           ↓
    防抖等待 2 秒（可配置）
           ↓
    自动同步到 Daytona 沙箱
           ↓
    Agent 立即使用最新文件
```

### 注意事项

- 首次启动时会自动安装 `watchdog` 依赖（已添加到 `pyproject.toml`）
- 隐藏文件（以 `.` 开头）、临时文件、`__pycache__` 等会被自动忽略
- 如果沙箱未初始化（如启动失败），自动监听将不会启动
## Milvus Lite 记忆检索脚本
新增脚本：`src/milvus_mem_search.py`

- 数据源目录：`memories/daily/*.md`（仅匹配 `YYYY-MM-DD.md`）
- 向量库：Milvus Lite 本地文件 `/.memories/milvus_memories.db`
- 向量模型：`sentence-transformers` 的 `all-MiniLM-L6-v2`

常用命令：

```bash
# 首次或增量索引 daily 记忆
uv run python src/milvus_mem_search.py index

# 全量重建索引（drop + rebuild）
uv run python src/milvus_mem_search.py rebuild

# 语义检索
uv run python src/milvus_mem_search.py search "今天提过哪些客户需求" --top-k 5

# 查看 collection 统计
uv run python src/milvus_mem_search.py stats
```

```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 105.5s)

_Thinking:_

  我已经获取了参考文章和现有技能目录的信息。现在让我分析一下：

**从图片中获取的3个内部工具信息**：
1. **保险产品内容检索** - 根据产品内容检索产品，支持多种contentType（产品基本信息、投保规则、说明书、险种列表等）
2. **保险产品属性详情** - 根据产品编码或名称返回产品详细信息
3. **产品工具接口** - 可以通过MP_CODE查询责任详细信息

**第4个工具**：
- web_search.py - 入参是 --question "用户问题"

**从图片中获取的TODO要求**：
1. 外部网页搜索工具作为产品问答的补充，不用于通用问答的回答
2. 去除调内部资料/网络信息标识的输出，用引用的方式标识外部信息
3. 未指定产品的时候，默认先走平安产品
4. 去除脚本调用的思考过程生成（可能是因为plan.md没有写好）

**参考文章的核心理念**：
- Skill是文件夹，不只是单个Markdown文件
- 使用渐进式披露设计原则
- SKILL.md保留触发条件、任务目标、硬规则
- 细节拆到references/，脚本拆到scripts/，模板放到assets/
- Gotchas（坑点）很重要
- 验证很关键

现在我需要创建这个保险产品问答Skill技能包。让我更新任务状态并开始创建主Skill.md。

  我已阅读参考文章和现有技能结构。根据您的需求和图片中的工具信息，我来为您设计这套保险产品问答Skill技能包。

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "分析参考文章和现有技能目录结构",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "设计主Skill.md（触发条件、任务目标、硬规则）",
      "priority": "high",
      "status": "in_progress"
    },
    {
      "content": "设计子Skill - plan.md（问题拆分与工具调用计划）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - tool.md（工具调用执行）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - error.md（报错与冲突处理）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - uncertain.md（反问模块）",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "设计子Skill - format.md（输出规范）",
      "priority": "high",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "分析参考文章和现有技能目录结构",
    "priority": "high",
    "status": "completed"
  },
  {
    "content": "设计主Skill.md（触发条件、任务目标、硬规则）",
    "priority": "high",
    "status": "in_progress"
  },
  {
    "content": "设计子Skill - plan.md（问题拆分与工具调用计划）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - tool.md（工具调用执行）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - error.md（报错与冲突处理）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - uncertain.md（反问模块）",
    "priority": "high",
    "status": "pending"
  },
  {
    "content": "设计子Skill - format.md（输出规范）",
    "priority": "high",
    "status": "pending"
  }
]
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 144.9s)

_Thinking:_

  现在我开始创建主Skill.md和各个子Skill.md。首先创建主Skill.md。

   现在开始创建保险产品问答Skill技能包。首先创建主Skill.md：

**Tool: write**

**Input:**
```json
{
  "content": "---\nname: insurance-qa\nname: insurance-qa\ndescription: 中国平安保险产品问答专家，处理保险产品知识答疑、销售话术生成、内外部产品对比等需求。使用场景包括：(1)用户询问保险产品保障范围、投保规则、条款解读；(2)销售人员需要产品对比、话术支持；(3)查询具体产品属性、费率、责任详情；(4)内外部保险产品信息对比分析。当用户问题涉及保险产品设计、保障内容、投保条件、销售规则时触发本Skill。\nlicense: Proprietary - Ping An Insurance\n---\n\n# 保险产品问答 Skill\n\n## 任务目标\n\n帮助用户获得准确、完整、专业的保险产品信息，覆盖以下能力：\n- **知识答疑**：产品保障范围、条款解读、投保规则、理赔流程\n- **销售话术**：产品卖点提炼、客户异议处理、场景化推荐\n- **产品对比**：内外部产品责任对比、优劣势分析、适配性建议\n\n## 触发条件\n\n当用户问题涉及以下关键词或场景时，激活本Skill：\n\n| 触发类型 | 关键词/场景示例 |\n|---------|----------------|\n| 产品查询 | \"XX产品保什么\"、\"帮我查下保险\"、\"这个险种包含哪些责任\" |\n| 条款解读 | \"免责条款\"、\"等待期\"、\"免赔额\"、\"赔付比例\" |\n| 投保规则 | \"投保年龄\"、\"健康告知\"、\"保额上限\"、\"缴费期限\" |\n| 销售话术 | \"怎么跟客户说\"、\"卖点是什么\"、\"客户问XX怎么回答\" |\n| 产品对比 | \"和XX比怎么样\"、\"哪个更好\"、\"竞品分析\" |\n| 理赔相关 | \"怎么理赔\"、\"理赔材料\"、\"理赔时效\" |\n\n## 硬规则（必须遵守）\n\n### 1. 问题拆分原则\n\n**必须拆分的情况：**\n- 用户问题包含多个独立子问题（如：\"A产品和B产品哪个好，分别保什么\"）\n- 需要同时查询多个产品信息后进行对比\n- 问题涉及\"对比\"、\"分别\"、\"都\"、\"各\"等关键词\n\n**拆分后处理流程：**\n1. 识别子问题数量和类型\n2. 为每个子问题选择合适的工具\n3. 并行执行独立子问题的工具调用\n4. 合并结果后统一输出\n\n### 2. 工具选择优先级\n\n```\n优先级1（内部资料）: 保险产品内容检索 → 保险产品属性详情 → 产品工具接口\n优先级2（外部补充）: web_search.py（仅当内部资料不足时）\n```\n\n**强制规则：**\n- 必须先尝试内部工具获取信息\n- 外部搜索仅作为产品问答的补充，不用于通用问答\n- 未指定具体产品时，默认优先查询平安保险产品\n\n### 3. 反问触发条件\n\n**必须反问的情况（见 @references/uncertain.md）：**\n- 用户问题未明确保险产品大类（如只说\"帮我查下保险\"）\n- 问题中产品名称模糊或不存在\n- 需要用户确认时间范围、保障额度等关键参数\n- 多个产品同名，需要确认具体版本\n\n### 4. 信息冲突处理\n\n**冲突场景识别：**\n- 不同工具返回的产品信息不一致\n- 内部资料与外部搜索结果矛盾\n- 同一产品的不同版本信息冲突\n\n**处理原则（见 @references/error.md）：**\n- 内部资料优先级高于外部搜索\n- 以最新生效的产品信息为准\n- 记录冲突点并在输出中说明\n\n### 5. 输出格式规范\n\n**必须遵守的格式规则（见 @references/format.md）：**\n- 涉及多款产品：使用表格形式输出对比\n- 回答用户具体问题：先简明扼要回答，再详细展开\n- 引用外部信息：以Markdown格式标注来源网址\n- 涉及内部资料：不添加特殊标识，直接呈现\n\n## 工作流\n\n```mermaid\ngraph TD\n    A[接收用户问题] --> B{问题是否明确?}\n    B -->|否| C[执行uncertain.md反问模块]\n    C --> D[获取澄清后的问题]\n    D --> B\n    B -->|是| E[执行plan.md拆分问题]\n    E --> F{是否需要拆分?}\n    F -->|是| G[拆分为多个子问题]\n    F -->|否| H[单问题处理]\n    G --> I[执行tool.md工具调用]\n    H --> I\n    I --> J{工具调用成功?}\n    J -->|否| K[执行error.md错误处理]\n    K --> L{是否可重试?}\n    L -->|是| I\n    L -->|否| M[返回错误说明]\n    J -->|是| N[执行format.md格式化输出]\n    N --> O[返回最终答案]\n```\n\n## 工具概览\n\n| 工具名称 | 脚本路径 | 核心用途 | 调用时机 |\n|---------|---------|---------|---------|\n| 保险产品内容检索 | `scripts/product_content_search.py` | 根据内容类型检索产品列表 | 需要查找产品、了解产品分类时 |\n| 保险产品属性详情 | `scripts/product_attribute_detail.py` | 查询产品具体属性信息 | 需要产品详细信息时 |\n| 产品工具接口 | `scripts/product_tool_interface.py` | 通过MP_CODE查询责任详情 | 需要责任详细信息时 |\n| 网页搜索 | `scripts/web_search.py` | 补充外部产品信息 | 内部资料不足时 |\n\n## 渐进式披露\n\n本Skill采用分层信息架构：\n\n1. **SKILL.md**（本文件）：核心规则和工作流\n2. **@references/plan.md**：问题拆分策略和工具选择逻辑\n3. **@references/tool.md**：工具调用详细说明和参数规范\n4. **@references/error.md**：错误处理和冲突解决机制\n5. **@references/uncertain.md**：反问策略和澄清话术\n6. **@references/format.md**：输出格式规范\n\n按需要加载对应的reference文件。\n\n## 常见坑点（Gotchas）\n\n1. **产品名称歧义**：同一产品可能有多个版本或别名，需要通过产品编码确认\n2. **contentType选择**：不同问题需要选择正确的contentType，错误选择会导致查不到信息\n3. **生效状态过滤**：查询时要关注产品是否处于\"生效\"状态，避免返回已停售产品\n4. **外部信息标识**：使用外部搜索结果时，必须用引用格式标注来源，不可与内部资料混淆\n5. **多产品对比**：对比时要确保字段对齐，避免A产品的A字段对比B产品的B字段\n6. **权限范围**：注意产品的渠道授权、APP授权、机构授权信息，不同渠道可能有不同规则\n\n## 质量检查清单\n\n在返回最终答案前，确认以下检查项：\n\n- [ ] 是否准确理解用户问题，无歧义\n- [ ] 是否选择了正确的工具和参数\n- [ ] 如涉及多款产品，是否使用表格对比\n- [ ] 外部信息是否已标注来源\n- [ ] 回答是否先简明后详细\n- [ ] 是否去除工具调用的思考过程\n- [ ] 未指定产品时是否默认查询平安产品\n- [ ] 信息冲突时是否已按规则处理并说明\n",
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/SKILL.md"
}
```

**Error:**
```
Error: File already exists. Use edit tool instead.
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 80.3s)

_Thinking:_

   文件已存在，让我先读取现有内容。

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/SKILL.md"
}
```

**Output:**
```
<path>/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/SKILL.md</path>
<type>file</type>
<content>1: ---
2: name: insurance-qa-skill
3: description: |
4:   保险与通用知识问答 Skill。当用户询问保险条款、产品、费率、理赔流程相关咨询，
5:   需要对比多个保险产品，询问实时信息（天气、新闻、政策变动），或问题涉及保险知识+外部信息的组合时，
6:   必须使用此 Skill。此 Skill 协调内部保险问答工具和外部网页搜索工具，通过问题拆分、验证、错误处理等模块，
7:   提供准确、完整、可追溯的问答服务。确保保险信息来自内部工具，外部信息标明来源，
8:   信息边界清晰，不混淆内外部数据。
9: ---
10: 
11: # 保险与通用知识问答 Skill
12: 
13: ## 触发条件
14: 当用户提出以下类型问题时激活：
15: - 保险条款、产品、费率、理赔流程相关咨询
16: - 需要对比多个保险产品
17: - 询问实时信息（天气、新闻、政策变动等）
18: - 问题涉及保险知识+外部信息的组合
19: 
20: ## 任务目标
21: 提供准确、完整、可追溯的问答服务，确保：
22: 1. 保险信息必须来自内部工具，不得 hallucinate
23: 2. 外部信息必须通过搜索工具获取，标明来源
24: 3. 多工具协作时，信息边界清晰，不混淆内外部数据
25: 4. 无法确认的信息明确告知用户，不强行回答
26: 
27: ## 执行流程（含具体工具调用）
28: 
29: **步骤一：问题拆分与计划**
30: - 读取 @references/plan.md
31: - 评估用户问题是否需要拆分为多个子问题
32: - 生成执行计划，确定每个子问题使用的工具
33: 
34: **步骤二：工具选择与调用**
35: 根据问题类型选择对应工具（详见 @references/tool.md）：
36: - **内部保险工具（product_answer.py）**：处理保险条款、产品、费率、理赔规则等结构化数据查询
37: - **外部搜索工具（web_search.py）**：处理新闻、天气、政策文件等非结构化实时信息查询
38: - **混合问题**：串行调用上述两个工具，先内部后外部
39: 
40: **步骤三：答案验证**
41: - 读取 @references/validation.md
42: - 检查工具返回数据的完整性、准确性、相关性、一致性
43: - 验证通过则进入下一步；验证失败则进入错误处理
44: 
45: **步骤四：错误处理（如需要）**
46: - 读取 @references/error.md
47: - 根据错误类型执行重试、调整或报错
48: - 处理完成后返回步骤三重新验证
49: 
50: **步骤五：格式组装与输出**
51: - 读取 @assets/format.md
52: - 按规范标注信息来源（【内部资料】/【网络信息】）
53: - 组装最终答案
54: 
55: **步骤六：关联问题推荐（可选）**
56: - 读取 @references/suggestions.md
57: - 基于用户问题和答案内容，选择合适的推荐策略
58: - 生成 2-3 个不同方向的关联问题
59: - 将推荐问题追加到输出末尾
60: 
61: ## 硬规则（不可违反）
62: 
63: ### 规则 1：问题拆分强制检查
64: - 所有问题必须先经过计划模块（详见 @references/plan.md）评估是否需要拆分
65: - 不得跳过拆分评估直接调用工具
66: 
67: ### 规则 2：工具调用规范（详见 @references/tool.md）
68: - **严禁直接回答**保险问题而不调用 `scripts/product_answer.py`
69: - **严禁使用内部知识**回答需要实时信息的问题，必须调用 `scripts/web_search.py`
70: - 工具调用必须严格按照 tool.md 规定的参数格式和解析方式
71: - 禁止并行调用工具，必须串行执行（避免信息污染）
72: 
73: ### 规则 3：工具选择优先级
74: - 保险相关问题（条款、产品、费率、理赔、保单）：**必须**使用 `product_answer.py`
75: - 实时性通用知识（新闻、天气、政策、市场动态）：**必须**使用 `web_search.py`
76: - 混合问题：先执行 `product_answer.py`，再执行 `web_search.py`，最后合并
77: 
78: ### 规则 4：验证强制
79: - 每个工具返回结果必须经过验证模块（详见 @references/validation.md）检查
80: - 特别注意检查 `product_answer.py` 返回的 `answer` 是否为空或含错误提示
81: - 特别注意检查 `web_search.py` 返回的 `web_sumn` 是否为有效总结
82: - 验证失败不得直接输出，必须进入错误处理模块（详见 @references/error.md）
83: 
84: ### 规则 5：输出规范（详见 @assets/format.md）
85: - 必须按照 format.md 的规范标注信息来源（【内部资料】/【网络信息】）
86: - 必须区分内外部信息边界
87: - 数值、日期等格式必须符合规范要求
88: 
89: ### 规则 6：脚本执行安全
90: - 只允许调用 `scripts/` 目录下的这两个脚本
91: - 禁止构造包含 shell 注入风险的命令（如 `; rm -rf /`）
92: - 参数中的引号必须正确转义
93: 
94: ## 工具调用速查表
95: 
96: | 问题类型 | 脚本 | 关键参数 | 输出字段 | 依赖 |
97: |---------|------|---------|---------|------|
98: | 保险条款/产品/费率 | `product_answer.py` | `--question` (str) | `answer` (str) | 无 |
99: | 新闻/天气/政策/市场 | `web_search.py` | `--question` (str) | `web_detail` (List[str]), `web_sumn` (str) | 无 |
100: 
101: **注意**：详细调用规范、参数说明、错误处理、返回值解析示例，请参阅 @references/tool.md
102: 
103: ## 关键概念定义
104: 
105: - **内部保险工具**：`product_answer.py`，查询保险产品条款、费率、理赔规则等结构化数据
106: - **外部搜索工具**：`web_search.py`，获取新闻、天气、政策文件等非结构化实时信息
107: - **子问题**：独立、可验证的最小问答单元，一个脚本调用对应一个子问题
108: - **信息冲突**：`product_answer.py` 返回与 `web_search.py` 返回的数据矛盾
109: 
110: ## Gotchas（关键陷阱）
111: 详见 @references/gotchas.md，核心陷阱包括：
112: - 保险条款版本混淆（2023版 vs 2024版）
113: - 地域限定条款未标注（某些产品仅限特定地区销售）
114: - 将 `web_sumn` 中的营销话术当作 `product_answer.py` 的条款承诺
115: - `web_detail` 中的过时保险信息覆盖 `product_answer.py` 的最新条款
116: - 脚本返回空字符串或错误信息时未捕获，直接当作有效答案输出

(End of file - total 116 lines)
</content>

[Project README: /Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/README.md]
# Insurance QA Skill

保险与通用知识问答 Skill，用于处理用户的保险产品问答和通用性知识问答（如天气、新闻等）。

## 功能特性

- **保险问答**：通过内部工具查询保险产品条款、费率、理赔规则等官方信息
- **通用搜索**：通过外部搜索工具获取实时新闻、政策、天气等外部信息
- **智能规划**：自动拆分复杂问题为可独立执行的子问题序列
- **答案验证**：多维度验证答案质量（完整性、准确性、相关性、一致性）
- **错误处理**：优雅处理工具调用失败、信息冲突等异常情况
- **来源标注**：清晰区分内部资料和外部信息，标注信息边界

## 文件结构

```
insurance-qa-skill/
├── SKILL.md                      # 主入口：触发条件、硬规则、总体流程
├── README.md                     # 本文件：项目说明和结构概览
├── references/                   # 参考文档：详细策略和规范
│   ├── plan.md                   # 计划模块：问题拆分策略
│   ├── tool.md                   # 工具规范：脚本调用方式和参数详解
│   ├── validation.md             # 验证模块：答案质量检查标准
│   ├── error.md                  # 错误处理：异常处理和冲突解决
│   └── gotchas.md                # 陷阱清单：保险场景特有风险
├── scripts/                      # 可执行脚本
│   ├── product_answer.py         # 内部保险问答工具
│   └── web_search.py             # 外部网页搜索工具
├── assets/                       # 资源文件
│   ├── format.md                 # 输出格式规范
│   ├── insurance-templates/      # 保险产品专用模板（待扩展）
│   └── search-templates/         # 通用搜索模板（待扩展）
└── examples/                     # 示例文档
    ├── tool-usage-example.md     # 工具调用示例（待扩展）
    └── error-recovery-example.md # 错误恢复示例（待扩展）
```

## 快速开始

### 1. 安装依赖

```bash
# 两个脚本仅依赖Python标准库，无需额外安装
python --version  # 需要 Python 3.7+
```

### 2. 使用内部保险问答工具

```bash
python scripts/product_answer.py --question "重疾险等待期是多少天"
python scripts/product_answer.py --question "30岁男性重疾险50万保额年缴保费"
```

**参数说明：**
- `--question` (必填): 标准化的保险问题描述
- `--format` (可选): 输出格式，`text` 或 `json`，默认 `text`
- `--version` (可选): 指定条款版本，如 `2024版`

**输出字段：**
- `answer` (str): 关于保险问题的文本答案

### 3. 使用外部网页搜索工具

```bash
python scripts/web_search.py --question "2025年3月保险监管新政策"
python scripts/web_search.py --question "北京今天天气"
```

**参数说明：**
- `--question` (必填): 搜索查询词
- `--format` (可选): 输出格式，`json` 或 `text`，默认 `json`
- `--num-results` (可选): 返回结果数量，默认 `3`

**输出字段：**
- `web_detail` (List[str]): 前3个相关网页的详细内容
- `web_sumn` (str): 基于搜索结果的总结

### 4. 混合查询示例

```bash
# 步骤1：查询内部保险产品信息
python scripts/product_answer.py --question "XX重疾险产品条款简介"

# 步骤2：搜索相关外部政策新闻
python scripts/web_search.py --question "2025年3月 XX重疾险 监管政策 新规"
```

## 核心流程

```
用户问题 → 计划模块（plan.md）→ 生成执行计划
   ↓
确定工具类型 → 调用对应脚本
   ↓
验证模块（validation.md）检查返回数据
   ↓
通过？ → 是：继续下一子问题或进入格式化
   ↓
否 → 错误模块（error.md）处理 → 重试/调整/报错
   ↓
格式模块（format.md）组装输出（标注数据来源）
```

## 硬规则

1. **问题拆分强制检查**：所有问题必须先经过计划模块评估是否需要拆分
2. **工具调用规范**：保险问题必须用 `product_answer.py`，实时信息必须用 `web_search.py`
3. **工具选择优先级**：保险相关问题优先使用内部工具
4. **验证强制**：每个工具返回结果必须经过验证模块检查
5. **输出规范**：必须按照 format.md 规范标注信息来源
6. **脚本执行安全**：只允许调用 `scripts/` 目录下的两个脚本

## 文档说明

### SKILL.md
主入口文件，包含：
- 触发条件：何时激活该 Skill
- 任务目标：核心服务质量要求
- 硬规则：不可违反的执行规则
- 执行流程：完整的工具调用流程
- 工具调用速查表

### references/plan.md
问题拆分与执行策略：
- 多意图问题拆分（含"和"、"以及"等连接词）
- 对比类问题拆分（含"对比"、"哪个更好"等关键词）
- 混合信息问题拆分（保险+外部信息）
- 条件依赖问题串行执行
- 执行计划格式（YAML 规范）
- 工具选择决策树

### references/tool.md
工具调用规范：
- `product_answer.py` 调用方式和参数说明
- `web_search.py` 调用方式和参数说明
- 输出格式详解（`answer`, `web_detail`, `web_sumn`）
- 返回值解析规范
- 来源可信度评估标准
- 工具调用组合示例
- 错误处理规范

### references/validation.md
答案质量检查：
- 完整性检查（Completeness）
- 准确性检查（Accuracy）
- 相关性检查（Relevance）
- 一致性检查（Consistency）
- 验证流程和失败类型处理
- 验证输出格式（YAML）

### references/error.md
错误处理策略：
- 工具调用失败（Technical Errors）
- 数据缺失（Data Missing）
- 信息冲突（Conflicts）
- 逻辑不一致（Logical Inconsistency）
- 错误恢复策略矩阵

### references/gotchas.md
关键陷阱清单：
- 🚨 高风险：条款版本混淆、地域限定遗漏、营销话术当条款
- ⚠️ 中风险：费率表误解、保障期限表述、等待期计算
- 通用问答陷阱：过时信息、AI幻觉
- 流程陷阱：错误链式反应、隐私泄露、循环调用

### assets/format.md
输出格式规范：
- 信息来源标记（【内部资料】/【网络信息】）
- 时间戳标注要求
- 纯保险产品问答格式
- 纯通用知识问答格式
- 混合问答格式和信息边界标注
- 信息边界硬规则
- 特殊场景处理话术

## 安全注意事项

1. **参数清理**：两个脚本都实现了输入清理，移除危险字符防止注入攻击
2. **隐私保护**：`web_search.py` 会自动脱敏敏感信息（保单号、身份证号、手机号）
3. **来源验证**：外部搜索结果会标注可信度级别（高/中/低）
4. **重试限制**：工具调用失败时有重试次数限制，避免无限循环

## 扩展开发

### 添加新的保险产品

编辑 `scripts/product_answer.py` 中的 `InsuranceDatabase` 类，添加新的产品数据。

### 接入真实搜索API

编辑 `scripts/web_search.py` 中的 `WebSearchAPI` 类，替换 `search` 方法为真实的搜索API调用（如 Google Custom Search API、Bing Search API 等）。

### 添加新的输出模板

在 `assets/insurance-templates/` 或 `assets/search-templates/` 目录下添加新的 Markdown 模板文件。

## 许可证

MIT License

## 维护者

- 创建日期：2025-03-29
- 版本：v1.0.0

## 参考

- [渐进式披露设计模式](https://mp.weixin.qq.com/s/c42XqFaEeNEhh6DtQgajFw)
- OpenCode Skill 框架规范
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 80.8s)

_Thinking:_

   我看到现有的SKILL.md文件内容比较旧，需要更新为新的设计。根据图片中的工具信息和TODO要求，我需要重新设计这个Skill。让我查看一下references目录下有什么文件。

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references"
}
```

**Output:**
```
<path>/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references</path>
<type>directory</type>
<entries>
error.md
gotchas.md
plan.md
suggestions.md
tool.md
validation.md

(6 entries)
</entries>
[Category+Skill Reminder]

**Built-in**: playwright, frontend-ui-ux, git-master, dev-browser, review-work, ai-slop-remover
**⚡ YOUR SKILLS (PRIORITY)**: gemini-computer-use, skill-creator, Desktop Control, wechat-reply, find-skills

> User-installed skills OVERRIDE built-in defaults. ALWAYS prefer YOUR SKILLS when domain matches.

```typescript
task(category="visual-engineering", load_skills=["gemini-computer-use"], run_in_background=true)
```

```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 144.5s)

_Thinking:_

    现在我看到了现有的结构。让我重新设计这个Skill，基于用户的具体需求：
1. 3个内部保险工具（从图片中获取的详细信息）
2. 1个web_search.py工具
3. 5个子模块：plan、tool、error、uncertain、format

我需要：
1. 更新主SKILL.md
2. 创建/更新references/plan.md
3. 创建/更新references/tool.md（基于图片中的工具信息）
4. 创建/更新references/error.md
5. 创建references/uncertain.md（新增）
6. 创建/更新references/format.md（从assets移到references）

让我逐一更新这些文件。

    现在我看到现有结构。根据您图片中的工具信息和需求，我来重新设计这个Skill。首先更新主SKILL.md：

**Tool: write**

**Input:**
```json
{
  "content": "---\nname: insurance-qa\ndescription: 中国平安保险产品问答专家，处理保险产品知识答疑、销售话术生成、内外部产品对比等需求。使用场景包括：(1)用户询问保险产品保障范围、投保规则、条款解读；(2)销售人员需要产品对比、话术支持；(3)查询具体产品属性、费率、责任详情；(4)内外部保险产品信息对比分析。当用户问题涉及保险产品设计、保障内容、投保条件、销售规则时触发本Skill。\nlicense: Proprietary - Ping An Insurance\n---\n\n# 保险产品问答 Skill\n\n## 任务目标\n\n帮助用户获得准确、完整、专业的保险产品信息，覆盖以下能力：\n- **知识答疑**：产品保障范围、条款解读、投保规则、理赔流程\n- **销售话术**：产品卖点提炼、客户异议处理、场景化推荐\n- **产品对比**：内外部产品责任对比、优劣势分析、适配性建议\n\n## 触发条件\n\n当用户问题涉及以下关键词或场景时，激活本Skill：\n\n| 触发类型 | 关键词/场景示例 |\n|---------|----------------|\n| 产品查询 | \"XX产品保什么\"、\"帮我查下保险\"、\"这个险种包含哪些责任\" |\n| 条款解读 | \"免责条款\"、\"等待期\"、\"免赔额\"、\"赔付比例\" |\n| 投保规则 | \"投保年龄\"、\"健康告知\"、\"保额上限\"、\"缴费期限\" |\n| 销售话术 | \"怎么跟客户说\"、\"卖点是什么\"、\"客户问XX怎么回答\" |\n| 产品对比 | \"和XX比怎么样\"、\"哪个更好\"、\"竞品分析\" |\n| 理赔相关 | \"怎么理赔\"、\"理赔材料\"、\"理赔时效\" |\n\n## 硬规则（必须遵守）\n\n### 1. 问题拆分原则\n\n**必须拆分的情况：**\n- 用户问题包含多个独立子问题（如：\"A产品和B产品哪个好，分别保什么\"）\n- 需要同时查询多个产品信息后进行对比\n- 问题涉及\"对比\"、\"分别\"、\"都\"、\"各\"等关键词\n\n**拆分后处理流程：**\n1. 识别子问题数量和类型\n2. 为每个子问题选择合适的工具\n3. 并行执行独立子问题的工具调用\n4. 合并结果后统一输出\n\n### 2. 工具选择优先级\n\n```\n优先级1（内部资料）: 保险产品内容检索 → 保险产品属性详情 → 产品工具接口\n优先级2（外部补充）: web_search.py（仅当内部资料不足时）\n```\n\n**强制规则：**\n- 必须先尝试内部工具获取信息\n- 外部搜索仅作为产品问答的补充，不用于通用问答\n- 未指定具体产品时，默认优先查询平安保险产品\n\n### 3. 反问触发条件\n\n**必须反问的情况（见 @references/uncertain.md）：**\n- 用户问题未明确保险产品大类（如只说\"帮我查下保险\"）\n- 问题中产品名称模糊或不存在\n- 需要用户确认时间范围、保障额度等关键参数\n- 多个产品同名，需要确认具体版本\n\n### 4. 信息冲突处理\n\n**冲突场景识别：**\n- 不同工具返回的产品信息不一致\n- 内部资料与外部搜索结果矛盾\n- 同一产品的不同版本信息冲突\n\n**处理原则（见 @references/error.md）：**\n- 内部资料优先级高于外部搜索\n- 以最新生效的产品信息为准\n- 记录冲突点并在输出中说明\n\n### 5. 输出格式规范\n\n**必须遵守的格式规则（见 @references/format.md）：**\n- 涉及多款产品：使用表格形式输出对比\n- 回答用户具体问题：先简明扼要回答，再详细展开\n- 引用外部信息：以Markdown格式标注来源网址\n- 涉及内部资料：不添加特殊标识，直接呈现\n\n## 工作流\n\n```\n接收用户问题\n    ↓\n问题是否明确？\n    ├─ 否 → 执行uncertain.md反问模块 → 获取澄清后的问题 → 重新评估\n    ↓\n是\n    ↓\n执行plan.md拆分问题\n    ↓\n是否需要拆分？\n    ├─ 是 → 拆分为多个子问题\n    └─ 否 → 单问题处理\n    ↓\n执行tool.md工具调用\n    ↓\n工具调用成功？\n    ├─ 否 → 执行error.md错误处理 → 是否可重试？\n    │                      ├─ 是 → 重新调用工具\n    │                      └─ 否 → 返回错误说明\n    ↓\n是\n    ↓\n执行format.md格式化输出\n    ↓\n返回最终答案\n```\n\n## 工具概览\n\n| 工具名称 | 脚本路径 | 核心用途 | 调用时机 |\n|---------|---------|---------|---------|\n| 保险产品内容检索 | `scripts/product_content_search.py` | 根据内容类型检索产品列表 | 需要查找产品、了解产品分类时 |\n| 保险产品属性详情 | `scripts/product_attribute_detail.py` | 查询产品具体属性信息 | 需要产品详细信息时 |\n| 产品工具接口 | `scripts/product_tool_interface.py` | 通过MP_CODE查询责任详情 | 需要责任详细信息时 |\n| 网页搜索 | `scripts/web_search.py` | 补充外部产品信息 | 内部资料不足时 |\n\n## 渐进式披露\n\n本Skill采用分层信息架构：\n\n1. **SKILL.md**（本文件）：核心规则和工作流\n2. **@references/plan.md**：问题拆分策略和工具选择逻辑\n3. **@references/tool.md**：工具调用详细说明和参数规范\n4. **@references/error.md**：错误处理和冲突解决机制\n5. **@references/uncertain.md**：反问策略和澄清话术\n6. **@references/format.md**：输出格式规范\n\n按需要加载对应的reference文件。\n\n## 常见坑点（Gotchas）\n\n1. **产品名称歧义**：同一产品可能有多个版本或别名，需要通过产品编码确认\n2. **contentType选择**：不同问题需要选择正确的contentType，错误选择会导致查不到信息\n3. **生效状态过滤**：查询时要关注产品是否处于\"生效\"状态，避免返回已停售产品\n4. **外部信息标识**：使用外部搜索结果时，必须用引用格式标注来源，不可与内部资料混淆\n5. **多产品对比**：对比时要确保字段对齐，避免A产品的A字段对比B产品的B字段\n6. **权限范围**：注意产品的渠道授权、APP授权、机构授权信息，不同渠道可能有不同规则\n\n## 质量检查清单\n\n在返回最终答案前，确认以下检查项：\n\n- [ ] 是否准确理解用户问题，无歧义\n- [ ] 是否选择了正确的工具和参数\n- [ ] 如涉及多款产品，是否使用表格对比\n- [ ] 外部信息是否已标注来源\n- [ ] 回答是否先简明后详细\n- [ ] 是否去除工具调用的思考过程\n- [ ] 未指定产品时是否默认查询平安产品\n- [ ] 信息冲突时是否已按规则处理并说明\n",
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/SKILL.md"
}
```

**Output:**
```
Wrote file successfully.
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 165.2s)

_Thinking:_

     主SKILL.md已更新。现在继续更新各个子模块文件。

     现在更新各个子模块文件。首先是plan.md：

**Tool: write**

**Input:**
```json
{
  "content": "# 计划模块：问题拆分与工具选择\n\n## 问题拆分策略\n\n### 1.1 需要拆分的情况\n\n当用户问题符合以下特征时，必须进行拆分：\n\n| 特征类型 | 具体表现 | 示例 |\n|---------|---------|------|\n| 多产品查询 | 包含多个产品名称 | \"A产品和B产品哪个好\" |\n| 多维度询问 | 询问同一产品的多个方面 | \"XX重疾险的等待期和保额上限是多少\" |\n| 对比类问题 | 包含\"对比\"、\"比较\"、\"vs\"等词 | \"平安福和国寿福有什么区别\" |\n| 多子问题 | 用\"和\"、\"以及\"、\"分别\"连接 | \"A产品保什么，B产品怎么理赔\" |\n| 混合信息 | 同时需要内部资料和外部信息 | \"XX产品的条款和最新监管政策\" |\n\n### 1.2 拆分执行流程\n\n```\n接收问题\n    ↓\n识别问题类型（单产品/多产品/对比/混合）\n    ↓\n提取关键实体（产品名称、属性、时间等）\n    ↓\n拆分为独立子问题\n    ↓\n为每个子问题分配工具\n    ↓\n确定执行顺序（并行/串行）\n    ↓\n生成执行计划\n```\n\n### 1.3 子问题定义规范\n\n每个子问题必须包含以下要素：\n\n```yaml\nsub_problem:\n  id: \"SP001\"                    # 子问题编号\n  type: \"product_query\"          # 问题类型：product_query/attribute_query/tool_query/web_query\n  question: \"查询XX产品的等待期\"  # 具体问题描述\n  tool: \"product_attribute_detail\" # 推荐工具\n  parameters:                    # 工具参数\n    productName: \"XX重疾险\"\n    attributeType: \"产品投保规则\"\n  dependencies: []               # 依赖的其他子问题ID\n  parallelizable: true           # 是否可并行执行\n```\n\n### 1.4 问题类型识别矩阵\n\n| 问题关键词 | 问题类型 | 推荐工具 | 参数要点 |\n|-----------|---------|---------|---------|\n| \"保什么\"、\"保障\"、\"责任\" | 内容检索 | product_content_search | contentType=产品险种列表 |\n| \"条款\"、\"说明书\" | 内容检索 | product_content_search | contentType=产品说明书 |\n| \"投保规则\"、\"年龄\"、\"健康告知\" | 属性查询 | product_attribute_detail | attributeType=产品投保规则 |\n| \"费率\"、\"多少钱\"、\"保费\" | 属性查询 | product_attribute_detail | attributeType=产品基本信息 |\n| \"责任详情\"、\"具体责任\" | 工具接口 | product_tool_interface | mktProdCode + requestFields |\n| \"竞品\"、\"对比\"、\"市场\" | 外部搜索 | web_search | --question |\n\n## 工具选择决策树\n\n```\n用户问题\n    ↓\n是否涉及具体产品？\n    ├─ 否 → 是否需要分类浏览？\n    │          ├─ 是 → product_content_search (contentType=产品险种列表)\n    │          └─ 否 → uncertain.md (反问模块)\n    ↓\n是\n    ↓\n是否知道产品编码？\n    ├─ 是 → product_tool_interface (查责任详情)\n    └─ 否 → 需要查询什么信息？\n               ├─ 产品基本信息 → product_attribute_detail (attributeType=产品基本信息)\n               ├─ 投保规则 → product_attribute_detail (attributeType=产品投保规则)\n               ├─ 产品说明书 → product_content_search (contentType=产品说明书)\n               ├─ 险种列表 → product_content_search (contentType=产品险种列表)\n               └─ 责任详情 → 先product_attribute_detail获取productCode，再product_tool_interface\n```\n\n## 特殊场景处理\n\n### 3.1 对比类问题拆分\n\n**场景**：用户询问\"A产品和B产品哪个更好\"\n\n**拆分方案**：\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询A产品的基本信息和保障责任\"\n    tool: \"product_attribute_detail\"\n    parameters:\n      productName: \"A产品\"\n      attributeType: \"产品基本信息,产品险种列表\"\n  \n  - id: \"SP002\"\n    type: \"product_query\"\n    question: \"查询B产品的基本信息和保障责任\"\n    tool: \"product_attribute_detail\"\n    parameters:\n      productName: \"B产品\"\n      attributeType: \"产品基本信息,产品险种列表\"\n  \n  - id: \"SP003\"\n    type: \"comparison\"\n    question: \"基于SP001和SP002的结果进行对比分析\"\n    tool: \"analysis\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n**执行顺序**：SP001和SP002并行执行 → SP003串行执行\n\n### 3.2 混合信息问题拆分\n\n**场景**：用户询问\"XX重疾险的最新条款和当前市场评价\"\n\n**拆分方案**：\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询XX重疾险的产品说明书\"\n    tool: \"product_content_search\"\n    parameters:\n      productName: \"XX重疾险\"\n      contentType: \"产品说明书\"\n    parallelizable: true\n  \n  - id: \"SP002\"\n    type: \"web_query\"\n    question: \"搜索XX重疾险的市场评价和口碑\"\n    tool: \"web_search\"\n    parameters:\n      question: \"XX重疾险 市场评价 口碑 测评\"\n    parallelizable: true\n  \n  - id: \"SP003\"\n    type: \"synthesis\"\n    question: \"整合内部条款和外部评价\"\n    tool: \"analysis\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n**执行顺序**：SP001和SP002并行执行 → SP003串行执行\n\n### 3.3 条件依赖问题\n\n**场景**：需要先查询A产品信息，再根据结果查询B产品\n\n**处理原则**：\n- 明确标识依赖关系\n- 串行执行依赖链\n- 前置问题失败时，终止后续执行\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询A产品的升级版本\"\n    tool: \"product_attribute_detail\"\n  \n  - id: \"SP002\"\n    type: \"product_query\"\n    question: \"查询A产品升级版的详细责任\"\n    tool: \"product_tool_interface\"\n    dependencies: [\"SP001\"]  # 依赖SP001的结果\n```\n\n## 执行计划生成模板\n\n```yaml\nplan:\n  version: \"1.0\"\n  original_question: \"用户原始问题\"\n  analysis:\n    intent: \"用户意图\"\n    entities:\n      - type: \"product\"\n        value: \"产品名称\"\n      - type: \"attribute\"\n        value: \"属性类型\"\n  sub_problems:\n    - id: \"SP001\"\n      type: \"...\"\n      question: \"...\"\n      tool: \"...\"\n      parameters: {...}\n      dependencies: []\n      parallelizable: true/false\n  execution_order:\n    - phase: 1\n      tasks: [\"SP001\", \"SP002\"]\n      mode: \"parallel\"\n    - phase: 2\n      tasks: [\"SP003\"]\n      mode: \"sequential\"\n  fallback_strategy:\n    - condition: \"工具返回空结果\"\n      action: \"调整参数重试\"\n    - condition: \"信息不足\"\n      action: \"调用web_search补充\"\n```\n\n## 常见错误避免\n\n### 5.1 过度拆分\n\n**错误示例**：将\"XX产品的等待期和免赔额是多少\"拆分为两个子问题\n\n**正确处理**：这是同一产品的不同属性，可以一次查询product_attribute_detail的多个attributeType\n\n### 5.2 遗漏依赖\n\n**错误示例**：对比两个产品时，未识别需要分别查询两个产品信息\n\n**正确处理**：对比类问题必须拆分为至少两个独立的产品查询子问题\n\n### 5.3 工具选择错误\n\n**错误示例**：查询责任详情时直接使用product_attribute_detail\n\n**正确处理**：责任详情需要通过product_tool_interface查询，需要mktProdCode\n\n### 5.4 参数遗漏\n\n**错误示例**：查询产品内容时未指定contentType\n\n**正确处理**：必须根据问题类型选择合适的contentType，否则可能返回不相关信息\n",
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/plan.md"
}
```

**Error:**
```
Error: File already exists. Use edit tool instead.
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 192.2s)

_Thinking:_

      文件已存在，使用edit工具更新。让我读取一下现有的plan.md，然后替换内容。

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/plan.md",
  "newString": "# 计划模块：问题拆分与工具选择\n\n## 问题拆分策略\n\n### 1.1 需要拆分的情况\n\n当用户问题符合以下特征时，必须进行拆分：\n\n| 特征类型 | 具体表现 | 示例 |\n|---------|---------|------|\n| 多产品查询 | 包含多个产品名称 | \"A产品和B产品哪个好\" |\n| 多维度询问 | 询问同一产品的多个方面 | \"XX重疾险的等待期和保额上限是多少\" |\n| 对比类问题 | 包含\"对比\"、\"比较\"、\"vs\"等词 | \"平安福和国寿福有什么区别\" |\n| 多子问题 | 用\"和\"、\"以及\"、\"分别\"连接 | \"A产品保什么，B产品怎么理赔\" |\n| 混合信息 | 同时需要内部资料和外部信息 | \"XX产品的条款和最新监管政策\" |\n\n### 1.2 拆分执行流程\n\n```\n接收问题\n    ↓\n识别问题类型（单产品/多产品/对比/混合）\n    ↓\n提取关键实体（产品名称、属性、时间等）\n    ↓\n拆分为独立子问题\n    ↓\n为每个子问题分配工具\n    ↓\n确定执行顺序（并行/串行）\n    ↓\n生成执行计划\n```\n\n### 1.3 子问题定义规范\n\n每个子问题必须包含以下要素：\n\n```yaml\nsub_problem:\n  id: \"SP001\"                    # 子问题编号\n  type: \"product_query\"          # 问题类型：product_query/attribute_query/tool_query/web_query\n  question: \"查询XX产品的等待期\"  # 具体问题描述\n  tool: \"product_attribute_detail\" # 推荐工具\n  parameters:                    # 工具参数\n    productName: \"XX重疾险\"\n    attributeType: \"产品投保规则\"\n  dependencies: []               # 依赖的其他子问题ID\n  parallelizable: true           # 是否可并行执行\n```\n\n### 1.4 问题类型识别矩阵\n\n| 问题关键词 | 问题类型 | 推荐工具 | 参数要点 |\n|-----------|---------|---------|---------|\n| \"保什么\"、\"保障\"、\"责任\" | 内容检索 | product_content_search | contentType=产品险种列表 |\n| \"条款\"、\"说明书\" | 内容检索 | product_content_search | contentType=产品说明书 |\n| \"投保规则\"、\"年龄\"、\"健康告知\" | 属性查询 | product_attribute_detail | attributeType=产品投保规则 |\n| \"费率\"、\"多少钱\"、\"保费\" | 属性查询 | product_attribute_detail | attributeType=产品基本信息 |\n| \"责任详情\"、\"具体责任\" | 工具接口 | product_tool_interface | mktProdCode + requestFields |\n| \"竞品\"、\"对比\"、\"市场\" | 外部搜索 | web_search | --question |\n\n## 工具选择决策树\n\n```\n用户问题\n    ↓\n是否涉及具体产品？\n    ├─ 否 → 是否需要分类浏览？\n    │          ├─ 是 → product_content_search (contentType=产品险种列表)\n    │          └─ 否 → uncertain.md (反问模块)\n    ↓\n是\n    ↓\n是否知道产品编码？\n    ├─ 是 → product_tool_interface (查责任详情)\n    └─ 否 → 需要查询什么信息？\n               ├─ 产品基本信息 → product_attribute_detail (attributeType=产品基本信息)\n               ├─ 投保规则 → product_attribute_detail (attributeType=产品投保规则)\n               ├─ 产品说明书 → product_content_search (contentType=产品说明书)\n               ├─ 险种列表 → product_content_search (contentType=产品险种列表)\n               └─ 责任详情 → 先product_attribute_detail获取productCode，再product_tool_interface\n```\n\n## 特殊场景处理\n\n### 3.1 对比类问题拆分\n\n**场景**：用户询问\"A产品和B产品哪个更好\"\n\n**拆分方案**：\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询A产品的基本信息和保障责任\"\n    tool: \"product_attribute_detail\"\n    parameters:\n      productName: \"A产品\"\n      attributeType: \"产品基本信息,产品险种列表\"\n  \n  - id: \"SP002\"\n    type: \"product_query\"\n    question: \"查询B产品的基本信息和保障责任\"\n    tool: \"product_attribute_detail\"\n    parameters:\n      productName: \"B产品\"\n      attributeType: \"产品基本信息,产品险种列表\"\n  \n  - id: \"SP003\"\n    type: \"comparison\"\n    question: \"基于SP001和SP002的结果进行对比分析\"\n    tool: \"analysis\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n**执行顺序**：SP001和SP002并行执行 → SP003串行执行\n\n### 3.2 混合信息问题拆分\n\n**场景**：用户询问\"XX重疾险的最新条款和当前市场评价\"\n\n**拆分方案**：\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询XX重疾险的产品说明书\"\n    tool: \"product_content_search\"\n    parameters:\n      productName: \"XX重疾险\"\n      contentType: \"产品说明书\"\n    parallelizable: true\n  \n  - id: \"SP002\"\n    type: \"web_query\"\n    question: \"搜索XX重疾险的市场评价和口碑\"\n    tool: \"web_search\"\n    parameters:\n      question: \"XX重疾险 市场评价 口碑 测评\"\n    parallelizable: true\n  \n  - id: \"SP003\"\n    type: \"synthesis\"\n    question: \"整合内部条款和外部评价\"\n    tool: \"analysis\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n**执行顺序**：SP001和SP002并行执行 → SP003串行执行\n\n### 3.3 条件依赖问题\n\n**场景**：需要先查询A产品信息，再根据结果查询B产品\n\n**处理原则**：\n- 明确标识依赖关系\n- 串行执行依赖链\n- 前置问题失败时，终止后续执行\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询A产品的升级版本\"\n    tool: \"product_attribute_detail\"\n  \n  - id: \"SP002\"\n    type: \"product_query\"\n    question: \"查询A产品升级版的详细责任\"\n    tool: \"product_tool_interface\"\n    dependencies: [\"SP001\"]  # 依赖SP001的结果\n```\n\n## 执行计划生成模板\n\n```yaml\nplan:\n  version: \"1.0\"\n  original_question: \"用户原始问题\"\n  analysis:\n    intent: \"用户意图\"\n    entities:\n      - type: \"product\"\n        value: \"产品名称\"\n      - type: \"attribute\"\n        value: \"属性类型\"\n  sub_problems:\n    - id: \"SP001\"\n      type: \"...\"\n      question: \"...\"\n      tool: \"...\"\n      parameters: {...}\n      dependencies: []\n      parallelizable: true/false\n  execution_order:\n    - phase: 1\n      tasks: [\"SP001\", \"SP002\"]\n      mode: \"parallel\"\n    - phase: 2\n      tasks: [\"SP003\"]\n      mode: \"sequential\"\n  fallback_strategy:\n    - condition: \"工具返回空结果\"\n      action: \"调整参数重试\"\n    - condition: \"信息不足\"\n      action: \"调用web_search补充\"\n```\n\n## 常见错误避免\n\n### 5.1 过度拆分\n\n**错误示例**：将\"XX产品的等待期和免赔额是多少\"拆分为两个子问题\n\n**正确处理**：这是同一产品的不同属性，可以一次查询product_attribute_detail的多个attributeType\n\n### 5.2 遗漏依赖\n\n**错误示例**：对比两个产品时，未识别需要分别查询两个产品信息\n\n**正确处理**：对比类问题必须拆分为至少两个独立的产品查询子问题\n\n### 5.3 工具选择错误\n\n**错误示例**：查询责任详情时直接使用product_attribute_detail\n\n**正确处理**：责任详情需要通过product_tool_interface查询，需要mktProdCode\n\n### 5.4 参数遗漏\n\n**错误示例**：查询产品内容时未指定contentType\n\n**正确处理**：必须根据问题类型选择合适的contentType，否则可能返回不相关信息\n",
  "oldString": "# Plan Module: Problem Decomposition\n\n## 1. Decomposition Strategy\n\n### 1.1 When to Decompose\n\nDecomposition is REQUIRED when the user query matches any of the following patterns:\n\n| Pattern | Examples | Decomposition Required |\n|---------|----------|----------------------|\n| Multiple intentions | \"查询XX保险条款和今天北京天气\" | Yes - Separate insurance and general queries |\n| Comparison requests | \"对比A产品和B产品\" | Yes - Query each product separately |\n| Multi-part questions | \"A产品保障什么，B产品费率多少\" | Yes - Separate product queries |\n| Insurance + external info | \"XX条款和最新监管政策\" | Yes - Internal tool + web search |\n| Conditional dependencies | \"查完A产品后对比B产品\" | Yes - Sequential execution |\n\n### 1.2 Sub-problem Definition\n\nEach sub-problem MUST be:\n- **Atomic**: Cannot be split further without losing meaning\n- **Verifiable**: Has clear success criteria\n- **Tool-mappable**: Maps to exactly one tool invocation\n\n### 1.3 Sub-problem Types\n\n```yaml\nsub_problem_types:\n  insurance_query:\n    description: \"Queries about insurance products, terms, rates\"\n    tool: \"scripts/product_answer.py\"\n    output_fields: [\"answer\"]\n  \n  general_query:\n    description: \"Real-time info: weather, news, policies\"\n    tool: \"scripts/web_search.py\"\n    output_fields: [\"web_detail\", \"web_sumn\"]\n  \n  synthesis:\n    description: \"Combine results from multiple sub-problems\"\n    tool: \"analysis\"\n    input: \"Results from dependent sub-problems\"\n```\n\n## 2. Execution Order Rules\n\n### 2.1 Parallel Execution\n\nSub-problems CAN run in parallel when:\n- No data dependencies between them\n- All are insurance queries OR all are general queries\n- Example: Querying A product and B product simultaneously\n\n### 2.2 Sequential Execution\n\nSub-problems MUST run sequentially when:\n- Later sub-problem depends on earlier results\n- Mixing insurance and general queries (insurance first)\n- Example: \"查询XX条款和最新政策\" → insurance query first, then web search\n\n### 2.3 Execution Plan Format\n\n```yaml\nexecution_plan:\n  original_query: \"用户原始问题\"\n  \n  sub_problems:\n    - id: \"SP001\"\n      type: \"insurance_query\"\n      query: \"XX产品条款内容\"\n      tool: \"scripts/product_answer.py\"\n      params:\n        question: \"XX产品条款\"\n      dependencies: []  # No dependencies\n      \n    - id: \"SP002\"\n      type: \"general_query\"\n      query: \"XX产品相关新闻\"\n      tool: \"scripts/web_search.py\"\n      params:\n        question: \"XX产品 2025年 新闻\"\n      dependencies: []  # Can run in parallel with SP001\n      \n    - id: \"SP003\"\n      type: \"synthesis\"\n      description: \"Combine insurance terms and news\"\n      dependencies: [\"SP001\", \"SP002\"]\n  \n  phases:\n    - phase: 1\n      parallel: true\n      tasks: [\"SP001\", \"SP002\"]\n    - phase: 2\n      parallel: false\n      tasks: [\"SP003\"]\n```\n\n## 3. Decision Tree\n\n```\nUser Query\n    |\n    v\nIs it a compound question?\n    |\n    ├─ No → Single sub-problem\n    |\n    └─ Yes\n         |\n         v\nWhat type of compound?\n    |\n    ├─ Insurance + Insurance\n    │     └─ Parallel execution\n    │\n    ├─ Insurance + General\n    │     └─ Sequential: Insurance first, then General\n    │\n    ├─ General + General\n    │     └─ Parallel execution\n    │\n    └─ Comparison (A vs B)\n          └─ Decompose: Query A, Query B, then Compare\n```\n\n## 4. Example Decompositions\n\n### Example 1: Simple Comparison\n\n**Query**: \"对比平安福和国寿福\"\n\n**Decomposition**:\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"insurance_query\"\n    query: \"平安福产品信息\"\n    tool: \"scripts/product_answer.py\"\n    params: {question: \"平安福保障内容\"}\n    \n  - id: \"SP002\"\n    type: \"insurance_query\"\n    query: \"国寿福产品信息\"\n    tool: \"scripts/product_answer.py\"\n    params: {question: \"国寿福保障内容\"}\n    \n  - id: \"SP003\"\n    type: \"synthesis\"\n    description: \"对比两款产品\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n### Example 2: Insurance + Policy\n\n**Query**: \"XX重疾险条款和2025年监管新规\"\n\n**Decomposition**:\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"insurance_query\"\n    query: \"XX重疾险条款\"\n    tool: \"scripts/product_answer.py\"\n    params: {question: \"XX重疾险条款\"}\n    \n  - id: \"SP002\"\n    type: \"general_query\"\n    query: \"2025年重疾险监管新规\"\n    tool: \"scripts/web_search.py\"\n    params: {question: \"2025年 重疾险 监管新规\"}\n    dependencies: []  # Can parallel, but sequential preferred for clarity\n    \n  - id: \"SP003\"\n    type: \"synthesis\"\n    description: \"整合条款和监管要求\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n### Example 3: Multi-product Attributes\n\n**Query**: \"A产品等待期和B产品免赔额\"\n\n**Decomposition**:\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"insurance_query\"\n    query: \"A产品等待期\"\n    tool: \"scripts/product_answer.py\"\n    params: {question: \"A产品等待期\"}\n    \n  - id: \"SP002\"\n    type: \"insurance_query\"\n    query: \"B产品免赔额\"\n    tool: \"scripts/product_answer.py\"\n    params: {question: \"B产品免赔额\"}\n    \n  - id: \"SP003\"\n    type: \"synthesis\"\n    description: \"汇总两款产品的关键信息\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n## 5. Common Pitfalls\n\n### 5.1 Over-decomposition\n\n**DON'T**: Split \"XX产品等待期和免赔额\" into two sub-problems\n**DO**: Keep as single query - product_answer.py handles multiple attributes\n\n### 5.2 Missing Dependencies\n\n**DON'T**: Mark comparison synthesis with no dependencies\n**DO**: Explicitly list dependent sub-problem IDs\n\n### 5.3 Wrong Tool Selection\n\n**DON'T**: Use web_search for insurance terms queries\n**DO**: Always use product_answer.py for insurance questions first\n\n### 5.4 Parameter Format Errors\n\n**DON'T**: Pass non-string parameters\n**DO**: All parameters must be properly escaped strings\n"
}
```

**Error:**
```
Error: You must read file /Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/plan.md before overwriting it. Use the Read tool first
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 69.6s)

_Thinking:_

        让我先读取plan.md文件。

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/plan.md"
}
```

**Output:**
```
<path>/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/plan.md</path>
<type>file</type>
<content>1: # 计划模块：问题拆分与执行策略
2: 
3: ## 目标
4: 将用户复杂问题拆解为可独立执行的子问题序列，确保每个子问题：
5: - 单一职责（只问一件事）
6: - 工具明确（知道用哪个工具）
7: - 可验证（有明确的成功标准）
8: 
9: ## 拆分策略
10: 
11: ### 类型 1：多意图问题（必须拆分）
12: **识别特征**：包含"和"、"以及"、"顺便"、"还有"等连接词，或同时涉及多个独立主题
13: 
14: 示例：
15: - "我想买重疾险，现在最好的产品是什么，保费多少，怎么理赔"
16:   - 子问题 1：查询当前在售重疾险产品列表（内部工具）
17:   - 子问题 2：获取某具体产品的保费计算（内部工具）
18:   - 子问题 3：查询该产品理赔流程（内部工具）
19: 
20: ### 类型 2：对比类问题（必须拆分）
21: **识别特征**：包含"对比"、"vs"、"哪个更好"、"有什么区别"、"和...相比"等关键词
22: 
23: 示例：
24: - "A产品和B产品哪个保障更全面"
25:   - 子问题 1：查询A产品保障范围（内部工具）
26:   - 子问题 2：查询B产品保障范围（内部工具）
27:   - 子问题 3：（无需工具）基于前两步结果生成对比分析
28: 
29: **注意**：对比类问题禁止直接调用工具问"A和B哪个更好"，因为：
30: 1. 工具可能不支持比较类查询
31: 2. 需要分别获取完整信息后才能客观比较
32: 3. 避免工具返回主观判断而非客观数据
33: 
34: ### 类型 3：混合信息问题（必须拆分）
35: **识别特征**：同时涉及保险专业知识+实时外部信息
36: 
37: 示例：
38: - "最近有什么新的保险政策吗，对我买的XX险有影响吗"
39:   - 子问题 1：搜索最新保险政策新闻（外部搜索）
40:   - 子问题 2：查询XX险现有条款（内部工具）
41:   - 子问题 3：（无需工具）分析政策对条款的潜在影响
42: 
43: **关键原则**：
44: - 保险部分必须用 `product_answer.py`
45: - 外部信息部分必须用 `web_search.py`
46: - 两个子问题必须独立执行，禁止合并为一个查询
47: 
48: ### 类型 4：条件依赖问题（必须串行）
49: **识别特征**：后一个问题依赖前一个问题的答案
50: 
51: 示例：
52: - "30岁男性买50万保额的重疾险多少钱"
53:   - 子问题 1：确认30岁男性可购买的重疾险产品（内部工具）
54:   - 子问题 2：基于上一步返回的产品，查询50万保额保费（内部工具）
55: 
56: **执行要求**：
57: - 必须等待子问题1返回后，提取产品名称
58: - 子问题2的查询词必须包含子问题1返回的具体产品名
59: - 禁止假设产品名称直接执行子问题2
60: 
61: ## 执行计划格式
62: 
63: 每个执行计划必须包含：
64: 
65: ```yaml
66: plan:
67:   original_question: "用户原始问题"
68:   sub_questions:
69:     - id: 1
70:       query: "具体问题描述"
71:       tool: "internal_insurance|web_search|none"
72:       dependency: null| [1]  # 依赖哪些前置子问题
73:       validation_criteria: "如何验证这个答案是否成功"
74:       fallback_action: "失败时如何处理"
75:     
76:     - id: 2
77:       query: "..."
78:       tool: "..."
79:       dependency: [1]
80:       
81:   merge_strategy: "如何合并多个子问题的答案"
82:   risk_flags: ["潜在风险点1", "风险点2"]
83: ```
84: 
85: ## 工具选择决策树
86: 
87: 问题是关于...?
88: ├── 保险条款、产品、费率、理赔、保单查询
89: │   └── → 内部保险工具 (product_answer.py)
90: ├── 实时新闻、天气、政策、市场动态
91: │   └── → 外部搜索工具 (web_search.py)
92: ├── 保险知识+外部信息混合
93: │   └── → 拆分为两个子问题，分别使用对应工具
94: └── 开放式建议（"我应该买什么保险"）
95:     └── → 先内部工具查用户已有保单 → 再外部搜索市场趋势 → 最后综合分析
96: 
97: ## Gotchas（计划阶段常见错误）
98: 
99: 1. **过度拆分**：不要把简单问题拆太碎，增加调用开销
100:    - 错误："XX险的保费是多少"拆成"什么是XX险"+"XX险保费"
101:    - 正确：直接查询XX险保费信息（内部工具支持一次性查询）
102: 
103: 2. **忽视依赖关系**：并行调用有依赖关系的子问题
104:    - 错误：同时问"有哪些重疾险"和"XX重疾险保费多少"
105:    - 正确：先执行1，拿到具体产品名后再执行2
106: 
107: 3. **工具选择错误**：
108:    - 错误：用外部搜索查询具体保单信息（隐私泄露风险）
109:    - 正确：保单信息必须通过内部工具查询
110: 
111: 4. **遗漏验证步骤**：计划中必须包含每个子问题的验证标准

(End of file - total 111 lines)
</content>
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 183.5s)

_Thinking:_

           我已经读取了现有的plan.md。现在我需要更新它以匹配新的工具定义（3个内部工具+1个外部工具）。让我用edit工具更新。

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/plan.md",
  "newString": "# 计划模块：问题拆分与工具选择\n\n## 目标\n将用户复杂问题拆解为可独立执行的子问题序列，确保每个子问题：\n- 单一职责（只问一件事）\n- 工具明确（知道用哪个工具）\n- 可验证（有明确的成功标准）\n\n## 问题拆分策略\n\n### 1.1 需要拆分的情况\n\n当用户问题符合以下特征时，必须进行拆分：\n\n| 特征类型 | 具体表现 | 示例 |\n|---------|---------|------|\n| 多产品查询 | 包含多个产品名称 | \"A产品和B产品哪个好\" |\n| 多维度询问 | 询问同一产品的多个方面 | \"XX重疾险的等待期和保额上限是多少\" |\n| 对比类问题 | 包含\"对比\"、\"比较\"、\"vs\"等词 | \"平安福和国寿福有什么区别\" |\n| 多子问题 | 用\"和\"、\"以及\"、\"分别\"连接 | \"A产品保什么，B产品怎么理赔\" |\n| 混合信息 | 同时需要内部资料和外部信息 | \"XX产品的条款和最新监管政策\" |\n\n### 1.2 拆分执行流程\n\n```\n接收问题\n    ↓\n识别问题类型（单产品/多产品/对比/混合）\n    ↓\n提取关键实体（产品名称、属性、时间等）\n    ↓\n拆分为独立子问题\n    ↓\n为每个子问题分配工具\n    ↓\n确定执行顺序（并行/串行）\n    ↓\n生成执行计划\n```\n\n### 1.3 子问题定义规范\n\n每个子问题必须包含以下要素：\n\n```yaml\nsub_problem:\n  id: \"SP001\"                    # 子问题编号\n  type: \"product_query\"          # 问题类型：product_query/attribute_query/tool_query/web_query\n  question: \"查询XX产品的等待期\"  # 具体问题描述\n  tool: \"product_attribute_detail\" # 推荐工具\n  parameters:                    # 工具参数\n    productName: \"XX重疾险\"\n    attributeType: \"产品投保规则\"\n  dependencies: []               # 依赖的其他子问题ID\n  parallelizable: true           # 是否可并行执行\n```\n\n### 1.4 问题类型识别矩阵\n\n| 问题关键词 | 问题类型 | 推荐工具 | 参数要点 |\n|-----------|---------|---------|---------|\n| \"保什么\"、\"保障\"、\"责任\" | 内容检索 | product_content_search | contentType=产品险种列表 |\n| \"条款\"、\"说明书\" | 内容检索 | product_content_search | contentType=产品说明书 |\n| \"投保规则\"、\"年龄\"、\"健康告知\" | 属性查询 | product_attribute_detail | attributeType=产品投保规则 |\n| \"费率\"、\"多少钱\"、\"保费\" | 属性查询 | product_attribute_detail | attributeType=产品基本信息 |\n| \"责任详情\"、\"具体责任\" | 工具接口 | product_tool_interface | mktProdCode + requestFields |\n| \"竞品\"、\"对比\"、\"市场\" | 外部搜索 | web_search | --question |\n\n## 工具选择决策树\n\n```\n用户问题\n    ↓\n是否涉及具体产品？\n    ├─ 否 → 是否需要分类浏览？\n    │          ├─ 是 → product_content_search (contentType=产品险种列表)\n    │          └─ 否 → uncertain.md (反问模块)\n    ↓\n是\n    ↓\n是否知道产品编码？\n    ├─ 是 → product_tool_interface (查责任详情)\n    └─ 否 → 需要查询什么信息？\n               ├─ 产品基本信息 → product_attribute_detail (attributeType=产品基本信息)\n               ├─ 投保规则 → product_attribute_detail (attributeType=产品投保规则)\n               ├─ 产品说明书 → product_content_search (contentType=产品说明书)\n               ├─ 险种列表 → product_content_search (contentType=产品险种列表)\n               └─ 责任详情 → 先product_attribute_detail获取productCode，再product_tool_interface\n```\n\n## 特殊场景处理\n\n### 3.1 对比类问题拆分\n\n**场景**：用户询问\"A产品和B产品哪个更好\"\n\n**拆分方案**：\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询A产品的基本信息和保障责任\"\n    tool: \"product_attribute_detail\"\n    parameters:\n      productName: \"A产品\"\n      attributeType: \"产品基本信息,产品险种列表\"\n  \n  - id: \"SP002\"\n    type: \"product_query\"\n    question: \"查询B产品的基本信息和保障责任\"\n    tool: \"product_attribute_detail\"\n    parameters:\n      productName: \"B产品\"\n      attributeType: \"产品基本信息,产品险种列表\"\n  \n  - id: \"SP003\"\n    type: \"comparison\"\n    question: \"基于SP001和SP002的结果进行对比分析\"\n    tool: \"analysis\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n**执行顺序**：SP001和SP002并行执行 → SP003串行执行\n\n### 3.2 混合信息问题拆分\n\n**场景**：用户询问\"XX重疾险的最新条款和当前市场评价\"\n\n**拆分方案**：\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询XX重疾险的产品说明书\"\n    tool: \"product_content_search\"\n    parameters:\n      productName: \"XX重疾险\"\n      contentType: \"产品说明书\"\n    parallelizable: true\n  \n  - id: \"SP002\"\n    type: \"web_query\"\n    question: \"搜索XX重疾险的市场评价和口碑\"\n    tool: \"web_search\"\n    parameters:\n      question: \"XX重疾险 市场评价 口碑 测评\"\n    parallelizable: true\n  \n  - id: \"SP003\"\n    type: \"synthesis\"\n    question: \"整合内部条款和外部评价\"\n    tool: \"analysis\"\n    dependencies: [\"SP001\", \"SP002\"]\n```\n\n**执行顺序**：SP001和SP002并行执行 → SP003串行执行\n\n### 3.3 条件依赖问题\n\n**场景**：需要先查询A产品信息，再根据结果查询B产品\n\n**处理原则**：\n- 明确标识依赖关系\n- 串行执行依赖链\n- 前置问题失败时，终止后续执行\n\n```yaml\nsub_problems:\n  - id: \"SP001\"\n    type: \"product_query\"\n    question: \"查询A产品的升级版本\"\n    tool: \"product_attribute_detail\"\n  \n  - id: \"SP002\"\n    type: \"product_query\"\n    question: \"查询A产品升级版的详细责任\"\n    tool: \"product_tool_interface\"\n    dependencies: [\"SP001\"]  # 依赖SP001的结果\n```\n\n## 执行计划生成模板\n\n```yaml\nplan:\n  version: \"1.0\"\n  original_question: \"用户原始问题\"\n  analysis:\n    intent: \"用户意图\"\n    entities:\n      - type: \"product\"\n        value: \"产品名称\"\n      - type: \"attribute\"\n        value: \"属性类型\"\n  sub_problems:\n    - id: \"SP001\"\n      type: \"...\"\n      question: \"...\"\n      tool: \"...\"\n      parameters: {...}\n      dependencies: []\n      parallelizable: true/false\n  execution_order:\n    - phase: 1\n      tasks: [\"SP001\", \"SP002\"]\n      mode: \"parallel\"\n    - phase: 2\n      tasks: [\"SP003\"]\n      mode: \"sequential\"\n  fallback_strategy:\n    - condition: \"工具返回空结果\"\n      action: \"调整参数重试\"\n    - condition: \"信息不足\"\n      action: \"调用web_search补充\"\n```\n\n## 常见错误避免\n\n### 5.1 过度拆分\n\n**错误示例**：将\"XX产品的等待期和免赔额是多少\"拆分为两个子问题\n\n**正确处理**：这是同一产品的不同属性，可以一次查询product_attribute_detail的多个attributeType\n\n### 5.2 遗漏依赖\n\n**错误示例**：对比两个产品时，未识别需要分别查询两个产品信息\n\n**正确处理**：对比类问题必须拆分为至少两个独立的产品查询子问题\n\n### 5.3 工具选择错误\n\n**错误示例**：查询责任详情时直接使用product_attribute_detail\n\n**正确处理**：责任详情需要通过product_tool_interface查询，需要mktProdCode\n\n### 5.4 参数遗漏\n\n**错误示例**：查询产品内容时未指定contentType\n\n**正确处理**：必须根据问题类型选择合适的contentType，否则可能返回不相关信息\n",
  "oldString": "# 计划模块：问题拆分与执行策略\n\n## 目标\n将用户复杂问题拆解为可独立执行的子问题序列，确保每个子问题：\n- 单一职责（只问一件事）\n- 工具明确（知道用哪个工具）\n- 可验证（有明确的成功标准）\n\n## 拆分策略\n\n### 类型 1：多意图问题（必须拆分）\n**识别特征**：包含\"和\"、\"以及\"、\"顺便\"、\"还有\"等连接词，或同时涉及多个独立主题\n\n示例：\n- \"我想买重疾险，现在最好的产品是什么，保费多少，怎么理赔\"\n  - 子问题 1：查询当前在售重疾险产品列表（内部工具）\n  - 子问题 2：获取某具体产品的保费计算（内部工具）\n  - 子问题 3：查询该产品理赔流程（内部工具）\n\n### 类型 2：对比类问题（必须拆分）\n**识别特征**：包含\"对比\"、\"vs\"、\"哪个更好\"、\"有什么区别\"、\"和...相比\"等关键词\n\n示例：\n- \"A产品和B产品哪个保障更全面\"\n  - 子问题 1：查询A产品保障范围（内部工具）\n  - 子问题 2：查询B产品保障范围（内部工具）\n  - 子问题 3：（无需工具）基于前两步结果生成对比分析\n\n**注意**：对比类问题禁止直接调用工具问\"A和B哪个更好\"，因为：\n1. 工具可能不支持比较类查询\n2. 需要分别获取完整信息后才能客观比较\n3. 避免工具返回主观判断而非客观数据\n\n### 类型 3：混合信息问题（必须拆分）\n**识别特征**：同时涉及保险专业知识+实时外部信息\n\n示例：\n- \"最近有什么新的保险政策吗，对我买的XX险有影响吗\"\n  - 子问题 1：搜索最新保险政策新闻（外部搜索）\n  - 子问题 2：查询XX险现有条款（内部工具）\n  - 子问题 3：（无需工具）分析政策对条款的潜在影响\n\n**关键原则**：\n- 保险部分必须用 `product_answer.py`\n- 外部信息部分必须用 `web_search.py`\n- 两个子问题必须独立执行，禁止合并为一个查询\n\n### 类型 4：条件依赖问题（必须串行）\n**识别特征**：后一个问题依赖前一个问题的答案\n\n示例：\n- \"30岁男性买50万保额的重疾险多少钱\"\n  - 子问题 1：确认30岁男性可购买的重疾险产品（内部工具）\n  - 子问题 2：基于上一步返回的产品，查询50万保额保费（内部工具）\n\n**执行要求**：\n- 必须等待子问题1返回后，提取产品名称\n- 子问题2的查询词必须包含子问题1返回的具体产品名\n- 禁止假设产品名称直接执行子问题2\n\n## 执行计划格式\n\n每个执行计划必须包含：\n\n```yaml\nplan:\n  original_question: \"用户原始问题\"\n  sub_questions:\n    - id: 1\n      query: \"具体问题描述\"\n      tool: \"internal_insurance|web_search|none\"\n      dependency: null| [1]  # 依赖哪些前置子问题\n      validation_criteria: \"如何验证这个答案是否成功\"\n      fallback_action: \"失败时如何处理\"\n    \n    - id: 2\n      query: \"...\"\n      tool: \"...\"\n      dependency: [1]\n      \n  merge_strategy: \"如何合并多个子问题的答案\"\n  risk_flags: [\"潜在风险点1\", \"风险点2\"]\n```\n\n## 工具选择决策树\n\n问题是关于...?\n├── 保险条款、产品、费率、理赔、保单查询\n│   └── → 内部保险工具 (product_answer.py)\n├── 实时新闻、天气、政策、市场动态\n│   └── → 外部搜索工具 (web_search.py)\n├── 保险知识+外部信息混合\n│   └── → 拆分为两个子问题，分别使用对应工具\n└── 开放式建议（\"我应该买什么保险\"）\n    └── → 先内部工具查用户已有保单 → 再外部搜索市场趋势 → 最后综合分析\n\n## Gotchas（计划阶段常见错误）\n\n1. **过度拆分**：不要把简单问题拆太碎，增加调用开销\n   - 错误：\"XX险的保费是多少\"拆成\"什么是XX险\"+\"XX险保费\"\n   - 正确：直接查询XX险保费信息（内部工具支持一次性查询）\n\n2. **忽视依赖关系**：并行调用有依赖关系的子问题\n   - 错误：同时问\"有哪些重疾险\"和\"XX重疾险保费多少\"\n   - 正确：先执行1，拿到具体产品名后再执行2\n\n3. **工具选择错误**：\n   - 错误：用外部搜索查询具体保单信息（隐私泄露风险）\n   - 正确：保单信息必须通过内部工具查询\n\n4. **遗漏验证步骤**：计划中必须包含每个子问题的验证标准"
}
```

**Output:**
```
Edit applied successfully.
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 79.2s)

_Thinking:_

               plan.md已更新。现在继续更新tool.md。

               继续更新tool.md：

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/tool.md"
}
```

**Output:**
```
<path>/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/tool.md</path>
<type>file</type>
<content>1: # 工具调用规范（Tool Specification）
2: 
3: ## 目标
4: 明确两个核心脚本的调用方式、参数格式、输出解析和错误处理，确保 Agent 能正确执行工具调用并处理返回结果。
5: 
6: ---
7: 
8: ## 工具 1：内部保险问答工具
9: 
10: ### 基本信息
11: - **脚本路径**：`scripts/product_answer.py`
12: - **功能**：查询内部保险产品数据库，获取条款、费率、理赔规则等官方信息
13: - **适用场景**：所有涉及具体保险产品、保单、条款、费率的问题
14: 
15: ### 调用方式
16: 
17: ```bash
18: python scripts/product_answer.py --question "<保险问题>"
19: ```
20: 
21: ### 参数说明
22: 
23: | 参数 | 类型 | 必填 | 说明 | 示例 |
24: |-----|------|------|------|------|
25: | `--question` | str | 是 | 标准化的保险问题描述 | `"重疾险等待期是多少天"` |
26: 
27: **参数构建规则**：
28: - 必须保留用户问题的关键要素（产品名、年龄、保额等）
29: - 去除与保险查询无关的寒暄（如"请问一下"、"麻烦你"）
30: - 如涉及具体保单，确保保单号已脱敏（只保留后4位或完全去除）
31: 
32: ### 输出格式
33: 
34: **标准输出（stdout）**：
35: - 字段名：`answer`
36: - 类型：`str`
37: - 内容：关于保险问题的文本答案（可能包含结构化数据如表格）
38: 
39: **成功返回示例**：
40: ```
41: 根据《XX终身寿险（2024版）》条款第3.2条：
42: 
43: 等待期：自合同生效日起 90 天（等待期内非意外身故退还已交保费）
44: 
45: 费率示例（标准体，10万保额）：
46: - 30岁男性：年缴 2,500 元
47: - 30岁女性：年缴 2,300 元
48: 
49: 注：最终费率以核保结果为准。
50: ```
51: 
52: **空结果返回示例**：
53: ```
54: 未找到与"XX超级保险"相关的产品信息。可能原因：
55: 1. 产品名称不准确
56: 2. 该产品已停售
57: 3. 暂无此产品数据
58: ```
59: 
60: **错误返回示例**：
61: ```
62: [ERROR] 数据库连接超时，请稍后重试
63: [ERROR] 查询参数异常：年龄超出范围（0-100）
64: ```
65: 
66: ### 返回值解析规范
67: 
68: 1. **检查是否以 `[ERROR]` 开头**：
69:    - 是 → 进入 error.md 处理流程
70:    - 否 → 继续下一步
71: 
72: 2. **检查是否包含关键信息**：
73:    - 若包含"未找到"、"不存在"、"无此产品" → 标记为 DATA_MISSING
74:    - 若包含具体条款、费率、日期 → 标记为 SUCCESS
75: 
76: 3. **提取结构化数据**（如有）：
77:    - 使用正则或字符串处理提取数值（保费、保额、天数等）
78:    - 保留原始文本用于后续输出
79: 
80: ---
81: 
82: ## 工具 2：外部网页搜索工具
83: 
84: ### 基本信息
85: - **脚本路径**：`scripts/web_search.py`
86: - **功能**：执行网络搜索，获取实时新闻、政策、市场动态等外部信息
87: - **适用场景**：天气、新闻、政策变动、市场分析、第三方评价等
88: 
89: ### 调用方式
90: 
91: ```bash
92: python scripts/web_search.py --question "<搜索问题>"
93: ```
94: 
95: ### 参数说明
96: 
97: | 参数 | 类型 | 必填 | 说明 | 示例 |
98: |-----|------|------|------|------|
99: | `--question` | str | 是 | 搜索查询词 | `"2025年3月保险监管新政策"` |
100: 
101: **参数构建规则**：
102: - 保留关键时间、地点、主体（如"2025年3月"、"北京"、"银保监会"）
103: - 去除保险敏感信息（保单号、身份证号、详细个人信息）
104: - 对于比较类问题，确保查询词中立（如"重疾险和医疗险区别"而非"重疾险是不是骗局"）
105: 
106: ### 输出格式
107: 
108: **标准输出（stdout）包含两个部分**：
109: 
110: #### 1. web_detail（原始网页详情）
111: - 类型：`List[str]`
112: - 内容：前3个相关网页的详细内容片段（原始文本）
113: - 用途：验证 `web_sumn` 的准确性，提供详细引用来源
114: 
115: **格式示例**：
116: ```python
117: [
118:   "网页1标题：2025年保险监管新规出台\nURL：xxx\n内容：银保监会今日发布...",
119:   "网页2标题：解读最新保险政策\nURL：xxx\n内容：专家分析认为...",
120:   "网页3标题：保险市场动态\nURL：xxx\n内容：根据最新数据..."
121: ]
122: ```
123: 
124: #### 2. web_sumn（内容总结）
125: - 类型：`str`
126: - 内容：基于搜索结果的总结性回答
127: - 用途：直接作为主要参考内容呈现给用户
128: 
129: **格式示例**：
130: ```
131: 根据搜索结果，2025年3月保险监管主要新政策包括：
132: 
133: 1. 重疾险定义更新：扩大轻症保障范围...
134: 2. 互联网保险新规：要求明确披露...
135: 3. 代理人管理：加强资质审核...
136: 
137: 信息来源：银保监会官网、新华网等
138: ```
139: 
140: ### 返回值解析规范
141: 
142: 1. **解析输出**：将 stdout 解析为 Python 对象（假设为 JSON 或特定分隔格式）
143:    
144:    **假设返回格式为 JSON**：
145:    ```json
146:    {
147:      "web_detail": ["...", "...", "..."],
148:      "web_sumn": "..."
149:    }
150:    ```
151: 
152: 2. **检查 `web_sumn` 内容**：
153:    - 如果为 `""` 或 `"未找到相关信息"` → 标记为 NO_DATA
154:    - 如果包含内容 → 标记为 SUCCESS
155: 
156: 3. **检查 `web_detail` 长度**：
157:    - 正常情况下包含 1-3 个页面详情
158:    - 如果为空列表 `[]` → 说明搜索无结果
159: 
160: 4. **提取来源信息**：
161:    - 从 `web_detail` 中提取 URL 域名和标题，用于标注来源
162: 
163: ### 来源可信度评估（用于验证模块）
164: 
165: 基于 `web_detail` 中的 URL 进行可信度分级：
166: 
167: | 级别 | 域名特征 | 可信度 | 使用建议 |
168: |-----|---------|--------|---------|
169: | 高 | `.gov.cn`, `cbirc.gov.cn`, 保险公司官网 | 高 | 优先采信，可用于验证保险政策 |
170: | 中 | 主流新闻站 (`sina.com`, `qq.com` 等) | 中 | 可使用，但需交叉验证 |
171: | 低 | 论坛、博客、自媒体 | 低 | 仅作参考，不得用于保险条款依据 |
172: 
173: ---
174: 
175: ## 工具调用组合示例
176: 
177: ### 场景 1：纯保险问题（仅 product_answer.py）
178: 
179: **用户问题**："30岁男性买你们公司重疾险50万保额，年缴多少钱？"
180: 
181: **执行步骤**：
182: ```bash
183: # 步骤 1：调用内部工具
184: python scripts/product_answer.py --question "30岁男性重疾险50万保额年缴保费"
185: ```
186: 
187: **接收返回**：
188: - `answer`: "XX重疾险（2024版），30岁男性，50万保额，年缴保费 8,500.00 元（标准体）..."
189: 
190: **验证**：包含具体数值、产品版本 → SUCCESS
191: 
192: **格式化输出**：
193: ```
194: 【内部资料】根据查询结果：
195: 
196: 产品：XX重疾险（2024版）
197: - 被保人：30岁男性
198: - 保额：500,000 元
199: - 年缴保费：¥8,500.00（标准体费率）
200: 
201: *注：最终保费以实际核保结果为准，可能因健康状况调整。*
202: ```
203: 
204: ---
205: 
206: ### 场景 2：纯外部搜索（仅 web_search.py）
207: 
208: **用户问题**："今天北京天气怎么样？"
209: 
210: **执行步骤**：
211: ```bash
212: python scripts/web_search.py --question "北京今天天气 2025-03-28"
213: ```
214: 
215: **接收返回**：
216: - `web_sumn`: "北京今日晴，气温 15-25°C，北风 3 级..."
217: - `web_detail`: ["网页1...", "网页2..."]
218: 
219: **格式化输出**：
220: ```
221: 【网络信息，仅供参考，2025-03-28】
222: 
223: 北京今日天气：晴朗
224: - 气温：15°C ~ 25°C
225: - 风向：北风 3 级
226: - 空气质量：良
227: 
228: *来源：中国天气网、新浪天气*
229: ```
230: 
231: ---
232: 
233: ### 场景 3：混合查询（先 product_answer.py，后 web_search.py）
234: 
235: **用户问题**："我买的XX重疾险最近有什么新政策影响吗？"
236: 
237: **执行步骤 1**：
238: ```bash
239: python scripts/product_answer.py --question "XX重疾险产品条款简介"
240: ```
241: 
242: **返回 1**：
243: - `answer`: "XX重疾险（2023版），保障范围包括..."
244: 
245: **执行步骤 2**（基于步骤 1 确认的产品名）：
246: ```bash
247: python scripts/web_search.py --question "2025年3月 XX重疾险 监管政策 新规"
248: ```
249: 
250: **返回 2**：
251: - `web_sumn`: "近期监管发布重疾险新规，要求...（不涉及2023版条款调整）"
252: - `web_detail`: ["...", "..."]
253: 
254: **合并输出**：
255: ```
256: 【内部资料】您的保单信息：
257: 产品：XX重疾险（2023版）
258: 保障范围：...
259: 条款状态：正常有效
260: 
261: ---
262: 
263: 【网络信息，2025-03-28，仅供参考】
264: 近期监管动态：
265: 2025年3月发布的新规主要针对新备案的重疾险产品，要求扩大轻症保障范围。
266: 经比对，该政策不影响您持有的2023版保单条款。
267: 
268: *来源：银保监会官网、保险业协会*
269: ```
270: 
271: ---
272: 
273: ## 错误处理规范
274: 
275: ### product_answer.py 常见错误
276: 
277: | 错误标识 | 含义 | 处理建议 |
278: |---------|------|---------|
279: | `[ERROR] 数据库连接超时` | 服务暂时不可用 | 重试1次，仍失败则提示用户稍后重试 |
280: | `[ERROR] 查询参数异常` | 输入参数格式错误 | 检查 question 参数，修正后重试 |
281: | `[ERROR] 产品不存在` | 无此保险产品 | 尝试模糊查询或询问用户是否记错名称 |
282: | `未找到...` | 空结果 | 按 DATA_MISSING 处理，提供替代方案 |
283: 
284: ### web_search.py 常见错误
285: 
286: | 错误标识 | 含义 | 处理建议 |
287: |---------|------|---------|
288: | 返回空 JSON | 搜索服务异常 | 重试1次，仍失败则告知无法获取外部信息 |
289: | `web_sumn` 为空字符串 | 无搜索结果 | 尝试简化查询词再次搜索 |
290: | `web_detail` 全为低可信度来源 | 缺乏权威信息 | 标注"暂无权威来源信息"，建议用户咨询官方 |
291: 
292: ---
293: 
294: ## 性能与限制
295: 
296: - **超时设置**：两个脚本均应在 10 秒内返回，超时视为失败
297: - **字符限制**：`answer` 和 `web_sumn` 通常不超过 2000 字，超长内容可能被截断
298: - **频率限制**：
299:   - `product_answer.py`：无严格限制，但避免无意义重复查询
300:   - `web_search.py`：注意外部 API 限流，同一问题禁止重复搜索超过 2 次
301: - **并发限制**：禁止同时调用两个脚本（避免上下文混乱）
302: 
303: ---
304: 
305: ## Gotchas（工具调用陷阱）
306: 
307: 1. **参数注入风险**：
308:    - 陷阱：用户问题包含 `" ; rm -rf /"` 等恶意代码
309:    - 防护：必须对 `question` 参数进行转义或 sanitization，禁止直接拼接 shell 命令
310: 
311: 2. **编码问题**：
312:    - 陷阱：中文参数在命令行传输中出现乱码
313:    - 防护：确保使用 UTF-8 编码，必要时使用 base64 编码传输
314: 
315: 3. **输出解析失败**：
316:    - 陷阱：假设返回是 JSON 但实际是纯文本，导致解析报错
317:    - 防护：先检查输出格式，使用 try-except 包裹解析逻辑
318: 
319: 4. **混淆两个工具的输出**：
320:    - 陷阱：将 `web_search.py` 返回的保险营销文章当作 `product_answer.py` 的官方条款
321:    - 防护：严格区分 `answer` 和 `web_sumn` 的使用场景，不同来源必须标注
322: 
323: 5. **忽视 web_detail**：
324:    - 陷阱：只看 `web_sumn` 总结，不看 `web_detail` 原文，导致来源不明
325:    - 防护：验证模块必须检查 `web_detail` 中的 URL 来源可信度

(End of file - total 325 lines)
</content>
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 272.1s)

_Thinking:_

                现在更新tool.md以反映图片中的3个内部工具+web_search。

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/tool.md",
  "newString": "# 工具调用规范（Tool Specification）\n\n## 目标\n明确4个核心脚本的调用方式、参数格式、输出解析和错误处理，确保 Agent 能正确执行工具调用并处理返回结果。\n\n---\n\n## 工具概览\n\n| 工具名称 | 脚本路径 | 核心功能 | 优先级 |\n|---------|---------|---------|--------|\n| 保险产品内容检索 | `scripts/product_content_search.py` | 根据内容类型检索产品列表 | 高 |\n| 保险产品属性详情 | `scripts/product_attribute_detail.py` | 查询产品具体属性信息 | 高 |\n| 产品工具接口 | `scripts/product_tool_interface.py` | 通过MP_CODE查询责任详情 | 高 |\n| 网页搜索 | `scripts/web_search.py` | 补充外部产品信息 | 低（仅内部资料不足时使用）|\n\n---\n\n## 工具 1：保险产品内容检索\n\n### 基本信息\n- **脚本路径**：`scripts/product_content_search.py`\n- **功能**：根据产品内容检索保险产品，支持按内容类型、状态、类别筛选\n- **适用场景**：查找产品列表、了解产品分类、查询产品说明书/险种列表\n\n### 调用方式\n\n```bash\npython scripts/product_content_search.py \\\n  --productContent \"产品内容\" \\\n  --contentType \"内容类型\" \\\n  --effectiveState \"生效/失效\" \\\n  --productCategory \"产品目录\" \\\n  --productType \"产品类别\" \\\n  --topK 3\n```\n\n### 参数说明\n\n| 参数 | 类型 | 必填 | 说明 | 示例 |\n|-----|------|------|------|------|\n| `--productContent` | str | 否 | 产品内容关键词 | `\"重疾险\"` |\n| `--contentType` | str | 否 | 内容类型，默认空（全部类型） | `\"产品说明书\"` |\n| `--effectiveState` | str | 否 | 产品状态：生效/失效 | `\"生效\"` |\n| `--productCategory` | str | 否 | 产品目录/知识库目录 | `\"健康险\"` |\n| `--productType` | str | 否 | 产品类别：标准产品/自选产品/不可销售产品 | `\"标准产品\"` |\n| `--productName` | str | 否 | 产品名称，支持模糊搜索 | `\"平安福\"` |\n| `--productCode` | str | 否 | 产品编码，精准匹配 | `\"PA0001\"` |\n| `--topK` | int | 否 | 返回产品个数，默认3 | `5` |\n\n**contentType可选值**：\n- `产品基本信息` - 查询产品基本资料\n- `产品投保规则` - 查询投保条件、年龄限制等\n- `产品说明书` - 查询完整产品条款\n- `产品险种列表` - 查询产品包含的险种\n- `产品套餐列表` - 查询套餐组合信息\n- `渠道授权列表` - 查询销售渠道授权\n- `APP授权列表` - 查询APP销售授权\n- `机构授权列表` - 查询机构销售授权\n\n### 输出格式\n\n**成功返回示例**：\n```json\n{\n  \"products\": [\n    {\n      \"productCode\": \"PA0001\",\n      \"productName\": \"平安福重疾险\",\n      \"productCategory\": \"健康险\",\n      \"effectiveState\": \"生效\",\n      \"contentType\": \"产品说明书\",\n      \"content\": \"产品说明书内容摘要...\"\n    }\n  ],\n  \"total\": 1\n}\n```\n\n### 使用场景示例\n\n**场景1：查询某产品的说明书**\n```bash\npython scripts/product_content_search.py \\\n  --productName \"平安福\" \\\n  --contentType \"产品说明书\" \\\n  --effectiveState \"生效\"\n```\n\n**场景2：浏览某类产品列表**\n```bash\npython scripts/product_content_search.py \\\n  --productCategory \"健康险\" \\\n  --contentType \"产品险种列表\" \\\n  --topK 10\n```\n\n---\n\n## 工具 2：保险产品属性详情\n\n### 基本信息\n- **脚本路径**：`scripts/product_attribute_detail.py`\n- **功能**：根据产品编码或产品名称，返回产品基础信息、投保规则、产品说明书、险种列表等\n- **适用场景**：查询特定产品的详细信息、投保条件、费率等\n\n### 调用方式\n\n```bash\npython scripts/product_attribute_detail.py \\\n  --productName \"产品名称\" \\\n  --productCode \"产品编码\" \\\n  --attributeType \"属性类型\"\n```\n\n### 参数说明\n\n| 参数 | 类型 | 必填 | 说明 | 示例 |\n|-----|------|------|------|------|\n| `--productName` | str | 否 | 产品名称，支持模糊搜索 | `\"平安福\"` |\n| `--productCode` | str | 否 | 产品编码，精准匹配，支持单个或多个 | `\"PA0001\"` |\n| `--attributeType` | str | 否 | 属性类型，支持多个用逗号分隔 | `\"产品基本信息,产品投保规则\"` |\n\n**attributeType可选值**（与contentType相同）：\n- `产品基本信息` - 产品名称、编码、类别、状态等\n- `产品投保规则` - 投保年龄、健康告知、保额限制等\n- `产品说明书` - 完整条款内容\n- `产品险种列表` - 包含的险种及责任\n- `产品套餐列表` - 套餐组合及价格\n- `APP授权列表` - 线上销售渠道授权\n- `机构授权列表` - 线下机构销售授权\n- `渠道授权列表` - 全渠道授权信息\n\n**注意**：`productName`和`productCode`至少填一个\n\n### 输出格式\n\n**成功返回示例**：\n```json\n{\n  \"productCode\": \"PA0001\",\n  \"productName\": \"平安福重疾险\",\n  \"attributes\": {\n    \"产品基本信息\": {\n      \"产品类别\": \"健康险\",\n      \"投保年龄\": \"18-55周岁\",\n      \"保障期限\": \"终身\",\n      \"缴费方式\": \"年缴/趸交\"\n    },\n    \"产品投保规则\": {\n      \"最低保额\": \"10万元\",\n      \"最高保额\": \"100万元\",\n      \"等待期\": \"90天\",\n      \"健康告知\": \"需如实告知\"\n    }\n  }\n}\n```\n\n### 使用场景示例\n\n**场景1：查询产品投保规则**\n```bash\npython scripts/product_attribute_detail.py \\\n  --productName \"平安福\" \\\n  --attributeType \"产品投保规则\"\n```\n\n**场景2：同时查询多个属性**\n```bash\npython scripts/product_attribute_detail.py \\\n  --productCode \"PA0001\" \\\n  --attributeType \"产品基本信息,产品投保规则,产品险种列表\"\n```\n\n---\n\n## 工具 3：产品工具接口\n\n### 基本信息\n- **脚本路径**：`scripts/product_tool_interface.py`\n- **功能**：通过MP_CODE查询关于责任更详细的信息，支持指定查询字段\n- **适用场景**：需要查询产品责任详情、特定字段信息时\n\n### 调用方式\n\n```bash\npython scripts/product_tool_interface.py \\\n  --mktProdCode \"产品编码\" \\\n  --requestFields \"查询字段\"\n```\n\n### 参数说明\n\n| 参数 | 类型 | 必填 | 说明 | 示例 |\n|-----|------|------|------|------|\n| `--mktProdCode` | str | 是 | 产品编码（MP_CODE） | `\"PA0001\"` |\n| `--requestFields` | str | 否 | 查询的表格和字段，多个用逗号分隔 | `\"责任详情,费率表\"` |\n\n### 输出格式\n\n**成功返回示例**：\n```json\n{\n  \"mktProdCode\": \"PA0001\",\n  \"productName\": \"平安福重疾险\",\n  \"responsibilities\": [\n    {\n      \"责任代码\": \"RESP001\",\n      \"责任名称\": \"重大疾病保险金\",\n      \"责任描述\": \"被保险人初次发生合同约定的重大疾病...\",\n      \"赔付比例\": \"100%\",\n      \"等待期\": \"90天\"\n    }\n  ],\n  \"fields\": {\n    \"费率表\": {...},\n    \"免责条款\": {...}\n  }\n}\n```\n\n### 使用场景示例\n\n**场景：查询产品责任详情**\n```bash\npython scripts/product_tool_interface.py \\\n  --mktProdCode \"PA0001\" \\\n  --requestFields \"责任详情,费率表,免责条款\"\n```\n\n---\n\n## 工具 4：网页搜索（外部补充）\n\n### 基本信息\n- **脚本路径**：`scripts/web_search.py`\n- **功能**：执行网络搜索，获取外部产品信息、市场评价、竞品对比等\n- **适用场景**：内部资料不足时补充外部信息，或查询竞品信息\n\n### 调用方式\n\n```bash\npython scripts/web_search.py --question \"搜索问题\"\n```\n\n### 参数说明\n\n| 参数 | 类型 | 必填 | 说明 | 示例 |\n|-----|------|------|------|------|\n| `--question` | str | 是 | 搜索查询词 | `\"平安福重疾险 市场评价\"` |\n\n### 输出格式\n\n**成功返回示例**：\n```json\n{\n  \"web_detail\": [\n    {\n      \"title\": \"网页标题\",\n      \"url\": \"https://example.com/article\",\n      \"content\": \"网页内容摘要...\"\n    }\n  ],\n  \"web_sumn\": \"搜索结果总结...\",\n  \"sources\": [\"https://example.com/article\"]\n}\n```\n\n### 使用约束\n\n1. **仅作为补充**：外部搜索仅用于内部资料不足时的补充，不用于通用问答\n2. **来源标注**：使用外部信息时必须标注来源URL\n3. **可信度评估**：优先采信官方渠道（保险公司官网、监管网站），谨慎使用论坛、自媒体信息\n\n---\n\n## 工具选择决策流程\n\n```\n用户问题\n    ↓\n是否涉及具体产品？\n    ├─ 否 → 使用product_content_search浏览产品分类\n    ↓\n是\n    ↓\n需要查询什么信息？\n    ├─ 产品列表/分类浏览 → product_content_search\n    ├─ 产品基本信息/投保规则/险种列表 → product_attribute_detail\n    ├─ 责任详情/特定字段 → product_tool_interface\n    └─ 外部评价/竞品信息 → web_search（内部资料不足时）\n```\n\n---\n\n## 工具调用组合示例\n\n### 示例1：查询产品保障责任\n\n**用户问题**：\"平安福重疾险保什么？\"\n\n**执行流程**：\n```bash\n# 步骤1：查询产品险种列表\npython scripts/product_content_search.py \\\n  --productName \"平安福\" \\\n  --contentType \"产品险种列表\"\n\n# 步骤2：如有需要，查询详细责任\npython scripts/product_tool_interface.py \\\n  --mktProdCode \"PA0001\" \\\n  --requestFields \"责任详情\"\n```\n\n### 示例2：对比两款产品\n\n**用户问题**：\"平安福和国寿福有什么区别？\"\n\n**执行流程**：\n```bash\n# 步骤1：查询平安福详细信息（并行）\npython scripts/product_attribute_detail.py \\\n  --productName \"平安福\" \\\n  --attributeType \"产品基本信息,产品险种列表\"\n\n# 步骤2：查询国寿福详细信息（并行）\npython scripts/product_attribute_detail.py \\\n  --productName \"国寿福\" \\\n  --attributeType \"产品基本信息,产品险种列表\"\n\n# 步骤3：整合对比（Agent分析）\n```\n\n### 示例3：内部资料不足时补充外部信息\n\n**用户问题**：\"平安福的市场评价如何？\"\n\n**执行流程**：\n```bash\n# 步骤1：先查询内部产品信息\npython scripts/product_attribute_detail.py \\\n  --productName \"平安福\" \\\n  --attributeType \"产品基本信息\"\n\n# 步骤2：补充外部市场评价\npython scripts/web_search.py \\\n  --question \"平安福重疾险 市场评价 用户反馈\"\n```\n\n---\n\n## 错误处理规范\n\n### 常见错误及处理\n\n| 错误类型 | 错误标识 | 处理建议 |\n|---------|---------|---------|\n| 参数错误 | `[ERROR] 参数异常` | 检查必填参数，修正后重试 |\n| 产品不存在 | `未找到相关产品` | 尝试模糊搜索或询问用户确认产品名称 |\n| 编码错误 | `[ERROR] 产品编码不存在` | 先通过productName查询productCode |\n| 服务超时 | `[ERROR] 服务超时` | 重试1次，仍失败则提示用户稍后重试 |\n| 外部搜索失败 | `搜索服务异常` | 重试1次或告知无法获取外部信息 |\n\n### 重试策略\n\n1. **参数错误**：立即修正，不重试\n2. **服务超时**：等待2秒后重试1次\n3. **空结果**：尝试调整参数（如模糊搜索）后重试\n4. **连续失败**：转入error.md处理流程\n\n---\n\n## Gotchas（工具调用陷阱）\n\n1. **混淆contentType和attributeType**\n   - 陷阱：两个参数可选值相同，但使用场景不同\n   - 正确：contentType用于product_content_search，attributeType用于product_attribute_detail\n\n2. **忽视effectiveState**\n   - 陷阱：查询时未指定生效状态，返回已停售产品\n   - 正确：查询在售产品时务必指定`--effectiveState \"生效\"`\n\n3. **productCode和productName混淆**\n   - 陷阱：将产品名称当作productCode传入\n   - 正确：productCode是编码（如PA0001），productName是名称（如平安福）\n\n4. **web_search过度使用**\n   - 陷阱：优先使用web_search而非内部工具\n   - 正确：必须先尝试内部工具，外部搜索仅作为补充\n\n5. **未指定产品时的默认行为**\n   - 陷阱：用户未指定产品时随机返回结果\n   - 正确：未指定产品时默认优先查询平安保险产品\n",
  "oldString": "# 工具调用规范（Tool Specification）\n\n## 目标\n明确两个核心脚本的调用方式、参数格式、输出解析和错误处理，确保 Agent 能正确执行工具调用并处理返回结果。\n\n---\n\n## 工具 1：内部保险问答工具\n\n### 基本信息\n- **脚本路径**：`scripts/product_answer.py`\n- **功能**：查询内部保险产品数据库，获取条款、费率、理赔规则等官方信息\n- **适用场景**：所有涉及具体保险产品、保单、条款、费率的问题\n\n### 调用方式\n\n```bash\npython scripts/product_answer.py --question \"<保险问题>\"\n```\n\n### 参数说明\n\n| 参数 | 类型 | 必填 | 说明 | 示例 |\n|-----|------|------|------|------|\n| `--question` | str | 是 | 标准化的保险问题描述 | `\"重疾险等待期是多少天\"` |\n\n**参数构建规则**：\n- 必须保留用户问题的关键要素（产品名、年龄、保额等）\n- 去除与保险查询无关的寒暄（如\"请问一下\"、\"麻烦你\"）\n- 如涉及具体保单，确保保单号已脱敏（只保留后4位或完全去除）\n\n### 输出格式\n\n**标准输出（stdout）**：\n- 字段名：`answer`\n- 类型：`str`\n- 内容：关于保险问题的文本答案（可能包含结构化数据如表格）\n\n**成功返回示例**：\n```\n根据《XX终身寿险（2024版）》条款第3.2条：\n\n等待期：自合同生效日起 90 天（等待期内非意外身故退还已交保费）\n\n费率示例（标准体，10万保额）：\n- 30岁男性：年缴 2,500 元\n- 30岁女性：年缴 2,300 元\n\n注：最终费率以核保结果为准。\n```\n\n**空结果返回示例**：\n```\n未找到与\"XX超级保险\"相关的产品信息。可能原因：\n1. 产品名称不准确\n2. 该产品已停售\n3. 暂无此产品数据\n```\n\n**错误返回示例**：\n```\n[ERROR] 数据库连接超时，请稍后重试\n[ERROR] 查询参数异常：年龄超出范围（0-100）\n```\n\n### 返回值解析规范\n\n1. **检查是否以 `[ERROR]` 开头**：\n   - 是 → 进入 error.md 处理流程\n   - 否 → 继续下一步\n\n2. **检查是否包含关键信息**：\n   - 若包含\"未找到\"、\"不存在\"、\"无此产品\" → 标记为 DATA_MISSING\n   - 若包含具体条款、费率、日期 → 标记为 SUCCESS\n\n3. **提取结构化数据**（如有）：\n   - 使用正则或字符串处理提取数值（保费、保额、天数等）\n   - 保留原始文本用于后续输出\n\n---\n\n## 工具 2：外部网页搜索工具\n\n### 基本信息\n- **脚本路径**：`scripts/web_search.py`\n- **功能**：执行网络搜索，获取实时新闻、政策、市场动态等外部信息\n- **适用场景**：天气、新闻、政策变动、市场分析、第三方评价等\n\n### 调用方式\n\n```bash\npython scripts/web_search.py --question \"<搜索问题>\"\n```\n\n### 参数说明\n\n| 参数 | 类型 | 必填 | 说明 | 示例 |\n|-----|------|------|------|------|\n| `--question` | str | 是 | 搜索查询词 | `\"2025年3月保险监管新政策\"` |\n\n**参数构建规则**：\n- 保留关键时间、地点、主体（如\"2025年3月\"、\"北京\"、\"银保监会\"）\n- 去除保险敏感信息（保单号、身份证号、详细个人信息）\n- 对于比较类问题，确保查询词中立（如\"重疾险和医疗险区别\"而非\"重疾险是不是骗局\"）\n\n### 输出格式\n\n**标准输出（stdout）包含两个部分**：\n\n#### 1. web_detail（原始网页详情）\n- 类型：`List[str]`\n- 内容：前3个相关网页的详细内容片段（原始文本）\n- 用途：验证 `web_sumn` 的准确性，提供详细引用来源\n\n**格式示例**：\n```python\n[\n  \"网页1标题：2025年保险监管新规出台\\nURL：xxx\\n内容：银保监会今日发布...\",\n  \"网页2标题：解读最新保险政策\\nURL：xxx\\n内容：专家分析认为...\",\n  \"网页3标题：保险市场动态\\nURL：xxx\\n内容：根据最新数据...\"\n]\n```\n\n#### 2. web_sumn（内容总结）\n- 类型：`str`\n- 内容：基于搜索结果的总结性回答\n- 用途：直接作为主要参考内容呈现给用户\n\n**格式示例**：\n```\n根据搜索结果，2025年3月保险监管主要新政策包括：\n\n1. 重疾险定义更新：扩大轻症保障范围...\n2. 互联网保险新规：要求明确披露...\n3. 代理人管理：加强资质审核...\n\n信息来源：银保监会官网、新华网等\n```\n\n### 返回值解析规范\n\n1. **解析输出**：将 stdout 解析为 Python 对象（假设为 JSON 或特定分隔格式）\n   \n   **假设返回格式为 JSON**：\n   ```json\n   {\n     \"web_detail\": [\"...\", \"...\", \"...\"],\n     \"web_sumn\": \"...\"\n   }\n   ```\n\n2. **检查 `web_sumn` 内容**：\n   - 如果为 `\"\"` 或 `\"未找到相关信息\"` → 标记为 NO_DATA\n   - 如果包含内容 → 标记为 SUCCESS\n\n3. **检查 `web_detail` 长度**：\n   - 正常情况下包含 1-3 个页面详情\n   - 如果为空列表 `[]` → 说明搜索无结果\n\n4. **提取来源信息**：\n   - 从 `web_detail` 中提取 URL 域名和标题，用于标注来源\n\n### 来源可信度评估（用于验证模块）\n\n基于 `web_detail` 中的 URL 进行可信度分级：\n\n| 级别 | 域名特征 | 可信度 | 使用建议 |\n|-----|---------|--------|---------|\n| 高 | `.gov.cn`, `cbirc.gov.cn`, 保险公司官网 | 高 | 优先采信，可用于验证保险政策 |\n| 中 | 主流新闻站 (`sina.com`, `qq.com` 等) | 中 | 可使用，但需交叉验证 |\n| 低 | 论坛、博客、自媒体 | 低 | 仅作参考，不得用于保险条款依据 |\n\n---\n\n## 工具调用组合示例\n\n### 场景 1：纯保险问题（仅 product_answer.py）\n\n**用户问题**：\"30岁男性买你们公司重疾险50万保额，年缴多少钱？\"\n\n**执行步骤**：\n```bash\n# 步骤 1：调用内部工具\npython scripts/product_answer.py --question \"30岁男性重疾险50万保额年缴保费\"\n```\n\n**接收返回**：\n- `answer`: \"XX重疾险（2024版），30岁男性，50万保额，年缴保费 8,500.00 元（标准体）...\"\n\n**验证**：包含具体数值、产品版本 → SUCCESS\n\n**格式化输出**：\n```\n【内部资料】根据查询结果：\n\n产品：XX重疾险（2024版）\n- 被保人：30岁男性\n- 保额：500,000 元\n- 年缴保费：¥8,500.00（标准体费率）\n\n*注：最终保费以实际核保结果为准，可能因健康状况调整。*\n```\n\n---\n\n### 场景 2：纯外部搜索（仅 web_search.py）\n\n**用户问题**：\"今天北京天气怎么样？\"\n\n**执行步骤**：\n```bash\npython scripts/web_search.py --question \"北京今天天气 2025-03-28\"\n```\n\n**接收返回**：\n- `web_sumn`: \"北京今日晴，气温 15-25°C，北风 3 级...\"\n- `web_detail`: [\"网页1...\", \"网页2...\"]\n\n**格式化输出**：\n```\n【网络信息，仅供参考，2025-03-28】\n\n北京今日天气：晴朗\n- 气温：15°C ~ 25°C\n- 风向：北风 3 级\n- 空气质量：良\n\n*来源：中国天气网、新浪天气*\n```\n\n---\n\n### 场景 3：混合查询（先 product_answer.py，后 web_search.py）\n\n**用户问题**：\"我买的XX重疾险最近有什么新政策影响吗？\"\n\n**执行步骤 1**：\n```bash\npython scripts/product_answer.py --question \"XX重疾险产品条款简介\"\n```\n\n**返回 1**：\n- `answer`: \"XX重疾险（2023版），保障范围包括...\"\n\n**执行步骤 2**（基于步骤 1 确认的产品名）：\n```bash\npython scripts/web_search.py --question \"2025年3月 XX重疾险 监管政策 新规\"\n```\n\n**返回 2**：\n- `web_sumn`: \"近期监管发布重疾险新规，要求...（不涉及2023版条款调整）\"\n- `web_detail`: [\"...\", \"...\"]\n\n**合并输出**：\n```\n【内部资料】您的保单信息：\n产品：XX重疾险（2023版）\n保障范围：...\n条款状态：正常有效\n\n---\n\n【网络信息，2025-03-28，仅供参考】\n近期监管动态：\n2025年3月发布的新规主要针对新备案的重疾险产品，要求扩大轻症保障范围。\n经比对，该政策不影响您持有的2023版保单条款。\n\n*来源：银保监会官网、保险业协会*\n```\n\n---\n\n## 错误处理规范\n\n### product_answer.py 常见错误\n\n| 错误标识 | 含义 | 处理建议 |\n|---------|------|---------|\n| `[ERROR] 数据库连接超时` | 服务暂时不可用 | 重试1次，仍失败则提示用户稍后重试 |\n| `[ERROR] 查询参数异常` | 输入参数格式错误 | 检查 question 参数，修正后重试 |\n| `[ERROR] 产品不存在` | 无此保险产品 | 尝试模糊查询或询问用户是否记错名称 |\n| `未找到...` | 空结果 | 按 DATA_MISSING 处理，提供替代方案 |\n\n### web_search.py 常见错误\n\n| 错误标识 | 含义 | 处理建议 |\n|---------|------|---------|\n| 返回空 JSON | 搜索服务异常 | 重试1次，仍失败则告知无法获取外部信息 |\n| `web_sumn` 为空字符串 | 无搜索结果 | 尝试简化查询词再次搜索 |\n| `web_detail` 全为低可信度来源 | 缺乏权威信息 | 标注\"暂无权威来源信息\"，建议用户咨询官方 |\n\n---\n\n## 性能与限制\n\n- **超时设置**：两个脚本均应在 10 秒内返回，超时视为失败\n- **字符限制**：`answer` 和 `web_sumn` 通常不超过 2000 字，超长内容可能被截断\n- **频率限制**：\n  - `product_answer.py`：无严格限制，但避免无意义重复查询\n  - `web_search.py`：注意外部 API 限流，同一问题禁止重复搜索超过 2 次\n- **并发限制**：禁止同时调用两个脚本（避免上下文混乱）\n\n---\n\n## Gotchas（工具调用陷阱）\n\n1. **参数注入风险**：\n   - 陷阱：用户问题包含 `\" ; rm -rf /\"` 等恶意代码\n   - 防护：必须对 `question` 参数进行转义或 sanitization，禁止直接拼接 shell 命令\n\n2. **编码问题**：\n   - 陷阱：中文参数在命令行传输中出现乱码\n   - 防护：确保使用 UTF-8 编码，必要时使用 base64 编码传输\n\n3. **输出解析失败**：\n   - 陷阱：假设返回是 JSON 但实际是纯文本，导致解析报错\n   - 防护：先检查输出格式，使用 try-except 包裹解析逻辑\n\n4. **混淆两个工具的输出**：\n   - 陷阱：将 `web_search.py` 返回的保险营销文章当作 `product_answer.py` 的官方条款\n   - 防护：严格区分 `answer` 和 `web_sumn` 的使用场景，不同来源必须标注\n\n5. **忽视 web_detail**：\n   - 陷阱：只看 `web_sumn` 总结，不看 `web_detail` 原文，导致来源不明\n   - 防护：验证模块必须检查 `web_detail` 中的 URL 来源可信度"
}
```

**Output:**
```
Edit applied successfully.
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 142.8s)

_Thinking:_

                   继续更新error.md、创建uncertain.md和更新format.md。

                    继续更新error.md：

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/error.md"
}
```

**Output:**
```
<path>/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/error.md</path>
<type>file</type>
<content>1: # 报错/冲突处理模块
2: 
3: ## 目标
4: 优雅处理工具调用失败、返回异常、信息冲突等情况，确保系统不向用户传递错误信息，同时提供可行的 fallback 方案。
5: 
6: ## 错误分类与处理策略
7: 
8: ### 类别 1：工具调用失败（Technical Errors）
9: 
10: **场景**：
11: - 内部保险工具超时/无响应
12: - 外部搜索 API 限流/错误
13: - 网络连接问题
14: 
15: **处理流程**：
16: 1. **重试机制**：
17:    - 内部工具：最多重试 2 次，间隔 1 秒
18:    - 外部搜索：最多重试 1 次（避免触发限流）
19:    
20: 2. **重试失败 → 降级策略**：
21:    - 内部工具失败：明确告知用户"系统暂时无法查询保险资料，建议稍后重试或联系客服"
22:    - 外部搜索失败：如果问题是保险相关的，尝试用内部工具回答基础部分；如果是纯外部信息，告知用户"暂时无法获取最新信息"
23: 
24: 3. **禁止行为**：
25:    - 禁止用外部搜索替代内部工具回答保险问题
26:    - 禁止编造数据"假装"工具返回成功
27: 
28: **输出模板**：
29: ```
30: 【系统提示】
31: 暂时无法查询到 [具体信息类型]，可能原因：[简要说明]
32: 建议：[具体行动建议，如"稍后重试"/"拨打客服热线 400-xxx"]
33: ```
34: 
35: ### 类别 2：数据缺失（Data Missing）
36: 
37: **场景**：
38: - 内部工具返回空结果（产品不存在/已停售）
39: - 查询条件过于具体，无匹配数据
40: 
41: **处理流程**：
42: 1. **确认查询参数**：
43:    - 检查是否拼写错误（如"重级险" vs "重疾险"）
44:    - 检查是否包含不可能的限定条件（如"100岁购买少儿险"）
45: 
46: 2. **扩大查询范围**：
47:    - 如果查询具体产品失败，尝试列出该类别所有产品
48:    - 如果带条件查询失败，尝试无条件下查询，再人工筛选
49: 
50: 3. **仍无结果 → 明确告知**：
51:    - "未找到名为'XX'的产品，是否指以下产品：[相似产品列表]"
52:    - "您描述的保障需求暂无完全匹配产品，建议咨询顾问定制方案"
53: 
54: ### 类别 3：信息冲突（Conflicts）
55: 
56: **场景**：
57: - 内部工具显示产品A在售，外部搜索显示已停售
58: - 内部费率与外部报道不一致
59: - 不同外部来源信息矛盾
60: 
61: **处理优先级**：
62: 1. **保险条款、费率、状态**：优先采信**内部工具**
63: 2. **市场新闻、政策解读**：优先采信**官方监管/公司官网**
64: 3. **用户评价、非官方解读**：仅作参考，必须标注来源
65: 
66: **冲突处理流程**：
67: 发现冲突
68:    ↓
69: 标记冲突点（记录双方信息+来源+时间）
70:    ↓
71: 优先级判断
72:    ↓
73: 高优先级可信？→ 是：采用高优先级，但必须在答案中标注冲突
74:    ↓
75: 否 → 标记为 UNRESOLVED，不回答该子问题，建议人工核实
76: 
77: **输出模板（冲突情况）**：
78: ```
79: 【信息说明】
80: 关于 [具体问题]，不同来源信息存在差异：
81: 
82: ✓ 内部资料（[日期]）：[内部工具返回的信息]
83: ⚠ 网络信息（[来源]，[日期]）：[外部搜索返回的信息]
84: 
85: 建议以官方最新公告为准，或联系客服核实：[客服方式]
86: ```
87: 
88: ### 类别 4：逻辑不一致（Logical Inconsistency）
89: 
90: **场景**：
91: - 子问题1说"30岁可投保"，子问题2说"该产品仅限18-25岁"
92: - 保费计算结果与保额不成比例（如50万保额比30万便宜）
93: 
94: **处理流程**：
95: 1. **标记逻辑矛盾**
96: 2. **回溯检查**：是否误解了用户问题？是否调用了错误的产品代码？
97: 3. **无法解释的矛盾**：不合并答案，分别呈现并标注矛盾点
98: 4. **建议人工复核**
99: 
100: ## 错误恢复策略矩阵
101: 
102: | 错误场景 | 自动重试 | 切换工具 | 人工提示 | 终止流程 |
103: |---------|---------|---------|---------|---------|
104: | 工具超时 | ✓ 2次 | ✗ | ✓ | 最终手段 |
105: | 空结果 | ✗ | ✓（扩大查询） | ✓ | ✗ |
106: | 内外部冲突 | ✗ | ✗ | ✓ 必须标注 | ✗ |
107: | 逻辑矛盾 | ✗ | ✗ | ✓ 必须标注 | 严重时可终止 |
108: | 敏感信息泄露风险 | ✗ | ✗ | ✗ | ✓ 立即终止 |
109: 
110: ## Gotchas（错误处理陷阱）
111: 
112: 1. **静默失败**：工具返回空结果或错误，但系统"假装"成功继续执行
113:    - 陷阱：内部工具报错，系统用外部搜索替代，导致错误信息
114:    - 防护：必须检查工具返回状态码，非成功状态一律进入错误处理
115: 
116: 2. **冲突掩盖**：发现冲突但选择"简单处理"只呈现一方
117:    - 陷阱：内部显示在售，外部显示停售，只告诉用户"在售"，导致用户无法购买
118:    - 防护：任何冲突必须在答案中显性标注，不能隐瞒
119: 
120: 3. **过度重试**：无限重试导致响应时间过长或触发限流
121:    - 陷阱：外部搜索失败后不断重试，导致 IP 被封
122:    - 防护：严格限制重试次数，失败后立即降级
123: 
124: 4. **错误信息传递**：将工具原始错误信息直接暴露给用户
125:    - 陷阱："SQL Error: Table not found" 直接显示给用户
126:    - 防护：所有错误必须转化为用户友好的提示，技术细节记录日志

(End of file - total 126 lines)
</content>
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 191.0s)

_Thinking:_

                        error.md的内容已经比较完善，我只需要做一些更新以匹配新的工具和策略。让我更新它。

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/error.md",
  "newString": "# 报错/冲突处理模块\n\n## 目标\n优雅处理工具调用失败、返回异常、信息冲突等情况，确保不向用户传递错误技术信息，同时提供可行的 fallback 方案。\n\n## 错误分类与处理策略\n\n### 类别 1：工具调用失败（Technical Errors）\n\n**场景**：\n- 内部保险工具超时/无响应\n- 外部搜索 API 限流/错误\n- 网络连接问题\n\n**处理流程**：\n\n1. **重试机制**：\n   - `product_content_search`/`product_attribute_detail`/`product_tool_interface`：最多重试 2 次，间隔 1 秒\n   - `web_search`：最多重试 1 次（避免触发限流）\n\n2. **重试失败 → 降级策略**：\n   - **内部工具失败**：\n     - 尝试切换同类型工具（如`product_attribute_detail`失败时尝试`product_content_search`）\n     - 仍失败：明确告知用户\"系统暂时无法查询保险资料，建议稍后重试或联系客服\"\n   - **外部搜索失败**：\n     - 如果问题是保险相关的，尝试用内部工具回答基础部分\n     - 如果是纯外部信息，告知用户\"暂时无法获取最新信息\"\n\n3. **禁止行为**：\n   - 禁止用`web_search`替代内部工具回答保险问题\n   - 禁止编造数据\"假装\"工具返回成功\n   - 禁止向用户暴露技术错误信息（如SQL错误、堆栈跟踪等）\n\n**输出模板**：\n```\n【系统提示】\n暂时无法查询到 [具体信息类型]，可能原因：[简要说明]\n建议：[具体行动建议，如\"稍后重试\"/\"拨打客服热线 95511\"]\n```\n\n### 类别 2：数据缺失（Data Missing）\n\n**场景**：\n- 工具返回空结果（产品不存在/已停售）\n- 查询条件过于具体，无匹配数据\n- 产品编码/名称错误\n\n**处理流程**：\n\n1. **确认查询参数**：\n   - 检查产品名称是否拼写错误（如\"重级险\" vs \"重疾险\"）\n   - 检查产品编码格式是否正确\n   - 检查是否包含不可能的限定条件（如\"100岁购买少儿险\"）\n\n2. **扩大查询范围**：\n   - 使用`product_content_search`的模糊搜索（`--productName`支持模糊匹配）\n   - 列出该类别所有产品供用户选择\n   - 尝试不带`effectiveState`筛选，查看是否存在但已停售\n\n3. **仍无结果 → 明确告知**：\n   ```\n   未找到名为'XX'的产品，是否指以下产品：\n   - 相似产品A\n   - 相似产品B\n   \n   如您不确定产品名称，可以告诉我您想了解的保险类型（如重疾险、医疗险等）。\n   ```\n\n### 类别 3：信息冲突（Conflicts）\n\n**场景**：\n- 不同内部工具返回的产品信息不一致\n- 内部资料与外部搜索结果矛盾\n- 同一产品的不同版本信息冲突\n- 不同外部来源信息矛盾\n\n**处理优先级**（优先级从高到低）：\n1. **`product_tool_interface`**（责任详情）> `product_attribute_detail` > `product_content_search`\n2. **内部工具** > **外部搜索**（保险条款、费率、状态等核心信息）\n3. **官方监管/公司官网** > **主流新闻** > **论坛/自媒体**（外部信息）\n4. **最新生效版本** > **旧版本**（同一产品多版本）\n\n**冲突处理流程**：\n```\n发现冲突\n    ↓\n标记冲突点（记录双方信息+来源+时间）\n    ↓\n按优先级判断可信度\n    ↓\n高优先级可信？\n    ├─ 是 → 采用高优先级，但在答案中标注冲突\n    └─ 否 → 标记为 UNRESOLVED，建议人工核实\n```\n\n**输出模板（冲突情况）**：\n```\n【信息说明】\n关于 [具体问题]，不同来源信息存在差异：\n\n✓ 内部资料（[工具名称]，[日期]）：[高优先级信息]\n⚠ 其他来源（[来源]，[日期]）：[低优先级信息]\n\n建议以官方最新公告为准，或联系客服核实：95511\n```\n\n### 类别 4：工具返回不完整\n\n**场景**：\n- `product_attribute_detail`返回的属性信息缺失某些字段\n- `product_tool_interface`查询的字段不存在\n- `web_search`返回的`web_sumn`为空但`web_detail`有内容\n\n**处理流程**：\n\n1. **检查缺失字段重要性**：\n   - 核心字段缺失（如产品名称、保障责任）：尝试其他工具补充\n   - 非核心字段缺失（如销售渠道）：继续执行，在输出中标注\"信息待补充\"\n\n2. **尝试补充查询**：\n   - 使用其他工具查询缺失信息\n   - 调整参数后重新查询\n\n3. **输出模板**：\n   ```\n   已获取以下信息：\n   - 产品名称：XX重疾险\n   - 投保年龄：18-55周岁\n   \n   以下信息暂未获取：[缺失字段列表]\n   如需了解详细信息，建议联系客服：95511\n   ```\n\n### 类别 5：逻辑不一致（Logical Inconsistency）\n\n**场景**：\n- 子问题1说\"30岁可投保\"，子问题2说\"该产品仅限18-25岁\"\n- 同一产品的投保规则前后矛盾\n\n**处理流程**：\n1. **标记逻辑矛盾**\n2. **回溯检查**：是否调用了不同版本的产品？是否参数设置错误？\n3. **无法解释的矛盾**：不合并答案，分别呈现并标注矛盾点\n4. **建议人工复核**\n\n## 错误恢复策略矩阵\n\n| 错误场景 | 自动重试 | 切换工具 | 人工提示 | 终止流程 |\n|---------|---------|---------|---------|---------|\n| 工具超时 | ✓ 2次 | ✓（同类型工具） | ✓ | 最终手段 |\n| 空结果 | ✗ | ✓（扩大查询） | ✓ | ✗ |\n| 内外部冲突 | ✗ | ✗ | ✓ 必须标注 | ✗ |\n| 逻辑矛盾 | ✗ | ✗ | ✓ 必须标注 | 严重时可终止 |\n| 敏感信息泄露风险 | ✗ | ✗ | ✗ | ✓ 立即终止 |\n\n## 常见错误及处理\n\n### product_content_search 常见错误\n\n| 错误标识 | 含义 | 处理建议 |\n|---------|------|---------|\n| `[ERROR] 参数格式错误` | contentType等参数值不在枚举范围内 | 检查参数值是否在允许的枚举列表中 |\n| `[ERROR] 未找到匹配产品` | 无符合条件的产品 | 尝试移除部分筛选条件或扩大topK |\n| `返回空列表` | 查询条件过于严格 | 逐步移除筛选条件重试 |\n\n### product_attribute_detail 常见错误\n\n| 错误标识 | 含义 | 处理建议 |\n|---------|------|---------|\n| `[ERROR] productName和productCode至少填一个` | 缺少必填参数 | 补充产品名称或编码 |\n| `[ERROR] 产品编码不存在` | productCode错误 | 先通过productName查询正确编码 |\n| `[ERROR] 属性类型不存在` | attributeType值错误 | 检查是否在允许的枚举列表中 |\n\n### product_tool_interface 常见错误\n\n| 错误标识 | 含义 | 处理建议 |\n|---------|------|---------|\n| `[ERROR] mktProdCode不能为空` | 缺少必填参数 | 补充产品编码 |\n| `[ERROR] 产品不存在` | 编码错误 | 通过其他工具查询正确编码 |\n| `[ERROR] 字段不存在` | requestFields包含无效字段 | 检查字段名称是否正确 |\n\n### web_search 常见错误\n\n| 错误标识 | 含义 | 处理建议 |\n|---------|------|---------|\n| `[ERROR] 搜索服务异常` | 外部服务问题 | 重试1次，仍失败则告知无法获取 |\n| `web_sumn为空` | 无搜索结果 | 尝试简化查询词 |\n| `全为低可信度来源` | 缺乏权威信息 | 标注\"暂无权威来源\" |\n\n## Gotchas（错误处理陷阱）\n\n1. **静默失败**\n   - 陷阱：工具返回空结果或错误，但系统\"假装\"成功继续执行\n   - 示例：`product_attribute_detail`返回空，系统用假设的数据继续\n   - 防护：必须检查工具返回状态，空结果或错误状态一律进入错误处理\n\n2. **冲突掩盖**\n   - 陷阱：发现冲突但选择\"简单处理\"只呈现一方\n   - 示例：内部显示在售，外部显示停售，只告诉用户\"在售\"\n   - 防护：任何冲突必须在答案中显性标注，不能隐瞒\n\n3. **过度重试**\n   - 陷阱：无限重试导致响应时间过长或触发限流\n   - 示例：外部搜索失败后不断重试，导致IP被封\n   - 防护：严格限制重试次数，失败后立即降级\n\n4. **错误信息传递**\n   - 陷阱：将工具原始错误信息直接暴露给用户\n   - 示例：\"SQL Error: Table not found\"直接显示给用户\n   - 防护：所有错误必须转化为用户友好的提示\n\n5. **工具切换不当**\n   - 陷阱：`product_tool_interface`失败后切换到`web_search`查询保险信息\n   - 示例：查询责任详情失败，改用外部搜索获取\n   - 防护：工具切换只能在同类工具间进行，禁止用外部搜索替代内部工具\n",
  "oldString": "# 报错/冲突处理模块\n\n## 目标\n优雅处理工具调用失败、返回异常、信息冲突等情况，确保系统不向用户传递错误信息，同时提供可行的 fallback 方案。\n\n## 错误分类与处理策略\n\n### 类别 1：工具调用失败（Technical Errors）\n\n**场景**：\n- 内部保险工具超时/无响应\n- 外部搜索 API 限流/错误\n- 网络连接问题\n\n**处理流程**：\n1. **重试机制**：\n   - 内部工具：最多重试 2 次，间隔 1 秒\n   - 外部搜索：最多重试 1 次（避免触发限流）\n   \n2. **重试失败 → 降级策略**：\n   - 内部工具失败：明确告知用户\"系统暂时无法查询保险资料，建议稍后重试或联系客服\"\n   - 外部搜索失败：如果问题是保险相关的，尝试用内部工具回答基础部分；如果是纯外部信息，告知用户\"暂时无法获取最新信息\"\n\n3. **禁止行为**：\n   - 禁止用外部搜索替代内部工具回答保险问题\n   - 禁止编造数据\"假装\"工具返回成功\n\n**输出模板**：\n```\n【系统提示】\n暂时无法查询到 [具体信息类型]，可能原因：[简要说明]\n建议：[具体行动建议，如\"稍后重试\"/\"拨打客服热线 400-xxx\"]\n```\n\n### 类别 2：数据缺失（Data Missing）\n\n**场景**：\n- 内部工具返回空结果（产品不存在/已停售）\n- 查询条件过于具体，无匹配数据\n\n**处理流程**：\n1. **确认查询参数**：\n   - 检查是否拼写错误（如\"重级险\" vs \"重疾险\"）\n   - 检查是否包含不可能的限定条件（如\"100岁购买少儿险\"）\n\n2. **扩大查询范围**：\n   - 如果查询具体产品失败，尝试列出该类别所有产品\n   - 如果带条件查询失败，尝试无条件下查询，再人工筛选\n\n3. **仍无结果 → 明确告知**：\n   - \"未找到名为'XX'的产品，是否指以下产品：[相似产品列表]\"\n   - \"您描述的保障需求暂无完全匹配产品，建议咨询顾问定制方案\"\n\n### 类别 3：信息冲突（Conflicts）\n\n**场景**：\n- 内部工具显示产品A在售，外部搜索显示已停售\n- 内部费率与外部报道不一致\n- 不同外部来源信息矛盾\n\n**处理优先级**：\n1. **保险条款、费率、状态**：优先采信**内部工具**\n2. **市场新闻、政策解读**：优先采信**官方监管/公司官网**\n3. **用户评价、非官方解读**：仅作参考，必须标注来源\n\n**冲突处理流程**：\n发现冲突\n   ↓\n标记冲突点（记录双方信息+来源+时间）\n   ↓\n优先级判断\n   ↓\n高优先级可信？→ 是：采用高优先级，但必须在答案中标注冲突\n   ↓\n否 → 标记为 UNRESOLVED，不回答该子问题，建议人工核实\n\n**输出模板（冲突情况）**：\n```\n【信息说明】\n关于 [具体问题]，不同来源信息存在差异：\n\n✓ 内部资料（[日期]）：[内部工具返回的信息]\n⚠ 网络信息（[来源]，[日期]）：[外部搜索返回的信息]\n\n建议以官方最新公告为准，或联系客服核实：[客服方式]\n```\n\n### 类别 4：逻辑不一致（Logical Inconsistency）\n\n**场景**：\n- 子问题1说\"30岁可投保\"，子问题2说\"该产品仅限18-25岁\"\n- 保费计算结果与保额不成比例（如50万保额比30万便宜）\n\n**处理流程**：\n1. **标记逻辑矛盾**\n2. **回溯检查**：是否误解了用户问题？是否调用了错误的产品代码？\n3. **无法解释的矛盾**：不合并答案，分别呈现并标注矛盾点\n4. **建议人工复核**\n\n## 错误恢复策略矩阵\n\n| 错误场景 | 自动重试 | 切换工具 | 人工提示 | 终止流程 |\n|---------|---------|---------|---------|---------|\n| 工具超时 | ✓ 2次 | ✗ | ✓ | 最终手段 |\n| 空结果 | ✗ | ✓（扩大查询） | ✓ | ✗ |\n| 内外部冲突 | ✗ | ✗ | ✓ 必须标注 | ✗ |\n| 逻辑矛盾 | ✗ | ✗ | ✓ 必须标注 | 严重时可终止 |\n| 敏感信息泄露风险 | ✗ | ✗ | ✗ | ✓ 立即终止 |\n\n## Gotchas（错误处理陷阱）\n\n1. **静默失败**：工具返回空结果或错误，但系统\"假装\"成功继续执行\n   - 陷阱：内部工具报错，系统用外部搜索替代，导致错误信息\n   - 防护：必须检查工具返回状态码，非成功状态一律进入错误处理\n\n2. **冲突掩盖**：发现冲突但选择\"简单处理\"只呈现一方\n   - 陷阱：内部显示在售，外部显示停售，只告诉用户\"在售\"，导致用户无法购买\n   - 防护：任何冲突必须在答案中显性标注，不能隐瞒\n\n3. **过度重试**：无限重试导致响应时间过长或触发限流\n   - 陷阱：外部搜索失败后不断重试，导致 IP 被封\n   - 防护：严格限制重试次数，失败后立即降级\n\n4. **错误信息传递**：将工具原始错误信息直接暴露给用户\n   - 陷阱：\"SQL Error: Table not found\" 直接显示给用户\n   - 防护：所有错误必须转化为用户友好的提示，技术细节记录日志"
}
```

**Output:**
```
Edit applied successfully.
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 148.6s)

_Thinking:_

                           现在创建uncertain.md（反问模块），然后更新format.md。

                           现在创建uncertain.md（反问模块）：

**Tool: write**

**Input:**
```json
{
  "content": "# 反问模块：问题澄清与信息补全\n\n## 目标\n当用户问题主体不明确、关键信息缺失或存在歧义时，通过反问获取必要信息，确保后续工具调用能够准确执行。\n\n## 必须反问的情况\n\n### 情况1：未明确保险产品大类\n\n**触发条件**：\n- 用户问题中未提及具体保险产品名称或类型\n- 问题过于宽泛（如\"帮我查下保险\"、\"保险可以保什么\"）\n\n**示例**：\n- 用户：\"帮我查下保险\"\n- 用户：\"保险能保哪些病？\"\n- 用户：\"我想买保险，有什么推荐？\"\n\n**反问话术**：\n```\n您好！为了更好地为您服务，请告诉我：\n\n1. 您想了解哪类保险产品？\n   - 重疾险（保障重大疾病）\n   - 医疗险（报销医疗费用）\n   - 意外险（保障意外伤害）\n   - 寿险（身故保障）\n   - 年金险（养老/教育金规划）\n\n2. 或者您是否有具体想了解的产品名称？\n\n请告诉我您的需求，我立即为您查询详细信息。\n```\n\n### 情况2：产品名称模糊或不存在\n\n**触发条件**：\n- 产品名称拼写错误或过于简略\n- 产品名称不存在于产品库中\n- 多个产品名称相似，无法确定具体是哪个\n\n**示例**：\n- 用户：\"平安福怎么样？\"（存在平安福、平安福重疾、平安福医疗等多个版本）\n- 用户：\"那个重疾险\"（未指明具体产品）\n- 用户：\"XX保险\"（产品名称拼写错误）\n\n**反问话术**：\n```\n您提到的\"[产品名称]\"可能存在以下情况：\n\n**情况1：产品名称不完整**\n我们系统中有以下相关产品：\n- 平安福（2024版）重疾险\n- 平安福（2024版）医疗险\n- 平安福（2023版）重疾险（已停售）\n\n请问您想了解的是哪一款？\n\n**情况2：产品名称可能有误**\n未找到名为\"[产品名称]\"的产品，您是否指：\n- [相似产品A]\n- [相似产品B]\n\n请确认产品名称，我为您查询准确信息。\n```\n\n### 情况3：需要确认关键参数\n\n**触发条件**：\n- 查询保费、保额等需要具体参数\n- 用户未提供年龄、性别、缴费期限等必要信息\n- 问题涉及多个可选方案，需要用户确认\n\n**示例**：\n- 用户：\"这个保险多少钱？\"（未提供年龄、性别、保额）\n- 用户：\"能保多少？\"（未指明是保额上限还是具体保障内容）\n\n**反问话术（保费查询）**：\n```\n查询保费需要以下信息，请提供：\n\n1. **被保险人年龄**：____岁\n2. **性别**：男 / 女\n3. **保额需求**：____万元\n4. **缴费期限**：趸交（一次性）/ 5年 / 10年 / 20年 / 30年\n5. **保障期限**：终身 / 定期（____年）\n\n或者您告诉我大致预算和保障需求，我为您推荐合适的方案。\n```\n\n**反问话术（保障内容查询）**：\n```\n您询问\"能保多少\"，请问您想了解的是：\n\nA. **保额上限**：该产品最高可投保多少万元？\nB. **保障范围**：该产品具体保障哪些疾病/情况？\nC. **赔付金额**：发生理赔时能赔付多少钱？\n\n请告诉我您的具体需求，我为您详细解答。\n```\n\n### 情况4：多个产品同名需确认版本\n\n**触发条件**：\n- 同一产品名称存在多个版本（如2023版、2024版）\n- 同一产品在不同渠道（线上/线下）规则不同\n\n**示例**：\n- 用户：\"平安福的等待期是多久？\"（存在2023版和2024版，等待期可能不同）\n\n**反问话术**：\n```\n\"平安福\"有多个版本在售，不同版本规则可能不同：\n\n| 版本 | 状态 | 等待期 |\n|------|------|--------|\n| 平安福（2024版） | 在售 | 90天 |\n| 平安福（2023版） | 已停售 | 180天 |\n\n请问您：\n1. 您想了解哪个版本？\n2. 或者您是在哪一年购买的？我帮您确认对应版本。\n```\n\n### 情况5：问题意图不明确\n\n**触发条件**：\n- 用户问题可以有多重理解\n- 问题涉及多个不相关的子问题\n- 用户使用了口语化、歧义化的表达\n\n**示例**：\n- 用户：\"这个怎么样？\"（未指明\"这个\"指什么）\n- 用户：\"A产品和B产品\"（未说明是想对比、分别了解还是其他意图）\n\n**反问话术**：\n```\n您的问题\"[用户问题]\"可以从以下几个角度理解：\n\nA. [理解1]\nB. [理解2]\nC. [理解3]\n\n请问您想了解的是哪一种？或者您可以详细描述一下您的具体需求。\n```\n\n## 反问策略\n\n### 策略1：提供选项而非开放式提问\n\n**不推荐**：\n```\n您想了解什么保险产品？\n```\n\n**推荐**：\n```\n您想了解哪类保险产品？\n- 重疾险（保障重大疾病）\n- 医疗险（报销医疗费用）\n- 意外险（保障意外伤害）\n- 寿险（身故保障）\n- 年金险（养老/教育金规划）\n```\n\n### 策略2：一次反问不超过3个问题\n\n**不推荐**：\n```\n请提供：1.产品名称 2.年龄 3.性别 4.保额 5.缴费期限 6.保障期限...\n```\n\n**推荐**：\n```\n查询保费需要以下核心信息：\n1. 被保险人年龄：____岁\n2. 性别：男 / 女\n3. 保额需求：____万元\n\n其他参数我按常见方案为您估算，确认后可调整。\n```\n\n### 策略3：提供默认值降低用户负担\n\n**示例**：\n```\n查询保费需要提供：\n- 年龄：____岁\n- 性别：男 / 女\n- 保额：____万元（默认50万）\n- 缴费期限：____年（默认20年）\n\n您可以先按默认值了解大致费率，如有具体需求再调整。\n```\n\n### 策略4：引导用户提供更精准信息\n\n**示例**：\n```\n您想了解\"平安福\"，但平安福系列产品较多。为了更精准地为您服务：\n\n**方式1**：告诉我产品全称（如\"平安福2024重疾险\"）\n**方式2**：告诉我您的需求（如\"30岁男性，50万保额的重疾险\"），我为您推荐合适产品\n**方式3**：告诉我您从哪了解到的这个产品（如\"朋友推荐\"/\"网上看到的\"），我帮您确认\n\n请选择最方便的方式。\n```\n\n## 反问后的处理流程\n\n```\n用户问题不明确\n    ↓\n执行反问模块，提出澄清问题\n    ↓\n等待用户回复\n    ↓\n获取澄清后的问题\n    ↓\n是否仍不明确？\n    ├─ 是 → 继续反问（最多3轮）\n    └─ 否 → 进入正常处理流程\n```\n\n**注意事项**：\n- 反问轮次不超过3轮，避免用户体验下降\n- 每轮反问后总结已确认的信息，让用户感知进展\n- 如用户始终无法提供明确信息，给出\"基于常见情况的默认回答\"并标注\n\n## 常见场景快速反问模板\n\n| 场景 | 反问模板 |\n|------|---------|\n| 未指定产品类型 | \"您想了解哪类保险产品？（重疾险/医疗险/意外险/寿险/年金险）\" |\n| 未指定产品名称 | \"您是否有具体想了解的产品名称？或告诉我您的保障需求，我为您推荐。\" |\n| 未提供年龄 | \"查询保费需要知道被保险人年龄，请问是____岁？\" |\n| 未提供性别 | \"请问被保险人是男性还是女性？\" |\n| 未提供保额 | \"您计划投保多少保额？（如50万、100万）\" |\n| 产品版本不明 | \"该产品有多个版本，您想了解的是：A.2024版 B.2023版 C.不清楚\" |\n| 问题意图不明 | \"您是想：A.对比两款产品 B.分别了解两款产品 C.了解其中一款\" |\n\n## Gotchas（反问模块陷阱）\n\n1. **过度反问**\n   - 陷阱：对用户明确的问题仍反复确认\n   - 示例：用户明确问\"平安福2024版重疾险\"，仍反问\"您想了解哪款产品\"\n   - 防护：先判断问题是否明确，明确的问题直接进入处理流程\n\n2. **反问过于宽泛**\n   - 陷阱：反问问题让用户更难回答\n   - 示例：\"请详细描述您的需求\"（用户不知道从何说起）\n   - 防护：提供具体选项，降低用户回答难度\n\n3. **忽视用户上下文**\n   - 陷阱：每次反问都从零开始，不利用已有信息\n   - 示例：用户已说\"30岁男性\"，反问时仍问年龄\n   - 防护：反问前总结已确认信息，避免重复提问\n\n4. **反问语气生硬**\n   - 陷阱：反问像审问，影响用户体验\n   - 示例：\"请提供：1.产品名称 2.年龄 3.性别...\"\n   - 防护：使用礼貌、引导性的语言，解释为什么需要这些信息\n",
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/references/uncertain.md"
}
```

**Output:**
```
Wrote file successfully.
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 77.5s)

_Thinking:_

                            现在更新format.md。根据用户的要求，这个文件应该在references目录下（而不是assets）。让我先检查assets/format.md是否存在。

                            现在检查并更新format.md。用户说原来在@assets/format.md，但按Skill最佳实践应该放在references目录下：

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/assets/format.md"
}
```

**Output:**
```
<path>/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/assets/format.md</path>
<type>file</type>
<content>1: # 输出格式规范
2: 
3: ## 目标
4: 确保不同来源的信息清晰可区分，保险信息准确规范，外部信息来源可追溯。
5: 
6: ## 通用格式原则
7: 
8: ### 信息来源标记（强制）
9: 
10: 所有答案必须在关键信息点标注来源类型：
11: 
12: | 标记 | 含义 | 使用场景 |
13: |-----|------|---------|
14: | 【内部资料】 | 来自内部保险工具 | 条款、费率、理赔规则等 |
15: | 【网络信息，仅供参考】 | 来自外部搜索 | 新闻、市场动态、第三方评价 |
16: | 【系统推测】 | LLM 基于已有信息的合理推断 | 逻辑分析、建议类内容（必须明确标注） |
17: 
18: ### 时间戳标注（强制）
19: - 保险条款：标注条款版本/生效日期（如【内部资料，2024版条款】）
20: - 外部信息：标注信息获取时间（如【网络信息，2025-03-27，仅供参考】）
21: 
22: ## 场景 1：纯保险产品问答（仅内部工具）
23: 
24: ### 格式模板
25: 
26: ```markdown
27: **问题**：[用户原始问题]
28: 
29: **答案**：
30: 
31: 【内部资料】[具体答案内容]
32: 
33: **详细信息**：
34: - 产品名称：[官方完整名称]
35: - 条款依据：[具体条款编号，如"第3.2条"]
36: - 数据更新时间：[系统数据版本日期]
37: 
38: **温馨提示**：
39: - [相关注意事项，如"具体以保险合同为准"]
40: - [下一步建议，如"如需投保请联系..."]
41: ```
42: 
43: ### 数值呈现规范
44: - **保费**：精确到分，格式 `¥8,500.00/年`
45: - **保额**：格式 `500,000元（50万）`
46: - **百分比**：格式 `100%` 或 `赔付比例：100%`
47: - **日期**：格式 `2025年03月27日`
48: 
49: ### 禁止行为
50: - 不得添加内部工具未提供的营销话术
51: - 不得对费率进行"优惠"、"划算"等主观评价
52: - 不得承诺理赔结果（使用"依照条款规定..."）
53: 
54: ---
55: 
56: ## 场景 2：纯通用知识问答（仅外部搜索）
57: 
58: ### 格式模板
59: 
60: ```markdown
61: **问题**：[用户原始问题]
62: 
63: **答案**：
64: 
65: 【网络信息，仅供参考，[日期]】[综合多个来源的答案]
66: 
67: **信息来源**：
68: 1. [来源1名称]（[URL 域名]，[发布日期]）：[简要说明该来源提供了什么信息]
69: 2. [来源2名称]（[URL 域名]，[发布日期]）：[简要说明]
70: 
71: **免责声明**：
72: 以上信息来源于网络搜索，可能存在时效性或准确性偏差，建议通过官方渠道核实最新信息。
73: ```
74: 
75: ### 多来源冲突处理
76: 如果不同来源信息不一致：
77: 
78: ```markdown
79: **答案**：
80: 
81: 关于 [问题]，不同来源存在不同说法：
82: 
83: 【来源 A，[日期]】[来源A的观点]
84: 【来源 B，[日期]】[来源B的观点]
85: 
86: [如可能，提供背景说明为什么存在差异]
87: 
88: **建议**：[建议用户如何进一步核实]
89: ```
90: 
91: ---
92: 
93: ## 场景 3：混合问答（内部工具 + 外部搜索）
94: 
95: ### 格式模板
96: 
97: ```markdown
98: **问题**：[用户原始问题]
99: 
100: **保险相关信息** 【内部资料】：
101: 
102: [内部工具返回的保险条款、费率等信息]
103: *数据来源：[具体产品名称]，条款版本：[版本号]*
104: 
105: ---
106: 
107: **市场/政策相关信息** 【网络信息，仅供参考，[日期]】：
108: 
109: [外部搜索返回的新闻、政策、市场分析等]
110: 
111: *主要参考：[来源1]、[来源2]*
112: 
113: ---
114: 
115: **综合分析** 【系统推测】：
116: 
117: [基于以上信息的分析建议，必须明确标注为推测]
118: 
119: **重要提示**：
120: - 内部资料部分基于您当前的保单/产品查询
121: - 外部信息部分仅供参考，政策变动请以监管部门最新公告为准
122: - 如涉及保单变更，请联系官方客服核实
123: ```
124: 
125: ### 信息边界标注示例
126: 
127: **用户问题**："我买的XX险最近有什么新闻吗，保障够不够？"
128: 
129: **正确格式**：
130: 
131: ```markdown
132: **您的保单信息** 【内部资料】：
133: - 产品：XX终身寿险（2023版）
134: - 保额：100万元
135: - 保障范围：身故/全残保障
136: 
137: **近期相关新闻** 【网络信息，2025-03-27，仅供参考】：
138: - [新闻标题1]：关于保险行业调整的报道...
139: - [新闻标题2]：XX公司服务升级公告...
140: 
141: **保障分析** 【系统推测】：
142: 基于您的保单信息，当前保障集中在身故/全残责任。如需要重疾、医疗等保障，可能需要额外配置。
143: 
144: ⚠️ **注意**：以上分析仅供参考，具体保障需求建议咨询专业顾问。
145: ```
146: 
147: **错误格式**（混淆边界）：
148: 
149: ```markdown
150: XX险最近有很多负面新闻（没有标注来源），你买的这个保额100万（内部资料）
151: 可能不太够（没有标注这是推测），建议赶紧加保（不当建议）。
152: ```
153: 
154: 
155: ## 特殊场景处理
156: 
157: ### 场景：无法回答时的标准话术
158: 
159: **内部工具无结果**：
160: ```
161: 【内部资料】经查询，暂未找到与"[查询关键词]"相关的保险产品信息。
162: 
163: 可能原因：
164: 1. 产品名称可能有差异（如"超级玛丽" vs "超级玛丽重疾险"）
165: 2. 该产品可能已停售或仅限特定渠道销售
166: 3. 查询条件可能存在限制（如年龄、地域）
167: 
168: 建议：
169: - 核对产品完整名称后重试
170: - 联系客服人工查询：400-XXX-XXXX
171: ```
172: 
173: **需要人工介入**：
174: ```
175: 您的问题涉及 [具体原因，如"复杂的理赔纠纷"/"个性化方案设计"]，超出了自动查询的范围。
176: 
177: 建议：
178: - 拨打客服热线：400-XXX-XXXX（工作日 9:00-18:00）
179: - 在线咨询：[链接]
180: - 前往就近营业厅：[查询方式]
181: 
182: 您可以提供以下信息以便更快获得帮助：
183: - [需要准备的材料清单]
184: ```
185: 

(End of file - total 185 lines)
</content>
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 199.1s)

_Thinking:_

                              现在更新format.md以匹配用户的需求。

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/felixcxr/code/wanxiao_demo/skills/insurance-qa-skill/assets/format.md",
  "newString": "# 输出格式规范\n\n## 目标\n确保输出内容符合用户需求：多产品对比使用表格、先简明后详细、外部信息标注来源、去除工具调用思考过程。\n\n---\n\n## 核心格式原则\n\n### 原则1：去除工具调用思考过程\n\n**禁止输出**：\n- ❌ \"我需要先调用product_content_search查询产品信息...\"\n- ❌ \"让我分析一下应该使用哪个工具...\"\n- ❌ \"工具返回结果如下，让我整理...\"\n\n**正确做法**：\n- ✅ 直接呈现最终答案，不展示中间思考过程\n- ✅ 所有工具调用、分析过程对用户不可见\n\n### 原则2：内部资料不添加特殊标识\n\n**正确做法**：\n- ✅ 直接呈现内部工具返回的信息\n- ✅ 不需要标注【内部资料】或类似标记\n\n### 原则3：外部信息必须标注来源\n\n**格式要求**：\n```markdown\n内容内容内容[^1]内容内容\n\n[^1]: 来源：https://example.com/article-title\n```\n\n**示例**：\n```markdown\n根据市场反馈，平安福2024版在重疾保障方面表现较好[^1]。\n\n[^1]: 来源：https://www.example.com/pinganfu-review-2024\n```\n\n---\n\n## 场景1：单一产品问答\n\n**适用场景**：用户询问某个具体产品的特定问题（如\"XX产品可以保肺结核吗\"）\n\n### 格式要求\n\n1. **先简明扼要回答**：用1-2句话直接回答用户问题\n2. **再详细展开**：提供详细信息、条款依据、注意事项等\n\n### 模板示例\n\n**用户问题**：\"平安福重疾险可以保肺结核吗？\"\n\n```markdown\n**简要回答**：\n平安福重疾险（2024版）将肺结核列为轻症保障责任，赔付比例为基本保额的30%。\n\n**详细说明**：\n\n1. **保障责任**\n   - 责任类型：轻症疾病保险金\n   - 疾病定义：符合条款约定的轻度肺结核\n   - 赔付比例：基本保额的30%\n   - 等待期：90天\n\n2. **条款依据**\n   - 依据《平安福重疾险（2024版）》条款第2.3条轻症疾病定义\n   - 具体疾病定义以保险合同为准\n\n3. **注意事项**\n   - 投保前已患肺结核属于既往症，可能除外承保或拒保\n   - 具体核保结果以实际审核为准\n   - 理赔时需提供完整病历资料和诊断证明\n\n4. **理赔流程**\n   - 确诊后30日内通知保险公司\n   - 提交理赔申请材料\n   - 保险公司审核（通常5-10个工作日）\n   - 赔付到账\n```\n\n---\n\n## 场景2：多产品对比\n\n**适用场景**：用户询问多款产品的对比（如\"A和B哪个好\"、\"对比几款重疾险\"）\n\n### 格式要求\n\n1. **必须使用表格**：涉及多款产品时，关键对比项用表格呈现\n2. **表格后加分析**：表格后提供文字分析和建议\n\n### 模板示例\n\n**用户问题**：\"平安福和国寿福有什么区别？\"\n\n```markdown\n**简要回答**：\n平安福（2024版）和国寿福（至尊版）在重疾保障、轻症赔付、保费方面存在差异，具体如下：\n\n**产品对比**：\n\n| 对比项目 | 平安福（2024版） | 国寿福（至尊版） |\n|---------|------------------|------------------|\n| **重疾保障** | 120种重疾，赔付100%保额 | 100种重疾，赔付100%保额 |\n| **轻症保障** | 40种轻症，赔付30%保额 | 30种轻症，赔付20%保额 |\n| **中症保障** | 20种中症，赔付50%保额 | 无中症保障 |\n| **等待期** | 90天 | 180天 |\n| **30岁男性50万保额年缴保费** | ¥12,500 | ¥11,800 |\n| **特色责任** | 运动达标增额 | 特定疾病额外赔付 |\n\n**详细分析**：\n\n1. **保障范围**\n   - 平安福重疾种类更多（120种 vs 100种）\n   - 平安福包含中症保障，国寿福无此责任\n   - 轻症赔付比例平安福更高（30% vs 20%）\n\n2. **投保规则**\n   - 平安福等待期更短（90天 vs 180天）\n   - 两款产品投保年龄范围相同（18-55周岁）\n\n3. **保费对比**\n   - 国寿福年缴保费略低（约低5-10%）\n   - 但平安福保障范围更广\n\n4. **选择建议**\n   - **注重全面保障**：建议选择平安福\n   - **注重性价比**：国寿福保费更低\n   - 具体选择需结合个人健康状况、预算、保障需求综合考虑\n\n**温馨提示**：\n- 以上信息基于公开产品资料，具体以保险合同条款为准\n- 投保前请仔细阅读条款，特别是免责条款和等待期约定\n- 建议咨询专业顾问获取个性化方案\n```\n\n---\n\n## 场景3：涉及外部信息的问答\n\n**适用场景**：内部资料不足，需要补充外部搜索信息\n\n### 格式要求\n\n1. **内部信息直接呈现**：不添加特殊标识\n2. **外部信息用Markdown引用标注**：使用`[^数字]`格式\n3. **引用来源列在文末**：提供完整URL\n\n### 模板示例\n\n**用户问题**：\"平安福的市场口碑怎么样？\"\n\n```markdown\n**简要回答**：\n平安福（2024版）作为平安人寿的主力重疾险产品，在市场上有较高的知名度，用户评价整体较好[^1]，但也有用户认为保费偏高[^2]。\n\n**产品基本信息**：\n- 产品名称：平安福重疾险（2024版）\n- 保险公司：中国平安人寿\n- 产品类型：终身重疾险\n- 主要特点：重疾+中症+轻症全面保障，运动达标可增额\n\n**市场评价分析**：\n\n1. **正面评价**\n   - 品牌认可度高，理赔服务较好[^1]\n   - 保障责任全面，重疾种类覆盖广\n   - 运动增额功能鼓励健康生活方式\n\n2. **负面反馈**\n   - 保费相对较高，性价比不如部分互联网产品[^2]\n   - 部分用户反映免责条款较严格[^3]\n\n3. **行业对比**\n   - 与传统大公司产品相比，保障范围处于中上水平[^1]\n   - 与互联网保险产品相比，保费偏高但服务网点多[^2]\n\n**综合建议**：\n平安福适合注重品牌、服务网点覆盖、偏好线下服务的客户。如对价格敏感或追求极致性价比，可考虑对比其他产品。\n\n---\n\n**参考来源**：\n\n[^1]: 来源：https://www.xyz.com/insurance-review-2024\n[^2]: 来源：https://www.abc.com/pinganfu-comparison  \n[^3]: 来源：https://www.def.com/user-feedback-pingan\n```\n\n---\n\n## 场景4：销售话术生成\n\n**适用场景**：销售人员询问如何向客户介绍产品或回应异议\n\n### 格式要求\n\n1. **先给核心话术**：1-2句简洁有力的核心卖点\n2. **再给详细话术**：分场景提供完整话术\n3. **标注适用场景**：说明每段话术适合什么场景使用\n\n### 模板示例\n\n**用户问题**：\"怎么跟客户介绍平安福？\"\n\n```markdown\n**核心卖点**（一句话介绍）：\n平安福2024是一款保障全面、可随运动增额的重疾险，120种重疾+20种中症+40种轻症全方位守护您的健康。\n\n**场景话术**：\n\n**场景1：初次介绍**\n> \"张先生，我给您推荐的是我们平安的王牌重疾险——平安福2024版。这款产品最大的特点是保障全、还能'运动涨保障'。它覆盖120种重大疾病，加上中症和轻症，一共180种疾病都有保障。而且如果您坚持运动，保额最高还能增加10%，越健康保障越高。\"\n\n**场景2：应对'保费贵'异议**\n> \"张先生，我理解您觉得保费不便宜。平安福的保费确实比一些互联网产品高一些，但您享受到的是：\n> 1. 平安全国2800多个服务网点，理赔更方便\n> 2. 重疾种类120种，比市场平均水平多20%\n> 3. 运动增额功能，健康还能省钱\n> 4. 30年理赔服务，大品牌更安心\n> 买保险是几十年的承诺，选择稳健的大公司，后续服务更有保障。\"\n\n**场景3：促成话术**\n> \"张先生，重疾险越早买越划算。您现在30岁，身体健康，投保可以标准体承保。如果等过几年体检发现异常，可能就要加费或除外承保了。我建议您今天先确定方案，犹豫期内还有15天时间考虑，不合适可以无损退保。\"\n\n**关键数据速记**：\n- 重疾：120种，100%保额\n- 中症：20种，50%保额  \n- 轻症：40种，30%保额\n- 等待期：90天\n- 运动增额：最高10%\n```\n\n---\n\n## 输出质量检查清单\n\n在返回最终答案前，确认以下检查项：\n\n- [ ] 是否去除了工具调用的思考过程\n- [ ] 涉及多款产品时是否使用了表格\n- [ ] 回答是否先简明扼要，再详细展开\n- [ ] 外部信息是否用`[^数字]`格式标注了来源\n- [ ] 内部资料是否没有添加特殊标识\n- [ ] 数值、日期等关键信息是否准确\n- [ ] 是否包含必要的温馨提示或免责声明\n- [ ] 语言是否通俗易懂，避免过多专业术语\n\n---\n\n## 禁止行为\n\n1. **禁止输出思考过程**\n   - ❌ \"让我先查询一下产品信息...\"\n   - ❌ \"根据工具返回的结果...\"\n\n2. **禁止混淆内外部信息**\n   - ❌ 将外部搜索的营销文章当作内部条款\n   - ❌ 不标注来源就引用外部信息\n\n3. **禁止主观臆断**\n   - ❌ \"这个产品肯定适合您\"\n   - ❌ \"这个产品是最好的选择\"\n   - ✅ \"这个产品适合注重XX的客户\"\n\n4. **禁止过度承诺**\n   - ❌ \"保证能理赔\"\n   - ❌ \"肯定能过核保\"\n   - ✅ \"具体以核保结果为准\"\n\n5. **禁止添加未经确认的信息**\n   - ❌ 工具未返回的信息自行补充\n   - ❌ 使用过时的产品信息\n",
  "oldString": "# 输出格式规范\n\n## 目标\n确保不同来源的信息清晰可区分，保险信息准确规范，外部信息来源可追溯。\n\n## 通用格式原则\n\n### 信息来源标记（强制）\n\n所有答案必须在关键信息点标注来源类型：\n\n| 标记 | 含义 | 使用场景 |\n|-----|------|---------|\n| 【内部资料】 | 来自内部保险工具 | 条款、费率、理赔规则等 |\n| 【网络信息，仅供参考】 | 来自外部搜索 | 新闻、市场动态、第三方评价 |\n| 【系统推测】 | LLM 基于已有信息的合理推断 | 逻辑分析、建议类内容（必须明确标注） |\n\n### 时间戳标注（强制）\n- 保险条款：标注条款版本/生效日期（如【内部资料，2024版条款】）\n- 外部信息：标注信息获取时间（如【网络信息，2025-03-27，仅供参考】）\n\n## 场景 1：纯保险产品问答（仅内部工具）\n\n### 格式模板\n\n```markdown\n**问题**：[用户原始问题]\n\n**答案**：\n\n【内部资料】[具体答案内容]\n\n**详细信息**：\n- 产品名称：[官方完整名称]\n- 条款依据：[具体条款编号，如\"第3.2条\"]\n- 数据更新时间：[系统数据版本日期]\n\n**温馨提示**：\n- [相关注意事项，如\"具体以保险合同为准\"]\n- [下一步建议，如\"如需投保请联系...\"]\n```\n\n### 数值呈现规范\n- **保费**：精确到分，格式 `¥8,500.00/年`\n- **保额**：格式 `500,000元（50万）`\n- **百分比**：格式 `100%` 或 `赔付比例：100%`\n- **日期**：格式 `2025年03月27日`\n\n### 禁止行为\n- 不得添加内部工具未提供的营销话术\n- 不得对费率进行\"优惠\"、\"划算\"等主观评价\n- 不得承诺理赔结果（使用\"依照条款规定...\"）\n\n---\n\n## 场景 2：纯通用知识问答（仅外部搜索）\n\n### 格式模板\n\n```markdown\n**问题**：[用户原始问题]\n\n**答案**：\n\n【网络信息，仅供参考，[日期]】[综合多个来源的答案]\n\n**信息来源**：\n1. [来源1名称]（[URL 域名]，[发布日期]）：[简要说明该来源提供了什么信息]\n2. [来源2名称]（[URL 域名]，[发布日期]）：[简要说明]\n\n**免责声明**：\n以上信息来源于网络搜索，可能存在时效性或准确性偏差，建议通过官方渠道核实最新信息。\n```\n\n### 多来源冲突处理\n如果不同来源信息不一致：\n\n```markdown\n**答案**：\n\n关于 [问题]，不同来源存在不同说法：\n\n【来源 A，[日期]】[来源A的观点]\n【来源 B，[日期]】[来源B的观点]\n\n[如可能，提供背景说明为什么存在差异]\n\n**建议**：[建议用户如何进一步核实]\n```\n\n---\n\n## 场景 3：混合问答（内部工具 + 外部搜索）\n\n### 格式模板\n\n```markdown\n**问题**：[用户原始问题]\n\n**保险相关信息** 【内部资料】：\n\n[内部工具返回的保险条款、费率等信息]\n*数据来源：[具体产品名称]，条款版本：[版本号]*\n\n---\n\n**市场/政策相关信息** 【网络信息，仅供参考，[日期]】：\n\n[外部搜索返回的新闻、政策、市场分析等]\n\n*主要参考：[来源1]、[来源2]*\n\n---\n\n**综合分析** 【系统推测】：\n\n[基于以上信息的分析建议，必须明确标注为推测]\n\n**重要提示**：\n- 内部资料部分基于您当前的保单/产品查询\n- 外部信息部分仅供参考，政策变动请以监管部门最新公告为准\n- 如涉及保单变更，请联系官方客服核实\n```\n\n### 信息边界标注示例\n\n**用户问题**：\"我买的XX险最近有什么新闻吗，保障够不够？\"\n\n**正确格式**：\n\n```markdown\n**您的保单信息** 【内部资料】：\n- 产品：XX终身寿险（2023版）\n- 保额：100万元\n- 保障范围：身故/全残保障\n\n**近期相关新闻** 【网络信息，2025-03-27，仅供参考】：\n- [新闻标题1]：关于保险行业调整的报道...\n- [新闻标题2]：XX公司服务升级公告...\n\n**保障分析** 【系统推测】：\n基于您的保单信息，当前保障集中在身故/全残责任。如需要重疾、医疗等保障，可能需要额外配置。\n\n⚠️ **注意**：以上分析仅供参考，具体保障需求建议咨询专业顾问。\n```\n\n**错误格式**（混淆边界）：\n\n```markdown\nXX险最近有很多负面新闻（没有标注来源），你买的这个保额100万（内部资料）\n可能不太够（没有标注这是推测），建议赶紧加保（不当建议）。\n```\n\n\n## 特殊场景处理\n\n### 场景：无法回答时的标准话术\n\n**内部工具无结果**：\n```\n【内部资料】经查询，暂未找到与\"[查询关键词]\"相关的保险产品信息。\n\n可能原因：\n1. 产品名称可能有差异（如\"超级玛丽\" vs \"超级玛丽重疾险\"）\n2. 该产品可能已停售或仅限特定渠道销售\n3. 查询条件可能存在限制（如年龄、地域）\n\n建议：\n- 核对产品完整名称后重试\n- 联系客服人工查询：400-XXX-XXXX\n```\n\n**需要人工介入**：\n```\n您的问题涉及 [具体原因，如\"复杂的理赔纠纷\"/\"个性化方案设计\"]，超出了自动查询的范围。\n\n建议：\n- 拨打客服热线：400-XXX-XXXX（工作日 9:00-18:00）\n- 在线咨询：[链接]\n- 前往就近营业厅：[查询方式]\n\n您可以提供以下信息以便更快获得帮助：\n- [需要准备的材料清单]\n```"
}
```

**Output:**
```
Edit applied successfully.
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 76.7s)

_Thinking:_

                                现在所有文件都已经更新。让我更新todo列表并给用户一个总结。

                                所有子模块文件都已创建/更新完成。现在更新任务状态：

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "分析参考文章和现有技能目录结构",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "设计主Skill.md（触发条件、任务目标、硬规则）",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "设计子Skill - plan.md（问题拆分与工具调用计划）",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "设计子Skill - tool.md（工具调用执行）",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "设计子Skill - error.md（报错与冲突处理）",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "设计子Skill - uncertain.md（反问模块）",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "设计子Skill - format.md（输出规范）",
      "priority": "high",
      "status": "completed"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "分析参考文章和现有技能目录结构",
    "priority": "high",
    "status": "completed"
  },
  {
    "content": "设计主Skill.md（触发条件、任务目标、硬规则）",
    "priority": "high",
    "status": "completed"
  },
  {
    "content": "设计子Skill - plan.md（问题拆分与工具调用计划）",
    "priority": "high",
    "status": "completed"
  },
  {
    "content": "设计子Skill - tool.md（工具调用执行）",
    "priority": "high",
    "status": "completed"
  },
  {
    "content": "设计子Skill - error.md（报错与冲突处理）",
    "priority": "high",
    "status": "completed"
  },
  {
    "content": "设计子Skill - uncertain.md（反问模块）",
    "priority": "high",
    "status": "completed"
  },
  {
    "content": "设计子Skill - format.md（输出规范）",
    "priority": "high",
    "status": "completed"
  }
]
```



---

## Assistant (​Sisyphus - Ultraworker · k2p5 · 107.7s)

_Thinking:_

                                所有任务都已完成。让我给用户提供一个总结。

                                保险产品问答Skill技能包已设计完成。以下是完整的文件结构和核心内容说明：

## 📁 文件结构

```
skills/insurance-qa-skill/
├── SKILL.md                      # 主入口：触发条件、任务目标、硬规则
├── references/
│   ├── plan.md                   # 计划模块：问题拆分与工具选择逻辑
│   ├── tool.md                   # 工具规范：4个工具的调用方式和参数
│   ├── error.md                  # 错误处理：报错/冲突解决机制
│   ├── uncertain.md              # 反问模块：问题澄清与信息补全（新增）
│   ├── gotchas.md                # 坑点清单：常见陷阱
│   ├── suggestions.md            # 关联问题推荐
│   └── validation.md             # 验证模块（已有）
└── assets/
    └── format.md                 # 输出规范：格式要求（已更新）
```

## 🎯 核心设计要点

### 1. **主Skill.md**
- **触发条件**：保险条款、产品、费率、理赔、销售话术、产品对比等
- **硬规则**：
  - 问题拆分原则（多产品/对比/混合信息必须拆分）
  - 工具选择优先级（内部工具优先，web_search仅作补充）
  - 未指定产品时默认优先查询平安产品
  - 去除工具调用的思考过程

### 2. **Plan模块**（references/plan.md）
- 问题拆分策略和识别矩阵
- 工具选择决策树
- 特殊场景处理（对比类、混合信息、条件依赖）
- 执行计划生成模板

### 3. **Tool模块**（references/tool.md）
基于您图片中的工具信息，定义了4个工具：

| 工具 | 用途 | 关键参数 |
|------|------|---------|
| `product_content_search.py` | 保险产品内容检索 | `--productContent`, `--contentType`, `--effectiveState` |
| `product_attribute_detail.py` | 保险产品属性详情 | `--productName`/`--productCode`, `--attributeType` |
| `product_tool_interface.py` | 产品工具接口 | `--mktProdCode`, `--requestFields` |
| `web_search.py` | 网页搜索（外部补充） | `--question` |

### 4. **Uncertain模块**（references/uncertain.md，新增）
5种必须反问的情况：
- 未明确保险产品大类
- 产品名称模糊或不存在
- 需要确认关键参数（年龄、保额等）
- 多个产品同名需确认版本
- 问题意图不明确

### 5. **Error模块**（references/error.md）
- 5类错误处理策略（工具失败、数据缺失、信息冲突、返回不完整、逻辑不一致）
- 内部工具优先级高于外部搜索
- 重试策略矩阵

### 6. **Format模块**（assets/format.md）
按照您的TODO要求：
- ✅ 去除工具调用的思考过程
- ✅ 内部资料不添加特殊标识
- ✅ 外部信息以Markdown引用格式标注来源（`[^1]: 来源：URL`）
- ✅ 涉及多款产品时使用表格对比
- ✅ 回答先简明扼要，再详细展开
- ✅ 未指定产品时默认先走平安产品

## 📋 工作流程

```
用户问题
    ↓
是否明确？→ 否 → uncertain.md反问 → 获取澄清
    ↓ 是
plan.md拆分问题
    ↓
tool.md调用工具（内部优先，外部补充）
    ↓
成功？→ 否 → error.md错误处理
    ↓ 是
format.md格式化输出
    ↓
返回最终答案（无思考过程）
```

## 💡 关键特性

1. **渐进式披露**：采用分层信息架构，按需加载reference文件
2. **硬规则保护**：工具选择优先级、信息冲突处理、输出格式规范
3. **Gotchas陷阱清单**：每个模块都包含常见错误和避免方法
4. **质量检查清单**：输出前的自我检查项

这套Skill设计覆盖了您的全部需求，可以直接在`skills/insurance-qa-skill/`目录下使用。

---

