# Quality Guardrails

本文件定义科研质量护栏。用于防止论文叙事过强、实验不足、引用失真和复现缺失。

---

## TLDR_STATE_FOR_AGENT

审查重点：

1. Claim 是否有证据等级。
2. 实验是否有 baseline、指标、数据、seed、命令和日志。
3. 引用是否真实可核验。
4. 结论是否强于证据。
5. 失败结果是否被记录。
6. 是否存在伦理、隐私、版权或数据许可风险。

---

## 1. Claim Guardrail

每个论文 claim 必须回答：

```text
Claim:
Evidence Level: A / B / C / D / X
Supporting Evidence:
Contradicting Evidence:
Allowed Wording:
Forbidden Wording:
```

若证据等级为 C/D/X，禁止作为核心贡献或核心结论。

---

## 2. Experiment Guardrail

每个实验必须具备：

- 研究问题
- baseline
- 指标
- 数据集来源和许可
- 代码版本
- 环境
- seed
- 命令
- 原始输出
- 失败记录
- 对 claim 的影响

缺任意关键项，不得写成强结论。

---

## 3. Citation Guardrail

引用必须满足：

- 作者、年份、标题、 venue 可核验。
- 不得编造 DOI。
- 不得把 survey 写成实验论文。
- 不得把未发表博客当作强学术证据。
- 不得引用与 claim 无关的论文当装饰。

---

## 4. Writing Guardrail

禁止无证据强词：

- 首次
- 最优
- 显著
- 证明
- 完全解决
- 通用
- SOTA
- robustly outperforms

建议替代表达：

- preliminary results suggest
- under our evaluated setting
- improves the construction reliability in our benchmark
- reduces observed failure cases
- provides an auditable intermediate representation

---

## 5. Reproducibility Guardrail

复现等级：

| 等级 | 含义 |
|---|---|
| R0 | 无法复现 |
| R1 | 只有描述 |
| R2 | 有代码但缺配置或数据 |
| R3 | 有代码、配置、数据说明 |
| R4 | 可一键运行主要实验 |
| R5 | 可完整复现全部结果、表格和图 |

投稿前核心实验至少应达到 R3，最好达到 R4。
