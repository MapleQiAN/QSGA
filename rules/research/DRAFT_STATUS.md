# DRAFT_STATUS.md

---

## TLDR_STATE_FOR_AGENT

当前草稿状态：

- Route B draft is integrated into the existing paper: docs/paper/qsga_ccf_draft.md

已验证 claim：

- CLAIM-RB-001：仅针对保存的 qwen3.6-flash live-QYIR 运行，失败主要集中在 schema、alias/reference、unsafe intent 和 risk violation 等类别。
- CLAIM-RB-004：在 QSI-Bench expected slots 输入下，deterministic Route B builder 当前可构造 55/55 construct cases，并正确终止 10 个 clarify 与 15 个 reject cases。
- CLAIM-RB-002：official `deepseek-v4-flash` Route B live 诊断达到 schema_validity 0.709、construction_success 0.364、E2E 0.475；仅限 single-model diagnostic。

未验证 claim：

- CLAIM-RB-003：Route B 可以支撑 CCF-B 强度主张。

需要降级表述：

- 禁止把 official DeepSeek single-model diagnostic 写成广泛模型结论或投稿就绪结论。

下一步：

- 后续应做 reviewer gate、limitation tightening，并决定是否需要第二个 full 80-case live model。

---

## Section Status

| Section | Status | Owner | Notes |
|---|---|---|---|
| Abstract | draft_updated | Writer Agent | 已写入 Route B framing 和 official DeepSeek 80-case diagnostic。 |
| Introduction | draft_updated | Writer Agent | 已改为 verification-guided NL-to-QYIR construction 问题。 |
| Related Work | partial_verified | Writer Agent | 已核验 QuantCode-Bench、SysTradeBench、Market-Bench、QuantEval、OQL、CNFinBench；其余通用引用待核验。 |
| Method | draft_updated | Writer Agent | 已加入 slot extraction、builder、canonicalization、validator-feedback retry。 |
| Experiments | draft_updated | Writer Agent | 已加入 official DeepSeek Route B 80-case live diagnostic。 |
| Results | draft_updated | Writer Agent | 已写入 official DeepSeek metrics、category results、failure breakdown。 |
| Limitations | draft_updated | Writer Agent | 已保留 single-model/live construction limitation。 |
| Conclusion | draft_updated | Writer Agent | 已同步 Route B live diagnostic 状态。 |
| Route B CCF Draft | draft_updated | Writer Agent | `docs/paper/qsga_ccf_draft.md`，基于原 CCF draft 改写。 |

---

## Claim Registry

| Claim ID | Claim | Evidence Level | Allowed Wording | Forbidden Wording | Status |
|---|---|---|---|---|---|
| CLAIM-RB-001 | Saved qwen3.6-flash live-QYIR results exhibit concrete failure buckets across schema, alias/reference, safety, and risk audit stages. | A | "In the saved qwen3.6-flash live-QYIR run, failure breakdown shows..." | "LLM-to-QYIR generally fails mainly because..." | verified_for_saved_run |
| CLAIM-RB-002 | Route B constrained construction produces a stronger official DeepSeek live diagnostic than whole-QYIR prompting, but model/provider differences prevent broad comparison claims. | B | "In the official deepseek-v4-flash diagnostic, Route B reaches..." | "Route B generally beats all raw QYIR prompting or direct code." | verified_for_single_model_diagnostic |
| CLAIM-RB-003 | The current paper can claim CCF-B-level strength. | X | "The work is being prepared toward a stronger submission target." | "This is CCF-B ready." | unverified |
| CLAIM-RB-004 | Deterministic Route B builder constructs valid QYIR from QSI-Bench expected slots for current construct cases. | A | "Under expected-slot input, the deterministic builder constructs valid QYIR for..." | "The live LLM constructs valid QYIR for..." | verified_gold_slot_builder |

---

## Unverified Claims

- CLAIM-RB-003：requires stronger method, experiments, related work verification, and reviewer simulation.
