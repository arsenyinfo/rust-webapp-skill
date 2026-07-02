# Config, Tracking, Logging

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

## Timestamped Run Directories

```python
from datetime import UTC, datetime
from pathlib import Path


def create_run_dir(base: str | Path = "experiments") -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
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

## Memos

Write findings to `memos/` as markdown:

- Hypothesis
- Experiment setup
- Results: tables and key numbers
- Error analysis
- Conclusions and next steps

## Reproducibility

- Seed everything at run start. For numpy, prefer passing an explicit `np.random.default_rng(seed)` over global `np.random.seed`.
- Save config to experiment dir
- Log git commit hash
- Use temporal splits for time-series
- Compare against baseline before claiming improvement
- Save predictions for error analysis

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
