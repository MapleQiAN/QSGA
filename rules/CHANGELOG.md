# CHANGELOG.md

## v3.1

### Added

- `scripts/check_research_ops.py`: zero-dependency quality checker for Research Ops repositories.
- README usage notes for normal, strict, and JSON quality-check modes.

### Checks Covered

- Required file existence.
- Unexpanded initialization headings.
- `TLDR_STATE_FOR_AGENT` coverage.
- Task queue schema, priority, status, risk, safety, and human-review consistency.
- Pending human decisions.
- Critical / High active risks without mitigation tasks.
- Claim evidence levels and conservative wording requirements.
- Experiment result completeness and reproducibility metadata.
- Run record presence and structure.

## v3.0

### Added

- `TASK_QUEUE.md`
- `protocols/EXECUTION_LOOP.md`
- `protocols/CONTEXT_POLICY.md`
- `profiles/QSGA_PROFILE.md`

### Changed

- `AGENTS.md` now prioritizes task queue based execution.
- Multi-Agent rule now supports Orchestrator serial simulation in single-window environments.
- README now describes Research Ops as a task-driven execution system.
- All long-running documents now include `TLDR_STATE_FOR_AGENT` blocks.

### Fixed

- Replaced broken initialized titles like `# $(basename $f .md)` with real document headers.
- Reduced ambiguity in automatic execution rules.
- Added explicit context budget to prevent full-document over-reading.
