---
name: autoresearch-trading
description: "Autonomous self-improvement loop for AI_TUNE trading strategies. Iteratively modifies strategy parameters, evaluates against 12 binary criteria (survival/quality/robustness), keeps improvements, discards regressions."
---

# Autoresearch — AI_TUNE Trading Strategies

Autonomous iteration loop to improve the forex and crypto trading strategies.
Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch).

**Core loop:** Modify strategy code → Run eval → Keep if improved (no Tier 1 regression), discard if not → Update TradingBrain → Repeat.

## Eval Command

```bash
cd C:/Users/User/WORK/AI_TUNE && .venv/Scripts/python -m autoresearch.run_eval --engine {forex|crypto} --iteration N
```

Parse output:
- `eval_score: X` — total score (higher is better, max 12)
- `eval_max: 12`
- `eval_details: survival(...) | quality(...) | robustness(...)`

## 12 Evaluation Criteria (3 Tiers, 4 each)

### Tier 1 — Survival (MUST NOT REGRESS)

| # | Criterion | Threshold | Key |
|---|-----------|-----------|-----|
| S1 | Max drawdown | < 12% | `max_drawdown_pct` |
| S2 | Trade count | >= 100 | `total_trades` |
| S3 | Profit factor | > 1.3 | `profit_factor` |
| S4 | Net profit | > 0 | `net_profit_after_fees` |

### Tier 2 — Quality

| # | Criterion | Threshold | Key |
|---|-----------|-----------|-----|
| Q1 | Sharpe ratio | > 1.0 + progressive penalty | `sharpe_ratio` |
| Q2 | Win rate | > 40% | `win_rate` |
| Q3 | Calmar ratio | > 1.0 | `calmar_ratio` |
| Q4 | Trade expectancy | > 0 | `avg_trade_expectancy` |

**Progressive Sharpe Penalty:** base 1.0, +0.05 per 10 iterations, ceiling 1.5.
Formula: `min(1.0 + (iteration // 10) * 0.05, 1.5)`

### Tier 3 — Robustness

| # | Criterion | Threshold | Key |
|---|-----------|-----------|-----|
| R1 | OOS/IS Sharpe ratio | > 0.5 | `oos_sharpe / is_sharpe` |
| R2 | Walk-forward efficiency | > 50% | `wf_efficiency` |
| R3 | Monte Carlo DD 95th pct | < 25% | `mc_dd_95th` |
| R4 | Recovery factor | > 3.0 | `recovery_factor` |

## Scope — Files You CAN Modify

**Forex:**
- `C:/Users/User/WORK/AI_TUNE/forex/strategy.py` — `ForexMeanRevStrategy` (BB, RSI, ATR params)
- `C:/Users/User/WORK/AI_TUNE/config.yaml` — `forex.strategy.*` section (bb_period, bb_std, rsi_*, atr_*)

**Crypto:**
- `C:/Users/User/WORK/AI_TUNE/crypto/strategy.py` — `CryptoMeanRevStrategy`
- `C:/Users/User/WORK/AI_TUNE/config.yaml` — `crypto.strategies.mean_rev.*` section

## Read-Only — Files You CANNOT Modify

- `autoresearch/run_eval.py` — Eval harness (ground truth)
- `autoresearch/eval_survival.py` — Tier 1 criteria
- `autoresearch/eval_quality.py` — Tier 2 criteria
- `autoresearch/eval_robustness.py` — Tier 3 criteria
- `autoresearch/walk_forward.py` — Walk-forward splitter
- `autoresearch/monte_carlo.py` — Monte Carlo engine
- `autoresearch/results/*.tsv` — Results log (written by harness, never manually edited)
- `forex/backtester.py` — VectorBT wrapper
- `crypto/backtester.py` — Crypto backtester
- `forex/data_loader.py` — Data loading
- `memory/trading_brain.py` — TradingBrain implementation

## The Loop

```
LOOP FOREVER (for given --engine):
  1. Read current eval score:
       cd C:/Users/User/WORK/AI_TUNE && .venv/Scripts/python -m autoresearch.run_eval --engine {engine} --iteration N
     Parse: eval_score, eval_details (note which criteria FAIL per tier)
  2. Read TradingBrain context (last 10 lessons + all knowledge):
       cat AI_TUNE/memory/lessons.json | python -c "import json,sys; [print(l) for l in json.load(sys.stdin)[-10:]]"
       cat AI_TUNE/memory/knowledge.json
  3. Read last 10 rows of results TSV to avoid re-trying discarded changes:
       cat AI_TUNE/autoresearch/results/{engine}-results.tsv
  4. Pick ONE focused change targeting a FAILING criterion:
       - Prioritize: Tier 1 failures first → Tier 2 → Tier 3
       - Never repeat a change that was already discarded (check TSV)
       - One parameter tweak or one logic improvement — nothing more
  5. Apply the change to the strategy file (Edit tool)
  6. git commit the change:
       cd C:/Users/User/WORK/AI_TUNE && git add forex/strategy.py config.yaml  # (or crypto/)
       git commit -m "autoresearch iter {N}: {one-sentence description}"
  7. Re-run eval:
       cd C:/Users/User/WORK/AI_TUNE && .venv/Scripts/python -m autoresearch.run_eval --engine {engine} --iteration N
  8. Decision:
       IF new_score > old_score AND no Tier 1 criterion that was YES became NO → KEEP
         → Log "keep" in TSV
       ELSE → DISCARD
         → cd C:/Users/User/WORK/AI_TUNE && git reset --hard HEAD~1
         → Log "discard" in TSV
  9. Update TradingBrain — add a lesson:
       - Use TradingBrain.add_lesson(iteration=N, engine="{engine}", change="...", result="keep|discard", lesson_text="...", rule_tag="...")
       - Example: python -c "import sys; sys.path.insert(0,'C:/Users/User/WORK/AI_TUNE'); from memory.trading_brain import TradingBrain; TradingBrain().add_lesson(...)"
  10. Check for knowledge promotions:
       python -c "import sys; sys.path.insert(0,'C:/Users/User/WORK/AI_TUNE'); from memory.trading_brain import TradingBrain; TradingBrain().check_promotions()"
  11. Increment N → REPEAT — NEVER STOP, NEVER ASK "should I continue?"
```

## Crash / Error Handling

- If eval crashes (Python exception, missing data): attempt fix max 3 times, else log "crash" and revert with `git reset --hard HEAD~1`
- If data is missing: check `AI_TUNE/data/forex/` or `AI_TUNE/data/crypto/` — the eval will download a sample automatically if empty
- If git commit fails: fix the issue (stage the right files), do not skip with `--no-verify`

## Results Log

File: `AI_TUNE/autoresearch/results/{engine}-results.tsv` (tab-separated)
The eval harness appends automatically. Do NOT write to this file manually.

```tsv
iteration	commit	score	max	status	description
0	a1b2c3d	6	12	FAIL	baseline: survival(3/4)...
1	b2c3d4e	8	12	keep	increased bb_period from 20 to 25 → trades hit 100
2	-	7	12	discard	lowered rsi_entry_low from 30 to 25 — no improvement
```

## TradingBrain — Memory System

3-layer memory at `AI_TUNE/memory/`:
- `working.json` — current run state (ephemeral, updated each iteration)
- `lessons.json` — per-iteration record: what changed, keep/discard, why
- `knowledge.json` — promoted rules (rule_tag seen >= 5 times across lessons)

Read context before proposing a change:
```python
import sys; sys.path.insert(0, 'C:/Users/User/WORK/AI_TUNE')
from memory.trading_brain import TradingBrain
print(TradingBrain().get_context_for_claude(last_n_lessons=10))
```

Common `rule_tag` values to use when adding lessons:
- `bb_wider_helps` — wider Bollinger Band improves signals
- `rsi_tighter_helps` — tighter RSI thresholds improve quality
- `atr_stop_conservative` — larger ATR multiplier improves survival
- `ma_filter_helps` — trend filter reduces false signals
- `fewer_params_better` — simpler config generalizes better

## Key Files Reference

| File | Role |
|------|------|
| `AI_TUNE/docs/superpowers/specs/2026-03-17-ai-tune-trading-bot-design.md` | Full system spec |
| `AI_TUNE/config.yaml` | All thresholds & strategy params |
| `AI_TUNE/forex/strategy.py` | `ForexMeanRevStrategy` — main modification target |
| `AI_TUNE/crypto/strategy.py` | `CryptoMeanRevStrategy` — main modification target |
| `AI_TUNE/autoresearch/run_eval.py` | Eval harness (read-only) |
| `AI_TUNE/autoresearch/results/{engine}-results.tsv` | TSV log (read-only) |
| `AI_TUNE/memory/working.json` | Current run state |
| `AI_TUNE/memory/lessons.json` | Per-iteration lessons |
| `AI_TUNE/memory/knowledge.json` | Promoted rules (high-confidence) |

## Strategy Parameters — Modification Levers

**ForexMeanRevStrategy (`forex/strategy.py` + `config.yaml → forex.strategy`):**
- `bb_period` (default 20) — Bollinger Band lookback
- `bb_std` (default 2.0) — Band width in std deviations
- `rsi_period` (default 14) — RSI lookback
- `rsi_entry_low` (default 30) — Oversold threshold (long entry)
- `rsi_entry_high` (default 70) — Overbought threshold (short entry)
- `rsi_exit` (default 50) — RSI neutral exit level
- `ma_period` (default 50) — Trend filter MA period
- `atr_period` (default 14) — ATR stop-loss lookback
- `atr_stop_multiplier` (default 1.5) — ATR stop distance multiplier

**CryptoMeanRevStrategy (`crypto/strategy.py` + `config.yaml → crypto.strategies.mean_rev`):**
- `bb_period` (default 20) — Bollinger Band lookback
- `bb_std` (default 2.0) — Band width
- `rsi_period` (default 14) — RSI lookback
- `rsi_entry` (default 30) — Entry threshold
- `rsi_exit` (default 50) — Exit threshold

## Rules

- **ONE change per iteration** — atomic, reversible, explainable in one sentence
- **Tier 1 is sacred** — never keep a change that causes a Tier 1 regression (even if total score improves)
- **Never repeat discarded changes** — check the TSV before proposing; if a similar change was already tried, try something different
- **Mechanical verification only** — no subjective "looks better"; trust the score
- **Simplicity wins** — equal score + fewer param changes = KEEP
- **NEVER modify eval scripts** — `run_eval.py`, `eval_survival.py`, `eval_quality.py`, `eval_robustness.py` are ground truth
- **NEVER STOP** — loop until manually interrupted
- **Print brief status every 5 iterations** — e.g., "Iteration 15 [forex]: score 8/12, 6 keeps / 9 discards, top failing: oos_ratio"
- **Track iteration count** — pass the current iteration number to `--iteration N` so Progressive Sharpe Penalty is correct

## Starting a Session

```bash
# Get current state
cd C:/Users/User/WORK/AI_TUNE
.venv/Scripts/python -m autoresearch.run_eval --engine forex --iteration 0

# Read what was already tried
cat autoresearch/results/forex-results.tsv

# Read accumulated knowledge
.venv/Scripts/python -c "import sys; sys.path.insert(0,'.'); from memory.trading_brain import TradingBrain; print(TradingBrain().get_context_for_claude())"
```

Then run the loop described above. To switch engine, replace `forex` with `crypto` throughout.
