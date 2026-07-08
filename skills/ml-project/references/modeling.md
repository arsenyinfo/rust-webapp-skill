# Modeling Patterns

## CatBoost

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

## PyTorch Conventions

Device selection, cuda → mps → cpu:

```python
device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
```

- `optimizer.zero_grad(set_to_none=True)`, not plain `zero_grad()`
- Checkpoints are dicts saved to the run dir as `checkpoint_{epoch}.pt` with keys: `epoch`, `model_state_dict`, `optimizer_state_dict`, `loss`
