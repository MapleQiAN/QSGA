# AUDIT_LOG.md

本文件记录关键科研操作。默认不需要每轮全文读取，但关键操作必须追加记录。

---

## TLDR_STATE_FOR_AGENT

最近关键操作：

- 暂无

最近失败或重试：

- 暂无

注意：

- 追加日志即可，不要为了追加而读取全文。
- 若需要追溯，优先读取最近 1 到 3 条相关记录。

---

## Audit Entries

暂无。

---

## Audit Entry Template

```yaml
Audit ID: AUDIT-YYYYMMDD-NNN
Timestamp:
Actor:
Action Type: Search / Read / Experiment / Write / Review / Decision / ToolFailure / Release / DataChange / Refactor
Related Task ID:
Related Decision ID:
Related Risk ID:
Summary:
Inputs:
Outputs:
Evidence:
Files Changed:
Commands:
Result:
Failure:
Retry:
Notes:
```
