from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split

from .core import HeatModel
from .data import generate_demo_city

FEATURES = (
    "land_surface_temp_c",
    "air_temp_c",
    "humidity_pct",
    "wind_speed_ms",
    "ndvi",
    "ndbi",
    "albedo",
    "impervious_fraction",
    "tree_canopy_fraction",
    "water_fraction",
    "building_density",
    "anthropogenic_heat_wm2",
)


@dataclass(frozen=True, slots=True)
class TrainingReport:
    samples: int
    validation_mae_c: float
    validation_rmse_c: float
    feature_importance: dict[str, float]
    note: str


def build_synthetic_training_set(
    cities: int = 150, seed: int = 2026
) -> tuple[np.ndarray, np.ndarray]:
    rng = Random(seed)
    baseline = HeatModel()
    rows: list[list[float]] = []
    targets: list[float] = []
    for city_idx in range(cities):
        zones = generate_demo_city(seed=seed + city_idx * 17)
        rural_reference = 31.5 + rng.uniform(-1.2, 1.2)
        for zone in zones:
            predicted, _ = baseline.predict_temperature(zone)
            physics_noise = rng.gauss(0, 0.34) + 0.18 * max(0, predicted - rural_reference)
            rows.append([float(getattr(zone, feature)) for feature in FEATURES])
            targets.append(predicted + physics_noise)
    return np.asarray(rows, dtype=float), np.asarray(targets, dtype=float)


def train(output: Path, seed: int = 2026) -> TrainingReport:
    x, y = build_synthetic_training_set(seed=seed)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=seed
    )
    model = HistGradientBoostingRegressor(
        learning_rate=0.07,
        max_iter=180,
        max_leaf_nodes=18,
        l2_regularization=0.4,
        random_state=seed,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    importance = permutation_importance(
        model,
        x_test,
        y_test,
        n_repeats=5,
        random_state=seed,
        scoring="neg_mean_absolute_error",
    )
    normalized = np.maximum(importance.importances_mean, 0)
    normalized = normalized / normalized.sum() if normalized.sum() else normalized
    report = TrainingReport(
        samples=len(x),
        validation_mae_c=round(float(mean_absolute_error(y_test, predictions)), 3),
        validation_rmse_c=round(float(root_mean_squared_error(y_test, predictions)), 3),
        feature_importance={
            feature: round(float(value), 4)
            for feature, value in zip(FEATURES, normalized, strict=True)
        },
        note="Metrics are from synthetic demonstration data and are not field validation.",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return report
