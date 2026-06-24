from pathlib import Path

from fedcourtsai.registry import enabled_predictors, load_predictors


def test_loads_repo_predictors() -> None:
    cfg = Path("config/predictors.yaml")
    preds = load_predictors(cfg)
    assert preds, "expected at least one predictor configured"
    ids = {p.id for p in preds}
    assert "claude-baseline" in ids
    assert all(Path(p.prompt).exists() for p in enabled_predictors(cfg))
