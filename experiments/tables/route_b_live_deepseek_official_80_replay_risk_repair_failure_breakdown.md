| Method | Failure Type | Count | Percentage | Representative Case | Representative Reason |
| --- | --- | ---: | ---: | --- | --- |
| replay_route_b_slot_builder_risk_repair::deepseek-v4-flash | success | 64 | 0.800 | qsi_001 | end_to_end_success=true |
| replay_route_b_slot_builder_risk_repair::deepseek-v4-flash | schema_failure | 1 | 0.013 | qsi_037 | slot_schema: 1 validation error for StrategySlotSpec indicators.0.role   Input should be 'fast', 'slow', 'signal', 'thre |
| replay_route_b_slot_builder_risk_repair::deepseek-v4-flash | unsupported_indicator | 3 | 0.037 | qsi_025 | indicators[0].name: Unsupported or unknown indicator. |
| replay_route_b_slot_builder_risk_repair::deepseek-v4-flash | clarification_failure | 12 | 0.150 | qsi_028 | safe_action: Clarification required: entry_threshold. |
