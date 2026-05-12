# RISKS.md

本文件记录科研项目中的方法、实验、写作、伦理、复现和投稿风险。

---

## TLDR_STATE_FOR_AGENT

Critical Active Risks：

- 暂无

High Active Risks：

- 暂无

需要关注：

- 新增强 claim、实验协议变化、baseline 变化、数据来源变化时，必须检查是否产生新风险。

---

## Active Risks

暂无。

---

## Resolved Risks

### RISK-20260512-001

```yaml
Risk ID: RISK-20260512-001
Title: Route B live smoke blocked by API authentication failure
Status: resolved
Level: High
Type: Tooling
Created: 2026-05-12
Updated: 2026-05-12
Related Task ID: TASK-20260512-009
Related Claim ID: CLAIM-RB-002
Description:
  - Initial bounded deepseek-v4-flash Route B live smoke returned 401 invalid_api_key on the DashScope-compatible endpoint.
Evidence:
  - experiments/results/route_b_live_smoke_deepseek_flash_5_results.csv
  - experiments/results/route_b_live_smoke_deepseek_flash_filekey_5_results.csv
Resolution Evidence:
  - experiments/results/route_b_live_smoke_deepseek_official_5_v4_results.csv
  - experiments/results/route_b_live_deepseek_official_80_results.csv
  - experiments/results/route_b_live_deepseek_official_80_metadata.json
Impact:
  - Authentication/endpoint no longer blocks Route B live diagnostics.
Residual Risk:
  - Official DeepSeek results are still single-model and provider-specific; claims must remain diagnostic.
Likelihood: Low
Mitigation Plan:
  - Preserve official endpoint metadata and raw outputs.
  - Keep future API experiments scoped and logged.
Mitigation Applied:
  - Switched to official DeepSeek OpenAI-compatible endpoint https://api.deepseek.com.
  - Enabled JSON Output mode and disabled thinking for short structured slot extraction.
Owner: Research Orchestrator
Human Review Required: No
Current Decision:
  - DEC-20260512-002 accepted.
Next Action:
  - Continue paper revision and failure analysis using saved official DeepSeek artifacts.
```

---

## Risk Levels

| 等级 | 含义 | 处理 |
|---|---|---|
| Critical | 可能导致论文不可投、实验无效、伦理违规或数据不可用 | 必须优先处理，通常需要人审 |
| High | 可能显著影响核心 claim 或实验可信度 | 必须进入任务队列 |
| Medium | 影响局部质量或叙事完整性 | 按优先级处理 |
| Low | 格式、表达、局部清晰度问题 | 可延后处理 |

---

## Risk Template

```yaml
Risk ID: RISK-YYYYMMDD-NNN
Title:
Status: active / mitigated / accepted / resolved / obsolete
Level: Critical / High / Medium / Low
Type: Method / Experiment / Data / Ethics / Writing / Reproducibility / Submission / Tooling
Created:
Updated:
Related Task ID:
Related Claim ID:
Description:
Evidence:
Impact:
Likelihood: High / Medium / Low
Mitigation Plan:
Owner:
Human Review Required: Yes / No
Current Decision:
Next Action:
```
