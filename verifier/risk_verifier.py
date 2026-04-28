"""Risk auditing for QYIR strategies.

The auditor checks QYIR risk controls and optional backtest metrics. It is a
paper-prototype risk gate, not investment advice or a production risk engine.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


RiskLevel = Literal["low", "medium", "high", "rejected"]
Severity = Literal["medium", "high", "rejected"]

DEFAULT_DRAWDOWN_LIMIT = 0.2
MIN_TRADE_COUNT = 3
LOW_SHARPE_THRESHOLD = 0.5
HIGH_RETURN_THRESHOLD = 0.5
EXTREME_DRAWDOWN_THRESHOLD = 0.3


@dataclass(frozen=True)
class RiskIssue:
    """One risk audit finding."""

    type: str
    severity: Severity
    path: str
    message: str
    recommendation: str
    actual: Any = None
    threshold: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
            "recommendation": self.recommendation,
            "actual": self.actual,
            "threshold": self.threshold,
        }


@dataclass(frozen=True)
class RiskAuditResult:
    """Structured risk audit output."""

    risk_level: RiskLevel
    passed: bool
    issues: list[RiskIssue] = field(default_factory=list)

    @property
    def warnings(self) -> list[str]:
        return [issue.message for issue in self.issues if issue.severity != "rejected"]

    @property
    def recommendations(self) -> list[str]:
        return [issue.recommendation for issue in self.issues]

    @property
    def valid(self) -> bool:
        """Compatibility alias for verifier-style callers."""
        return self.passed

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_level": self.risk_level,
            "passed": self.passed,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def audit_risk(
    qyir: dict[str, Any],
    backtest_metrics: dict[str, Any] | None = None,
) -> RiskAuditResult:
    """Audit QYIR risk controls plus optional backtest metrics."""
    risk_control = qyir.get("risk_control", {}) if isinstance(qyir, dict) else {}
    metrics = backtest_metrics or {}
    issues: list[RiskIssue] = []

    _audit_risk_control(risk_control, issues)
    _audit_backtest_metrics(risk_control, metrics, issues)

    risk_level = _risk_level(issues)
    return RiskAuditResult(
        risk_level=risk_level,
        passed=risk_level != "rejected",
        issues=issues,
    )


def _audit_risk_control(risk: dict[str, Any], issues: list[RiskIssue]) -> None:
    position_size = _number(risk.get("position_size"), default=1.0)
    leverage = _number(risk.get("leverage"), default=1.0)
    stop_loss = risk.get("stop_loss")

    if position_size > 1.0:
        issues.append(
            RiskIssue(
                type="risk_violation",
                severity="rejected",
                path="risk_control.position_size",
                message="The strategy position_size exceeds 1.0 and must be rejected.",
                recommendation="Reduce position size to 1.0 or below before execution.",
                actual=position_size,
                threshold=1.0,
            )
        )

    if leverage > 1.0:
        issues.append(
            RiskIssue(
                type="risk_warning",
                severity="high",
                path="risk_control.leverage",
                message="The strategy uses leverage greater than 1.0.",
                recommendation="Set leverage to 1.0 for novice-facing QYIR v1 strategies.",
                actual=leverage,
                threshold=1.0,
            )
        )

    if stop_loss is None:
        issues.append(
            RiskIssue(
                type="risk_warning",
                severity="medium",
                path="risk_control.stop_loss",
                message="The strategy does not specify stop-loss.",
                recommendation="Add a stop-loss threshold, e.g. 8%.",
                actual=None,
                threshold="non-null",
            )
        )


def _audit_backtest_metrics(
    risk: dict[str, Any],
    metrics: dict[str, Any],
    issues: list[RiskIssue],
) -> None:
    if not metrics:
        return

    drawdown_limit = _number(
        risk.get("max_drawdown_limit"),
        default=DEFAULT_DRAWDOWN_LIMIT,
    )
    max_drawdown = _number(metrics.get("max_drawdown"), default=0.0)
    drawdown_abs = abs(max_drawdown)

    if drawdown_abs > drawdown_limit:
        issues.append(
            RiskIssue(
                type="risk_warning",
                severity="medium",
                path="backtest_metrics.max_drawdown",
                message=f"The backtest max drawdown exceeds {drawdown_limit:.1%}.",
                recommendation="Reduce position size, add stop-loss, or use a more conservative exit rule.",
                actual=max_drawdown,
                threshold=-drawdown_limit,
            )
        )

    num_trades = int(_number(metrics.get("num_trades"), default=0.0))
    if num_trades < MIN_TRADE_COUNT:
        issues.append(
            RiskIssue(
                type="risk_warning",
                severity="medium",
                path="backtest_metrics.num_trades",
                message="The backtest has too few trades for a reliable sample.",
                recommendation="Extend the backtest period or adjust rules to generate more observations.",
                actual=num_trades,
                threshold=MIN_TRADE_COUNT,
            )
        )

    sharpe = _number(metrics.get("sharpe_ratio"), default=0.0)
    if sharpe < LOW_SHARPE_THRESHOLD:
        issues.append(
            RiskIssue(
                type="risk_warning",
                severity="medium",
                path="backtest_metrics.sharpe_ratio",
                message="The strategy Sharpe ratio is low.",
                recommendation="Review signal quality before presenting the strategy as suitable for novices.",
                actual=sharpe,
                threshold=LOW_SHARPE_THRESHOLD,
            )
        )

    total_return = _number(metrics.get("total_return"), default=0.0)
    if total_return > HIGH_RETURN_THRESHOLD and drawdown_abs > EXTREME_DRAWDOWN_THRESHOLD:
        issues.append(
            RiskIssue(
                type="risk_warning",
                severity="medium",
                path="backtest_metrics.risk_return_balance",
                message="The strategy has high total return but extreme max drawdown.",
                recommendation="Do not rely on return alone; reduce risk exposure and re-run backtest.",
                actual={
                    "total_return": total_return,
                    "max_drawdown": max_drawdown,
                },
                threshold={
                    "total_return": HIGH_RETURN_THRESHOLD,
                    "max_drawdown": -EXTREME_DRAWDOWN_THRESHOLD,
                },
            )
        )


def _risk_level(issues: list[RiskIssue]) -> RiskLevel:
    severities = {issue.severity for issue in issues}
    if "rejected" in severities:
        return "rejected"
    if "high" in severities:
        return "high"
    if "medium" in severities:
        return "medium"
    return "low"


def _number(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for risk auditing."""
    parser = argparse.ArgumentParser(description="Audit QYIR risk controls and optional backtest metrics.")
    parser.add_argument("--qyir", required=True, help="Path to QYIR JSON file.")
    parser.add_argument("--metrics", help="Optional path to backtest metrics JSON file.")
    args = parser.parse_args(argv)

    qyir = json.loads(Path(args.qyir).read_text(encoding="utf-8"))
    metrics = None
    if args.metrics:
        metrics = json.loads(Path(args.metrics).read_text(encoding="utf-8"))

    result = audit_risk(qyir, metrics)
    print("Risk audit completed.")
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
