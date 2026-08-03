from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ZoneFeatures:
    zone_id: str
    name: str
    row: int
    column: int
    area_km2: float
    land_surface_temp_c: float
    air_temp_c: float
    humidity_pct: float
    wind_speed_ms: float
    ndvi: float
    ndbi: float
    albedo: float
    impervious_fraction: float
    tree_canopy_fraction: float
    water_fraction: float
    building_density: float
    anthropogenic_heat_wm2: float
    population_density_km2: float
    vulnerable_fraction: float

    def to_dict(self) -> dict[str, float | str | int]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class HeatAssessment:
    zone_id: str
    predicted_air_temp_c: float
    heat_index_c: float
    uhi_intensity_c: float
    heat_risk_score: float
    exposed_population: int
    vulnerable_population: int
    confidence: float
    driver_contributions: Mapping[str, float]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class HeatModel:
    """Interpretable physics-guided baseline for urban heat screening.

    The model is intentionally lightweight so the complete application remains
    operational without a bundled proprietary checkpoint. Coefficients encode
    physically plausible directions and can be replaced by fitted parameters
    through the training pipeline.
    """

    version = "physics-baseline-1.0"

    def __init__(self, coefficients: Mapping[str, float] | None = None) -> None:
        defaults = {
            "intercept": 5.15,
            "land_surface_temp_c": 0.54,
            "air_temp_c": 0.42,
            "humidity_pct": 0.018,
            "wind_speed_ms": -0.46,
            "ndvi": -2.45,
            "ndbi": 1.72,
            "albedo": -2.85,
            "impervious_fraction": 2.18,
            "tree_canopy_fraction": -2.70,
            "water_fraction": -1.85,
            "building_density": 0.92,
            "anthropogenic_heat_wm2": 0.018,
        }
        self.coefficients = {**defaults, **(coefficients or {})}

    def predict_temperature(self, zone: ZoneFeatures) -> tuple[float, dict[str, float]]:
        c = self.coefficients
        terms = {
            "surface heating": c["land_surface_temp_c"] * zone.land_surface_temp_c,
            "background air": c["air_temp_c"] * zone.air_temp_c,
            "humidity": c["humidity_pct"] * zone.humidity_pct,
            "ventilation": c["wind_speed_ms"] * zone.wind_speed_ms,
            "vegetation": c["ndvi"] * zone.ndvi
            + c["tree_canopy_fraction"] * zone.tree_canopy_fraction,
            "built form": c["ndbi"] * zone.ndbi
            + c["impervious_fraction"] * zone.impervious_fraction
            + c["building_density"] * zone.building_density,
            "surface reflectance": c["albedo"] * zone.albedo,
            "blue infrastructure": c["water_fraction"] * zone.water_fraction,
            "anthropogenic heat": c["anthropogenic_heat_wm2"]
            * zone.anthropogenic_heat_wm2,
        }
        prediction = c["intercept"] + sum(terms.values())
        prediction = max(zone.air_temp_c - 1.2, min(zone.land_surface_temp_c - 0.3, prediction))
        return round(prediction, 2), {k: round(v, 3) for k, v in terms.items()}

    @staticmethod
    def apparent_temperature(temp_c: float, humidity_pct: float, wind_ms: float) -> float:
        vapor_pressure = (humidity_pct / 100.0) * 6.105 * exp(
            17.27 * temp_c / (237.7 + temp_c)
        )
        apparent = temp_c + 0.33 * vapor_pressure - 0.70 * wind_ms - 4.0
        return round(apparent, 2)

    @staticmethod
    def confidence(zone: ZoneFeatures) -> float:
        coverage = 1.0
        if zone.wind_speed_ms < 0.2:
            coverage -= 0.05
        if zone.ndvi < -0.15 or zone.ndvi > 0.9:
            coverage -= 0.06
        if zone.albedo < 0.05 or zone.albedo > 0.65:
            coverage -= 0.06
        if zone.land_surface_temp_c - zone.air_temp_c > 18:
            coverage -= 0.05
        return round(max(0.70, min(0.97, coverage)), 2)

    def assess(self, zone: ZoneFeatures, rural_reference_c: float) -> HeatAssessment:
        predicted, contributions = self.predict_temperature(zone)
        heat_index = self.apparent_temperature(
            predicted, zone.humidity_pct, zone.wind_speed_ms
        )
        uhi = max(0.0, predicted - rural_reference_c)
        population = int(zone.population_density_km2 * zone.area_km2)
        vulnerability = population * zone.vulnerable_fraction
        thermal = _sigmoid((heat_index - 35.0) / 3.2)
        morphology = 0.55 * zone.impervious_fraction + 0.45 * zone.building_density
        social = zone.vulnerable_fraction
        risk = 100.0 * (0.62 * thermal + 0.22 * morphology + 0.16 * social)
        return HeatAssessment(
            zone_id=zone.zone_id,
            predicted_air_temp_c=predicted,
            heat_index_c=heat_index,
            uhi_intensity_c=round(uhi, 2),
            heat_risk_score=round(max(0.0, min(100.0, risk)), 1),
            exposed_population=population if heat_index >= 38 else int(population * thermal),
            vulnerable_population=int(vulnerability * max(0.35, thermal)),
            confidence=self.confidence(zone),
            driver_contributions=contributions,
        )


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-value))
