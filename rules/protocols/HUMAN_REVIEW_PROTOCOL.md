# Human Review Protocol

本文件定义哪些节点必须人类确认，以及 Agent 如何提交决策项。

---

## TLDR_STATE_FOR_AGENT

必须人审：

- 改研究方向
- 改核心 claim
- 冻结或修改核心实验协议
- 新增或删除关键 baseline
- 接受与假设相反的结果并改论文叙事
- 投稿、公开代码、公开数据、署名、致谢
- 使用付费 API、隐私数据、版权不明数据

Agent 不能原地等待，必须写入 `DECISIONS.md` 后继续非阻塞任务。

---

## 1. 人审触发条件

触发条件：

1. 影响研究问题。
2. 影响核心贡献。
3. 影响实验协议。
4. 影响论文主张强度。
5. 影响投稿目标。
6. 涉及伦理、隐私、版权、署名、费用。
7. 涉及不可逆操作。

---

## 2. 决策项格式

```yaml
Decision ID:
Title:
Context:
Options:
AI Recommendation:
Default Assumption:
Risk if Wrong:
Blocking:
Non-Blocked Work Can Continue:
```

---

## 3. 默认假设

在等待人类回复时，Agent 可以使用默认假设继续低风险工作，但不得执行不可逆操作。

示例：

```text
默认假设：暂不新增该 baseline，但继续整理已有 baseline 的实验协议。
```
