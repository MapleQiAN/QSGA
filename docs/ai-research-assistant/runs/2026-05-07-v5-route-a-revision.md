# Run Record: V5 Route-A Paper Revision

## Metadata

- Run ID: RUN-20260507-V5-ROUTE-A
- Date: 2026-05-07
- Operator: Codex AI research assistant
- Workspace: `E:\QSGA`
- Goal: apply `ccf_c_reviewer_report_v5.md` and the AI research assistant rules to strengthen the QSGA paper draft without overstating live LLM generation claims.

## Inputs

- `docs/paper/ccf_c_reviewer_report_v5.md`
- `docs/ai-research-assistant/AI_RULES.md`
- `docs/ai-research-assistant/SOP.md`
- `docs/ai-research-assistant/README.md`
- `docs/ai-research-assistant/QUALITY_GUARDRAILS.md`
- `docs/ai-research-assistant/DRAFT_STATUS.md`
- `docs/ai-research-assistant/RISKS.md`
- `docs/ai-research-assistant/DECISIONS.md`
- `docs/paper/qsga_ccf_c_draft.md`
- Existing result CSVs under `experiments/results/`

## Actions

1. Reframed the paper title from QSGA-centered reliable construction to QYIR-centered verifiable and repairable intermediate representation.
2. Rewrote the abstract to directly report oracle-slot E2E 0.963, deterministic no-oracle E2E 0.887, and live prompt-only QYIR construction success 0.091.
3. Rewrote the Introduction research questions and contribution list to separate IR verification from prompt-only live LLM bottleneck diagnosis.
4. Strengthened QYIR Method with compact grammar, validity conjunction, operand type system, deterministic rule compilation semantics, and QYIR-versus-JSON distinction.
5. Strengthened QSGA Method with explicit semantic-slot verification algorithm and stricter repair invariants.
6. Reordered Results so oracle-slot component validation precedes deterministic no-oracle construction, and renamed live QYIR as bottleneck analysis.
7. Added `experiments/run_slot_diagnostics.py` and generated no-oracle slot-level precision/recall/F1 artifacts.
8. Added Discussion sections explaining what QYIR solves, what it does not solve, and why the negative live result matters.
9. Updated Conclusion, Ethics, `DRAFT_STATUS.md`, `RISKS.md`, and `AUDIT_LOG.md`.

## Evidence State

- Oracle-slot verification-chain E2E remains 0.963 from existing generated metrics.
- Deterministic no-oracle E2E remains 0.887 from `experiments/results/no_oracle_metrics.csv`.
- No-oracle slot diagnostics show indicator F1 0.637, risk-control F1 0.685, market F1 0.250, and fine-grained entry/exit F1 0.000 under strict key-value grouping.
- Live QSGA-wrapped QYIR construction success remains 0.091 from `experiments/results/live_qyir_80_metrics.csv`.
- No new live/API experiment was run in this revision.
- `scripts/reproduce_all.ps1` completed successfully after the revision with 179 tests passing and saved live replays regenerated.

## Human Decisions

No new human decision was added. Existing human-review gates still apply for final claim freeze, authorship, public release, and submission.

## Risks

- `RISK-20260507-002`: per-slot no-oracle diagnostics were added and the remaining extractor weakness is scoped as front-end bottleneck evidence.
- `RISK-20260507-003`: final V5 route-A framing requires human review before submission.

## Next Actions

1. Run consistency checks over headings, claim wording, and changed documentation.
2. Improve extractor or add constrained parser before any stronger no-oracle parsing claim.
3. Continue citation verification before any submission-ready draft.
