| Method | Failure Type | Count | Percentage | Representative Case | Representative Reason |
| --- | --- | ---: | ---: | --- | --- |
| live_qsga_qyir::qwen3.6-flash | success | 30 | 0.375 | qsi_006 | end_to_end_success=true |
| live_qsga_qyir::qwen3.6-flash | schema_failure | 40 | 0.500 | qsi_005 | indicators.0: Value error, MACD.output must be one of ['macd_line', 'signal_line', 'histogram']; indicators.1: Value err |
| live_qsga_qyir::qwen3.6-flash | alias_failure | 5 | 0.062 | qsi_003 | root: Value error, entry_rules[0].left references unknown alias 'close' |
| live_qsga_qyir::qwen3.6-flash | compilation_failure | 1 | 0.013 | qsi_018 | Exit rule 0 failed: 'float' object has no attribute 'shift' |
| live_qsga_qyir::qwen3.6-flash | risk_violation | 4 | 0.050 | qsi_001 | backtest_metrics.max_drawdown: The backtest max drawdown exceeds 20.0%.; backtest_metrics.sharpe_ratio: The strategy Sha |
| live_raw_qyir::qwen3.6-flash | success | 6 | 0.075 | qsi_006 | end_to_end_success=true |
| live_raw_qyir::qwen3.6-flash | schema_failure | 49 | 0.613 | qsi_005 | indicators.0: Value error, MACD.output must be one of ['macd_line', 'signal_line', 'histogram']; indicators.1: Value err |
| live_raw_qyir::qwen3.6-flash | alias_failure | 5 | 0.062 | qsi_003 | root: Value error, entry_rules[0].left references unknown alias 'close' |
| live_raw_qyir::qwen3.6-flash | risk_violation | 5 | 0.062 | qsi_001 | backtest_metrics.max_drawdown: The backtest max drawdown exceeds 20.0%.; backtest_metrics.sharpe_ratio: The strategy Sha |
| live_raw_qyir::qwen3.6-flash | unsafe_intent_failure | 15 | 0.188 | qsi_066 | raw live LLM baseline has no safe-rejection gate |
