# QSGA 论文改进意见

## 一、总体判断

当前论文已经具备 **CCF C 候选稿雏形**，核心故事基本成立：

> 不是让 LLM 直接生成 Python 策略代码，而是先生成受约束的 QYIR 策略中间表示，再通过 schema verification、semantic verification、deterministic compilation、execution validation、risk audit、safe rejection 和 localized repair 来提高策略构造可靠性。

这个方向是合理的，而且比“我做了一个量化 Agent”更像科研论文。

但当前最大风险是：

> **主实验较依赖 deterministic prototype，而 live LLM 生成 QYIR 的 construction success 较低。**

所以论文不能吹成“QSGA 已经解决自然语言到可靠量化策略生成”，而应该收束成：

> **QSGA 证明了 IR-first verification pipeline 在受限规则策略空间内能显著提升策略规格构造的可验证性、可执行性、风险可控性和可修复性；当前 live LLM 生成 QYIR 仍是主要瓶颈。**

这句话就是论文的安全绳，系牢它，别让审稿人把你从悬崖边上一脚踹成科研蒲公英。🍃

------

# 二、必须优先修改的问题

## 1. 标题建议降火

当前标题：

> QSGA: Verification-Guided Strategy Specification Generation for Reliable Quantitative Strategy Construction from Natural Language

问题是 **from Natural Language** 会让审稿人期待你做了很强的自然语言理解或 LLM parsing。但当前 live QYIR construction success 只有 0.091，这会形成预期落差。

建议改成下面三选一。

### 推荐标题 1，最稳

> **QSGA: An IR-First Verification Framework for Reliable Rule-Based Quantitative Strategy Construction**

优点：稳、准、防御性强。

### 推荐标题 2，保留自然语言但降低承诺

> **QSGA: IR-First Verification-Guided Construction of Rule-Based Quantitative Strategies from Natural-Language Intents**

优点：保留 natural-language intents，但强调是 intents，不是任意自然语言到完整策略代码。

### 推荐标题 3，更像系统论文

> **QSGA: A Verification-Guided Intermediate Representation Framework for Reliable Quantitative Strategy Specification**

优点：突出 QYIR 和 verification，适合系统型 CCF C。

个人最推荐 **标题 1**。它像穿了防弹背心的标题，不浮夸，但很能活。

------

## 2. Abstract 需要重写，避免结果堆叠

当前 Abstract 信息很全，但数字太多，读者会先被 live 0.091 吓一跳。建议改成四段式：

### 建议结构

第一段：指出问题。

> LLMs enable novice users to express quantitative trading ideas in natural language, but directly generating executable code may introduce semantic omissions, invalid programs, hidden financial assumptions, and uncontrolled risk exposure.

第二段：提出方法。

> We propose QSGA, an IR-first verification-guided framework built around QYIR, a constrained strategy intermediate representation that exposes market scope, indicators, entry and exit rules, and risk controls as explicit slots.

第三段：解释实验层级。

> We evaluate QSGA through a three-level evidence hierarchy: a deterministic no-oracle prototype, an oracle-slot upper-bound verification-chain evaluation, and live LLM diagnostics.

第四段：谨慎结论。

> Results show that QYIR-based construction improves reliability when valid or partially valid strategy specifications can be constructed, while live diagnostics reveal that prompt-only QYIR generation remains the main bottleneck.

重点是：
**把 live 低结果从“失败”改写成“瓶颈定位证据”。**

科研写作里这叫“把摔跤写成地面摩擦系数测量”，优雅一点，别硬撑。🧪

------

## 3. Contribution 需要更锋利

当前贡献点偏长，可以压缩成四条，每条都要对应论文内容和实验。

建议改为：

### Contribution 1：问题形式化

> We formulate novice-oriented rule-based quantitative strategy construction as a bounded, verifiable, and risk-aware strategy specification generation problem, and define explicit failure types including schema failure, semantic inconsistency, compilation failure, execution failure, risk violation, ambiguity, unsupported intent, and unsafe intent.

### Contribution 2：QYIR

> We propose QYIR, a constrained quantitative strategy intermediate representation that makes market scope, indicators, trading rules, and risk controls interpretable, compilable, verifiable, and repairable.

### Contribution 3：QSGA

> We design QSGA, a verification-guided framework that integrates schema checking, semantic slot verification, deterministic compilation, execution validation, risk auditing, safe rejection, clarification, and localized repair.

### Contribution 4：实验与证据层级

> We construct QSI-Bench v1 and evaluate QSGA through deterministic no-oracle construction, oracle-slot upper-bound verification, live LLM diagnostics, ablation studies, and failure analysis.

这样贡献点会更像论文，不像项目说明书。

------

# 三、实验部分改进建议

## 1. 明确主实验不是 live LLM superiority

当前实验结果其实有三层：

| 层级                    | 作用                                      | 风险                      |
| ----------------------- | ----------------------------------------- | ------------------------- |
| deterministic no-oracle | 主实验，证明规则抽取 + QYIR pipeline 可行 | 会被说成不是 LLM          |
| oracle-slot upper-bound | 证明 verification chain 上限              | 会被说成 oracle leakage   |
| live diagnostics        | 证明真实 LLM 当前瓶颈                     | construction success 太低 |

建议在 Results 开头加一段非常明确的话：

> The live LLM results are not used as the main evidence of QSGA's superiority over direct code generation. Instead, they are included as diagnostic evidence to identify whether current prompt-only models can reliably enter the QYIR verification chain. The main claim is based on the deterministic no-oracle prototype and the oracle-slot verification-chain evaluation.

中文意思：

> live 不是我的主胜利证据，是我定位瓶颈的解剖刀。

这能挡住很多攻击。

------

## 2. `qsga_full` 必须反复标注为 upper-bound

你现在已经写了 oracle-slot upper-bound，但建议所有相关表格标题都显式写：

> **Oracle-Slot Upper-Bound Verification-Chain Evaluation**

不要只写 `qsga_full`，否则审稿人可能以为你在拿金标槽位和 baseline 公平比较。

建议表格里把方法名改成：

| 原方法名             | 建议论文展示名                         |
| -------------------- | -------------------------------------- |
| qsga_full            | QSGA oracle-slot upper bound           |
| qsga_no_oracle_slots | QSGA no-oracle deterministic prototype |
| live_qsga_qyir       | Live QSGA-wrapped QYIR diagnostic      |
| live_direct_code     | Live direct-code diagnostic            |

命名要像交通标志一样清楚，别让审稿人在雾里开车。🚦

------

## 3. 增加一个 “QYIR vs JSON Schema” 强案例表

这是目前最值得补的一张表。因为审稿人一定会问：

> 你这个 QYIR 不就是 JSON Schema 吗？

建议新增表格：

| User Intent                                            | Schema-Valid JSON? | QYIR Check                          | Result                    |
| ------------------------------------------------------ | ------------------ | ----------------------------------- | ------------------------- |
| “不要杠杆” but leverage=2.0                            | Yes                | semantic slot verification          | reject or repair leverage |
| Rule refers to undefined `sma_60`                      | Possibly Yes       | alias resolution before compilation | compilation blocked       |
| “最大回撤不超过10%” but max_drawdown_limit=0.2         | Yes                | risk slot consistency check         | repair or reject          |
| “稳赚不亏”                                             | Yes                | safe rejection                      | no QYIR generation        |
| `entry_rules` has valid array but unsupported operator | Possibly Yes       | QYIR operator semantics             | schema/compile failure    |

然后在正文中强调：

> JSON Schema checks shape; QYIR checks domain meaning.

这句话很关键。建议写进论文。

------

## 4. 补充统计置信度或至少补充 Wilson interval

当前没有显著性检验，你也说明了原因。但为了显得更严谨，可以加一个简单的置信区间，尤其是样本量只有 80。

例如：

> We report Wilson 95% confidence intervals for major proportion metrics.

不用复杂统计，Wilson interval 就够。比如 E2E success 0.887 on 80 samples，可以给区间。这样审稿人会觉得你知道样本小这个问题，不是在装看不见。

------

## 5. 增加 case-level appendix

建议附录增加 6 到 8 个完整案例，每个案例包含：

1. user query
2. generated QYIR
3. verification trace
4. repair diff if any
5. final decision
6. whether counted as success

尤其要覆盖：

| 类型                | 案例                 |
| ------------------- | -------------------- |
| trend following     | 双均线               |
| mean reversion      | RSI 反转             |
| risk constrained    | 最大回撤不超过 10%   |
| ambiguous           | 稳一点，别追高       |
| unsafe              | 稳赚不亏             |
| live QYIR failure   | Bollinger 字段错误   |
| direct-code failure | 语义不匹配但代码能跑 |

这会让论文从“表格堆数据”变成“机制可视化”。审稿人读起来不至于变成 Excel 囚犯。📊

------

# 四、方法部分改进建议

## 1. QYIR 定义可以更形式化

现在 QYIR 写成：

> S = <M, I, E_in, E_out, R>

很好，但可以再加强一点。

建议增加：

```text
A QYIR strategy is valid iff:
1. all indicators belong to the supported indicator set;
2. all rule operands resolve to either market fields or indicator aliases;
3. all rule operators belong to the supported operator set;
4. risk-control fields satisfy hard constraints;
5. the compiled strategy produces executable signal series over the target data schema.
```

这能让 QYIR 看起来不像“配置文件”，而是有 formal semantics 的 IR。

------

## 2. Semantic Verification 要严格降级

你现在提到了 semantic slot checking，但一定不要暗示它能理解所有模糊金融意图。

建议加一句：

> Semantic verification in QSGA is intentionally limited to explicit or conservatively extracted intent slots. It does not claim to infer hidden investor preferences, subjective risk tolerance, or vague financial goals.

这能防止 “LLM-as-judge 悖论” 攻击。

尤其是 “稳一点”“别追高” 这类表达，应该明确：

> ambiguous intent should trigger clarification rather than forced semantic interpretation.

这句话要在 Method 和 Threats to Validity 里各出现一次。

------

## 3. Safe Rejection 不能写成金融安全

当前 safe rejection 只是 explicit unsafe phrases 和 unsupported intents 的边界控制，不是完整金融合规系统。

建议统一称为：

> boundary-control rejection

或者：

> explicit unsafe-intent rejection

避免让审稿人以为你在做金融安全合规。

建议加一句：

> Safe rejection in this paper refers only to explicit unsafe or unsupported requests in the benchmark, not to comprehensive investment safety, compliance, or suitability assessment.

这句话很救命。它是论文里的安全气囊。🎈

------

## 4. Repair 机制要强调“保守修复”

当前 repair 很重要，但要避免被质疑：

> 你是不是为了通过风险审计，偷偷改用户约束？

建议补充 repair invariant：

```text
Repair invariant:
1. The system may reduce risk exposure.
2. The system may add conservative risk controls.
3. The system must not weaken user-specified constraints.
4. The system must not change the strategy family unless explicitly allowed.
5. Every repair must be recorded as a field-level diff.
```

这个可以放在 Localized Repair 小节。

------

# 五、Related Work 改进建议

## 1. Related Work 现在已经够完整，但要更早进入“closest work”

当前 Related Work 写得很扎实，但略长。建议把最重要的三类提前：

1. QuantCode-Bench / Market-Bench / QuantEval
2. SysTradeBench
3. OQL / Domain IR

然后再写 general code generation、Toolformer、ReAct、PICARD。

原因是审稿人最关心：

> 你和最近这些 trading / finance / strategy benchmark 到底有什么区别？

不要让他读到第 4 页才看到核心对比。先把最近邻居摆出来，别让审稿人在论文小区里迷路。

------

## 2. Closest Work 表格很好，建议保留并前移

你现在的 Positioning Against Closest Work 表格是亮点，建议不要只放在 Related Work 最后，可以在 Introduction 末尾提前引用一次：

> Table X summarizes QSGA's position against closest trading-strategy generation and financial LLM benchmarks.

这会让论文的差异性更早出现。

------

# 六、Threats to Validity 改进建议

当前 Threats 写得比较诚实，这是好事。但可以再加一个小节：

## 1. Add: “Rule-Based Extractor Bias”

因为 no-oracle extractor 是 deterministic rule-based，可能偏向 benchmark 中的规则表达方式。

建议增加：

> The no-oracle extractor may benefit from lexical overlap with QSI-Bench v1 because both are built within the same bounded strategy taxonomy. Therefore, the result should be interpreted as prototype feasibility rather than robust open-domain natural-language understanding.

这句话虽然听着像自砍一刀，但其实是主动缴械，换取审稿人信任。

------

## 2. Add: “Benchmark Construction Bias”

QSI-Bench v1 是你自己构造的 benchmark，审稿人可能问是否 biased。

建议增加：

> QSI-Bench v1 is curated to test predefined failure modes in the supported rule-based strategy space. It is not a naturally collected user-query corpus. Future work should include real novice-user queries and independent annotation.

这个必须写。

------

## 3. Add: “Financial Validity”

你已经说不保证收益，但还可以更明确：

> Passing QSGA verification means that the artifact is structurally valid, executable, and consistent with selected risk constraints under the prototype setting. It does not imply profitability, robustness, suitability, or deployability in real financial markets.

这句话建议放进 Conclusion 前后都可以。

------

# 七、如果时间允许，建议补一个小用户实验

如果你想把 novice-oriented 讲得更硬，建议加一个轻量用户研究。

## 实验设计

参与者：6 到 10 名非量化专业学生。

任务材料：

| 条件        | 材料                       |
| ----------- | -------------------------- |
| Direct Code | LLM 生成的 Python 策略函数 |
| QYIR        | QSGA 生成的 QYIR 策略规格  |

任务：

1. 判断策略使用了什么指标。
2. 判断是否使用杠杆。
3. 判断是否包含止损。
4. 判断最大仓位是多少。
5. 判断入场条件和出场条件。
6. 给出可理解性评分，1 到 5。
7. 给出可修改性评分，1 到 5。

指标：

| 指标                       | 含义                       |
| -------------------------- | -------------------------- |
| Understanding Accuracy     | 用户正确理解策略规则的比例 |
| Risk Recognition Accuracy  | 用户正确识别风险设置的比例 |
| Time to Answer             | 完成理解任务时间           |
| Perceived Interpretability | 主观可解释性评分           |
| Perceived Editability      | 主观可修改性评分           |

如果结果显示 QYIR 比 direct code 更容易理解，你的 novice-facing claim 会立刻硬起来。

没有用户实验也能投 C，但有这个会更香，像论文里撒了一把科研孜然。🌶️

------

# 八、建议新增或重画的图表

## Figure 1：Problem Motivation

展示：

```text
Natural Language Intent
        ↓
Direct Code Generation
        ↓
Failure Surface:
semantic omission / invalid program / runtime error / risk violation / unsafe intent
```

旁边再展示：

```text
Natural Language Intent
        ↓
QYIR
        ↓
Verification Chain
        ↓
Executable Strategy + Risk Report
```

重点是形成对照。

------

## Figure 2：QSGA Architecture

保留当前架构，但建议图中把每个 verifier 的输入输出写清楚：

| 模块              | 输入            | 输出                |
| ----------------- | --------------- | ------------------- |
| Safe Rejection    | user query      | reject / continue   |
| QYIR Generator    | user query      | candidate QYIR      |
| Schema Verifier   | QYIR            | schema errors       |
| Semantic Verifier | query + QYIR    | slot conflicts      |
| Compiler          | QYIR            | executable strategy |
| Backtester        | strategy + data | metrics             |
| Risk Auditor      | QYIR + metrics  | pass / repair       |
| Repair            | errors + QYIR   | repaired QYIR       |

------

## Figure 3：QYIR vs JSON Schema

强烈建议画成对照图。

左边：

```text
Generic JSON Schema:
field exists?
type correct?
enum valid?
```

右边：

```text
QYIR:
alias resolves?
rule compiles?
risk slot matches intent?
unsafe intent rejected?
repair path localized?
```

这张图非常适合放论文里，杀伤力比一堆文字强。

------

# 九、建议的修改优先级

## P0：必须改，不改容易被打

| 问题                   | 修改                                  |
| ---------------------- | ------------------------------------- |
| 标题承诺过强           | 改成 IR-first verification framework  |
| Abstract 数字堆叠      | 重写成问题、方法、实验层级、谨慎结论  |
| live QYIR 结果低       | 明确作为 diagnostic，不作为主胜利证据 |
| oracle-slot 可能被质疑 | 所有地方标注 upper-bound              |
| QYIR 像 JSON Schema    | 增加 QYIR vs JSON Schema 案例表       |
| novice claim 缺证据    | 弱化 novice usability，或补小用户实验 |

## P1：强烈建议改，能明显提分

| 问题                             | 修改                             |
| -------------------------------- | -------------------------------- |
| QYIR formalization 不够          | 增加 valid iff 条件              |
| Semantic Verification 容易被攻击 | 明确只检查 explicit slots        |
| Repair 可能被质疑                | 增加 repair invariant            |
| 样本量小                         | 加 Wilson confidence interval    |
| benchmark 自建                   | 增加 benchmark construction bias |

## P2：有时间再改，会锦上添花

| 问题              | 修改                                          |
| ----------------- | --------------------------------------------- |
| case 不够生动     | 加 appendix case trace                        |
| 图表还可增强      | 重画 motivation / architecture / QYIR-vs-JSON |
| Related Work 偏长 | 前移 closest work                             |
| 用户研究缺失      | 做 6 到 10 人小实验                           |

------

# 十、最终建议版本定位

建议你把论文最终定位改成下面这句话：

> **This paper does not claim to solve open-domain natural-language trading strategy generation. Instead, it studies whether an explicit, constrained strategy intermediate representation can make rule-based quantitative strategy construction more verifiable, executable, risk-aware, and repairable in a bounded novice-facing setting.**

中文意思：

> 本文不声称解决开放域自然语言量化策略生成，而是研究在受限的新手友好规则策略空间中，显式策略中间表示是否能让策略构造过程更可验证、可执行、风险可控、可修复。

这就是你的论文护城河.

------

## 最后结论

现在这篇论文最该做的不是继续膨胀成“量化 Agent 银河战舰”，而是收束成一篇 **IR-first verification framework** 的系统论文。

你要让审稿人看到三件事：

1. **问题真实**：LLM 直接生成策略代码确实不可靠。
2. **机制清楚**：QYIR 让策略语义、风险约束、编译引用和修复位置显式化。
3. **证据诚实**：deterministic pipeline 有效，oracle 是上限，live LLM 暴露瓶颈。

这样写，CCF C 是能冲的。
别贪大，贪稳。论文不是烟花，是桥。你现在桥墩已经打下去了，下一步是把桥面铺平，别让审稿人开车开到一半掉进实验设计的河里。🌉