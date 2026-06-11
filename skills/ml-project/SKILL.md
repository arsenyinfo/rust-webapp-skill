---
name: ml-project
description: Guidelines for ML projects. Use when building ML pipelines, training models, running experiments, or analyzing results. Auto-invoked for ML-related tasks.
---

# ML Project Guidelines

## Philosophy

- **Validation is king** - always define clear train/val/test splits before training
- **Error analysis is queen** - understand failures, not just metrics
- **No mocks** - test with real data and objects
- **Raw over abstraction** - YAML configs, tensorboard, raw plots. No MLflow/W&B complexity
- **Hyperparam tuning is overrated** - usually low-hanging fruit elsewhere: features, data, target. Highly tuned models are brittle
- **Simple ensembles only** - if needed, blend linear model + CatBoost. No stacking towers
- **Too good = suspicious** - great results warrant paranoid leakage checks before celebration
- **Apples to apples** - always compare full baseline vs full experiment on the same data. No cherrypicked subsamples
- **Hypotheses need origins** - every experiment starts with "why". No random fishing expeditions

## Default Workflow

1. Inspect the project first: data shape, target definition, existing metrics, existing split, and current baseline.
2. Define or verify train/val/test before training anything. For time-series, use chronological splits by default.
3. Write the hypothesis before the experiment: what should improve, why, and which metric should move.
4. Run the simplest baseline that answers the question, then compare the full baseline and full experiment on identical splits.
5. Save the frozen config, metrics, predictions, model artifact, and any feature importance or plots into the run directory.
6. Do error analysis before declaring success: inspect false positives/negatives, high-loss examples, calibration, slices, and date/entity drift.
7. If results look very strong, assume leakage until checked.
8. Write a short memo with hypothesis, setup, results, conclusion, and next step.

## Stack

| Purpose | Tool |
|---------|------|
| Tabular ML | CatBoost |
| Deep Learning | PyTorch |
| DataFrames | Polars, never pandas |
| Logging | coloredlogs + `logging.getLogger(__name__)` |
| CLI | fire |
| Config | dataclass + YAML |
| Plots | matplotlib, raw |
| Tracking | tensorboard + `memos/` |
| Performance | Rust via maturin, when needed |

## Project Structure

```
project/
├── core/               # metrics, validation, shared utils
├── pipeline/           # production baseline code
├── experimental/       # exp_name/ subdirs for throwaway code
│   └── exp_name/       # migrate to pipeline/ if works
├── features/           # feature engineering modules
├── data/
│   ├── raw/            # immutable source data
│   └── processed/      # transformed data
├── models/             # saved model artifacts
├── memos/              # experiment results, markdown
├── configs/            # YAML job configs
├── experiments/        # timestamped run outputs
├── tests/              # pytest tests
└── temp/               # validation scripts, clean up after
```

## Config Pattern

```python
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Config:
    seed: int = 42
    val_days: int = 3
    use_gpu: bool = False

    def __post_init__(self) -> None:
        if self.val_days <= 0:
            raise ValueError("val_days must be positive")

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Config":
        config_path = Path(path)
        with config_path.open(encoding="utf-8") as f:
            data: Any = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Config {config_path} must contain a mapping")

        return cls(**data)

    def save(self, path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8") as f:
            yaml.safe_dump(asdict(self), f, sort_keys=True)
```

Save a config copy to each experiment dir for reproducibility.

## Validation Patterns

### Temporal Split

Default for time-series. No lookahead bias.

```python
import polars as pl


def temporal_split(
    df: pl.DataFrame,
    date_col: str,
    val_days: int = 3,
    test_days: int = 5,
) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    if date_col not in df.columns:
        raise ValueError(f"Missing date column: {date_col}")
    if val_days <= 0 or test_days <= 0:
        raise ValueError("val_days and test_days must be positive")

    date_expr = pl.col(date_col)
    if df.schema[date_col] != pl.Date:
        date_expr = date_expr.dt.date()

    with_dates = df.with_columns(date_expr.alias("_split_date"))
    unique_dates = (
        with_dates.select("_split_date")
        .unique()
        .sort("_split_date")
        .get_column("_split_date")
        .to_list()
    )

    required_days = val_days + test_days + 1
    if len(unique_dates) < required_days:
        raise ValueError(
            f"Need at least {required_days} unique dates, got {len(unique_dates)}"
        )

    train_end = -(val_days + test_days)
    val_end = -test_days

    train_dates = unique_dates[:train_end]
    val_dates = unique_dates[train_end:val_end]
    test_dates = unique_dates[val_end:]

    train = with_dates.filter(pl.col("_split_date").is_in(train_dates)).drop("_split_date")
    val = with_dates.filter(pl.col("_split_date").is_in(val_dates)).drop("_split_date")
    test = with_dates.filter(pl.col("_split_date").is_in(test_dates)).drop("_split_date")

    return train, val, test
```

### Leakage Checks

Always verify:

- Features are available at prediction time
- Aggregations and normalizers are fit on train only
- No target, future, backtest, or execution columns enter features
- Entity duplicates do not cross splits unless that is intentional
- Time-series tasks use chronological splits, and embargo gaps where labels overlap windows
- A too-good metric is reproduced on a fresh holdout before it is trusted

### Feature Column Filtering

```python
import polars as pl


EXCLUDED_PREFIXES = ("target_", "backtest_", "aux_", "exec_")
EXCLUDED_COLS = {"timestamp", "date", "id"}


def get_feature_cols(df: pl.DataFrame) -> list[str]:
    return [
        col
        for col in df.columns
        if not any(col.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
        and col not in EXCLUDED_COLS
    ]
```

## Logging Standards

```python
import logging

import coloredlogs


coloredlogs.install(level="INFO")
logger = logging.getLogger(__name__)

logger.info("Loaded %s rows", df.height)
logger.warning("Missing values in %s", col)

try:
    df = load_data(data_path)
except OSError:
    logger.exception("Failed to load data")  # not logger.error(str(e))
    raise
```

Log at key checkpoints:

- Data loading: row counts, date ranges
- Train/val/test split: sizes and date boundaries
- Feature selection: what is included and excluded
- Training: class balance, early stopping, final metrics
- Evaluation: all metrics with confidence intervals if possible

## Experiment Tracking

### Timestamped Directories

```python
from datetime import datetime, timezone
from pathlib import Path


def create_run_dir(base: str | Path = "experiments") -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    run_dir = Path(base) / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir
```

Each run saves:

- `config.yaml` - frozen config
- `metrics.json` - final metrics
- `model.cbm` or `model.pt` - trained model
- `feature_importance.csv` - if applicable
- `predictions.parquet` - test set predictions

### Memos

Write findings to `memos/` as markdown:

- Hypothesis
- Experiment setup
- Results: tables and key numbers
- Error analysis
- Conclusions and next steps

## Reproducibility Checklist

```python
import random

import numpy as np
import torch


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
```

Always:

- [ ] Fix random seed at entry point
- [ ] Save config to experiment dir
- [ ] Log git commit hash
- [ ] Use temporal splits for time-series
- [ ] Compare against baseline before claiming improvement
- [ ] Save predictions for error analysis

## Data Patterns

### JSON + Parquet Pairs

```python
import json
from pathlib import Path

import polars as pl


slug = "train"
data_dir = Path("data")

with (data_dir / f"{slug}.json").open(encoding="utf-8") as f:
    metadata = json.load(f)

trades = pl.read_parquet(data_dir / f"{slug}.parquet")
```

### Memory Optimization

```python
import polars as pl


float_cols = [name for name, dtype in df.schema.items() if dtype == pl.Float64]
df = df.with_columns([pl.col(col).cast(pl.Float32) for col in float_cols])
```

### Caching

```python
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def list_data_files(data_dir: str | Path) -> tuple[Path, ...]:
    return tuple(sorted(Path(data_dir).glob("*.parquet")))
```

## CatBoost Patterns

```python
from catboost import CatBoostClassifier, Pool


model = CatBoostClassifier(
    iterations=1000,
    learning_rate=0.05,
    depth=6,
    random_seed=config.seed,
    early_stopping_rounds=50,
    verbose=100,
    task_type="GPU" if config.use_gpu else "CPU",
)

train_pool = Pool(X_train, y_train, cat_features=cat_cols)
val_pool = Pool(X_val, y_val, cat_features=cat_cols)

model.fit(train_pool, eval_set=val_pool)
model.save_model(str(run_dir / "model.cbm"))
```

## PyTorch Patterns

```python
import torch


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

model.train()
for inputs, targets in train_loader:
    inputs = inputs.to(device)
    targets = targets.to(device)

    optimizer.zero_grad(set_to_none=True)
    logits = model(inputs)
    loss = criterion(logits, targets)
    loss.backward()
    optimizer.step()

torch.save(
    {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "loss": float(loss.detach().cpu()),
    },
    run_dir / f"checkpoint_{epoch}.pt",
)
```

## Quick CLI with Fire

```python
import fire


def train(config_path: str = "configs/default.yaml") -> None:
    config = Config.from_yaml(config_path)
    ...


def evaluate(model_path: str, data_path: str) -> None:
    ...


if __name__ == "__main__":
    fire.Fire({"train": train, "evaluate": evaluate})
```

## Anti-Patterns to Avoid

- pandas, use Polars
- print statements, use logger
- mocking in tests, use real data
- MLflow/W&B, use tensorboard + memos
- hardcoded paths, use config
- random splits for time-series, use temporal splits
- training without baseline comparison
- celebrating great metrics before leakage checks
