#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Research Ops Quality Checker

一个轻量、零第三方依赖的 Research Ops 质量检查脚本。
用于在每轮 Agent 工作结束后，检查任务队列、风险、决策、claim、实验结果和基础文档结构。

用法：
    python scripts/check_research_ops.py
    python scripts/check_research_ops.py --root .
    python scripts/check_research_ops.py --strict
    python scripts/check_research_ops.py --json

退出码：
    0：没有 FAIL；如果启用 --strict，则没有 FAIL 且没有 WARN
    1：存在 FAIL，或 strict 模式下存在 WARN
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


VALID_TASK_STATUS = {
    "todo",
    "in_progress",
    "blocked_human",
    "blocked_dependency",
    "review_ready",
    "revision_needed",
    "done",
    "archived",
    "dropped",
}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
VALID_RISK_LEVELS = {"Low", "Medium", "High", "Critical"}
VALID_YES_NO = {"Yes", "No"}
VALID_DECISION_STATUS = {
    "PendingReview",
    "waiting_human",
    "accepted",
    "rejected",
    "superseded",
}
VALID_RESULT_STATUS = {"success", "failed", "partial", "invalid"}
VALID_REPRO_LEVELS = {"R0", "R1", "R2", "R3", "R4", "R5"}
VALID_EVIDENCE_LEVELS = {"A", "B", "C", "D", "X", "N/A", "NA", ""}

REQUIRED_FILES = [
    "AGENTS.md",
    "TASK_QUEUE.md",
    "CURRENT_PROGRESS.md",
    "DECISIONS.md",
    "RISKS.md",
    "AUDIT_LOG.md",
    "protocols/EXECUTION_LOOP.md",
    "protocols/CONTEXT_POLICY.md",
    "protocols/QUALITY_GUARDRAILS.md",
    "protocols/REVIEWER_GATE.md",
    "research/RESEARCH_PLAN.md",
    "research/PAPER_MATRIX.md",
    "research/EXPERIMENT_PLAN.md",
    "research/RESULTS_LOG.md",
    "research/DRAFT_STATUS.md",
]

TLDR_REQUIRED_FILES = [
    "AGENTS.md",
    "TASK_QUEUE.md",
    "CURRENT_PROGRESS.md",
    "DECISIONS.md",
    "RISKS.md",
    "protocols/EXECUTION_LOOP.md",
    "protocols/CONTEXT_POLICY.md",
    "protocols/QUALITY_GUARDRAILS.md",
    "protocols/REVIEWER_GATE.md",
    "protocols/HUMAN_REVIEW_PROTOCOL.md",
    "protocols/MULTI_AGENT_PROTOCOL.md",
    "protocols/SOP.md",
    "research/RESEARCH_PLAN.md",
    "research/PAPER_MATRIX.md",
    "research/EXPERIMENT_PLAN.md",
    "research/RESULTS_LOG.md",
    "research/DRAFT_STATUS.md",
    "runs/RUN_TEMPLATE.md",
]

TASK_REQUIRED_FIELDS = [
    "Task ID",
    "Title",
    "Status",
    "Priority",
    "Owner",
    "Inputs",
    "Outputs",
    "Dependencies",
    "Blocking",
    "Evidence Required",
    "Estimated Cost",
    "Risk Level",
    "Safe to Run Automatically",
    "Human Review Required",
    "Quality Gate",
    "Fallback if Blocked",
    "Last Result",
    "Next Action",
]

RISK_REQUIRED_FIELDS = [
    "Risk ID",
    "Title",
    "Status",
    "Level",
    "Type",
    "Related Task ID",
    "Related Claim ID",
    "Description",
    "Evidence",
    "Impact",
    "Likelihood",
    "Mitigation Plan",
    "Owner",
    "Human Review Required",
    "Next Action",
]

DECISION_REQUIRED_FIELDS = [
    "Decision ID",
    "Title",
    "Status",
    "Related Task ID",
    "Context",
    "Options",
    "AI Recommendation",
    "Default Assumption Before Human Response",
    "Risk if Wrong",
    "Blocking",
    "Non-Blocked Work Can Continue",
    "Final Decision",
]

RESULT_REQUIRED_FIELDS = [
    "Experiment ID",
    "Date",
    "Task ID",
    "Status",
    "Code Version",
    "Dataset Version",
    "Command",
    "Seed",
    "Environment",
    "Raw Output Path",
    "Metrics",
    "Failure",
    "Reproducibility Level",
    "Claim Impact",
]


@dataclass
class Finding:
    severity: str
    code: str
    file: str
    message: str
    suggestion: str = ""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def is_placeholder_value(value: Optional[str]) -> bool:
    if value is None:
        return True
    clean = str(value).strip()
    return clean == "" or clean in {"-", "暂无", "待填写", "未执行"}


def is_template_id(value: str) -> bool:
    value = (value or "").strip()
    return (
        value == ""
        or "YYYYMMDD" in value
        or "YYYY-MM-DD" in value
        or "NNN" in value
        or (value.endswith("-001") and "TASK-YYYY" in value)
    )


def normalize_scalar(value: str) -> str:
    return value.strip().strip("`").strip()


def extract_yaml_blocks(markdown: str) -> List[str]:
    return re.findall(r"```yaml\s*(.*?)\s*```", markdown, flags=re.DOTALL | re.IGNORECASE)


def parse_loose_yaml_block(block: str) -> Dict[str, str]:
    """
    解析模板中的宽松 YAML。
    这里不追求完整 YAML 语义，只提取顶层 `Key: value`，便于 Agent 文档质检。
    """
    data: Dict[str, str] = {}
    current_key: Optional[str] = None
    current_lines: List[str] = []

    def flush() -> None:
        nonlocal current_key, current_lines
        if current_key is not None:
            joined = "\n".join(line.rstrip() for line in current_lines).strip()
            data[current_key] = joined
        current_key = None
        current_lines = []

    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # 顶层 key，允许 key 中含空格。
        if not line.startswith((" ", "\t", "-")) and ":" in line:
            flush()
            key, value = line.split(":", 1)
            current_key = key.strip()
            current_lines = [value.strip()] if value.strip() else []
        elif current_key is not None:
            current_lines.append(line)
    flush()
    return data


def extract_table_rows(markdown: str, header_keyword: str) -> List[Dict[str, str]]:
    """从 Markdown 表格中提取包含特定 header_keyword 的表。"""
    lines = markdown.splitlines()
    rows: List[Dict[str, str]] = []
    for i, line in enumerate(lines):
        if not line.strip().startswith("|") or header_keyword not in line:
            continue
        if i + 1 >= len(lines) or "---" not in lines[i + 1]:
            continue
        headers = [h.strip() for h in line.strip().strip("|").split("|")]
        j = i + 2
        while j < len(lines) and lines[j].strip().startswith("|"):
            cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
            j += 1
        break
    return rows


def extract_section(markdown: str, heading: str) -> str:
    """提取某个二级标题下，到下一个二级标题前的内容。"""
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    lines = markdown.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def section_has_real_content(markdown: str, heading: str) -> bool:
    content = extract_section(markdown, heading)
    content = re.sub(r"[-\s。.]+", "", content)
    return content not in {"", "暂无"}


def add(findings: List[Finding], severity: str, code: str, file: str, message: str, suggestion: str = "") -> None:
    findings.append(Finding(severity=severity, code=code, file=file, message=message, suggestion=suggestion))


def check_required_files(root: Path, findings: List[Finding]) -> None:
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            add(findings, "FAIL", "MISSING_FILE", rel, "必需文件不存在。", "补齐该文件，或从 research-ops 模板恢复。")


def check_unexpanded_placeholders(root: Path, findings: List[Finding]) -> None:
    for path in root.rglob("*.md"):
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            # 只把真实标题中的未展开变量视为错误；README / CHANGELOG 中提到这个旧 bug 不算。
            if line.strip().startswith("# $(basename"):
                add(
                    findings,
                    "FAIL",
                    "UNEXPANDED_SHELL_PLACEHOLDER",
                    rel,
                    f"第 {line_no} 行发现未展开的 shell 占位符 `$(basename ...)`。",
                    "把标题改成真实文件名，例如 `# DECISIONS.md`。",
                )


def check_tldr_blocks(root: Path, findings: List[Finding]) -> None:
    for rel in TLDR_REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            continue
        text = read_text(path)
        if "## TLDR_STATE_FOR_AGENT" not in text:
            add(
                findings,
                "WARN",
                "MISSING_TLDR",
                rel,
                "长文档缺少 `## TLDR_STATE_FOR_AGENT` 摘要块。",
                "在文件顶部补充当前有效结论、阻塞、最近更新和下一步。",
            )


def check_task_queue(root: Path, findings: List[Finding]) -> None:
    rel = "TASK_QUEUE.md"
    path = root / rel
    if not path.exists():
        return
    text = read_text(path)
    blocks = [parse_loose_yaml_block(b) for b in extract_yaml_blocks(text)]
    task_blocks = [b for b in blocks if "Task ID" in b]
    concrete_tasks = [b for b in task_blocks if not is_template_id(b.get("Task ID", ""))]

    if not task_blocks:
        add(findings, "FAIL", "NO_TASK_BLOCK", rel, "没有发现任何任务 YAML 块。", "至少添加一个符合模板的任务。")
        return

    if not concrete_tasks:
        add(
            findings,
            "WARN",
            "NO_CONCRETE_TASK",
            rel,
            "当前只有示例任务或占位任务，没有真实可执行任务。",
            "根据当前研究目标创建 3 到 7 个真实任务。",
        )

    active_nonblocked = 0
    high_priority_active = 0

    for task in concrete_tasks:
        task_id = task.get("Task ID", "<unknown>")
        missing = [f for f in TASK_REQUIRED_FIELDS if f not in task]
        if missing:
            add(findings, "FAIL", "TASK_MISSING_FIELDS", rel, f"任务 {task_id} 缺少字段：{', '.join(missing)}。", "补齐 TASK_QUEUE.md 的完整任务模板字段。")

        status = normalize_scalar(task.get("Status", ""))
        priority = normalize_scalar(task.get("Priority", ""))
        risk = normalize_scalar(task.get("Risk Level", ""))
        safe = normalize_scalar(task.get("Safe to Run Automatically", ""))
        human = normalize_scalar(task.get("Human Review Required", ""))

        if status and status not in VALID_TASK_STATUS:
            add(findings, "FAIL", "TASK_INVALID_STATUS", rel, f"任务 {task_id} 的 Status 非法：{status}。", f"允许值：{', '.join(sorted(VALID_TASK_STATUS))}。")
        if priority and priority not in VALID_PRIORITIES:
            add(findings, "FAIL", "TASK_INVALID_PRIORITY", rel, f"任务 {task_id} 的 Priority 非法：{priority}。", "使用 P0 / P1 / P2 / P3。")
        if risk and risk not in VALID_RISK_LEVELS:
            add(findings, "FAIL", "TASK_INVALID_RISK", rel, f"任务 {task_id} 的 Risk Level 非法：{risk}。", "使用 Low / Medium / High / Critical。")
        if safe and safe not in VALID_YES_NO:
            add(findings, "FAIL", "TASK_INVALID_SAFE_FLAG", rel, f"任务 {task_id} 的 Safe to Run Automatically 非法：{safe}。", "使用 Yes / No。")
        if human and human not in VALID_YES_NO:
            add(findings, "FAIL", "TASK_INVALID_HUMAN_REVIEW_FLAG", rel, f"任务 {task_id} 的 Human Review Required 非法：{human}。", "使用 Yes / No。")

        if status in {"todo", "in_progress", "revision_needed", "review_ready"}:
            if status != "review_ready" and risk not in {"Critical"}:
                active_nonblocked += 1
            if priority in {"P0", "P1"}:
                high_priority_active += 1

        if priority in {"P0", "P1"} and status in {"todo", "in_progress", "revision_needed"}:
            for field in ["Outputs", "Evidence Required", "Quality Gate", "Next Action"]:
                if is_placeholder_value(task.get(field)):
                    add(findings, "WARN", "HIGH_PRIORITY_TASK_WEAK_SPEC", rel, f"高优先级任务 {task_id} 的 {field} 不够明确。", "把输出、证据、质量门和下一步写成可验证条目。")

        if safe == "Yes" and (risk in {"High", "Critical"} or human == "Yes"):
            add(
                findings,
                "FAIL" if risk == "Critical" else "WARN",
                "UNSAFE_AUTO_TASK",
                rel,
                f"任务 {task_id} 标记为可自动运行，但风险为 {risk}，Human Review Required 为 {human}。",
                "高风险或需人审任务应设置 Safe to Run Automatically: No，除非已有明确保护措施。",
            )

        if status in {"blocked_human", "blocked_dependency"} and is_placeholder_value(task.get("Fallback if Blocked")):
            add(findings, "WARN", "BLOCKED_TASK_NO_FALLBACK", rel, f"阻塞任务 {task_id} 没有明确 fallback。", "写明阻塞后可转向的非依赖任务或记录方式。")

    if concrete_tasks and active_nonblocked == 0:
        add(findings, "WARN", "NO_ACTIVE_NONBLOCKED_TASK", rel, "没有可立即执行的非阻塞任务。", "新增或拆分一个低风险、可验证、无需人审的任务。")
    if concrete_tasks and high_priority_active == 0:
        add(findings, "WARN", "NO_P0_P1_ACTIVE_TASK", rel, "没有 P0/P1 活跃任务。", "确认当前阶段是否至少有一个高价值推进任务。")


def check_decisions(root: Path, findings: List[Finding]) -> None:
    rel = "DECISIONS.md"
    path = root / rel
    if not path.exists():
        return
    text = read_text(path)
    blocks = [parse_loose_yaml_block(b) for b in extract_yaml_blocks(text)]
    decisions = [b for b in blocks if "Decision ID" in b and not is_template_id(b.get("Decision ID", ""))]

    for dec in decisions:
        dec_id = dec.get("Decision ID", "<unknown>")
        missing = [f for f in DECISION_REQUIRED_FIELDS if f not in dec]
        if missing:
            add(findings, "FAIL", "DECISION_MISSING_FIELDS", rel, f"决策 {dec_id} 缺少字段：{', '.join(missing)}。", "补齐 Decision Template 的关键字段。")
        status = normalize_scalar(dec.get("Status", ""))
        if status and status not in VALID_DECISION_STATUS:
            add(findings, "FAIL", "DECISION_INVALID_STATUS", rel, f"决策 {dec_id} 的 Status 非法：{status}。", f"允许值：{', '.join(sorted(VALID_DECISION_STATUS))}。")
        if status in {"PendingReview", "waiting_human"}:
            add(findings, "WARN", "OPEN_HUMAN_DECISION", rel, f"存在待人类确认的决策：{dec_id}。", "确保相关任务已标记为 blocked_human，并继续推进非依赖任务。")

    if section_has_real_content(text, "PendingReview"):
        add(findings, "WARN", "PENDING_REVIEW_SECTION_NOT_EMPTY", rel, "PendingReview 区域可能存在待处理事项。", "检查是否需要写入 TASK_QUEUE.md 的 blocked_human 任务。")


def check_risks(root: Path, findings: List[Finding]) -> None:
    rel = "RISKS.md"
    path = root / rel
    if not path.exists():
        return
    text = read_text(path)
    blocks = [parse_loose_yaml_block(b) for b in extract_yaml_blocks(text)]
    risks = [b for b in blocks if "Risk ID" in b and not is_template_id(b.get("Risk ID", ""))]

    for risk in risks:
        risk_id = risk.get("Risk ID", "<unknown>")
        missing = [f for f in RISK_REQUIRED_FIELDS if f not in risk]
        if missing:
            add(findings, "FAIL", "RISK_MISSING_FIELDS", rel, f"风险 {risk_id} 缺少字段：{', '.join(missing)}。", "补齐 Risk Template 的关键字段。")
        level = normalize_scalar(risk.get("Level", ""))
        status = normalize_scalar(risk.get("Status", ""))
        human = normalize_scalar(risk.get("Human Review Required", ""))
        related_task = normalize_scalar(risk.get("Related Task ID", ""))

        if level and level not in VALID_RISK_LEVELS:
            add(findings, "FAIL", "RISK_INVALID_LEVEL", rel, f"风险 {risk_id} 的 Level 非法：{level}。", "使用 Critical / High / Medium / Low。")
        if human and human not in VALID_YES_NO:
            add(findings, "FAIL", "RISK_INVALID_HUMAN_FLAG", rel, f"风险 {risk_id} 的 Human Review Required 非法：{human}。", "使用 Yes / No。")
        if status == "active" and level == "Critical" and human != "Yes":
            add(findings, "FAIL", "CRITICAL_RISK_WITHOUT_HUMAN_REVIEW", rel, f"Critical 活跃风险 {risk_id} 未要求人审。", "Critical 风险通常必须 Human Review Required: Yes。")
        if status == "active" and level in {"Critical", "High"} and is_placeholder_value(related_task):
            add(findings, "WARN", "HIGH_RISK_WITHOUT_TASK", rel, f"{level} 活跃风险 {risk_id} 没有关联任务。", "为该风险创建或绑定一个 P0/P1 缓解任务。")


def check_claims(root: Path, findings: List[Finding]) -> None:
    # DRAFT_STATUS.md 中的 Claim Registry
    draft_rel = "research/DRAFT_STATUS.md"
    draft_path = root / draft_rel
    if draft_path.exists():
        text = read_text(draft_path)
        rows = extract_table_rows(text, "Claim ID")
        concrete_rows = [r for r in rows if r.get("Claim ID") and "---" not in r.get("Claim ID", "")]
        for row in concrete_rows:
            claim_id = row.get("Claim ID", "<unknown>")
            evidence = normalize_scalar(row.get("Evidence Level", ""))
            status = normalize_scalar(row.get("Status", ""))
            forbidden = normalize_scalar(row.get("Forbidden Wording", ""))
            allowed = normalize_scalar(row.get("Allowed Wording", ""))
            if evidence not in VALID_EVIDENCE_LEVELS:
                add(findings, "WARN", "CLAIM_UNKNOWN_EVIDENCE_LEVEL", draft_rel, f"Claim {claim_id} 的证据等级不规范：{evidence}。", "使用 A/B/C/D/X，或明确 N/A。")
            if evidence in {"C", "D", "X", ""} and not forbidden:
                add(findings, "WARN", "WEAK_CLAIM_NO_FORBIDDEN_WORDING", draft_rel, f"Claim {claim_id} 证据较弱，但未写 Forbidden Wording。", "为弱证据 claim 写明禁止使用的强表述。")
            if evidence in {"C", "D", "X", ""} and not allowed:
                add(findings, "WARN", "WEAK_CLAIM_NO_ALLOWED_WORDING", draft_rel, f"Claim {claim_id} 证据较弱，但未写 Allowed Wording。", "为弱证据 claim 写一个保守表述版本。")
            if status.lower() in {"verified", "done"} and evidence in {"D", "X", ""}:
                add(findings, "FAIL", "CLAIM_VERIFIED_WITH_WEAK_EVIDENCE", draft_rel, f"Claim {claim_id} 标为已验证，但证据等级为 {evidence or '空'}。", "降低状态，或补充实验/引用证据。")

    # PAPER_MATRIX.md 中的 Claim-Evidence Matrix
    matrix_rel = "research/PAPER_MATRIX.md"
    matrix_path = root / matrix_rel
    if matrix_path.exists():
        text = read_text(matrix_path)
        rows = extract_table_rows(text, "Claim ID")
        concrete_rows = [r for r in rows if r.get("Claim ID") and "---" not in r.get("Claim ID", "")]
        for row in concrete_rows:
            claim_id = row.get("Claim ID", "<unknown>")
            evidence = normalize_scalar(row.get("Evidence Level", ""))
            support = normalize_scalar(row.get("Supporting Papers", ""))
            if evidence in {"A", "B"} and is_placeholder_value(support):
                add(findings, "WARN", "STRONG_CLAIM_WITHOUT_SUPPORTING_PAPERS", matrix_rel, f"Claim {claim_id} 证据等级为 {evidence}，但 Supporting Papers 为空。", "补充引用或降低证据等级。")


def check_results(root: Path, findings: List[Finding]) -> None:
    rel = "research/RESULTS_LOG.md"
    path = root / rel
    if not path.exists():
        return
    text = read_text(path)
    blocks = [parse_loose_yaml_block(b) for b in extract_yaml_blocks(text)]
    results = [b for b in blocks if "Experiment ID" in b and not is_template_id(b.get("Experiment ID", ""))]

    for result in results:
        exp_id = result.get("Experiment ID", "<unknown>")
        missing = [f for f in RESULT_REQUIRED_FIELDS if f not in result]
        if missing:
            add(findings, "FAIL", "RESULT_MISSING_FIELDS", rel, f"实验结果 {exp_id} 缺少字段：{', '.join(missing)}。", "补齐 Result Entry Template 的关键字段。")
        status = normalize_scalar(result.get("Status", ""))
        repro = normalize_scalar(result.get("Reproducibility Level", ""))
        metrics = normalize_scalar(result.get("Metrics", ""))
        failure = normalize_scalar(result.get("Failure", ""))
        raw_path = normalize_scalar(result.get("Raw Output Path", ""))

        if status and status not in VALID_RESULT_STATUS:
            add(findings, "FAIL", "RESULT_INVALID_STATUS", rel, f"实验 {exp_id} 的 Status 非法：{status}。", f"允许值：{', '.join(sorted(VALID_RESULT_STATUS))}。")
        if repro and repro not in VALID_REPRO_LEVELS:
            add(findings, "WARN", "RESULT_INVALID_REPRO_LEVEL", rel, f"实验 {exp_id} 的 Reproducibility Level 不规范：{repro}。", "使用 R0 到 R5。")
        if status == "success" and is_placeholder_value(metrics):
            add(findings, "FAIL", "SUCCESS_RESULT_WITHOUT_METRICS", rel, f"实验 {exp_id} 标为 success，但 Metrics 为空。", "补充核心指标、表格路径或原始日志路径。")
        if status in {"failed", "partial", "invalid"} and is_placeholder_value(failure):
            add(findings, "WARN", "FAILED_RESULT_WITHOUT_FAILURE_NOTE", rel, f"实验 {exp_id} 未成功，但 Failure 为空。", "记录失败原因，失败也是论文防弹衣。")
        if status == "success" and is_placeholder_value(raw_path):
            add(findings, "WARN", "SUCCESS_RESULT_WITHOUT_RAW_OUTPUT", rel, f"实验 {exp_id} 成功但没有 Raw Output Path。", "记录原始输出路径，便于复现。")


def check_run_records(root: Path, findings: List[Finding]) -> None:
    runs_dir = root / "runs"
    if not runs_dir.exists():
        add(findings, "WARN", "NO_RUNS_DIR", "runs/", "缺少 runs 目录。", "创建 runs/ 并保留 RUN_TEMPLATE.md。")
        return
    run_files = [p for p in runs_dir.glob("*.md") if p.name != "RUN_TEMPLATE.md"]
    if not run_files:
        add(findings, "WARN", "NO_RUN_RECORDS", "runs/", "还没有真实运行记录。", "每轮 Agent 工作结束后复制 RUN_TEMPLATE.md 创建一条运行记录。")
        return
    for path in run_files:
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        required_sections = ["## TLDR_STATE_FOR_AGENT", "## Evidence", "## Files Updated", "## Quality Gate", "## Carry Forward"]
        for sec in required_sections:
            if sec not in text:
                add(findings, "WARN", "RUN_RECORD_MISSING_SECTION", rel, f"运行记录缺少章节：{sec}。", "使用 RUN_TEMPLATE.md 补齐结构。")


def check_audit_log(root: Path, findings: List[Finding]) -> None:
    rel = "AUDIT_LOG.md"
    path = root / rel
    if not path.exists():
        return
    text = read_text(path)
    if "## TLDR_STATE_FOR_AGENT" not in text:
        add(findings, "WARN", "AUDIT_LOG_NO_TLDR", rel, "审计日志缺少 TLDR 摘要。", "补充最近关键变更、风险和待复查项。")


def run_checks(root: Path) -> List[Finding]:
    findings: List[Finding] = []
    check_required_files(root, findings)
    check_unexpanded_placeholders(root, findings)
    check_tldr_blocks(root, findings)
    check_task_queue(root, findings)
    check_decisions(root, findings)
    check_risks(root, findings)
    check_claims(root, findings)
    check_results(root, findings)
    check_run_records(root, findings)
    check_audit_log(root, findings)
    return findings


def print_text_report(findings: List[Finding], strict: bool) -> None:
    order = {"FAIL": 0, "WARN": 1, "INFO": 2}
    findings = sorted(findings, key=lambda f: (order.get(f.severity, 9), f.file, f.code))
    fail_count = sum(1 for f in findings if f.severity == "FAIL")
    warn_count = sum(1 for f in findings if f.severity == "WARN")
    info_count = sum(1 for f in findings if f.severity == "INFO")

    print("\nResearch Ops Quality Check")
    print("=" * 28)
    print(f"FAIL: {fail_count} | WARN: {warn_count} | INFO: {info_count} | strict: {strict}")

    if not findings:
        print("\nPASS：未发现问题。科研小车状态良好，可以继续上路。")
        return

    for f in findings:
        icon = {"FAIL": "[FAIL]", "WARN": "[WARN]", "INFO": "[INFO]"}.get(f.severity, "[????]")
        print(f"\n{icon} {f.code} :: {f.file}")
        print(f"  - {f.message}")
        if f.suggestion:
            print(f"  - 建议：{f.suggestion}")

    if fail_count == 0 and (not strict or warn_count == 0):
        print("\nPASS：没有阻断性问题。")
    elif fail_count == 0 and strict and warn_count > 0:
        print("\nSTRICT FAIL：strict 模式下 WARN 也会阻断。")
    else:
        print("\nFAIL：存在阻断性问题，请先修复 FAIL 项。")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check Research Ops project quality gates.")
    parser.add_argument("--root", default=".", help="Research Ops 根目录，默认当前目录。")
    parser.add_argument("--strict", action="store_true", help="strict 模式：WARN 也导致非零退出码。")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出。")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    findings = run_checks(root)

    fail_count = sum(1 for f in findings if f.severity == "FAIL")
    warn_count = sum(1 for f in findings if f.severity == "WARN")
    exit_code = 1 if fail_count > 0 or (args.strict and warn_count > 0) else 0

    if args.json:
        print(json.dumps({
            "root": str(root),
            "strict": args.strict,
            "exit_code": exit_code,
            "summary": {
                "fail": fail_count,
                "warn": warn_count,
                "info": sum(1 for f in findings if f.severity == "INFO"),
            },
            "findings": [asdict(f) for f in findings],
        }, ensure_ascii=False, indent=2))
    else:
        print_text_report(findings, args.strict)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
