# QYIR v1 规格设计文档

> 版本：v1.0
> 日期：2026-04-27
> 定位：CCF C 论文原型系统，支撑三类规则型策略（均线交叉、动量轮动、低波动过滤）

---

## 1. 设计目标

QYIR v1 需满足四个属性：

| 属性 | 含义 |
|------|------|
| **Interpretability** | 每个字段有明确策略语义，新手可读 |
| **Compilability** | 可确定性编译为交易信号序列 |
| **Verifiability** | 可被 Schema / 语义 / 执行 / 风险四层验证器检查 |
| **Repairability** | 错误可定位到字段路径并局部修复 |

v1 不声称覆盖任意金融意图，只在受支持规则型策略空间内提供可靠生成。

---

## 2. QYIR v1 支持范围

| 范围 | v1 支持 | 不支持 |
|------|----------|--------|
| 指标 | SMA, EMA, RSI, MACD, BOLLINGER | STOCH, ATR, OBV, ICHIMOKU 等 |
| 规则运算 | cross_over, cross_under, greater_than, less_than, between | rank_top_k, cross_down, 归因类等 |
| 数据频率 | daily | 分钟级、tick |
| 杠杆 | 固定 1.0 | 任意杠杆 |
| 做空 | 可选关闭 | 复杂做空策略 |
| 市场 | 单标的（ETF / 股票） | 多标的组合、期权、期货 |
| 策略类型 | 均线交叉、动量轮动、低波动过滤 | 高频、事件驱动、基本面 |

---

## 3. 顶层结构

```json
{
  "strategy_name": "string",
  "description": "string",
  "version": "string",
  "market": { ... },
  "indicators": [ ... ],
  "entry_rules": [ ... ],
  "exit_rules": [ ... ],
  "risk_control": { ... }
}
```

| 字段 | 类型 | 必需 | 约束 | 设计理由 |
|------|------|------|------|----------|
| `strategy_name` | `string` | 是 | 非空，仅含 `[a-z0-9_]`，最长 64 字符 | 策略唯一标识，用于日志、实验追踪 |
| `description` | `string` | 否 | 最长 512 字符 | 面向新手的策略说明，用于解释生成 |
| `version` | `string` | 是 | 枚举 `["1.0"]` | 版本控制，后续扩展不破坏已有 QYIR |
| `market` | `object` | 是 | 见 §4 | 定义标的空间与数据范围 |
| `indicators` | `array` | 是 | 非空，至少 1 个，最多 10 个；别名全局唯一 | 技术指标定义，别名供规则引用 |
| `entry_rules` | `array` | 是 | 非空，至少 1 个，最多 10 个 | 入场信号逻辑 |
| `exit_rules` | `array` | 是 | 非空，至少 1 个，最多 10 个 | 出场信号逻辑 |
| `risk_control` | `object` | 是 | 见 §8 | 风控参数，新手安全兜底 |

---

## 4. market 字段结构

```json
{
  "symbol": "SPY",
  "timeframe": "1d",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31"
}
```

| 字段 | 类型 | 必需 | 约束 | 设计理由 |
|------|------|------|------|----------|
| `symbol` | `string` | 是 | 非空，如 `"SPY"`、`"510300.SH"` | 确定回测标的，单标的系统 |
| `timeframe` | `string` | 是 | 枚举 `["1d"]` | v1 仅支持日频，避免频率复杂性 |
| `start_date` | `string` | 是 | 格式 `YYYY-MM-DD`，`start_date < end_date` | 回测起始时间 |
| `end_date` | `string` | 是 | 格式 `YYYY-MM-DD` | 回测结束时间 |

---

## 5. indicators 字段结构

```json
[
  {
    "name": "SMA",
    "params": { "window": 20 },
    "alias": "sma_short"
  },
  {
    "name": "MACD",
    "params": { "fast": 12, "slow": 26, "signal": 9, "output": "macd_line" },
    "alias": "macd_line"
  }
]
```

### 5.1 指标通用字段

| 字段 | 类型 | 必需 | 约束 | 设计理由 |
|------|------|------|------|----------|
| `name` | `string` | 是 | 枚举见 §5.2 | 限定指标空间，可控可验证 |
| `params` | `object` | 是 | 各指标不同，见 §5.2 | 指标计算参数 |
| `alias` | `string` | 是 | 非空，仅含 `[a-z0-9_]`，数组内全局唯一 | 规则通过别名引用指标序列 |

### 5.2 各指标 params 规格

#### SMA

| 参数 | 类型 | 必需 | 约束 | 默认值 |
|------|------|------|------|--------|
| `window` | `int` | 是 | `2 ≤ window ≤ 500` | - |

#### EMA

| 参数 | 类型 | 必需 | 约束 | 默认值 |
|------|------|------|------|--------|
| `window` | `int` | 是 | `2 ≤ window ≤ 500` | - |

#### RSI

| 参数 | 类型 | 必需 | 约束 | 默认值 |
|------|------|------|------|--------|
| `window` | `int` | 否 | `2 ≤ window ≤ 100` | `14` |

#### MACD

| 参数 | 类型 | 必需 | 约束 | 默认值 |
|------|------|------|------|--------|
| `fast` | `int` | 否 | `2 ≤ fast < slow` | `12` |
| `slow` | `int` | 否 | `slow > fast` | `26` |
| `signal` | `int` | 否 | `2 ≤ signal ≤ 100` | `9` |
| `output` | `string` | 是 | 枚举 `["macd_line", "signal_line", "histogram"]` | - |

> **多输出处理**：MACD 产生三条序列（MACD 线、信号线、柱状图）。v1 采用 **多定义方案**：同一 MACD 参数定义多个条目，各指定不同 `output` 和 `alias`。

#### BOLLINGER

| 参数 | 类型 | 必需 | 约束 | 默认值 |
|------|------|------|------|--------|
| `window` | `int` | 否 | `2 ≤ window ≤ 500` | `20` |
| `num_std` | `float` | 否 | `0.1 ≤ num_std ≤ 5.0` | `2.0` |
| `output` | `string` | 是 | 枚举 `["upper", "middle", "lower"]` | - |

> BOLLINGER 同理，需要 upper / middle / lower 时分别定义。

---

## 6. entry_rules 与 exit_rules 字段结构

规则数组中每个元素定义一条条件。多条规则之间为 **AND 逻辑**（所有条件同时满足时触发信号）。

### 6.1 规则类型

| type | 语义 | 所需字段 | 说明 |
|------|------|----------|------|
| `cross_over` | 左序列上穿右序列 | `left`, `right` | 前一时刻 `left ≤ right`，当前 `left > right` |
| `cross_under` | 左序列下穿右序列 | `left`, `right` | 前一时刻 `left ≥ right`，当前 `left < right` |
| `greater_than` | 左序列大于右序列 | `left`, `right` | 逐行比较 |
| `less_than` | 左序列小于右序列 | `left`, `right` | 逐行比较 |
| `between` | 左序列在区间内 | `left`, `lower`, `upper` | `lower ≤ left ≤ upper` |

### 6.2 规则字段定义

```json
// cross_over / cross_under / greater_than / less_than
{
  "type": "cross_over",
  "left": "sma_short",
  "right": "sma_long"
}

// between
{
  "type": "between",
  "left": "rsi_14",
  "lower": 30,
  "upper": 70
}
```

| 字段 | 类型 | 必需 | 约束 | 设计理由 |
|------|------|------|------|----------|
| `type` | `string` | 是 | 枚举 §6.1 中五种 | 限定运算空间，编译确定性 |
| `left` | `string` | 是 | 必须引用 `indicators` 中已定义的 `alias` | 编译时引用检查 |
| `right` | `string \| number` | 条件必需 | 字符串须为有效 alias，数值为 literal；`between` 类型不需要此字段 | 支持指标交叉和阈值比较 |
| `lower` | `string \| number` | `between` 必需 | 同 `right` 约束 | 区间下界 |
| `upper` | `string \| number` | `between` 必需 | 同 `right` 约束；`upper > lower`（数值时校验） | 区间上界 |

### 6.3 引用完整性约束

- `left`、`right`、`lower`、`upper` 中类型为 `string` 的值 **必须** 是 `indicators` 数组中某个条目的 `alias`
- 未引用任何已定义 alias 的规则为 **Schema Failure**
- alias 引用在 entry_rules 和 exit_rules 之间共享

---

## 7. 规则语义示例

| 策略类型 | entry_rules | exit_rules |
|----------|-------------|------------|
| 均线交叉 | SMA20 上穿 SMA60 | SMA20 下穿 SMA60 |
| RSI 超卖反弹 | RSI 上穿 30 | RSI 高于 70 |
| 布林带回归 | 收盘价低于布林下轨 | 收盘价回到布林中轨 |
| MACD 金叉 | MACD 线上穿信号线 | MACD 线下穿信号线 |

---

## 8. risk_control 字段结构

```json
{
  "position_size": 0.3,
  "stop_loss": 0.08,
  "take_profit": null,
  "max_drawdown_limit": 0.20,
  "allow_short": false,
  "leverage": 1.0
}
```

| 字段 | 类型 | 必需 | 约束 | 设计理由 |
|------|------|------|------|----------|
| `position_size` | `float` | 是 | `0.01 ≤ position_size ≤ 1.0` | 仓位比例，v1 为单标的系统，代表投入资金占比 |
| `stop_loss` | `float \| null` | 否 | `0.01 ≤ value ≤ 0.50`；`null` 表示未设置 | 止损比例，新手策略安全兜底 |
| `take_profit` | `float \| null` | 否 | `0.01 ≤ value ≤ 1.0`；`null` 表示未设置 | 止盈比例 |
| `max_drawdown_limit` | `float \| null` | 否 | `0.01 ≤ value ≤ 0.50`；`null` 表示未设置 | 最大回撤阈值，风险审计核心指标 |
| `allow_short` | `bool` | 是 | 默认 `false` | 新手默认禁止做空 |
| `leverage` | `float` | 是 | **必须为 1.0** | v1 不支持杠杆，硬约束 |

---

## 9. 合法 QYIR 示例

### 示例 1：双均线交叉策略

```json
{
  "strategy_name": "ma_cross_spy",
  "description": "SMA20 上穿 SMA60 买入，下穿卖出",
  "version": "1.0",
  "market": {
    "symbol": "SPY",
    "timeframe": "1d",
    "start_date": "2020-01-01",
    "end_date": "2024-12-31"
  },
  "indicators": [
    { "name": "SMA", "params": { "window": 20 }, "alias": "sma_short" },
    { "name": "SMA", "params": { "window": 60 }, "alias": "sma_long" }
  ],
  "entry_rules": [
    { "type": "cross_over", "left": "sma_short", "right": "sma_long" }
  ],
  "exit_rules": [
    { "type": "cross_under", "left": "sma_short", "right": "sma_long" }
  ],
  "risk_control": {
    "position_size": 0.5,
    "stop_loss": 0.10,
    "take_profit": null,
    "max_drawdown_limit": 0.20,
    "allow_short": false,
    "leverage": 1.0
  }
}
```

### 示例 2：RSI 超卖反弹策略

```json
{
  "strategy_name": "rsi_reversal",
  "description": "RSI 低于 30 买入，高于 70 卖出",
  "version": "1.0",
  "market": {
    "symbol": "510300.SH",
    "timeframe": "1d",
    "start_date": "2021-01-01",
    "end_date": "2024-06-30"
  },
  "indicators": [
    { "name": "RSI", "params": { "window": 14 }, "alias": "rsi_14" }
  ],
  "entry_rules": [
    { "type": "less_than", "left": "rsi_14", "right": 30 }
  ],
  "exit_rules": [
    { "type": "greater_than", "left": "rsi_14", "right": 70 }
  ],
  "risk_control": {
    "position_size": 0.3,
    "stop_loss": 0.05,
    "take_profit": 0.15,
    "max_drawdown_limit": 0.15,
    "allow_short": false,
    "leverage": 1.0
  }
}
```

### 示例 3：布林带回归 + MACD 确认

```json
{
  "strategy_name": "bollinger_macd_confirm",
  "description": "价格低于布林下轨且 MACD 金叉时买入",
  "version": "1.0",
  "market": {
    "symbol": "SPY",
    "timeframe": "1d",
    "start_date": "2020-01-01",
    "end_date": "2024-12-31"
  },
  "indicators": [
    { "name": "BOLLINGER", "params": { "window": 20, "num_std": 2.0, "output": "lower" }, "alias": "boll_lower" },
    { "name": "BOLLINGER", "params": { "window": 20, "num_std": 2.0, "output": "middle" }, "alias": "boll_middle" },
    { "name": "MACD", "params": { "fast": 12, "slow": 26, "signal": 9, "output": "macd_line" }, "alias": "macd_line" },
    { "name": "MACD", "params": { "fast": 12, "slow": 26, "signal": 9, "output": "signal_line" }, "alias": "signal_line" }
  ],
  "entry_rules": [
    { "type": "less_than", "left": "boll_lower", "right": "boll_middle" },
    { "type": "cross_over", "left": "macd_line", "right": "signal_line" }
  ],
  "exit_rules": [
    { "type": "greater_than", "left": "boll_middle", "right": "boll_lower" }
  ],
  "risk_control": {
    "position_size": 0.3,
    "stop_loss": 0.08,
    "take_profit": null,
    "max_drawdown_limit": 0.20,
    "allow_short": false,
    "leverage": 1.0
  }
}
```

---

## 10. 非法 QYIR 示例

### 非法 1：缺失必需字段

```json
{
  "strategy_name": "bad_strategy",
  "market": { "symbol": "SPY", "timeframe": "1d", "start_date": "2020-01-01", "end_date": "2024-12-31" },
  "indicators": []
}
```

> **错误类型**：Schema Failure
> **原因**：缺少 `version`、`entry_rules`、`exit_rules`、`risk_control`；`indicators` 为空数组

### 非法 2：使用不支持的指标

```json
{
  "strategy_name": "bad_indicator",
  "version": "1.0",
  "market": { "symbol": "SPY", "timeframe": "1d", "start_date": "2020-01-01", "end_date": "2024-12-31" },
  "indicators": [
    { "name": "STOCHASTIC", "params": { "k": 14, "d": 3 }, "alias": "stoch_k" }
  ],
  "entry_rules": [
    { "type": "cross_over", "left": "stoch_k", "right": 80 }
  ],
  "exit_rules": [
    { "type": "cross_under", "left": "stoch_k", "right": 20 }
  ],
  "risk_control": {
    "position_size": 0.5, "stop_loss": null, "take_profit": null,
    "max_drawdown_limit": 0.2, "allow_short": false, "leverage": 1.0
  }
}
```

> **错误类型**：Schema Failure（枚举不合法）
> **原因**：`STOCHASTIC` 不在 v1 支持指标列表中

### 非法 3：使用不支持的规则类型

```json
{
  "...": "...",
  "entry_rules": [
    { "type": "rank_top_k", "left": "momentum", "right": 3 }
  ]
}
```

> **错误类型**：Schema Failure（枚举不合法）
> **原因**：`rank_top_k` 不在 v1 支持规则类型中

### 非法 4：杠杆不为 1.0

```json
{
  "...": "...",
  "risk_control": {
    "position_size": 1.0, "stop_loss": null, "take_profit": null,
    "max_drawdown_limit": 0.5, "allow_short": true, "leverage": 3.0
  }
}
```

> **错误类型**：Schema Failure（硬约束违反）
> **原因**：v1 强制 `leverage = 1.0`，不接受其他值

### 非法 5：规则引用不存在的别名

```json
{
  "...": "...",
  "indicators": [
    { "name": "SMA", "params": { "window": 20 }, "alias": "sma_20" }
  ],
  "entry_rules": [
    { "type": "cross_over", "left": "sma_20", "right": "ema_50" }
  ]
}
```

> **错误类型**：Schema Failure（引用完整性违反）
> **原因**：`ema_50` 未在 `indicators` 中定义

### 非法 6：指标参数越界

```json
{
  "indicators": [
    { "name": "SMA", "params": { "window": 0 }, "alias": "bad_sma" }
  ]
}
```

> **错误类型**：Schema Failure（参数约束违反）
> **原因**：SMA `window` 必须 ≥ 2

---

## 11. QYIR 与 JSON Schema / Constrained Decoding 的区别

本节直接服务于论文论证，需在 Related Work 和 Method 中反复强调：

| 维度 | JSON Schema / Constrained Decoding | QYIR v1 |
|------|-----------------------------------|---------|
| 约束对象 | 输出格式（JSON 结构合法） | 策略语义（指标、规则、风控的行为约束） |
| 编译语义 | 无 | 有（确定性编译为交易信号序列） |
| 引用完整性 | 通常不检查 | 强制检查（alias → indicator 映射） |
| 风险约束 | 不直接支持 | 结构化嵌入（position_size, stop_loss 等） |
| 局部修复 | 弱（只知 JSON 路径，不知策略语义） | 强（Error-Location-Action 映射到策略字段） |
| 论文定位 | 生成约束技术 | 领域程序中间表示 |

> **Constrained Decoding constrains how the model says a strategy, while QYIR constrains what the strategy means and how it can be compiled, verified, audited, and repaired.**

---

## 12. 阶段一验收标准

### 12.1 必须通过

| # | 验收项 | 验证方式 |
|---|--------|----------|
| 1 | Pydantic Schema 定义完成 | `qyir/schema.py` 可 import 且无报错 |
| 2 | 合法 QYIR 通过验证 | 加载 §9 中 3 个示例，全部 `valid=True` |
| 3 | 非法 QYIR 被拒绝 | 加载 §10 中 6 个示例，全部 `valid=False` 并返回具体错误路径 |
| 4 | 至少 3 个合法示例文件 | `qyir/examples/` 下有 `.json` 文件 |
| 5 | 至少 3 个非法示例文件 | `qyir/examples/invalid/` 下有 `.json` 文件 |
| 6 | 5 种指标参数校验正确 | SMA/EMA/RSI/MACD/BOLLINGER 各类合法/非法参数组合测试通过 |
| 7 | 5 种规则类型校验正确 | 各运算类型的字段完整性校验通过 |
| 8 | alias 全局唯一性校验 | 重复 alias 被拒绝 |
| 9 | 引用完整性校验 | 规则中引用不存在 alias 被拒绝 |
| 10 | leverage 硬约束 | `leverage != 1.0` 被拒绝 |
| 11 | CLI 验证器可运行 | `python -m qyir.validator <file>` 输出验证结果 |

### 12.2 验收命令

```bash
# 验证合法 QYIR
python -m qyir.validator qyir/examples/ma_cross.json
# 预期输出：QYIR validation passed.

# 验证非法 QYIR
python -m qyir.validator qyir/examples/invalid/bad_leverage.json
# 预期输出：QYIR validation failed: leverage must be 1.0
```

### 12.3 阶段一不要求

以下内容属于后续阶段：

- LLM 生成 QYIR（阶段二）
- 指标计算引擎（阶段二）
- 回测器（阶段三）
- 语义验证（阶段四）
- 风险审计（阶段五）
- Safe Rejection（阶段六）
- 修复模块（阶段七）
- QSI-Bench（阶段八）
