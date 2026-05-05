# Citation Audit Backlog

Task ID: LIT-20260505-PDF-AUDIT-SCAFFOLD  
Status: active backlog after PDF-level verification of five priority papers  
Date: 2026-05-05  

This backlog covers citation and claim work needed before the paper draft should be treated as submission-ready. It is limited to the five priority papers requested in this pass and is intended to complement `citation_and_claim_matrix.md`.

## Verification Summary

| Paper | Matrix ID | PDF URL | Current Level | Upgrade Decision |
|---|---|---|---|---|
| QuantCode-Bench | P13 | https://arxiv.org/pdf/2604.15151 | Level A for comparator claims used in related work | Safe for staged executable-trading benchmark claims |
| SysTradeBench | P14 | https://arxiv.org/pdf/2604.04812 | Level A for governed build-test-patch and auditability claims | Safe for auditability, drift, determinism, and risk-discipline framing |
| Market-Bench | P15 | https://arxiv.org/pdf/2512.12264 | Level A for executable backtester and metric-reference claims | Safe for executability vs numerical-fidelity comparison |
| QuantEval | P16 | https://arxiv.org/pdf/2601.08689 | Level A for broad quant benchmark and CTA-style strategy-coding claims | Safe for broad financial quantitative task and strategy-coding context |
| OQL option-strategy paper | P17 | https://arxiv.org/pdf/2603.16434 | Level A for IR/DSL analogy claims | Safe for neuro-symbolic IR analogy, not for equity strategy coverage |

## Claim-Level Backlog

| Backlog ID | Draft/Matrix Claim | Status | Required Action |
|---|---|---|---|
| AUD-P13-001 | Direct trading-code benchmarks are closer comparators than broad financial LLM papers. | Supported for P13/P15/P16, but should be phrased conservatively. | In `qsga_ccf_c_draft.md`, keep this as a related-work positioning claim. Do not imply shared metrics or direct superiority. |
| AUD-P13-002 | QuantCode-Bench evaluates executable Backtrader strategy generation from textual descriptions. | PDF-verified. | Cite https://arxiv.org/pdf/2604.15151, Section 2.1 and Section 3.1, PDF P2-P3, lines 94-106 and 140-170. |
| AUD-P13-003 | QuantCode-Bench includes 400 tasks and uses multi-stage checks. | PDF-verified. | Cite https://arxiv.org/pdf/2604.15151, Section 2.2, PDF P2-P3, lines 107-133; Section 3.1, PDF P3, lines 140-170. |
| AUD-P13-004 | QuantCode-Bench shows syntax is not enough for trading strategy generation. | PDF-verified. | Cite https://arxiv.org/pdf/2604.15151, Section 5.1, PDF P5-P6, lines 244-261. Use this to support QSGA's "schema/code validity is insufficient" framing. |
| AUD-P14-001 | SysTradeBench evaluates strategy-to-code systems as governed, auditable software. | PDF-verified. | Cite https://arxiv.org/pdf/2604.04812, Abstract, PDF P0, lines 22-38. |
| AUD-P14-002 | SysTradeBench uses Base Strategy Docs, frozen semantics, strategy cards, executable code, and mandatory audit logs. | PDF-verified. | Cite https://arxiv.org/pdf/2604.04812, contributions and output contract, PDF P1/P4, lines 104-123 and 290-302. |
| AUD-P14-003 | SysTradeBench checks drift, determinism, leakage, auditability, risk discipline, and OOS robustness indicators. | PDF-verified. | Cite https://arxiv.org/pdf/2604.04812, Sections 4.4.1-4.4.4, PDF P4, lines 303-349. |
| AUD-P14-004 | SysTradeBench proves profitable trading performance. | Forbidden. | Do not use. The paper says D4 provides robustness indicators rather than definitive profitability claims; cite PDF P4, lines 344-349 if this limitation is mentioned. |
| AUD-P15-001 | Market-Bench asks models to construct executable backtesters from natural-language strategy descriptions and market assumptions. | PDF-verified. | Cite https://arxiv.org/pdf/2512.12264, Abstract, PDF P0, lines 5-22. |
| AUD-P15-002 | Market-Bench covers scheduled MSFT execution, KO/PEP pairs trading, and MSFT options delta hedging. | PDF-verified. | Cite https://arxiv.org/pdf/2512.12264, Section 3.2, PDF P2, lines 90-130. |
| AUD-P15-003 | Market-Bench evaluates executability separately from numerical agreement with reference metrics. | PDF-verified. | Cite https://arxiv.org/pdf/2512.12264, Sections 3.4-4.3, PDF P3-P4, lines 138-191. |
| AUD-P15-004 | Market-Bench is an IR/DSL benchmark. | Not supported by verified text. | Do not use. Frame it as executable backtester reconstruction and reference-metric comparison instead. |
| AUD-P16-001 | QuantEval covers knowledge QA, quantitative reasoning, and quantitative strategy coding. | PDF-verified. | Cite https://arxiv.org/pdf/2601.08689, Abstract, PDF P0, lines 11-31; Figure 1 discussion, PDF P1, lines 120-135. |
| AUD-P16-002 | QuantEval contains 1,575 curated samples. | PDF-verified. | Cite https://arxiv.org/pdf/2601.08689, PDF P1, line 127. |
| AUD-P16-003 | QuantEval strategy coding uses an integrated CTA-style backtesting framework for model-generated strategies. | PDF-verified. | Cite https://arxiv.org/pdf/2601.08689, Abstract, PDF P0, lines 19-24; PDF P1, lines 128-133. |
| AUD-P16-004 | QuantEval is evidence for QSGA-style safe rejection or localized repair. | Not supported by verified text. | Do not use. QuantEval is a broad benchmark and strategy-coding comparator, not a safe-rejection or IR-repair source. |
| AUD-P17-001 | OQL is a domain-specific intermediate representation for option strategies. | PDF-verified. | Cite https://arxiv.org/pdf/2603.16434, Abstract, PDF P0, lines 6-18; Section 4.2, PDF P3-P4, lines 252-277. |
| AUD-P17-002 | OQL decomposes natural-language option strategy construction into LLM semantic parsing and deterministic validation/execution. | PDF-verified. | Cite https://arxiv.org/pdf/2603.16434, Section 4, PDF P3-P5, lines 229-250 and 354-368. |
| AUD-P17-003 | OQL handles option chains, Greeks, strikes, maturities, roles, and aggregate constraints. | PDF-verified. | Cite https://arxiv.org/pdf/2603.16434, Sections 3.3 and 4.2, PDF P2-P4, lines 174-228 and 252-277. |
| AUD-P17-004 | QYIR supports OQL-style option strategies. | Forbidden for current draft. | Do not use. The supported claim is only architectural similarity between IR-based deterministic execution designs. |

## Draft Integration Checklist

| Item | Priority | Owner Pass | Notes |
|---|---:|---|---|
| Replace or audit Section 10.3 using the drop-in text in `related_work_verified.md`. | High | Next paper-edit pass | Preserve conservative scope: comparator, not direct baseline. |
| Replace or audit Section 10.4 using the drop-in text in `related_work_verified.md`. | High | Next paper-edit pass | Make the OQL analogy explicit but bounded by asset class and representation. |
| Add citation keys or BibTeX entries for P13-P17. | High | Next bibliography pass | Current draft uses bullet references; if moving to LaTeX, create stable keys such as `khoroshilov2026quantcodebench`, `cao2026systradebench`, `srivastava2025marketbench`, `kang2026quanteval`, `luo2026oql`. |
| Decide whether to cite PDF page/section evidence in final prose or only in reviewer-facing audit docs. | Medium | Submission-format pass | Many venues prefer normal bibliography citations; keep page/section evidence in audit docs unless required. |
| Re-check arXiv versions before submission. | Medium | Final pre-submission pass | Commands/URLs below. These 2026 arXiv papers may update. |
| Verify author lists and year formatting against final arXiv metadata. | Medium | Bibliography pass | Do not rely only on current draft reference bullets. |

## Commands and URLs for Next Pass

Use these commands from `E:\QSGA` if a future pass needs local PDF copies for manual annotation. Store downloaded PDFs outside the repository or in an ignored scratch directory unless the project owner explicitly approves committing source PDFs.

```powershell
Invoke-WebRequest -Uri "https://arxiv.org/pdf/2604.15151" -OutFile "$env:TEMP\quantcode-bench-2604.15151.pdf"
Invoke-WebRequest -Uri "https://arxiv.org/pdf/2604.04812" -OutFile "$env:TEMP\systradebench-2604.04812.pdf"
Invoke-WebRequest -Uri "https://arxiv.org/pdf/2512.12264" -OutFile "$env:TEMP\market-bench-2512.12264.pdf"
Invoke-WebRequest -Uri "https://arxiv.org/pdf/2601.08689" -OutFile "$env:TEMP\quanteval-2601.08689.pdf"
Invoke-WebRequest -Uri "https://arxiv.org/pdf/2603.16434" -OutFile "$env:TEMP\oql-option-strategies-2603.16434.pdf"
```

Primary source URLs:

- QuantCode-Bench: https://arxiv.org/abs/2604.15151 and https://arxiv.org/pdf/2604.15151
- SysTradeBench: https://arxiv.org/abs/2604.04812 and https://arxiv.org/pdf/2604.04812
- Market-Bench: https://arxiv.org/abs/2512.12264 and https://arxiv.org/pdf/2512.12264
- QuantEval: https://arxiv.org/abs/2601.08689 and https://arxiv.org/pdf/2601.08689
- OQL option-strategy paper: https://arxiv.org/abs/2603.16434 and https://arxiv.org/pdf/2603.16434

## Remaining Risks

These papers are recent arXiv works. Their titles, author lists, versions, tables, and reported numbers may change before submission. The final paper pass should re-open the arXiv abstract pages and PDFs, confirm version dates, and update bibliographic metadata accordingly.

The verified related-work scaffold does not audit the rest of the reference list in `citation_and_claim_matrix.md`. P01-P12 and P18-P20 remain at metadata/link-level unless separately upgraded.

The verified scaffold does not validate QSGA's local experimental claims. Those remain governed by local artifacts such as `experiments/results/*.csv`, `experiments/tables/*.md`, and the experiment audit documents.
