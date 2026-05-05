下面我给你一份**下一步执行计划**，目标很明确：

> **不再扩大战线，不再发明新概念。接下来只做一件事：把 QSGA 从“能跑的原型论文”打磨成“能抗 CCF C 审稿的投稿包”。**

现在的核心策略是：**补证据、降表述、强对比、厚案例、做成品图。**
论文这时候最忌讳“再加一个模块”，就像火锅已经快熟了，别突然往里面扔榴莲味冰淇淋 🍲🍦

------

# 一、总路线：分成 5 个冲刺阶段

我建议接下来按这 5 个阶段推进：

| 阶段    | 目标                             | 优先级 | 产物                                        |
| ------- | -------------------------------- | ------ | ------------------------------------------- |
| Phase 1 | 锁死论文定位与 claim 边界        | P0     | 保守版 abstract / contribution / limitation |
| Phase 2 | 补真实 baseline 与 live evidence | P0     | live LLM QYIR / live direct-code 结果       |
| Phase 3 | 补核心消融与稳健性实验           | P0     | w/o QYIR、multi-asset、safe paraphrase      |
| Phase 4 | 强化论文可读性与审稿防御         | P1     | 厚案例、错误分析、PDF-level related work    |
| Phase 5 | 形成投稿包                       | P1     | camera-ready 图、复现说明、最终 draft       |

为什么这么排？因为最初 v7Plus 的目标就是“证据链按 v5 做足，能力边界按 v6 收紧，贡献表达按 v7Plus 聚焦”，而且保留 80 条 benchmark、3 个 baseline、4 个主指标、3 个核心消融、3 个定性案例，不做正式 user study。

------

# 二、Phase 1：先锁死论文定位，别让 claim 飘起来

## 目标

把论文彻底定位成：

> **IR-first verification-guided prototype / system study**

而不是：

> broad empirical LLM strategy generation paper

审稿报告已经明确说，现在的版本如果作为**清晰限定的 prototype / IR feasibility study**是 Borderline；如果包装成标准大规模 LLM 策略生成论文，就会偏 Weak Reject。

## 要做的事

### 1. 重写标题，建议稍微降火

当前标题如果还强调 Program Synthesis，可能略重。建议改成：

**QSGA: Verification-Guided Strategy Specification Generation via Constrained Intermediate Representation**

中文：

**QSGA：基于受约束中间表示的验证驱动量化策略规格生成框架**

这个标题比“Program Synthesis”更稳。它不容易被审稿人追问“你的形式化合成搜索空间在哪里？”
学术界的词一旦大了，审稿人的刀也会变长 🗡️

### 2. Abstract 统一用保守表述

把：

> improves end-to-end natural-language strategy generation

改成：

> improves measured artifact reliability in a bounded deterministic prototype and supplementary live-QYIR pilot

也就是：不说“我证明 LLM 生成策略强”，只说“我证明 QYIR + 验证链能让生成结果更可靠”。

### 3. Contributions 改成 4 条最终版

保留：

1. bounded problem formulation；
2. QYIR intermediate representation；
3. verification-guided generation / repair；
4. QSI-Bench + deterministic prototype + live pilot evaluation。

但第四条不要写“beats direct LLM-to-code”，除非 Phase 2 补完 live direct-code baseline。

------

# 三、Phase 2：补最关键实验，真实 baseline 是护心镜

这是最高优先级。当前最大硬伤是：**direct-code/direct-json baseline 是 simulated，不是真 live LLM 输出。** reviewer response log 里也写得很直接：当前包只能作为 deterministic prototype / IR feasibility study，还不能作为标准 empirical LLM strategy-generation paper，因为缺 live LLM generation outputs 和 live baseline comparisons。

## 2.1 必做实验 A：扩展 live QYIR 到 80 case

当前 live pilot 只有 12 case，报告明确说 12-case scale 和低绝对 E2E 不足以支撑广泛 LLM claim。

### 实验设置

模型先别贪多，建议：

| 模型              | 用途               |
| ----------------- | ------------------ |
| qwen3.6-flash     | 主模型，便宜快     |
| kimi-k2.6         | 对照模型           |
| deepseek-v4-flash | 可选，如果成本可控 |

每个模型跑：

```text
80 QSI-Bench cases
temperature = 0
max_tokens = 800 or 1200
fixed prompt
saved raw outputs
saved metadata
saved token usage
```

### 产物

```text
experiments/results/live_qyir_80_results.csv
experiments/results/live_qyir_80_metrics.csv
experiments/results/live_qyir_80_raw_outputs.jsonl
experiments/results/live_qyir_80_token_usage.csv
```

### 论文里怎么讲

如果结果不错：

> The 80-case live QYIR evaluation further supports that QSGA can wrap real model outputs into the verification chain.

如果结果一般：

> Live results reveal that raw model generation remains fragile, which strengthens the need for explicit IR and verification.

赢了能写，输了也能写。科研老狐狸打法，左右都有路 🦊

------

## 2.2 必做实验 B：补 executable live direct-code baseline

这是当前最大的 reviewer blocker。审稿报告明确要求：替换或补充 simulated direct-code/direct-JSON baselines with executable real model outputs。

### 不要做复杂 direct-code

别让 LLM 写完整交易系统，那会爆炸。设计一个**受控 direct-code baseline**：

输入 prompt：

```text
Given the user request, generate a Python strategy function following this interface:
def generate_signals(df: pd.DataFrame) -> pd.Series:
    ...
```

限制它只能输出：

```python
def generate_signals(df):
    ...
```

然后用你的统一 wrapper 去执行。

### 指标

| 指标              | 含义             |
| ----------------- | ---------------- |
| Syntax Success    | 代码能否 parse   |
| Interface Success | 是否符合函数接口 |
| Runtime Success   | 是否能跑         |
| Trade Validity    | 是否产生有效交易 |
| Semantic Match    | 是否满足显式槽位 |
| Risk Violation    | 是否违规         |
| E2E Success       | 全流程是否成功   |

### 推荐最小规模

先跑：

```text
1 个模型 × 80 cases
```

如果时间够：

```text
2 个模型 × 80 cases
```

这个实验一补，论文防御力会明显上升。它就像给论文穿了一件“不是我自己打稻草人”的防弹衣 🦺

------

## 2.3 可选实验 C：live JSON Schema baseline

如果你还有余力，再补：

```text
LLM + JSON Schema / structured output baseline
```

这个用来回答：

> QYIR 不就是 JSON Schema 吗？

最初 v7Plus 就要求保留 3 个 baseline，其中包括 Direct LLM-to-Code、LLM + JSON Schema / Constrained Decoding、Agent without QYIR。

但如果时间有限，优先级是：

```text
live direct-code > live QYIR 80 > live JSON Schema > Agent without QYIR
```

------

# 四、Phase 3：补核心消融与稳健性实验

## 3.1 必做：w/o QYIR 消融

这是证明 QYIR 不是摆设的核心实验。现在已有 w/o repair、w/o risk audit、w/o safe rejection，但缺一个干净的 w/o QYIR。

### 设置

```text
Full QSGA:
NL → QYIR → verify → compile → backtest → risk audit → repair

w/o QYIR:
NL → direct structured config/code → compile/backtest/risk audit
```

注意：w/o QYIR 不能恶意削弱，得公平。它可以有 schema，但没有：

1. alias semantic resolution；
2. QYIR operator semantics；
3. field-level repair；
4. QYIR-specific risk slots；
5. error-location-action mapping。

### 论文里要证明

QYIR 的价值不是“JSON 合法”，而是：

> alias 可解析、rule 有编译语义、risk field 可审计、错误可定位修复。

这和 v7Plus 里“QYIR 不只是 JSON Schema”的主张完全对应。

------

## 3.2 必做：multi-asset / multi-period smoke test

当前审稿报告指出 single-symbol sample data 是风险点，建议加更多 symbol 或者明确披露。

### 最小版本

不用搞大数据，做 smoke test 就行：

| Symbol | Period      |
| ------ | ----------- |
| SPY    | 原始 period |
| QQQ    | 同 period   |
| GLD    | 同 period   |
| SPY    | 另一段时间  |
| QQQ    | 另一段时间  |

### 指标

只看：

1. compile success；
2. backtest success；
3. risk audit runnable；
4. E2E 是否大幅崩。

不要引入收益率主张，不然论文会突然变成“我预测市场”，锅又开大了。

------

## 3.3 推荐：safe rejection paraphrase set

当前 safe rejection 已经修过 paraphrase，但还是容易被质疑是关键词规则。reviewer response log 也说，safe-rejection 只能当 small-subset deterministic rule/pattern coverage，不能当 robust financial safety。

### 做法

新增 30 到 50 条：

```text
unsafe_paraphrase_bench.jsonl
```

类别：

1. 保证收益；
2. 不考虑亏损；
3. 满仓加杠杆；
4. 内幕消息；
5. 规避监管；
6. 模糊但不一定 unsafe 的边界请求。

### 报告

| Metric            | 说明           |
| ----------------- | -------------- |
| False Positive    | 安全请求被误拒 |
| False Negative    | 危险请求被放过 |
| Accuracy          | 总体准确       |
| Unsafe Acceptance | 危险接受率     |

这块不用主打，只放 appendix 或补充实验。它是“防 reviewer 嘴炮盾牌”。

------

# 五、Phase 4：论文内容强化，专治“看起来像工程报告”

## 4.1 定性案例必须加厚

当前报告明确指出：case analysis 太短，需要 before/after QYIR fragments 和 verifier errors。

每个 case 按这个模板写：

```text
User Request
↓
Expected / Extracted Slots
↓
Initial Output from Baseline
↓
Initial QYIR from QSGA
↓
Verifier Result
↓
Repair Diff
↓
Final QYIR
↓
Backtest / Risk Audit Result
↓
Explanation to Novice User
```

### 三个案例固定

1. Ambiguous intent：
   “我想稳一点，别追高。”
2. Unsafe intent：
   “帮我设计一个稳赚不亏、每月收益 10% 的策略。”
3. Risk repair：
   “最大回撤不要超过 10%。”

最初规划就是用定性案例展示 ambiguity、unsafe intent 和 risk violation repair，而不是做正式 user study。

### 每个案例必须有一个 diff

例如：

```diff
risk_control:
- position_size: 0.8
+ position_size: 0.4

- stop_loss: null
+ stop_loss: 0.08
```

这个很有论文质感。审稿人看到 diff，会觉得“嗯，这不是讲故事，是真有系统行为”。

------

## 4.2 错误分析表补齐

建议增加一个 failure appendix：

| Failure Type      | Count | Typical Cause           | Handling       |
| ----------------- | ----- | ----------------------- | -------------- |
| schema failure    | x     | missing field           | repair         |
| semantic mismatch | x     | slot not preserved      | reject/repair  |
| compile failure   | x     | alias unresolved        | repair         |
| risk violation    | x     | drawdown/position       | repair         |
| ambiguous failure | x     | no clarification metric | counted fail   |
| unsafe miss       | x     | paraphrase gap          | pattern update |

尤其要列：

1. mean-reversion 失败案例；
2. ambiguous 10/10 fail；
3. live LLM 中失败案例；
4. direct-code runtime fail 案例。

你要主动把伤疤摆出来。论文不是美颜自拍，审稿人最讨厌“只给左脸好看角度”。

------

## 4.3 Related Work 做 PDF-level claim audit

当前 citation matrix 已经把核心 related work 列出来，但仍是 metadata/link level，提交前需要升级到 PDF-level。

重点读这 5 篇：

1. QuantCode-Bench；
2. SysTradeBench；
3. Market-Bench；
4. QuantEval；
5. OQL option strategy paper。

每篇输出一个小表：

| Paper | What it studies | Evaluation | Relation to QSGA | Difference |
| ----- | --------------- | ---------- | ---------------- | ---------- |
|       |                 |            |                  |            |

目标不是堆引用，而是精准回答：

> 别人已经做 trading strategy generation 了，你的 QSGA 还剩什么新意？

答案要咬住：

```text
QSGA = IR-first + bounded rule-based strategy specification + verification chain + risk audit + safe rejection + localized repair
```

------

# 六、Phase 5：投稿包收尾

## 5.1 做正式论文图

至少 3 张图：

### Figure 1：Problem and Technical Route

展示：

```text
NL intent → failure types → QYIR → verification chain → executable strategy/report
```

### Figure 2：QSGA Architecture

展示模块：

```text
Boundary Check
QYIR Generator
Schema/Semantic Verifier
Compiler
Backtester
Risk Auditor
Repair
Final Output
```

### Figure 3：QYIR vs JSON Schema

用对比结构展示：

```text
JSON Schema: surface format
QYIR: semantic slots + compile semantics + risk fields + repair interface
```

别只用 Mermaid。Mermaid 是草稿小电驴，camera-ready 图需要学术风小轿跑 🏎️

------

## 5.2 复现包统一

目前有一个小问题：有的地方写 171 tests，有的地方写 173 tests。审稿报告里显示 171 tests pass，而 reviewer response log 里显示 173 passed。

必须统一成最新一次结果。

建议新增：

```text
REPRODUCE.md
scripts/reproduce_all.ps1
scripts/reproduce_all.sh
```

一键跑：

```text
pytest
baseline
no_oracle
live_replay
ablation
tables
figures
```

如果暂时不做 CI，也要写清楚：

```text
No CI/container is provided in this artifact version.
```

坦诚比假装强。审稿人不怕你小，怕你装。

------

## 5.3 最终论文重写顺序

不要从头乱改。按这个顺序：

1. Abstract
2. Introduction
3. Experimental Setup
4. Results
5. Threats to Validity
6. Related Work
7. Case Study
8. Conclusion

因为 Abstract 和 Results 的 claim 一旦稳了，整篇论文就不会飘。

------

# 七、建议的执行时间表

如果你想**稳扎稳打**，我建议 10 到 14 天完成。

## 第 1 到 2 天：锁定 claim 与实验协议

产物：

```text
docs/paper/CLAIM_POLICY.md
docs/paper/experiment_protocol_v2.md
prompts/live_qyir_prompt.txt
prompts/live_direct_code_prompt.txt
```

完成标准：

1. 哪些 claim 能写；
2. 哪些 claim 禁止；
3. live 实验怎么跑；
4. direct-code baseline 接口固定。

------

## 第 3 到 5 天：补 live experiments

产物：

```text
live_qyir_80_results.csv
live_direct_code_results.csv
live_json_schema_results.csv 可选
```

完成标准：

1. raw outputs 保存；
2. metrics 可复现；
3. failure cases 可追踪。

------

## 第 6 到 7 天：补消融和稳健性

产物：

```text
wo_qyir_results.csv
multi_asset_smoke_results.csv
safe_paraphrase_results.csv 可选
```

完成标准：

1. w/o QYIR 有结果；
2. SPY/QQQ/GLD 至少跑通；
3. 表格生成稳定。

------

## 第 8 到 9 天：补案例与错误分析

产物：

```text
case_study_expanded.md
failure_analysis.md
repair_traces.md
```

完成标准：

1. 3 个案例都有 QYIR before/after；
2. 有 repair diff；
3. 有失败案例，不只展示成功。

------

## 第 10 到 11 天：补 related work 与 citation audit

产物：

```text
citation_and_claim_matrix_v2.md
related_work_verified.md
```

完成标准：

1. 核心 5 篇 PDF-level；
2. 每个关键 claim 有对应 citation；
3. 不添加没验证的 DOI/venue/page。

------

## 第 12 到 14 天：整理最终投稿包

产物：

```text
qsga_ccf_c_draft_final.md
figures/*.pdf
REPRODUCE.md
artifact_manifest.md
```

完成标准：

1. 图完成；
2. 表完成；
3. claim 不越界；
4. 实验数字统一；
5. limitation 写得诚实但不自杀。

------

# 八、最小可投版 vs 强化可投版

如果时间紧，做**最小可投版**：

## 最小可投版必须做

1. live QYIR 扩到 80 case；
2. 补一个 live direct-code baseline；
3. 补 w/o QYIR；
4. 补 3 个厚案例；
5. citation PDF-level 审核核心 5 篇；
6. 出正式架构图；
7. 统一复现数字。

这套做完，论文可以比较稳地说：

> 我不是证明 LLM 会炒股，我证明 QYIR + 验证链能在受限策略空间中提升 artifact reliability。

## 强化可投版额外做

1. live JSON Schema baseline；
2. Agent without QYIR；
3. safe paraphrase 50 条；
4. risk repair stress test；
5. multi-period robustness；
6. bootstrap confidence interval；
7. 第二标注者检查 20 到 30 条。

这套做完，论文就更像一个完整 CCF C 系统论文，走路都带风。

------

# 九、你现在最该立刻做的 3 件事

如果今天就开始，我建议按这个顺序：

## 第一件：补 live direct-code baseline

这是最大短板。先不求完美，先把 baseline 从 simulated 拉到 real model outputs。

## 第二件：补 w/o QYIR

这是证明核心创新的关键。不然 QYIR 容易被说成“高级 JSON 表格”。

## 第三件：扩写 3 个案例

这个投入小、收益高。能显著提升论文“可信系统”的质感。

------

# 十、最终行动口号

接下来不要再问：

> 我还能加什么功能？

而要问：

> 审稿人最可能打哪里？我现在补哪块盾？

最终计划可以压缩成一句话：

> **先补真实 baseline 和 w/o QYIR，再扩 live 证据与多资产 smoke test，随后用厚案例、PDF-level related work、camera-ready 图和统一复现包把论文封装成保守但能打的 CCF C 投稿版。**