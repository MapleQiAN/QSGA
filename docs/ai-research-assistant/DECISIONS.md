# AI 科研人类决策登记表

本文件用于登记 AI 在科研流程中遇到的、必须由人类决定的问题。AI 写入决策项后，不得停止全部工作，必须继续推进不依赖该决策的任务。

## 状态说明

| 状态 | 含义 |
|---|---|
| `waiting_human` | 等待人类决策 |
| `need_more_evidence` | 人类要求 AI 补充证据 |
| `approved` | 人类批准 |
| `rejected` | 人类拒绝 |
| `superseded` | 被后续决策替代 |
| `applied` | 决策已执行 |

## 待决策队列

暂无。

## 决策模板

```markdown
### DEC-YYYYMMDD-NNN

Status: waiting_human
Owner: human
Raised by:
Date:
Deadline:

Question:

Context:

Options:
1. 
2. 
3. 

AI recommendation:

Evidence:

Risk if approved:

Risk if rejected:

What is blocked:

What AI will continue doing:

Human decision:

Decision rationale:

Follow-up actions:
```

## 审计要求

1. 不得删除历史决策项。
2. 若决策被替代，标记为 `superseded` 并链接新决策。
3. 若决策已执行，标记为 `applied` 并说明影响的文件、实验或论文段落。
4. 若人类口头给出决策，AI 必须转写到本文件并请求确认。
