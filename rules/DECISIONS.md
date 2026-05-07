# DECISIONS.md

本文件记录需要人类确认的研究决策。Agent 遇到人类决策点时写入这里，然后继续做不依赖该决策的任务，不要原地等待。

---

## TLDR_STATE_FOR_AGENT

当前待人类确认：

- 暂无

当前可继续推进：

- 所有不依赖待确认事项的低风险任务都可继续。

默认处理：

- 如果某任务被人类决策阻塞，将该任务标为 `blocked_human`。
- 返回 `TASK_QUEUE.md` 选择其它非阻塞任务。

---

## PendingReview

暂无。

---

## waiting_human

暂无。

---

## Done

暂无。

---

## Decision Template

```yaml
Decision ID: DEC-YYYYMMDD-NNN
Title:
Status: PendingReview / waiting_human / accepted / rejected / superseded
Created:
Updated:
Related Task ID:
Related Claim ID:
Context:
Options:
  A:
    Description:
    Pros:
    Cons:
  B:
    Description:
    Pros:
    Cons:
AI Recommendation:
Default Assumption Before Human Response:
Risk if Wrong:
Blocking:
  - 
Non-Blocked Work Can Continue:
  - 
Human Response:
Final Decision:
Audit Log Reference:
```
