| Method | Failure Type | Count | Percentage | Representative Case | Representative Reason |
| --- | --- | ---: | ---: | --- | --- |
| live_route_b_slot_builder::deepseek-v4-flash | success | 38 | 0.475 | qsi_003 | end_to_end_success=true |
| live_route_b_slot_builder::deepseek-v4-flash | schema_failure | 1 | 0.013 | qsi_037 | slot_schema: 1 validation error for StrategySlotSpec indicators.0.role   Input should be 'fast', 'slow', 'signal', 'thre |
| live_route_b_slot_builder::deepseek-v4-flash | unsupported_indicator | 3 | 0.037 | qsi_025 | indicators[0].name: Unsupported or unknown indicator. |
| live_route_b_slot_builder::deepseek-v4-flash | semantic_mismatch | 7 | 0.087 | qsi_056 | backtest_metrics.max_drawdown: The backtest max drawdown exceeds 20.0%.; backtest_metrics.sharpe_ratio: The strategy Sha |
| live_route_b_slot_builder::deepseek-v4-flash | risk_violation | 19 | 0.237 | qsi_001 | backtest_metrics.max_drawdown: The backtest max drawdown exceeds 20.0%.; backtest_metrics.sharpe_ratio: The strategy Sha |
| live_route_b_slot_builder::deepseek-v4-flash | clarification_failure | 12 | 0.150 | qsi_028 | safe_action: Clarification required: entry_threshold. |
