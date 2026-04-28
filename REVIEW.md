---
reviewed: 2026-04-28T02:35:17Z
scope: "docs/实现方案规划.md phases 1-4 completion review"
status: issues_found
files_reviewed:
  - docs/实现方案规划.md
  - qyir/schema.py
  - qyir/validator.py
  - qyir/__main__.py
  - qyir/constants.py
  - qyir/examples/ma_cross.json
  - qyir/examples/rsi_reversal.json
  - qyir/examples/bollinger_macd.json
  - compiler/indicator_engine.py
  - compiler/rule_engine.py
  - compiler/qyir_compiler.py
  - compiler/generate_sample_data.py
  - backtester/metrics.py
  - backtester/simple_backtester.py
  - backtester/data_loader.py
  - tests/test_schema.py
  - tests/test_validator.py
  - tests/test_indicator_engine.py
  - tests/test_rule_engine.py
  - tests/test_qyir_compiler.py
  - tests/test_backtester.py
findings:
  blocker: 8
  warning: 5
  total: 13
---

# Code Review: Phases 1-4 Completion

## Completion Matrix

| Phase | Verdict | Acceptance status |
| --- | --- | --- |
| 1. 定义 QYIR | 部分完成 | Schema、validator、3 个示例存在；规划中的 `python -m qyir.validator ...` 没有 CLI 入口，当前环境还会在导入 pydantic 时失败。 |
| 2. QYIR 执行链 | 部分完成 | 指标/规则/编译函数存在并有单元测试；规划中的 `python -m compiler.qyir_compiler --qyir ... --data data/raw/spy.csv` 不输出成功信息，且 `data/raw/spy.csv` 不存在。 |
| 3. 轻量回测器 | 部分完成 | 回测函数和指标存在；规划中的 CLI 不存在，结果没有 JSON/CSV 保存入口，且收益计算有前视偏差，止损/止盈不影响权益曲线。 |
| 4. LLM 生成 QYIR | 未完成 | 只有 `docs/phase4-research.md` 研究文档；没有 `generator/`、`run_qsga.py`、prompt、LLM client、QYIR generator 或相关测试。 |

## Acceptance Commands Observed

- `python -m qyir.validator qyir/examples/ma_cross.json`: 当前默认 Python 和 `.venv` 均在导入 pydantic 时失败，报 `OSError: [WinError 10106] 无法加载或初始化请求的服务提供程序`。即使环境正常，`qyir/validator.py` 也没有 `if __name__ == "__main__"`，不会实现规划命令的预期输出。
- `python -m qyir qyir/examples/ma_cross.json`: 代码提供了替代入口，但当前环境同样在导入 pydantic 时失败。
- `python -m compiler.qyir_compiler --qyir qyir/examples/ma_cross.json --data data/raw/spy.csv`: 退出码 0 但无输出，因为模块没有 CLI 入口；同时 `data/raw/spy.csv` 不存在，仓库只有 `data/raw/spy_sample.csv`。
- `python -m backtester.simple_backtester --qyir qyir/examples/ma_cross.json --data data/raw/spy.csv`: 退出码 0 但无输出，因为模块没有 CLI 入口；同样缺少 `data/raw/spy.csv`。
- `python run_qsga.py --query "我想做一个稳一点的双均线策略，不要杠杆"`: 失败，`run_qsga.py` 不存在。
- `.venv\Scripts\pytest.exe`: 收集阶段失败，pydantic 导入触发 Anaconda base stdlib 的 asyncio/_overlapped 错误；`.venv/pyvenv.cfg` 指向 `C:\Users\SerendyLin\anaconda3`。

## Blockers

### BLOCKER-01: Phase 4 has no implementation

**File:** `docs/实现方案规划.md:726`

**Issue:** 第四阶段要求 `generator/prompt.py`、`generator/llm_client.py`、`generator/qyir_generator.py` 和 `run_qsga.py` 完成“中文策略意图 -> 合法 QYIR”的链路。当前仓库没有 `generator/` 目录，也没有 `run_qsga.py`；`docs/phase4-research.md` 只是研究材料，不是可运行实现。

**Fix:** 新增 `generator` 包和 `run_qsga.py`，至少实现 prompt 构造、LLM client 抽象、JSON 解析错误捕获、`validate_qyir()` 调用和 CLI 成功/失败输出；为有效 JSON、非法 JSON、schema 失败添加 mock 单元测试。

### BLOCKER-02: Phase 1 documented acceptance command has no CLI implementation

**File:** `qyir/validator.py:59`

**Issue:** 规划验收命令是 `python -m qyir.validator qyir/examples/ma_cross.json`，但 `validator.py` 只暴露 `validate_qyir_file()`，没有 `main()` 或 `if __name__ == "__main__"`。当前 `qyir/__main__.py:9` 实现的是另一个命令 `python -m qyir <file>`，与规划不一致。

**Fix:** 在 `qyir/validator.py` 添加 CLI 入口，解析文件参数、打印 `result.summary`，并按验证结果返回 0/1；或更新规划/README 中的验收命令并确保测试覆盖实际命令。

### BLOCKER-03: Phase 2 documented compiler CLI is missing

**File:** `compiler/qyir_compiler.py:211`

**Issue:** 规划要求 `python -m compiler.qyir_compiler --qyir ... --data ...` 输出 `Signals generated successfully.`。当前文件只到 `compile_qyir_file()`，没有 argparse/main/打印逻辑。实际运行该命令退出码为 0 且无输出，验收会误判或失败。

**Fix:** 添加 `main()`，支持 `--qyir`、`--data`、可选 `--output`，调用 `compile_qyir_file()`，成功时打印预期消息，失败时打印错误并返回非零。

### BLOCKER-04: Phase 3 documented backtester CLI and result persistence are missing

**File:** `backtester/simple_backtester.py:192`

**Issue:** 规划要求 `python -m backtester.simple_backtester --qyir ... --data ...` 输出回测摘要，并且第三阶段验收要求“可以保存结果为 JSON 或 CSV”。当前只提供 `run_backtest_pipeline()` 和 `format_backtest_summary()`，没有 CLI，也没有保存 metrics 的入口。

**Fix:** 添加 CLI 入口，解析 `--qyir`、`--data`、`--output-json/--output-csv`，打印 `format_backtest_summary(result)`，并序列化 `result.metrics`。

### BLOCKER-05: Acceptance data path does not exist

**File:** `compiler/generate_sample_data.py:51`

**Issue:** 规划的第二、三阶段验收命令使用 `data/raw/spy.csv`，但生成脚本和仓库实际文件是 `data/raw/spy_sample.csv`。即使补上 CLI，照规划命令运行仍会因为文件缺失失败。

**Fix:** 要么生成并提交 `data/raw/spy.csv`，要么统一更新验收命令和文档为 `data/raw/spy_sample.csv`，并在 CLI 错误中明确提示缺失文件。

### BLOCKER-06: Backtester uses current-day position on prior-close-to-current-close return

**File:** `backtester/simple_backtester.py:81`

**Issue:** `asset_returns[i]` 是 `close[i-1] -> close[i]` 的收益，但 `strat_returns = positions * asset_returns * position_size` 在 `backtester/simple_backtester.py:85` 使用同一行的 `positions[i]`。`position[i]` 是由第 i 行信号生成的，等于在信号出现前就吃到了当天收益，存在前视偏差，会导致回测指标错误。

**Fix:** 使用上一期持仓计算收益，例如 `effective_positions = pd.Series(positions).shift(1).fillna(0).to_numpy()`，除非系统明确规定信号在前一日收盘前已知并在数据列中体现。

### BLOCKER-07: Stop-loss/take-profit only changes trade records, not equity or returns

**File:** `backtester/simple_backtester.py:98`

**Issue:** 权益曲线在 `backtester/simple_backtester.py:79-95` 已经按原始 `positions` 算完，之后 `_extract_trades()` 才在 `backtester/simple_backtester.py:146-174` 标记止损/止盈。止损触发后，策略收益和权益曲线仍继续按原始持仓波动，风控字段不会真正控制回测结果。

**Fix:** 在逐日回测状态机中同时更新持仓、止损/止盈退出和权益曲线；不要先计算全量 returns 再事后补 trade record。

### BLOCKER-08: Tests cannot currently run in the checked-in project environment

**File:** `.venv/pyvenv.cfg:1`

**Issue:** `.venv` 的 base 指向 `C:\Users\SerendyLin\anaconda3`。当前运行 `.venv\Scripts\pytest.exe` 在收集 `tests/test_schema.py` 和 `tests/test_validator.py` 时导入 pydantic 失败，错误来自 Anaconda stdlib 的 `asyncio/windows_events.py` 和 `_overlapped`。这会阻塞阶段验收测试。

**Fix:** 重建项目虚拟环境，避免混用损坏的 Anaconda base；在 README/开发说明中固定 `uv sync` 或等价步骤，并在 CI/本地验收中使用同一解释器。

## Warnings

### WARNING-01: Date validation accepts impossible dates and compiler can crash outside structured result

**File:** `qyir/schema.py:58`

**Issue:** `_validate_date()` 只检查 `YYYY-MM-DD` 正则，不验证真实日期。`2024-99-99` 可通过 schema 的格式检查，之后 `compiler/qyir_compiler.py:84` 的 `pd.Timestamp(start_date)` 会抛异常，而且该异常不在 `CompilationResult` 错误收集内。

**Fix:** 用 `datetime.date.fromisoformat()` 或 Pydantic 日期类型验证真实日期；编译器日期解析也应 catch 并返回 `result.add_error(...)`。

### WARNING-02: Short-position accounting is wrong if `allow_short` is enabled

**File:** `backtester/simple_backtester.py:149`

**Issue:** 编译器允许 `allow_short` 时生成 `-1` 仓位（`compiler/qyir_compiler.py:197`），但 `_extract_trades()` 始终用多头公式 `(close - entry_price) / entry_price` 计算 PnL，并用同一套 stop-loss/take-profit 判断。空头盈利会被记成亏损，风控方向也反了。

**Fix:** 记录 entry side，对空头使用 `(entry_price - close) / entry_price`，并按 side 分别判断止损/止盈。

### WARNING-03: `allow_short` opens shorts from long exit rules

**File:** `compiler/qyir_compiler.py:197`

**Issue:** 当空仓且 `exit_signal` 为真时，当前实现直接开空仓。QYIR 规划只有 `entry_rules`/`exit_rules`，没有独立 short entry/short exit 语义；把多头退出规则复用为空头入场会生成用户未声明的交易行为。

**Fix:** 第一版可先忽略自动做空，只在已有明确 short entry 规则时开空；或扩展 QYIR schema 增加 `short_entry_rules`/`short_exit_rules`。

### WARNING-04: Phase 3 pipeline test does not assert successful backtest

**File:** `tests/test_backtester.py:233`

**Issue:** `test_ma_cross_pipeline` 只断言返回 `BacktestResult`，注释允许“succeed or fail”。这不能覆盖第三阶段验收“手写 QYIR 可以完成完整回测、输出指标”。

**Fix:** 使用覆盖 QYIR 日期范围的数据，断言 `result.success is True`，并检查 `total_return`、`sharpe_ratio`、`max_drawdown`、`num_trades` 等指标存在。

### WARNING-05: CLI acceptance paths are not covered by tests

**File:** `tests/test_qyir_compiler.py:168`

**Issue:** 测试直接调用 Python 函数，没有任何 subprocess/runpy 覆盖 `python -m qyir.validator`、`python -m compiler.qyir_compiler`、`python -m backtester.simple_backtester` 或 `run_qsga.py`。因此验收命令缺失不会被测试发现。

**Fix:** 增加 CLI smoke tests，至少检查退出码、关键输出文本和缺失文件时的非零退出。

## Overall Assessment

前四阶段目前不是可验收闭环。第一阶段的模型和示例基本成型，但官方验收命令不匹配；第二阶段有函数级执行链但没有命令行入口；第三阶段有回测器雏形但存在会扭曲回测结果的核心行为错误；第四阶段尚未实现。

## Priority Fix Order

1. 重建可用 Python 环境并让测试可运行。
2. 补齐三个验收 CLI：`qyir.validator`、`compiler.qyir_compiler`、`backtester.simple_backtester`，同时统一 `spy.csv`/`spy_sample.csv`。
3. 修正回测器前视偏差，并把止损/止盈纳入实际权益曲线。
4. 补第三阶段成功回测断言和 CLI smoke tests。
5. 实现第四阶段 `generator/` 和 `run_qsga.py` 的最小可测链路。
