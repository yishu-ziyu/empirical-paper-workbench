# ai-agent-book 密提取：引言 + 第1–3章

> **来源根路径：** `/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book/book/`
>
> **覆盖文件：**
> - `introduction.md`（引言）
> - `chapter1.md`（AI Agent 入门）
> - `chapter2.md`（上下文工程）
> - `chapter3.md`（用户记忆和知识库）
>
> **提取重点：** harness 公式、loop、context、tools、memory。每条关键主张附路径锚点（`文件:主题/行附近`）。路径用仓库相对 `book/` 路径。

---

## 0. 引言定位（`introduction.md`）

### 0.1 书的主张与工作方式

| 主张 | 路径 |
|------|------|
| 目标：把 Agent 设计从“感觉驱动”变成“原则驱动”；不仅跑通 Demo，还要理解每个架构决策的取舍 | `introduction.md` 开篇 |
| 书本身用 **whisper coding**（口述协作）做成：口述提纲 → Agent 调研 → 初稿 → 反馈迭代；语音带宽约打字 4 倍 | `introduction.md` § whisper coding |
| **实践在前，命名在后**：Skill / harness / loop engineering 等名词流行前，头部产品已在做同类事；等名词流行再学就慢了一步 | `introduction.md` L9–L19 |
| 原则穿越模型迭代：好设计描述的是“智能系统与世界交互的基本模式”，不是某版模型的用法 | `introduction.md` L25 |
| 要赶在名词前：① 有能力上限极高、能持续反馈的真实业务；② **必须建立评估（Evaluation）**——没有评估就没有进步 | `introduction.md` L21–L23 |
| Pine 实战倒逼出的先见：动态加载提示词、CLI 工具防列表膨胀、状态栏、类似 Claude Code 的 harness、proposer-reviewer 防过早完成 | `introduction.md` L13–L15 |
| Sutton：Agent 可自举/自我进化；本书使命是理解这种创造原则 | `introduction.md` L27 |

### 0.2 核心公式（全书第一句）

| 主张 | 路径 |
|------|------|
| **Agent = LLM + 上下文 + 工具**；三者缺一不可 | `introduction.md` L29 |
| 直觉映射：**大脑 + 眼睛 + 手脚**；眼睛类比有局限——上下文里也包括“有哪些手脚可用”（工具定义） | `introduction.md` L31 |
| RL 映射：LLM → Policy；上下文 → Observation Space；工具 → Action Space | `introduction.md` L35 |
| 全书结构四层：① 基础框架 ② 构建（上下文/知识/工具/代码）③ 评估与进化 ④ 多模态与多 Agent | `introduction.md` L39–L52 |
| 时间有限优先：第1章全局 + **第2章上下文工程（最重要）**；KV Cache 原理可先跳过，只记三条结论 | `introduction.md` L59 |
| 术语：reasoning 译“思考”；inference 译“推理”；例外保留“逻辑推理/多跳推理”等习惯用法 | `introduction.md` L77 |

---

## 1. Harness 公式与工程观

### 1.1 组成公式（两层）

| 主张 | 路径 |
|------|------|
| 内部组成：**Agent = LLM + 上下文 + 工具** = 大脑 + 眼睛 + 手脚 | `chapter1.md` L11–L19；`introduction.md` L29 |
| 生产形态展开：**Agent = LLM + [上下文 + 工具 + 约束 + 验证 + 纠正] = Model + Harness** | `chapter1.md` L250–L256 |
| 最小可工作 = LLM + 上下文 + 工具（Demo）；生产长期可靠 = 再补 **Constrain / Verify / Correct** | `chapter1.md` L256 |
| Harness 原意“马具/赛车保障”：不限制能力，而是把不可预测的力量引导成可靠执行；模型越强，Harness 越关键 | `chapter1.md` L117；L262 |
| Harness 的**核心**是“上下文 + 工具”；约束/验证/纠正是围绕它们的保障层，不是平行第三方模块 | `chapter1.md` L250–L272 |
| 模型之外的全部基础设施都属于 Harness | `chapter1.md` L264 |

### 1.2 Harness 五功能

| 功能 | 一句话 | 与上下文/工具关系 | 核心原则 | 详见 | 路径 |
|------|--------|-------------------|----------|------|------|
| Context | 提供感知信息 | 核心能力 | 信息充分性 | 第2–3章 | `chapter1.md` L266–L272；L300–L310 |
| Tools | 提供行动手段 | 核心能力 | 接口清晰（命名直观、参数有例、边界有说明） | 第4章 | 同上 |
| Constrain | 设定行为边界 | 围绕上下文/工具的安全边界 | 故障安全默认：能力默认关，显式开放 | 第4章 | 同上 |
| Verify | 判断结果对错 | 围绕工具结果的检查 | 输入隔离：安全检查看结构化数据，不看模型自由文本 | 第5–6章 | 同上 |
| Correct | 修正或回退 | 围绕工具失败的恢复 | 确认无法恢复前不暴露中间态；静默重试→熔断→人工 | 第2、5章 | 同上 |

**闭环：** 上下文+工具支撑决策 → 约束预防 → 验证发现 → 纠正闭合；缺一则有可靠性缺口（`chapter1.md` L312）。

**退款例子（无/有 Harness）：** 无 = 缺上下文政策、缺工具、编造退款、无纠正；有 = 系统提示词写 7 天政策、`query_order`/`process_refund`、金额≤订单约束、库状态验证、超时重试（`chapter1.md` L260）。

### 1.3 能力更新三层（与 Harness 关系）

| 层 | 含义 | 路径 |
|----|------|------|
| **上下文适应** | 任务内：示例/状态/检索进上下文，会话结束不持久 | `chapter1.md` L125–L135 |
| **外部产物（artifact）** | 跨任务：知识文档、Prompt/Skill、程序与 Harness；可审计可修订 | 同上 |
| **参数更新** | 后训练内化高维/隐式能力 | 同上 |
| 三条路径协同不同时间尺度：临场 / 可控积累 / 内化 | 同上 |

### 1.4 “模型即 Agent” vs Harness 会被吃掉？

| 主张 | 路径 |
|------|------|
| 后训练（尤其 RL）把工具调用决策内化为原生能力；编排循环可从客户端移到服务端 | `chapter1.md` L115–L119；实验1-2/1-3 |
| **RL 内化的是决策策略，不是工具执行机制**（搜索/沙盒仍在框架/API） | `chapter1.md` L222–L226 |
| 模型越强，外围 Harness 越关键；厂商优势 = 模型与 Harness 协同优化 | `chapter1.md` L117–L119 |
| 对 Sutton《苦涩的教训》立场：**方向认同，节奏务实**——模型会逐步吃掉 Harness，但训练以月计且无法一次内化全部业务约束；**模型此刻边界 = Harness 此刻价值**；模型内化一层，Harness 卸一层并兜底新前沿 | `chapter1.md` L121 |

### 1.5 工程范式演进弧

```
软件工程
  ⊂ 提示工程（优化输入指令）
    ⊂ 上下文工程（管理模型能看到的全部信息）
      ⊂ Harness 工程（约束/验证/反馈/恢复等模型外全部）
        ⊂ Loop 工程（跨轮持续自主：谁发现下一件事、何时验证、何时算完成；第10章）
```

| 主张 | 路径 |
|------|------|
| 五阶段层层包含，非替代；模型能力商品化后，竞争优势在模型外工程 | `chapter1.md` L288–L298 |
| LangChain Terminal Bench：52.8%→66.5%（改 Harness 非改模型）；OpenAI 3 工程师 5 个月约百万行 ≈10× 速度，背后是 Harness | `chapter1.md` L298 |
| **Graph 工程**（2026-07 讨论）：节点/类型化边/可检查点状态；**不是** Loop 的替代，也非简单“第六层”；循环本身是带回边的图；名称未稳定，本书视为对既有编排与 Harness 的新称呼 | `chapter1.md` L294–L296 |
| Claude Code 经验：Harness 大部分代码在约束/验证/纠正（流程状态、多层压缩、权限、熔断、错误恢复），不是工具本身 | `chapter1.md` L278–L286 |
| 行业从“能做事”→“可靠地做事”；Harness = 核心竞争力 | `chapter1.md` L286 |

### 1.6 构建原则与 ACI

| 原则 | 内容 | 路径 |
|------|------|------|
| 保持简单 | 从最简方案起；API 调用 > 厚框架；清晰代码 > 聪明抽象 | `chapter1.md` L317–L323 |
| 保持透明 | 显示规划/日志/轨迹；黑箱错误无法外定位 | 同上 |
| **ACI（Agent-Computer Interface）** | 从 Agent 视角设计接口；防呆（Poka-yoke）；模糊接口会被模型放大成系统性错误 | 同上 |
| 模型选择 | 先在自己任务上评；多数 Agent 需**思考（Reasoning）**模型；关注输出速度与多模态；御三家+国内+开源权衡 | `chapter1.md` L327–L341 |

### 1.7 护栏 = Harness 的约束/验证/纠正落地

| 层 | 机制 | 路径 |
|----|------|------|
| 输入侧 | 相关性/安全分类器、内容审核、规则（黑名单/长度/正则）；越狱 vs 提示注入区分 | `chapter1.md` L417–L425 |
| 执行侧 | 工具风险评级（可逆性/权限/财务）；高风险人工确认 | 同上 |
| 输出侧 | PII 过滤、品牌一致验证 | 同上 |
| 分层防御 | 单护栏不够；Constitutional Classifiers：规则宪法 + 上下文联合判断 + 两级筛查 | `chapter1.md` L413–L429 |
| 人工干预 | 超过失败阈值；高风险不可逆操作 | `chapter1.md` L431–L443 |

### 1.8 全书章节 ↔ Harness 映射

| Harness 重点 | 章节 | 路径 |
|--------------|------|------|
| 上下文设计 | 第2章 | `chapter1.md` L451–L461 |
| 上下文扩展（知识持久化） | 第3章 | 同上 |
| 工具设计与安全约束 | 第4章 | 同上 |
| 工具的验证与纠正 | 第5章 | 同上 |
| 系统级验证 | 第6章 | 同上 |
| 模型层面的纠正 | 第7章 | 同上 |
| 经验驱动持续纠正 | 第8章 | 同上 |
| 多模态上下文与工具 | 第9章 | 同上 |
| 多 Agent 约束与纠正 | 第10章 | 同上 |

Anthropic 长任务：初始化 Agent + 执行 Agent + 清晰交接产物，解决上下文耗尽与过早完成（`chapter1.md` L463）。

---

## 2. Loop（循环 / 编排 / ReAct）

### 2.1 ReAct 定义

| 主张 | 路径 |
|------|------|
| **ReAct = Reasoning + Acting**；实际三环：**思考 → 行动（工具）→ 观察 → 再思考…** 直到完成 | `chapter1.md` L161–L165 |
| 工具调用四步：声明工具 → 模型决定调用 → 结果追加上下文 → 模型基于结果决策；是 ReAct 基础 | `chapter1.md` L75–L97 |
| **轨迹（trajectory）** = 动态消息历史：user + assistant（reasoning/content/tool_calls）+ tool results | `chapter1.md` L167–L213 |
| **Agent 的上下文 = 静态前缀 + 轨迹**；静态前缀 = 系统提示词 + 工具定义；轨迹 = 后三项 | `chapter1.md` L167；`chapter2.md` L363 |
| 每次 LLM 调用看到完整轨迹 → 全局任务认知、可解释、可调试；轨迹可进知识库/RL | `chapter1.md` L213–L215 |
| 多币种例子：3 次迭代、4 次工具调用；可并行转换再 code_interpreter | `chapter1.md` L169–L211 |
| API 实现：`请求 → tool_calls → 框架执行 → tool 消息回传 → 再请求`；无 tool_calls 则最终回复退出 | `chapter2.md` L86–L236；L292–L318 |
| **模型决策，框架执行**；模型可一次输出多个 tool_calls → 无依赖时并行 | `chapter2.md` L174；L393 |
| 生产循环需 **max_iterations** 上限，否则可能永远重复同一工具 | `chapter2.md` L293–L295 |
| Agent 框架核心工作 = **管理 messages 列表**并整表送模型 | `chapter2.md` L355 |

### 2.2 编排：工作流 vs 自主 Agent

| 模式 | 定义 | 优势 | 局限 | 路径 |
|------|------|------|------|------|
| **工作流** | 预定义代码路径编排 LLM+工具；节点间顺序写死 | 严格流程控制；攻击面限单节点 | 难覆盖未预设变通 | `chapter1.md` L350–L365 |
| **自主 Agent** | 执行路径由**环境反馈**实时决定 = ReAct 循环 | 开放式问题、SWE-bench、Computer Use、研究 | 成本高、复合错误；需停止条件 | `chapter1.md` L367–L381 |
| 停止条件 | 最终输出工具 / 无 tool_calls 响应 / 错误 / 最大轮次 | — | 否则死循环或过度执行 | `chapter1.md` L373–L375 |
| 混合 | 合规关键段用工作流，灵活段用自主；如 n8n | — | — | `chapter1.md` L383–L385 |
| 选型原则 | 单次 LLM 调用 → 工作流 → 最后才自主；Agent 用延迟/成本换性能 | — | — | `chapter1.md` L348 |

### 2.3 Loop 工程（更高一层）

| 主张 | 路径 |
|------|------|
| Loop 工程：从单次运行扩展到跨轮持续自主——谁发现下一件该做的事、何时验证、何时真正完成 | `chapter1.md` L292；`chapter2.md` L865 |
| 状态栏理论与 Loop 的接点：循环有真进步因为**验证把外部世界观测写回上下文**（模型自己想不出来的信息）；抽掉验证 = 旧信息原地重排；“瓶颈在验证器不在模型” | `chapter2.md` L857–L865 |
| Interaction Scaling 第三条轴：**交互**（外部仪器观测）相对“想更久/试更多” | `chapter2.md` L857–L863 |

### 2.4 智能体化 RAG 的 ReAct 形态

| 主张 | 路径 |
|------|------|
| Agentic RAG：检索封装为工具；Agent 以 ReAct 主导“思考→检索→评估→再检索→综合” | `chapter3.md` L574–L590 |
| 非智能体化 = 被动检索-生成管道；智能体化 = 动态迭代探索 | 同上 |
| 简单问题一次检索够用；复杂多跳需多轮 | 实验 3-9，`chapter3.md` L598–L609 |

---

## 3. Context（上下文工程）

### 3.1 定义与上限论

| 主张 | 路径 |
|------|------|
| 上下文 = 每次对话 AI 实际“看到”的全部信息（历史 + 系统指令 + 工具描述等） | `chapter2.md` L1–L3 |
| 上下文工程是 Harness 中“上下文与工具”层面的核心实现 | `chapter2.md` L3 |
| **上下文质量才是 Agent 能力真正上限**；中等模型+精上下文可胜顶级模型+贫信息 | `chapter2.md` L19；`chapter1.md` L473 |
| 编码 Agent 最低信息：实时代码上下文 + 流程规范 + 环境信息 | `chapter2.md` L13–L17 |
| 上下文工程既是技术问题更是**组织问题**（隐性知识黑洞）；远程友好文档文化 = AI 友好 | `chapter2.md` L21–L26 |
| 翁家翌：“人和模型一样，最重要的是 Context”；AI 难取代人的最大原因也是 context 不在同一环境 | `chapter2.md` L28 |
| 扩展观察/动作空间是模型固定时的主要杠杆；必须**按需、相关、可控** | `chapter1.md` L33–L39 |

### 3.2 五个组成部分 + API 角色

| 组件 | 角色/位置 | 动静 | 路径 |
|------|-----------|------|------|
| 系统提示词 | `role: system` | 静态前缀 | `chapter1.md` L139–L147；`chapter2.md` L36–L47 |
| 工具定义 | 请求顶层 `tools`（非消息角色） | 静态前缀（基础模式） | 同上 |
| 用户消息 | `user`；可含 RAG 外部知识 | 动态轨迹 | 同上 |
| 模型回复 | `assistant`：reasoning / content / tool_calls | 动态轨迹 | 同上 |
| 工具执行结果 | `role: tool` + `tool_call_id` | 动态轨迹 | 同上 |

| 主张 | 路径 |
|------|------|
| 四种消息角色 + `tools` 字段 = 五个组成部分 | `chapter2.md` L47 |
| **每次 API 调用无状态**；必须把完整历史送回 | `chapter2.md` L84；L216–L220 |
| 结构洞见：**前面不能动、后面可以压缩** | `chapter2.md` L363 |

### 3.3 消融实验 1-1（组件不可缺）

| 去掉什么 | 后果 | 路径 |
|----------|------|------|
| 工具定义 | 完全丧失行动能力 | `chapter1.md` L149–L159 |
| 工具执行结果 | 盲目执行、无限循环 | 同上 |
| 思考过程（reasoning） | 前后决策矛盾 | 同上 |
| 历史消息 | 失忆、重做已完成步骤 | 同上 |
| 系统提示词 | 不参与消融（无角色认知测试无意义） | 同上 |
| **核心洞察：Agent 只能基于它看到的信息做决策** | 同上 |

### 3.4 KV Cache / Prompt Cache（架构约束）

**三条必须记住的实践结论**（`chapter2.md` L412–L418）：

1. **系统提示词和工具定义一旦确定就不要改**（多一空格也整段失效）
2. **动态信息永远追加到末尾**（时间戳、用户状态等）
3. **使用标准 API 格式，不要自行拼接消息**

| 主张 | 路径 |
|------|------|
| KV Cache 前提：前缀字节级不变；改一字 → 全层缓存重算 | `chapter2.md` L404–L505 |
| 无缓存 prefill 注意力 ~ 平方级；有缓存省历史 K/V 投影，但注意力仍线性扫缓存 | `chapter2.md` L495–L503 |
| **KV Cache**（单次推理内）vs **Prompt Cache**（跨 API 请求前缀复用）；Prompt Cache 经济影响更大 | `chapter2.md` L523–L527 |
| 错误模式：动态系统提示词时间戳、动态用户配置、工具定义动态排序、滑动窗口丢结果、文本格式化破坏角色 | 实验 2-3，`chapter2.md` L507–L521 |
| 滑动窗口破坏前缀 + 丢工具结果 → 反复同一工具调用 | 同上 |
| 缓存作架构约束：提示词结构由缓存边界决定；子 Agent 与父字节级对齐；工具结果替换字符串首次冻结 | `chapter2.md` L529–L543 |
| 研究前沿：KV 可编辑/可组合（CoT 传播、RoPE 拼块）；生产仍默认遵守“前缀不动” | `chapter2.md` L545–L555 |
| 工具 schema 延迟加载：完整 schema **追加末尾** 不破坏已缓存 K/V；只增不改；只在发现那一轮追加，此后固定位置 | `chapter2.md` L646–L654 |

### 3.5 Chat Template

| 主张 | 路径 |
|------|------|
| API 结构化消息 → 线性 token 流；特殊标记分角色边界 | `chapter2.md` L473–L491 |
| 绕过标准角色会破坏思维链保留（工具结果误标 user → 清理思考） | 同上 |
| 行业从“剥离历史 CoT”转向“强制回传 reasoning_content”：**思考是状态不是废料**（DeepSeek V4 / Kimi K2 / GLM-5 / Claude thinking block） | `chapter2.md` L489 |

### 3.6 提示工程

| 主张 | 路径 |
|------|------|
| 检验标准：聪明新员工读完还不知道怎么做 → Agent 也不知道 | `chapter2.md` L569 |
| 语气：大写强调关键约束；过度稀释 | `chapter2.md` L573–L575 |
| 结构：XML 精确语义 + Markdown 组织逻辑 | `chapter2.md` L577–L581 |
| **流程驱动 vs 规则堆砌**：SOP 步骤优于上百条零散规则 | `chapter2.md` L583–L610 |
| 业务规则必须细化到可执行；PM 设计规则，工程师编码；勿给模型过多业务裁量权 | `chapter2.md` L612–L630 |
| Few-shot：难用规则描述时用 2–3 个高质量例；示例字节级稳定，勿每请求动态检索示例（破缓存） | `chapter2.md` L632–L638 |
| 工具定义：使用边界、具体例、性能提示、工具协作关系（详见第4章） | `chapter2.md` L640–L644 |
| 消融：信息组织打乱 → 成功率 **>30%↓**；去工具描述 → 调用错误率 **+45%**；语气影响有限 | 实验 2-4，`chapter2.md` L658–L670 |

### 3.7 提示注入（上下文安全）

| 主张 | 路径 |
|------|------|
| 外部内容伪装指令混入上下文劫持行为；Agent 有工具 → 比聊天危险 | `chapter2.md` L673–L679 |
| 防御：来源标记、结构化角色、输入清洗（辅助） | `chapter2.md` L681–L685 |
| Skills / 状态栏本身是新注入面（高信任） | `chapter2.md` L687 |
| 上下文层只是第一道防线；执行层/知识库投毒另章 | `chapter2.md` L689；`chapter3.md` L592 |

### 3.8 Agent Skills（动态提示词 / 渐进式披露）

| 主张 | 路径 |
|------|------|
| 问题：静态提示词膨胀 → 浪费 token + **注意力稀释** | `chapter2.md` L712–L717 |
| Skill = 可按需加载的领域知识包；**渐进式披露** | `chapter2.md` L719–L721 |
| **L1 元数据** `SKILL.md` frontmatter name+description（数百 token 常驻）；description 写 **Use when / Don't use when + 反例**（反例关键） | `chapter2.md` L725–L727 |
| **L2 核心流程** 按需加载完整 SKILL.md 作 tool result | `chapter2.md` L729 |
| **L3 细则** 子文档/脚本/模板再深入 | `chapter2.md` L733–L735 |
| 实现三方式：① 注入 system（遵循强、破缓存）② 普通文件中间位置（缓存友好、指令遵循要求高）③ **生产：元数据路由 + 专用工具加载全文** | `chapter2.md` L741–L755 |
| “对 KV 友好”= 一次性写入永久受益，非零成本 | `chapter2.md` L765 |
| Skills vs 工具：Skill+通用执行器可避免工具定义膨胀破坏前缀 | `chapter2.md` L767–L769 |
| 对齐厂商训练方法论：用 Claude 就用 Skills 等其优化过的交互约定 | `chapter2.md` L739 |

### 3.9 Agent 状态栏（Context Distillation）

| 主张 | 路径 |
|------|------|
| 在上下文**末尾**注入动态元信息（进度/环境/工具计数）；类手机状态栏 | `chapter2.md` L787–L798 |
| 理论：上下文学习更像**检索而非推理**；上下文窗口是“只有一半的检索引擎”——缺提炼层 | `chapter2.md` L800–L804；L977–L994 |
| 把隐式状态提炼为显式知识；操纵注意力（末尾高权重）；抗位置偏好/中部衰减 | `chapter2.md` L812–L816 |
| 量化：弱模型准确率 +40–54pp；强模型思考量/延迟/花费 ~ 一个数量级；思考量从随 N 增长变恒定 | `chapter2.md` L837–L841 |
| **三条工程经验：** ① 状态栏用**代码**维护，勿让 LLM 批量统计 ② 删原文前确认状态栏覆盖全部问法（有损投影；缺维则假权威）③ 状态栏准确率作生产指标——模型几乎无条件相信状态栏 | `chapter2.md` L847–L851 |
| 更深：状态栏注入模型**想不出来**的外部观测（Harness = 仪器） | `chapter2.md` L857–L861 |
| 构成：任务规划 TODO、侧信道、环境状态、可用能力清单 | `chapter2.md` L867–L877 |
| API：**user 角色消息**挂末尾（Harness 借用槽位，非终端用户输入）；勿改 system | `chapter2.md` L881–L910 |
| 更新两种：每轮替换（整洁、破末尾缓存）vs 持久追加（Claude Code system-reminder；陈旧累积） | `chapter2.md` L912–L920 |
| 实验 2-8：时间戳、工具计数、TODO、详细错误、系统状态；协同涌现 | `chapter2.md` L922–L938 |
| 时间感三轴：紧迫度 / 坚持度 / 警觉度；**只给读数不够，需操作策略手册**（+19–+49pp） | `chapter2.md` L941–L953 |

### 3.10 上下文压缩

| 主张 | 路径 |
|------|------|
| 双动机：① 长度/成本 ② **总结后知识更利于使用**（即使窗口未满） | `chapter2.md` L965–L975 |
| 状态栏 = 把结论**加**进上下文；压缩 = 把原文**换成**结论；同一枚硬币 | `chapter2.md` L981 |
| **上下文腐化（Context Rot）** ≠ 溢出：装得下但找不到；信息密度不对 | `chapter2.md` L996 |
| Karpathy：记忆差可是特性——迫使抽象 | `chapter2.md` L998 |
| 设计原则：主动提炼结构化知识，勿被动大海捞针 | `chapter2.md` L1000 |
| 与 KV 关系：两次 API 间预处理；静态前缀永不压；压 tool results → 替换点后缓存失效；宜阈值批量压 | `chapter2.md` L1006–L1014 |
| 六策略对比：无压溢出；非任务感知碎片；**上下文感知**最优（7 iter / 40k tok / ~3%）；带引用溯源；自适应 80% 触发 | 实验 2-9，`chapter2.md` L1018–L1036 |
| 生产五层：工具结果预算 → 噪声直删 → API 微压缩 → 归档式摘要 → 全量压缩+熔断 | `chapter2.md` L1043–L1053 |
| 四原则：价值非均匀、语义完整、任务相关、压缩即理解 | `chapter2.md` L1055–L1062 |
| 保留优先级：架构决策/约束不得摘要；改文件列表；验证状态；TODO；工具输出可只留 pass/fail；标识符原样 | `chapter2.md` L1070–L1078 |
| **隔离优于压缩**：子 Agent 探索，主上下文只收结论；噪声不进主 KV | `chapter2.md` L1080–L1086 |

### 3.11 注意力与位置偏好

| 主张 | 路径 |
|------|------|
| Query/Key/Value；热力图三角形（因果） | 实验 2-2，`chapter2.md` L422–L469 |
| Attention Sink：首 token 可吸 >70% 注意力 | 同上 |
| **Lost in the Middle**：关键信息放开头或结尾 | 同上 + 文献注 |
| 长思维链与工具调用强依赖 In-Context Learning | 同上 |

### 3.12 第2章收束

| 主张 | 路径 |
|------|------|
| 给模型看什么、怎么组织，比模型多聪明更影响结果 | `chapter2.md` L1090 |
| 新概念仍落在五个组成部分骨架：Skills→tool result；压缩→轨迹精炼；状态栏=user 槽位上的元信息注解 | `chapter2.md` L1094 |
| 本章 = 任务内状态；第8章 = 跨任务持久进化 | `chapter2.md` L1092 |

---

## 4. Tools（工具）

> 第1章建立分类与调用循环；第2章工具定义/延迟加载/状态栏与工具计数；第3章知识检索工具化。完整工具设计在第4章（本提取只覆盖 intro–ch3 内主张）。

### 4.1 定义与五类

| 类 | 作用 | 路径 |
|----|------|------|
| **感知** | 搜索/文件/API/DB 获取信息 | `chapter1.md` L61–L73 |
| **执行** | 改世界：代码、文件、命令、API | 同上 |
| **协作** | 子 Agent、人类确认、多 Agent 协调 | 同上 |
| **事件触发** | 非主动调用：邮件/定时/Webhook 驱动启动 | 同上 |
| **用户沟通** | 消息/语音/邮件传进展与关怀 | 同上 |

| 主张 | 路径 |
|------|------|
| 无工具只能纸上谈兵 | `chapter1.md` L59 |
| 接口不清 → 乱用；错误处理差 → 死锁；权限太宽 → 难挽回 | `chapter1.md` L73 |
| MCP 让接入像装插件 | `chapter1.md` L73 |
| **通用基础能力用于组合探索；专用工具约束高风险/强业务规则** | `chapter1.md` L99–L103 |
| 通用代码解释器需沙盒、默认无网、路径限制、资源上限 | `chapter1.md` L99 |
| 长程任务：受控虚拟工作目录保存计划/中间结果/日志/产物 | `chapter1.md` L101 |
| 开放式动作空间 + 内部思考 + 持续交互 = 现代 Agent 共性 | `chapter1.md` L55 |

### 4.2 观察/动作空间产品例

| 产品 | 扩展含义 | 路径 |
|------|----------|------|
| Manus | 合并 Deep Research / Coding / Computer Use 空间；后接 Drive/本地 | `chapter1.md` L35–L37 |
| OpenClaw | 消息渠道 + 本地优先 Gateway；更大数字生活边界 | 同上 |
| Cursor / Deep Research / Browser / 豆包 / Pine | 表：眼睛/手脚/策略 | `chapter1.md` L47–L53 |

### 4.3 工具调用与原生 Agent

| 主张 | 路径 |
|------|------|
| 开发者定义+执行；模型决策是否/哪个/参数 | `chapter1.md` L75–L97 |
| Kimi K3：RL 原生工具决策；长链 200–300 次调用稳定；Formula 服务端跑官方工具 | 实验 1-2，`chapter1.md` L220–L228 |
| GPT-5.6：内置 web_search/code_interpreter；自由格式工具调用；意图澄清 | 实验 1-3，`chapter1.md` L230–L240 |
| 工具延迟加载：OpenAI `tool_search`/`defer_loading`；Anthropic Tool Search；Codex `tool_search` 默认开 | `chapter2.md` L646–L650 |

### 4.4 编排中的工具组织

| 主张 | 路径 |
|------|------|
| 编排模式 = Harness 里上下文与工具的组织方式 | `chapter1.md` L344 |
| 框架表：Agents SDK / Claude Agent SDK / LangGraph / n8n / Dify / CrewAI / OpenClaw | `chapter1.md` L389–L401 |
| 框架价值转向：上下文管理、工具生态、安全、错误恢复，而非只编排调用 | `chapter1.md` L403 |

---

## 5. Memory（用户记忆与知识库）

### 5.1 双尺度问题

| 主张 | 路径 |
|------|------|
| **用户记忆** = 个体个性化；**知识库** = 群体共享领域知识 | `chapter3.md` L1–L7 |
| 同一问题两尺度；共享向量检索/压缩；共有冲突、过期、检索不准 | 同上 |
| 第2章单次会话 → 第3章跨会话持久化 | `chapter3.md` L9 |
| 用户记忆 vs 上下文学习：持久可审查 vs 临时会话结束消失 | `chapter3.md` L19 |

### 5.2 提取特征与评估

| 主张 | 路径 |
|------|------|
| 会话后专用 LLM 提取：选择性 / 抽象化 / 结构化 | `chapter3.md` L33–L43 |
| 八项能力归纳 + **三层次评估**：① 基础回忆 ② 多会话检索 ③ 主动服务 | `chapter3.md` L45–L66 |
| LoCoMo 等基准参考 | `chapter3.md` L47 |
| 评估协议：仅凭记忆不可回看原文；LLM-as-a-judge | 实验 3-1，`chapter3.md` L68–L72 |

### 5.3 记忆放哪里（层次）

| 层 | 定义 | 路径 |
|----|------|------|
| **轨迹** | 单次运行完整历史；append-only；即时上下文 | `chapter3.md` L78–L82 |
| **用户长期记忆** | 跨会话；用户 ID 绑定；工具显式读/写 | `chapter3.md` L84 |
| **业务状态** | 任务逻辑阶段（澄清/处理/付款…）；事件驱动重要 | `chapter3.md` L86 |
| 流水账 vs 档案 | 轨迹只增不改；长期记忆可改写合并淘汰 | `chapter3.md` L82 |

### 5.4 四种文本存储格式

| 格式 | 要点 | 路径 |
|------|------|------|
| Simple Notes | 原子事实；O(1)；丢关联 | `chapter3.md` L98 |
| Enhanced Notes | 完整段落；叙事完整；冗余/难更新/难嵌 | `chapter3.md` L100–L102 |
| JSON Cards | 类别→子类→KV；可部分更新；刚性分类丢多维 | `chapter3.md` L104 |
| Advanced JSON Cards | 事实 + backstory + person + relationship + 时间；消歧 | `chapter3.md` L106–L108 |
| 张力 | 简单性 vs 表达力；生产混合：关键少量 Advanced，大量临时 Simple | `chapter3.md` L110–L112 |
| 实验 3-2 | Simple 过 L1；Advanced 消歧/跨会话更好更贵 | `chapter3.md` L114–L118 |

### 5.5 进阶表示谱

| 形态 | 要点 | 路径 |
|------|------|------|
| **User as Code** | 类型化 Python 状态 + 函数约束；记忆阶段日志 + 结构化阶段检查点；聚合/冲突/约束接近 99% vs 文本 6–43% | `chapter3.md` L120–L174 |
| **User as Engram** | 哈希 N-gram 槽位写入；预训练学会何时取用；绕过“存了不会用” | `chapter3.md` L178 |
| **Parametric Multimodal** | 感知向量记忆库；非文字可述；可超编码器检索 | `chapter3.md` L180 |
| 外→内谱 | 外：易更新可审查；内：紧凑即时推理/感知 | `chapter3.md` L182 |

### 5.6 认知类型 × 三套正交分类

| 体系 | 问题 | 类别 | 路径 |
|------|------|------|------|
| 层次 | 存在哪 | 轨迹 / 长期 / 业务状态 | `chapter3.md` L198–L208 |
| 格式 | 怎么存 | Simple…Advanced | 同上 |
| 认知 | 存什么 | 情景 / 语义 / 程序 | 同上 |
| 工作记忆 | 上下文窗口；轨迹是核心，也可含从长期激活的信息 | `chapter3.md` L192；L233–L235 |
| 轨迹 vs 工作记忆 | 轨迹不可变全序列；工作记忆按相关裁剪的动态子集 | `chapter3.md` L235 |

### 5.7 框架案例

| 框架 | 机制 | 路径 |
|------|------|------|
| **Mem0** | 提取 → 向量找近邻 → LLM 决策 ADD/UPDATE/DELETE/NOOP；Mem0-g 图记忆 | `chapter3.md` L214–L222 |
| **Memobase** | Profile 槽位 + Event 时间线；缓冲批处理摊薄成本 | `chapter3.md` L224 |
| 多类型参考架构 | 情景多维元数据 + 语义 + 程序 + 工作记忆交互 | `chapter3.md` L226–L237 |

### 5.8 记忆压缩与隐私

| 主张 | 路径 |
|------|------|
| 重要性评分（频率/时间衰减/情感/独特性）→ 聚类摘要 → 抽象为语义/程序 | `chapter3.md` L239–L247 |
| 冲突：版本化；地址类只留最新，经历类留历史 | `chapter3.md` L249 |
| **存储层整理 ≠ 第2章会话内窗口压缩** | `chapter3.md` L251 |
| 日志脱敏：本地小模型 PII；召回 >95%；混合正则+LLM | 实验 3-3，`chapter3.md` L253–L261 |

### 5.9 RAG 基础管道

| 步骤/技术 | 主张 | 路径 |
|-----------|------|------|
| 流程 | 检索相关片段 → 注入上下文 → LLM 生成 | `chapter3.md` L265–L306 |
| Chunking | 固定大小 / 递归结构 / 语义切分；256–1024 token，重叠 10–20% | `chapter3.md` L314–L328 |
| 稠密嵌入 | 语义向量 + 余弦；Word2Vec 静态 → BERT/BGE 上下文；ANN：ANNOY vs HNSW | `chapter3.md` L330–L374 |
| 稀疏 | TF-IDF → BM25；精确词法；SPLADE 等学习型稀疏 | `chapter3.md` L376–L423 |
| 混合 | 并行 → 归一化加权或 **RRF** → **Cross-Encoder 重排** | `chapter3.md` L425–L437 |
| 指标 | recall@k（书中≈hit rate）、MRR、nDCG；失败率=1−recall@20 类 | `chapter3.md` L441–L453 |
| 多模态摄取 | 原生多模态 / 提文本 / 工具按需深入 | `chapter3.md` L465–L487 |
| 扁平化不足 | 黑猫白猫统计、Xfinity 规则片面：需索引前**提炼** | `chapter3.md` L497–L503 |

### 5.10 结构化组织与 Agentic / Contextual

| 技术 | 主张 | 路径 |
|------|------|------|
| **RAPTOR** | 树状递归摘要；宏观↔细节钻取 | `chapter3.md` L513–L515 |
| **GraphRAG** | 实体-关系；多跳；实体消歧；条件逻辑可能丢失 → 分层互补 | `chapter3.md` L521–L531 |
| 何时结构化 | 跨文档综合/多层次导航才值得；默认混合检索够用 | `chapter3.md` L541 |
| **OpenViking** | 文件系统 URI；**L0/L1/L2** 渐进加载；Markdown+链接索引（像 Wikipedia） | `chapter3.md` L543–L562 |
| 治理 | 增量索引选型；失效元数据过滤；**权限下推检索层**；租户隔离 | `chapter3.md` L564–L572 |
| **Agentic RAG** | 检索=工具；ReAct 迭代 | `chapter3.md` L574–L609 |
| RAG 安全 | 间接注入/知识投毒；来源标记；副作用操作独立授权 | `chapter3.md` L592 |
| **Contextual Retrieval** | 索引前 LLM 前缀锚定上下文；≠ 第2章运行期压缩；失败率可降 49%–67% | `chapter3.md` L630–L652 |
| 记忆上的应用 | 实验 3-10：search_user_memory 迭代；矛盾指令仍难 | `chapter3.md` L613–L626 |
| 实验 3-12 | 上下文前缀解冲突；**双层记忆** = Advanced JSON Cards 常驻概览 + 上下文感知检索取细节 → 支撑主动服务 | `chapter3.md` L656–L671 |
| 结构化数据知识发现 | 案例→JSON→因子重要性；对话式信息收集 | `chapter3.md` L673–L701 |

### 5.11 第3章收束

| 主张 | 路径 |
|------|------|
| 第2–3 章都是“上下文”：会话内 vs 跨会话 | `chapter3.md` L713 |
| 本章沉淀用户/世界**陈述性**知识；第8章复用基建做**行为**知识 | 同上 |
| 双层记忆架构 = 主动服务工程落地 | `chapter3.md` L671 |

---

## 6. 五主题交叉总图（决策用）

```text
                    Model (LLM / Policy)
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    Observation        Decision           Action
    (Context)          (Loop)             (Tools)
         │                 │                 │
    静态前缀+轨迹      ReAct while        感知/执行/协作/
    Skills/状态栏/压缩  工作流|自主         事件/沟通
    用户记忆/RAG       验证写回观测         约束/沙盒/权限
         │                 │                 │
         └────────── Harness 外壳 ───────────┘
              Constrain + Verify + Correct
              （+ 生产：熔断、人工、评估闭环）
```

**公式链（可直接验收用）：**

1. `Agent = LLM + Context + Tools`（最小）  
2. `Agent = Model + Harness`，`Harness ⊇ Context + Tools + Constrain + Verify + Correct`  
3. `Context = 静态前缀 + 轨迹`；`Context = system + tools + user + assistant + tool`  
4. `Loop = 思考 → 行动 → 观察`（ReAct）；可选工作流写死边  
5. `Memory = 轨迹(工作) + 长期用户记忆 + (可选)业务状态`；跨会话靠提取/RAG/双层架构  

---

## 7. 对本工作台（实证论文 Agent）的可迁移检查清单

> 从书中主张压出的**可观测**要求，非书原文口号。

| 维度 | 应能在代码/文档中指出 | 书锚点 |
|------|----------------------|--------|
| 公式 | 是否区分 Demo 最小 Agent 与生产 Harness 五功能 | ch1 L250–L272 |
| Loop | while + max_iter；tool 无则停；工具结果必须回写 | ch1 ReAct；ch2 L292–L318 |
| Context 五件套 | system / tools / user / assistant / tool 是否齐全；消融意识 | ch1 L139–L159 |
| KV 友好 | 动态时间/状态是否在末尾；工具顺序是否固定 | ch2 三条结论 |
| Skills | 是否元数据常驻 + 按需全文；description 有反例 | ch2 Skills |
| 状态栏 | 代码维护计数/TODO/环境；非 LLM 批统计 | ch2 状态栏 |
| 压缩 | 阈值批量；保决策/验证/标识符；优先子 Agent 隔离 | ch2 压缩 |
| Tools | 通用探索 vs 专用高风险；沙盒 | ch1 L99–L103 |
| Memory | 轨迹 vs 长期；冲突 UPDATE；双层概览+检索 | ch3 |
| 安全 | 来源标记；状态栏/Skill 不接污染源；检索不直驱副作用 | ch2/ch3 |
| 评估 | 有记忆/任务评估才谈进步 | intro L23；ch3 三层次 |

---

## 8. 源文件索引（便于回读）

| 文件 | 绝对路径 |
|------|----------|
| 引言 | `/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book/book/introduction.md` |
| 第1章 | `/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book/book/chapter1.md` |
| 第2章 | `/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book/book/chapter2.md` |
| 第3章 | `/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book/book/chapter3.md` |
| 配套代码 | https://github.com/bojieli/ai-agent-book（`chapter1/`…`chapter10/`） |

---

*提取完成。主张均回溯书中表述；未读第4章及以后，工具/多 Agent 细节以书内预告为限。*
