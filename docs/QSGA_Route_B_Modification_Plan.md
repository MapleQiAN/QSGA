# QSGA / QYIR 论文路线 B 修改意见

> 版本：Route B v1  
> 目标：从“IR 验证框架论文”升级为“自然语言到 QYIR 的可靠构造 + 验证修复闭环论文”  
> 核心任务：把 live prompt-only QYIR construction success 从当前 0.091 拉升到足以支撑端到端主张的水平

---

## 0. 路线 B 的一句话定位

路线 B 不再只是说明“QYIR 后端验证链有效”，而是要补齐前端：

> 本文提出一个 verification-guided natural-language-to-QYIR construction framework，使 LLM 不再直接裸生成完整策略代码或完整 QYIR，而是在结构化输出、槽位抽取、规范化构造、验证反馈修复和 QSGA 后端审计的共同约束下，稳定生成可验证、可编译、可审计、风险受控的规则型量化策略规格。

换句话说，路线 A 是：

> QYIR 后端验证链很强，LLM 生成是瓶颈。

路线 B 是：

> 我们识别了这个瓶颈，并通过 constrained generation + slot parser + canonicalizer + validation-feedback retry 进行了系统性修复。

这条路线更像真正的 AI / NLP / Agent 系统论文。它更猛，但也更吃实验结果。论文上限更高，工作量也明显更大。

---

## 1. 当前痛点与路线 B 要解决的问题

### 1.1 当前核心短板

现有实验结果里，最尴尬但也最重要的事实是：

| 模块 | 当前结果 | 解释 |
|---|---:|---|
| Oracle-slot verification-chain | E2E 0.963 | 后端验证链很强 |
| Deterministic no-oracle extractor | E2E 0.887 | 简单确定性前端也能较稳定进入 QYIR |
| Live prompt-only QYIR generation | Construction success 0.091 | 真实 LLM 直接生成 QYIR 极弱 |

如果论文想继续 claim “端到端可靠策略生成”，那 0.091 就是必须补上的洞。路线 B 的目标就是把这个洞变成论文新增贡献。

### 1.2 路线 B 的核心研究问题

路线 B 应该把研究问题改为：

```text
RQ1: Can constrained natural-language-to-QYIR construction improve the structural validity, semantic consistency, and executable construction success of LLM-generated strategy specifications?

RQ2: Which components, including structured output, slot extraction, canonicalization, validation-feedback retry, and QSGA repair, contribute most to improving live QYIR construction?

RQ3: Does the improved QYIR construction pipeline outperform direct LLM-to-code and raw prompt-only QYIR baselines under the same benchmark and safety constraints?
```

### 1.3 路线 B 的最低成功标准

建议设定三个阶段性门槛：

| 目标等级 | Construction Success | 论文定位 |
|---|---:|---|
| 最低可用 | ≥ 0.25 | 可以作为路线 A 的增强实验 |
| CCF C 主线可用 | ≥ 0.40 | 可以升级成路线 B 主线 |
| 更强论文版本 | ≥ 0.50 | 可以尝试 AI / NLP / Agent 应用方向 |
| 非常理想 | ≥ 0.60 | 端到端 claim 明显更有底气 |

注意：不要提前承诺这些数字。论文里只能写实际跑出来的数据。科研不是许愿池，不能往里面丢 prompt 就等着出锦鲤。🐟

---

## 2. 路线 B 的新论文故事

### 2.1 旧故事

旧故事大概是：

```text
User natural language
→ LLM generates QYIR
→ QSGA verifies and repairs
→ executable strategy
```

问题是：第一步失败率太高。

### 2.2 新故事

路线 B 改成：

```text
Natural-language strategy request
→ Structured slot extraction
→ Deterministic QYIR builder
→ QYIR canonicalizer
→ QYIR validator
→ Validation-feedback retry
→ QSGA backend verification
→ compilation / execution / risk audit / localized repair
```

核心思想：

> LLM 负责理解自然语言，程序负责生成标准 QYIR，验证器负责发现错误，修复器负责闭环改正。

这会把 LLM 从“全栈策略工程师”降级成“语义槽位提取员”。这不是降维打击，是岗位职责清晰化。LLM 不会失业，它只是终于不用一个人扛锅了。

---

## 3. 标题修改建议

路线 B 可以比路线 A 更进攻，因为你要证明 live LLM 生成被真正改进了。

### 3.1 首选标题

> **QSGA: Verification-Guided Natural-Language-to-QYIR Construction for Rule-Based Quantitative Strategies**

优点：  
准确表达路线 B 的新核心，即 natural-language-to-QYIR construction，而不是单纯 verification。

### 3.2 备选标题

> **From Intent to Verifiable Strategy IR: Constrained LLM Construction for Rule-Based Quantitative Strategies**

> **Schema-Guided Strategy Synthesis: Reliable QYIR Construction with Verification-Guided Repair**

> **QSGA: Constrained Strategy IR Construction and Verification for LLM-Based Quantitative Agents**

### 3.3 标题中可以恢复但要谨慎使用的词

路线 B 中可以使用：

```text
constrained generation
schema-guided synthesis
verification-guided construction
natural-language-to-QYIR
LLM-based quantitative strategy construction
```

但仍不建议过早使用：

```text
fully autonomous trading agent
safe trading agent
guaranteed reliable generation
```

金融场景里 “safe” 和 “guaranteed” 都是审稿人的红布，斗牛看了都想冲。

---

## 4. 摘要改写方向

路线 B 摘要必须跟路线 A 不一样。路线 A 是“收窄”，路线 B 是“补齐”。

### 4.1 摘要应包含的内容

1. 直接 LLM-to-code 和 raw QYIR prompting 都不稳定；
2. 提出 QYIR-constrained generation 或 NL-to-QYIR construction pipeline；
3. 说明 pipeline 包含 slot extraction、deterministic builder、canonicalizer、validation-feedback retry；
4. 说明 QSGA 后端继续执行 schema、semantic、compile、execution、risk、repair；
5. 报告新实验结果；
6. 和 baselines 对比；
7. 说明失败类型显著减少。

### 4.2 摘要模板

```text
Large language models enable novice users to express quantitative strategy ideas in natural language, but direct LLM-to-code generation and raw prompt-only structured generation often produce malformed artifacts, unresolved indicator references, missing risk constraints, and semantically inconsistent trading rules.

We propose QSGA, a verification-guided natural-language-to-QYIR construction framework for bounded rule-based quantitative strategies. Instead of asking LLMs to directly synthesize executable code or complete strategy IR, QSGA decomposes strategy construction into structured slot extraction, deterministic QYIR building, canonicalization, validator-guided retry, and downstream verification over a domain-specific intermediate representation.

The framework uses QYIR as both a generation target and an audit boundary. Candidate artifacts are checked through schema validation, reference and type checking, semantic slot verification, deterministic compilation, execution validation, risk auditing, unsafe-intent rejection, and localized repair.

On QSI-Bench v1, raw prompt-only QYIR generation achieves only 9.1% construction success. With the proposed constrained construction pipeline, construction success improves to XX%, and end-to-end success improves to YY%, outperforming direct-code and raw-QYIR baselines. Ablation results show that structured slot extraction, canonicalization, and validation-feedback retry each reduce distinct failure modes.

These results suggest that reliable rule-based quantitative strategy construction requires not only a verifiable intermediate representation, but also a generation process explicitly constrained by that representation.
```

### 4.3 摘要中的禁忌

不要写：

```text
QSGA guarantees safe strategy generation.
```

应该写：

```text
QSGA improves the reliability and auditability of bounded rule-based strategy construction under explicit validation and repair constraints.
```

---

## 5. 新贡献点写法

路线 B 的贡献点应该从路线 A 的四条升级为：

```text
The contributions of this paper are:

1. We propose QYIR, a constrained and verifiable intermediate representation for bounded rule-based quantitative strategy specifications.

2. We introduce a verification-guided natural-language-to-QYIR construction pipeline that decomposes strategy generation into structured slot extraction, deterministic QYIR building, canonicalization, and validator-feedback retry.

3. We design QSGA, an end-to-end verification and repair framework that validates QYIR artifacts through schema checking, reference and type checking, semantic slot verification, compilation, execution validation, risk auditing, unsafe-intent rejection, and localized repair.

4. We construct QSI-Bench v1 and evaluate QSGA against raw QYIR prompting, direct LLM-to-code generation, direct JSON baselines, and ablated variants, showing that constrained QYIR construction substantially improves live construction success.

5. We provide a failure-reduction analysis that identifies how different components reduce JSON parsing failures, schema violations, alias resolution errors, type mismatches, semantic inconsistencies, and missing risk controls.
```

路线 B 的新增核心贡献是第 2 条和第 5 条。没有这两条，路线 B 就只是路线 A 戴了个假发。

---

## 6. 方法章节重构

路线 B 的方法章节应改成下面结构。

```text
4. QYIR: Verifiable Strategy Intermediate Representation
  4.1 QYIR Grammar and Field Semantics
  4.2 Reference and Type Validity
  4.3 Rule Compilation Semantics
  4.4 Risk-Control Semantics

5. Verification-Guided NL-to-QYIR Construction
  5.1 Structured Slot Extraction
  5.2 Deterministic QYIR Builder
  5.3 QYIR Canonicalization
  5.4 Validation-Feedback Retry
  5.5 Construction Failure Taxonomy

6. QSGA Verification and Repair Backend
  6.1 Schema, Reference, and Type Verification
  6.2 Semantic Slot Verification
  6.3 Compilation and Execution Validation
  6.4 Risk Audit and Unsafe-Intent Rejection
  6.5 Localized Repair with Invariants
```

核心变化：

路线 A 的方法重点是第 4 和第 6 节。  
路线 B 新增的真正主角是第 5 节。

---

## 7. 模块一：Structured Slot Extraction

### 7.1 为什么要做 slot extraction

不要让 LLM 直接生成完整 QYIR。

原因：

1. 完整 QYIR 字段多，引用关系复杂；
2. LLM 容易生成未定义 alias；
3. LLM 容易混用 market field 和 indicator alias；
4. 风险字段容易漏；
5. 直接 JSON 输出即使格式合法，也可能领域语义错误。

路线 B 推荐：

```text
Natural Language → Simplified Slots → Deterministic QYIR
```

LLM 只需要输出比 QYIR 简单的 slot schema。

### 7.2 Slot Schema 建议

```json
{
  "strategy_family": "trend_following | mean_reversion | momentum | breakout | risk_controlled | unknown",
  "market_scope": {
    "symbol": "string | null",
    "asset_type": "stock | etf | index | unknown",
    "timeframe": "daily | weekly | unknown"
  },
  "indicators": [
    {
      "name": "SMA | EMA | RSI | MACD | BOLLINGER | UNKNOWN",
      "window": "integer | null",
      "role": "fast | slow | signal | threshold | unknown"
    }
  ],
  "entry_logic": {
    "operator": "cross_over | cross_under | greater_than | less_than | between | unknown",
    "left": "string | null",
    "right": "string | number | null",
    "natural_language": "string"
  },
  "exit_logic": {
    "operator": "cross_over | cross_under | greater_than | less_than | between | stop_loss | take_profit | unknown",
    "left": "string | null",
    "right": "string | number | null",
    "natural_language": "string"
  },
  "risk_constraints": {
    "position_size": "number | null",
    "max_drawdown_limit": "number | null",
    "stop_loss": "number | null",
    "take_profit": "number | null",
    "allow_short": "boolean | null",
    "leverage": "number | null"
  },
  "ambiguity": {
    "requires_clarification": "boolean",
    "missing_slots": ["string"],
    "ambiguous_phrases": ["string"]
  },
  "safe_action": "construct | clarify | reject"
}
```

### 7.3 Slot Extraction Prompt 设计

建议 prompt 分成三段：

```text
System:
You are a quantitative strategy slot extractor. Your task is not to write code and not to output QYIR. You must extract explicit strategy slots from the user's request.

Developer:
Only use supported indicators: SMA, EMA, RSI, MACD, BOLLINGER.
Only use supported operators: cross_over, cross_under, greater_than, less_than, between.
If the user intent is ambiguous, set safe_action = "clarify".
If the user asks for illegal, manipulative, or unsafe behavior, set safe_action = "reject".
Do not infer hidden constraints unless they are explicitly stated or mapped by the risk phrase dictionary.

User:
{query}

Output:
Return a strict JSON object matching the Slot Schema.
```

### 7.4 Slot Extraction 的论文表述

论文中不要说：

```text
We prompt the LLM to generate QYIR.
```

要说：

```text
We decompose language understanding from strategy artifact construction. The LLM is only responsible for extracting explicit semantic slots, while QYIR artifacts are constructed by a deterministic builder under domain constraints.
```

这句话很关键，科研味一下就出来了。

---

## 8. 模块二：Deterministic QYIR Builder

### 8.1 Builder 的作用

Slot parser 输出 slots 后，由 deterministic builder 生成标准 QYIR。

这样可以避免 LLM 直接处理复杂引用关系。

### 8.2 Builder 伪代码

```text
Algorithm 1: Deterministic QYIR Builder

Input:
  slot object S

Output:
  QYIR candidate Q or construction failure

1. if S.safe_action = reject:
2.     return RejectArtifact(reason)
3. if S.safe_action = clarify:
4.     return ClarificationArtifact(missing_slots)

5. Q.market ← normalize_market_scope(S.market_scope)

6. AliasSet ← {}
7. for each indicator slot i in S.indicators:
8.     if i.name not in SupportedIndicators:
9.         return failure(unsupported_indicator)
10.    alias ← allocate_alias(i.name, i.window, i.role)
11.    Q.indicators.append({alias, type: i.name, params: {window: i.window}})
12.    AliasSet.add(alias)

13. Q.entry_rules ← build_rules(S.entry_logic, AliasSet)
14. Q.exit_rules ← build_rules(S.exit_logic, AliasSet)

15. Q.risk_control ← build_risk_control(S.risk_constraints)

16. return canonicalize(Q)
```

### 8.3 Builder 规则示例

```text
if strategy_family = trend_following
and indicators contain SMA windows [20, 60]:
    create indicator sma_20
    create indicator sma_60
    if entry phrase contains "上穿":
        entry_rule = cross_over(sma_20, sma_60)
    if exit phrase contains "下穿":
        exit_rule = cross_under(sma_20, sma_60)

if risk_constraints.leverage is null:
    leverage = 1.0

if user says "不要杠杆":
    leverage = 1.0

if user says "不要做空":
    allow_short = false

if risk_constraints.position_size is null and phrase contains "稳一点":
    safe_action = clarify or set position_size <= 0.4 according to predefined policy
```

### 8.4 Builder 的论文价值

这部分的论文价值是：

> LLM 不直接负责策略工件完整生成。QYIR construction 由 deterministic builder 保证结构合法性、引用一致性和可编译性。

这可以显著改善 schema validity、alias resolution 和 type validity。

---

## 9. 模块三：QYIR Canonicalizer

### 9.1 Canonicalizer 的定位

Canonicalizer 是路线 B 的高性价比模块。它不一定很难，但能显著减少“格式正确但表达不统一”的失败。

### 9.2 Canonicalization 规则表

| 输入表达 | 规范化结果 |
|---|---|
| `close` | `market.close` |
| `price` | `market.close` |
| `closing_price` | `market.close` |
| `收盘价` | `market.close` |
| `open` | `market.open` |
| `volume` | `market.volume` |
| `sma20` | `sma_20` |
| `SMA_20` | `sma_20` |
| `20日均线` | `sma_20` |
| `60日均线` | `sma_60` |
| `20%` | `0.20` |
| `百分之十` | `0.10` |
| `不要杠杆` | `leverage = 1.0` |
| `别做空` | `allow_short = false` |
| `不要追高` | `requires_clarification = true` or map to risk policy |
| `稳一点` | `requires_clarification = true` or conservative risk default |
| `低风险` | `position_size <= 0.4` if policy allows |
| `激进一点` | clarification required |
| `最大回撤小于10%` | `max_drawdown_limit <= 0.10` |

### 9.3 Canonicalizer 输出

Canonicalizer 应输出两个东西：

```json
{
  "canonical_qyir": {},
  "canonicalization_log": [
    {
      "field": "risk_control.leverage",
      "original": "不要杠杆",
      "canonical": 1.0,
      "rule_id": "risk.no_leverage"
    }
  ]
}
```

### 9.4 论文里要强调

Canonicalizer 不是“拍脑袋改策略”，它只做：

1. 同义表达规范化；
2. 字段单位标准化；
3. alias 命名规范化；
4. 风险短语映射；
5. 产生可审计的 transformation log。

---

## 10. 模块四：Validation-Feedback Retry

### 10.1 为什么需要 retry

即使 structured output 和 builder 做了很多工作，仍会有：

1. 缺字段；
2. 未定义 alias；
3. unsupported indicator；
4. semantic mismatch；
5. risk slot missing；
6. 编译失败；
7. 执行失败。

Retry 的关键是利用 validator 的错误路径，让 LLM 修复明确字段。

### 10.2 Retry 流程

```text
Algorithm 2: Validation-Feedback Retry

Input:
  user request x
  max retry K

Output:
  valid QYIR candidate or failure report

1. slots_0 ← LLM_extract_slots(x)
2. Q_0 ← Builder(slots_0)
3. for k in 0...K:
4.     errors_k ← Validator(Q_k)
5.     if errors_k is empty:
6.         return Q_k
7.     feedback_k ← FormatErrors(errors_k)
8.     slots_{k+1} or Q_{k+1} ← LLM_repair(feedback_k, freeze_valid_fields=True)
9.     Q_{k+1} ← Canonicalizer(Q_{k+1})
10. return failure(errors_K)
```

### 10.3 Feedback Prompt 示例

```text
The generated QYIR failed validation.

Error type:
ReferenceValidityError

Error path:
entry_rules[0].operand_a

Problem:
The rule references alias "sma_60", but this alias is not defined in indicators.

Defined aliases:
["sma_20", "rsi_14"]

Instruction:
Fix only the invalid operand or add the missing indicator if it is explicitly required by the user request.
Do not change valid fields.
Do not weaken risk constraints.
Return only the corrected JSON object.
```

### 10.4 Retry 实验变量

建议设置：

| Setting | 说明 |
|---|---|
| K=0 | raw generation，无 retry |
| K=1 | 一轮 validator feedback |
| K=2 | 两轮 feedback |
| K=3 | 三轮 feedback |
| K=3 + freeze valid fields | 只修错字段，不重写全局 |
| K=3 + canonicalizer | retry 后再规范化 |

### 10.5 Retry 的指标

| Retry K | Schema Validity | Reference Validity | Type Validity | Semantic Consistency | Construction Success | Avg Tokens | Avg Latency |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 |  |  |  |  | 0.091 |  |  |
| 1 |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |

这张表很重要，它能证明 validator 不是单纯裁判，而是能指导生成器改作业的教练。📘

---

## 11. 模块五：Structured Output / JSON Schema / Pydantic

### 11.1 为什么要引入结构化输出

Raw JSON prompt 已经过时了。路线 B 如果要打 live LLM，就应该引入以下至少一种：

1. OpenAI-compatible `response_format`;
2. function calling;
3. Pydantic / instructor;
4. JSON Schema enforced decoding;
5. grammar-constrained decoding;
6. post-hoc strict parser + retry。

### 11.2 Pydantic Model 示例

```python
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field

IndicatorName = Literal["SMA", "EMA", "RSI", "MACD", "BOLLINGER"]
RuleOperator = Literal["cross_over", "cross_under", "greater_than", "less_than", "between"]
SafeAction = Literal["construct", "clarify", "reject"]

class MarketScope(BaseModel):
    symbol: Optional[str] = None
    asset_type: Literal["stock", "etf", "index", "unknown"] = "unknown"
    timeframe: Literal["daily", "weekly", "unknown"] = "daily"

class IndicatorSlot(BaseModel):
    name: IndicatorName
    window: Optional[int] = None
    role: Literal["fast", "slow", "signal", "threshold", "unknown"] = "unknown"

class LogicSlot(BaseModel):
    operator: Optional[RuleOperator] = None
    left: Optional[str] = None
    right: Optional[Union[str, float]] = None
    natural_language: str = ""

class RiskConstraints(BaseModel):
    position_size: Optional[float] = None
    max_drawdown_limit: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    allow_short: Optional[bool] = None
    leverage: Optional[float] = None

class Ambiguity(BaseModel):
    requires_clarification: bool = False
    missing_slots: List[str] = Field(default_factory=list)
    ambiguous_phrases: List[str] = Field(default_factory=list)

class StrategySlotSpec(BaseModel):
    strategy_family: Literal[
        "trend_following",
        "mean_reversion",
        "momentum",
        "breakout",
        "risk_controlled",
        "unknown"
    ]
    market_scope: MarketScope
    indicators: List[IndicatorSlot]
    entry_logic: LogicSlot
    exit_logic: LogicSlot
    risk_constraints: RiskConstraints
    ambiguity: Ambiguity
    safe_action: SafeAction
```

### 11.3 论文表述

```text
We use structured output not as a substitute for QYIR validation, but as the first layer of construction control. It reduces malformed outputs and missing fields, while QYIR validators further enforce reference consistency, operand typing, compilation semantics, and risk-slot constraints.
```

这句话能避免审稿人说：“你不就是用了 JSON Schema 吗？”  
你要强调：Schema 只管形状，QYIR 管领域语义。

---

## 12. Failure Taxonomy

路线 B 必须做 failure reduction analysis。

### 12.1 失败类型定义

| Failure Type | 描述 | 例子 |
|---|---|---|
| Parse Failure | 无法解析为 JSON | 输出夹杂解释文本，括号不闭合 |
| Schema Failure | JSON 字段不符合 schema | 缺 `exit_rules` |
| Unsupported Indicator | 使用未支持指标 | KDJ、ATR、OBV |
| Alias Failure | rule 引用未定义 alias | `sma_60` 未在 indicators 中 |
| Type Error | 操作数类型错误 | 对 scalar 做 cross_over |
| Semantic Mismatch | 显式约束被违反 | 用户说不要杠杆，输出 leverage=2 |
| Risk Slot Missing | 风险字段缺失 | 用户要求止损，但 stop_loss=null |
| Compilation Failure | 无法编译为策略逻辑 | rule 结构不完整 |
| Execution Failure | 回测执行报错 | 时间序列长度不足、字段不存在 |
| Unsafe Intent Failure | 不安全请求未拒绝 | 操纵市场、保证收益 |

### 12.2 原始失败分布表

| Failure Type | Raw QYIR Count | Percentage | Representative Example |
|---|---:|---:|---|
| Parse Failure |  |  |  |
| Schema Failure |  |  |  |
| Unsupported Indicator |  |  |  |
| Alias Failure |  |  |  |
| Type Error |  |  |  |
| Semantic Mismatch |  |  |  |
| Risk Slot Missing |  |  |  |
| Compilation Failure |  |  |  |
| Execution Failure |  |  |  |
| Unsafe Intent Failure |  |  |  |

### 12.3 增强后失败减少表

| Failure Type | Raw QYIR | + Structured Output | + Canonicalizer | + Retry | + Slot Parser + Builder |
|---|---:|---:|---:|---:|---:|
| Parse Failure |  |  |  |  |  |
| Schema Failure |  |  |  |  |  |
| Alias Failure |  |  |  |  |  |
| Type Error |  |  |  |  |  |
| Semantic Mismatch |  |  |  |  |  |
| Risk Slot Missing |  |  |  |  |  |

这张表是路线 B 的灵魂。它不能只说“成功率提高了”，还要说“哪些病灶被治好了”。

---

## 13. Baselines 设计

路线 B 的 baseline 必须补强，否则审稿人会说你只是在跟一个很弱的 raw prompt 比。

### 13.1 必须比较的 baseline

| Baseline | 作用 |
|---|---|
| Live direct-code | 传统 LLM 直接写 Python 策略 |
| Live raw QYIR prompting | 当前 0.091 版本，证明裸 prompt 不稳定 |
| Live direct JSON schema | 证明普通 schema 不等于 QYIR 语义约束 |
| Direct code + safety gate | 分离安全拦截贡献 |
| QYIR + structured output | 证明结构化输出收益 |
| QYIR + canonicalizer | 证明规范化收益 |
| QYIR + retry | 证明验证反馈收益 |
| Slot parser + builder | 证明分阶段构造收益 |
| Full QSGA-B | 最终方法 |

### 13.2 主结果表建议

| Method | Parse Valid | Schema Valid | Reference Valid | Type Valid | Semantic Consistency | Compile Success | Construction Success | E2E Success |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Direct Code |  |  |  |  |  |  |  |  |
| Raw QYIR Prompting |  |  |  |  |  |  | 0.091 |  |
| Direct JSON Schema |  |  |  |  |  |  |  |  |
| Structured QYIR |  |  |  |  |  |  |  |  |
| + Canonicalizer |  |  |  |  |  |  |  |  |
| + Retry |  |  |  |  |  |  |  |  |
| + Slot Parser + Builder |  |  |  |  |  |  |  |  |
| Full QSGA-B |  |  |  |  |  |  |  |  |

### 13.3 消融实验表

| Variant | Construction Success | E2E Success | Main Failure Increase |
|---|---:|---:|---|
| Full QSGA-B |  |  |  |
| w/o structured output |  |  | Parse / schema failure |
| w/o canonicalizer |  |  | alias / unit mismatch |
| w/o retry |  |  | unrepaired validation errors |
| w/o slot parser |  |  | semantic slot mismatch |
| w/o QYIR backend repair |  |  | risk / compile failures |
| w/o risk audit |  |  | unsafe or over-risk strategies |

---

## 14. Metrics 设计

路线 B 不要只看 construction success。要分层指标。

### 14.1 Structural Metrics

| Metric | 定义 |
|---|---|
| Parse Validity | 输出是否可解析为 JSON |
| Schema Validity | 是否符合 slot schema 或 QYIR schema |
| Reference Validity | rule 中所有 alias 是否已定义 |
| Type Validity | rule 操作数类型是否合法 |
| Operator Validity | rule operator 是否属于允许集合 |

### 14.2 Semantic Metrics

| Metric | 定义 |
|---|---|
| Slot Precision | 抽取出的槽位有多少是正确的 |
| Slot Recall | gold slot 中有多少被抽取 |
| Semantic Consistency | 是否满足用户显式语义要求 |
| Risk Constraint Satisfaction | 是否满足显式风险约束 |
| Safe Rejection Accuracy | 不安全意图是否被拒绝 |
| Clarification Accuracy | 模糊请求是否触发澄清 |

### 14.3 Execution Metrics

| Metric | 定义 |
|---|---|
| Compile Success | QYIR 是否能编译为策略逻辑 |
| Execution Success | 策略是否能完成回测 |
| Effective Trade Rate | 是否产生有效交易 |
| E2E Success | 从输入到可执行且风险合规策略的总成功率 |

### 14.4 Cost Metrics

| Metric | 定义 |
|---|---|
| Avg Tokens | 平均 token 消耗 |
| Avg Latency | 平均 API 延迟 |
| Avg Retry Count | 平均修复轮数 |
| Repair Success Rate | 失败样本经 retry 后成功比例 |

这些指标能让论文从“看一个总分”变成“看诊断面板”。科研版驾驶舱，仪表盘亮起来就不慌了。

---

## 15. Benchmark 扩展

路线 B 最好扩数据。只在 80 条上调参，很容易被质疑 benchmark overfitting。

### 15.1 最小扩展

新增 50 条 Hard Paraphrase：

| 类型 | 例子 |
|---|---|
| 口语化 | “帮我搞个别太激进的均线策略” |
| 错别字 | “止盈止损别太夸张” |
| 中英混合 | “用 SMA crossover 做一个 low risk 策略” |
| 模糊风险词 | “稳一点”“别追高”“别太猛” |
| 非标准指标表达 | “20天平均价格线” |
| 隐式风险约束 | “我不想亏太多” |
| 缺失字段 | “帮我做个 RSI 策略” |

### 15.2 更强扩展

| Set | 数量 | 作用 |
|---|---:|---|
| Original QSI-Bench v1 | 80 | 主集 |
| Hard Paraphrase | 50 | 鲁棒性 |
| Unsafe Adversarial | 30 | 安全边界 |
| Safe Boundary | 20 | 避免误拒 |
| Realistic Novice | 30 到 50 | 真实用户表达 |

### 15.3 OOD 验证

新增 10 到 15 条真实 query：

来源可以是：

1. QuantConnect 论坛策略讨论；
2. Reddit r/algotrading 新手提问；
3. 让非金融背景同学描述投资想法；
4. 你自己的 QYQuant 用户测试语料。

报告：

| Dataset | Construction Success | E2E Success | Main Failure |
|---|---:|---:|---|
| QSI-Bench v1 |  |  |  |
| Hard Paraphrase |  |  |  |
| OOD Realistic Novice |  |  |  |

---

## 16. 实验章节重构

路线 B 的实验章节不能再把 oracle 放在最前面。新的主角是 live enhanced construction。

建议结构：

```text
7. Experimental Setup
  7.1 QSI-Bench v1 and Extended Evaluation Sets
  7.2 Models and API Settings
  7.3 Baselines
  7.4 QSGA-B Variants
  7.5 Metrics

8. Results
  8.1 Main Results: Live NL-to-QYIR Construction
  8.2 Comparison with Direct-Code and Raw-QYIR Baselines
  8.3 Component Ablation
  8.4 Failure Reduction Analysis
  8.5 Verification Backend Reliability
  8.6 OOD and Hard Paraphrase Evaluation
  8.7 Case Studies
  8.8 Cost and Latency Analysis
```

### 16.1 8.1 主结果

核心表：

```text
Raw QYIR Prompting: 0.091
Structured QYIR: X
+ Canonicalizer: Y
+ Validation Retry: Z
+ Slot Parser + Builder: W
Full QSGA-B: Final
```

### 16.2 8.2 与直接代码对比

重点证明：

> 直接代码可能能跑，但语义、风险和审计性不够。

### 16.3 8.3 消融

证明每个组件有独立价值。

### 16.4 8.4 失败减少

证明失败不是随机减少，而是具体类别被系统性压低。

### 16.5 8.5 后端验证链

把 oracle 0.963 放在这里，作为补充说明：

> 即使前端生成改进了，QYIR 后端验证链仍然是系统可靠性的基础。

---

## 17. 论文 Discussion 写法

路线 B 的 Discussion 要讲清楚三件事：

### 17.1 为什么 slot parser 比 direct QYIR 更稳

```text
The slot-based design separates natural-language interpretation from artifact construction. This reduces the burden on the LLM and shifts reference allocation, type normalization, and risk-slot completion to deterministic components.
```

### 17.2 为什么 structured output 不等于完整解决

```text
Structured output reduces malformed responses and missing fields, but it does not guarantee domain-level validity. QYIR validators remain necessary for detecting unresolved references, invalid operands, semantic mismatches, and violated risk constraints.
```

### 17.3 为什么 retry 是 verification-guided construction

```text
Validator feedback converts failures into localized repair instructions. Rather than regenerating the entire strategy, QSGA uses field-level error paths to preserve valid fields and repair only invalid components.
```

---

## 18. Threats to Validity

路线 B 必须认真写风险。

### 18.1 Prompt / Benchmark Overfitting

风险：

> few-shot examples 和 benchmark taxonomy 可能过于接近。

缓解：

1. 加 hard paraphrase；
2. 加 OOD query；
3. 加多模型对比；
4. 报告真实失败案例。

### 18.2 Structured Output 的模型依赖

风险：

> 不同 API 的 response_format 支持不同。

缓解：

1. 使用 Pydantic 后验校验；
2. 报告 raw prompting 和 structured output 两种设置；
3. 明确 implementation-specific limitation。

### 18.3 Semantic Verification 边界

风险：

> semantic consistency 仍可能依赖人工 gold slot。

缓解：

1. 明确只检查显式约束；
2. 对模糊约束触发 clarification；
3. 报告 slot-level precision / recall。

### 18.4 Financial Generalization

风险：

> 当前只覆盖日频、规则型、股票或 ETF 策略。

缓解：

1. 明确 bounded scope；
2. 不 claim 高频、期权、复杂组合；
3. future work 扩展 asset classes 和 strategy families。

---

## 19. 路线 B 的代码任务清单

### 19.1 第一阶段：B-light

目标：不大重构，先证明能从 0.091 往上拉。

新增文件建议：

```text
experiments/
  run_live_qyir_retry.py
  analyze_failure_breakdown.py
  generate_route_b_tables.py

qsgi/
  construction/
    slot_schema.py
    canonicalizer.py
    retry_loop.py
    feedback_formatter.py
```

任务：

```text
1. 收集原始 80 case live LLM 输出日志
2. 标注失败类型
3. 实现 QYIR canonicalizer
4. 实现 validation-feedback retry
5. 跑 K=0,1,2,3
6. 输出 failure breakdown 表
7. 输出 construction success 对比表
```

### 19.2 第二阶段：B-medium

目标：正式引入 slot parser + builder。

新增：

```text
qsgi/
  construction/
    slot_extractor.py
    qyir_builder.py
    structured_output_client.py
```

任务：

```text
1. 定义 StrategySlotSpec Pydantic schema
2. 实现 structured slot extraction
3. 实现 deterministic QYIR builder
4. 实现 slot-to-QYIR canonicalization log
5. 跑 full pipeline
6. 与 raw QYIR prompting 对比
```

### 19.3 第三阶段：B-full

目标：达到论文主线可用。

任务：

```text
1. 加 direct-code baseline
2. 加 direct JSON schema baseline
3. 加多模型对比
4. 加 hard paraphrase set
5. 加 OOD realistic novice set
6. 做 component ablation
7. 做 cost / latency analysis
8. 更新论文路线 B 版本
```

---

## 20. 给 Codex / Claude Code 的完整任务提示词

可以直接复制下面内容。

```text
当前项目进入路线 B：提升 live LLM-to-QYIR construction success，使论文从 IR verification paper 升级为 NL-to-QYIR construction + verification paper。

目标：
在不破坏现有 QYIR/QSGA 后端验证链的前提下，实现一个 verification-guided NL-to-QYIR construction pipeline。

请按以下阶段执行。

阶段 1：失败诊断
1. 读取现有 live LLM 原始输出日志。
2. 对每个失败 case 标注 failure type：
   parse_failure
   schema_failure
   unsupported_indicator
   alias_failure
   type_error
   semantic_mismatch
   risk_slot_missing
   compilation_failure
   execution_failure
   unsafe_intent_failure
3. 输出 experiments/results/live_failure_breakdown.csv 和 markdown 表格。

阶段 2：B-light 增强
1. 实现 QYIR canonicalizer：
   - market field normalization
   - indicator alias normalization
   - percentage normalization
   - risk phrase normalization
   - canonicalization log
2. 实现 validation-feedback retry：
   - K=0,1,2,3
   - 将 validator error path 格式化为 repair prompt
   - freeze valid fields
   - do not weaken risk constraints
3. 新增 run_live_qyir_retry.py。
4. 输出对比表：
   raw live QYIR
   + canonicalizer
   + retry K=1
   + retry K=2
   + retry K=3
   + canonicalizer + retry
5. 指标包括：
   parse_validity
   schema_validity
   reference_validity
   type_validity
   semantic_consistency
   compile_success
   construction_success
   e2e_success
   avg_tokens
   avg_latency

阶段 3：B-medium 增强
1. 定义 StrategySlotSpec Pydantic schema。
2. 实现 structured slot extractor。
3. 实现 deterministic QYIR builder。
4. Pipeline 改为：
   natural language
   -> slot extraction
   -> deterministic QYIR builder
   -> canonicalizer
   -> validator
   -> retry
   -> QSGA backend
5. 输出主结果表：
   raw QYIR prompting
   structured QYIR
   + canonicalizer
   + retry
   + slot parser + builder
   full QSGA-B

阶段 4：实验扩展
1. 新增 direct-code baseline。
2. 新增 direct JSON schema baseline。
3. 新增 hard paraphrase set。
4. 新增 10 到 15 个 OOD realistic novice queries。
5. 新增多模型对比，如 qwen3.6-flash 与 GPT-4o-mini 或其他可用模型。
6. 输出 component ablation 和 failure reduction analysis。

约束：
1. 不要修改路线 A 的论文主张，除非 B 实验结果显著提升。
2. 不要提前写死提升数字，所有 XX 必须由实验结果生成。
3. 所有实验结果必须保存到 experiments/results。
4. 所有表格由 generate_route_b_tables.py 自动生成。
5. 每个 repair 都必须记录 field-level diff 和 validator error path。
```

---

## 21. 路线 B 论文替换表

| 路线 A 表述 | 路线 B 替换 |
|---|---|
| IR-first verification framework | verification-guided NL-to-QYIR construction framework |
| prompt-only QYIR generation remains a bottleneck | constrained construction reduces prompt-only QYIR bottlenecks |
| QYIR as audit boundary | QYIR as both generation target and audit boundary |
| deterministic no-oracle construction | structured slot extraction and deterministic QYIR building |
| live diagnostics | live construction evaluation |
| future work on constrained decoding | implemented constrained construction pipeline |
| verification chain effectiveness | end-to-end construction and verification effectiveness |

---

## 22. 路线 B 的阶段性决策规则

| 实验结果 | 决策 |
|---|---|
| Construction success < 0.20 | 不走路线 B 主线，只作为路线 A failure diagnosis |
| 0.20 到 0.30 | 写成路线 A 的 preliminary enhancement |
| 0.30 到 0.40 | 可作为弱路线 B，但主张要克制 |
| 0.40 到 0.50 | 可以正式写路线 B 主线，目标 CCF C |
| > 0.50 | 路线 B 有较强说服力，可以考虑更高目标 |
| 只有 schema validity 提升，semantic consistency 不升 | 只能 claim structural improvement，不能 claim reliable construction |
| retry 提升明显但 token 成本暴涨 | 需要加入 cost / latency trade-off 讨论 |
| 多模型差异很大 | 需要把 model dependency 写入 threats |

---

## 23. 最后建议

路线 B 的本质不是“多调几个 prompt”，而是把系统从：

```text
LLM 直接吐 QYIR
```

升级成：

```text
LLM 抽语义槽
程序构造 QYIR
验证器定位错误
LLM 局部修复
QSGA 后端审计
```

这才叫闭环。

如果路线 B 成功，你的论文就会从：

> 我提出了一个策略 IR，并证明后端验证链有效。

升级成：

> 我提出了一个面向规则型量化策略的自然语言到中间表示构造框架，并通过约束生成、确定性构造和验证反馈修复显著提升了 live LLM 策略构造可靠性。

这就不是“给论文补丁”，这是给论文装上第二台发动机。路线 A 是稳态飞行，路线 B 是准备爬升。🚀

