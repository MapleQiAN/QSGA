# Reviewer Gate

本文件用于模拟审稿人检查论文是否达到投稿标准，尤其面向计算机科学、人工智能、软件工程、信息安全、金融科技和智能体系统方向。

---

## TLDR_STATE_FOR_AGENT

审稿模拟时必须检查：

1. 问题是否真实且重要。
2. 方法是否有清晰贡献，而不是工具拼接。
3. 实验是否支撑核心 claim。
4. baseline 是否合理。
5. 消融是否解释方法组件价值。
6. 失败分析是否充分。
7. 引用是否准确。
8. 复现材料是否可信。
9. 结论是否克制。
10. 是否存在一票否决问题。

---

## 1. 一票否决项

出现以下问题，建议 Reject 或 Major Revision：

- 核心引用无法验证。
- 没有合理 baseline。
- 方法贡献说不清，只是工具堆叠。
- 实验指标与论文贡献不匹配。
- 结论明显强于证据。
- 数据集或实验设置不可复现。
- 伦理、隐私或版权风险没有处理。
- 声称金融收益但没有严格风控和评估。
- 使用 LLM 作为 judge 但没有说明其边界和校验方式。

---

## 2. 评分维度

| 维度 | 分数 1 | 分数 3 | 分数 5 |
|---|---|---|---|
| Novelty | 几乎无创新 | 有组合创新 | 明确方法或评估创新 |
| Technical Soundness | 逻辑不成立 | 基本成立但有缺口 | 严谨且证据充分 |
| Experiments | 缺 baseline | 有基本实验 | baseline、消融、失败分析完整 |
| Writing | 难以理解 | 基本清楚 | 叙事清晰有说服力 |
| Reproducibility | 不可复现 | 局部可复现 | 可完整复现 |
| Relevance | 与会议弱相关 | 相关 | 高度相关 |

---

## 3. 审稿输出模板

```text
## Reviewer Report

Overall Rating:
Confidence:
Summary:
Strengths:
Weaknesses:
Major Concerns:
Minor Concerns:
Questions for Authors:
Required Experiments:
Required Writing Changes:
Risk of Rejection:
Recommendation: Accept / Weak Accept / Borderline / Weak Reject / Reject
```

---

## 4. CCF C 投稿最低建议

面向 CCF C，至少需要：

- 一个清晰问题。
- 一个能讲明白的核心方法。
- 可信 baseline。
- 至少一个主实验。
- 至少一个消融或失败分析。
- 结论克制。
- 复现材料基本可用。
- 引用真实且覆盖相关方向。

如果实验很弱，必须收窄 claim。
如果 claim 很强，必须增强实验。
