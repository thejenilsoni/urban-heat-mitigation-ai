from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Literal

from .core import HeatAssessment, HeatModel, ZoneFeatures

InterventionKind = Literal[
    "tree_canopy",
    "cool_roof",
    "green_roof",
    "permeable_surface",
    "water_corridor",
    "traffic_heat_reduction",
]


@dataclass(frozen=True, slots=True)
class Intervention:
    kind: InterventionKind
    coverage_fraction: float
    unit_cost_crore_per_km2: float
    label: str


@dataclass(frozen=True, slots=True)
class InterventionResult:
    intervention: Intervention
    before: HeatAssessment
    after: HeatAssessment
    cooling_c: float
    heat_risk_reduction: float
    protected_population: int
    cost_crore: float
    updated_zone: ZoneFeatures

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["updated_zone"] = self.updated_zone.to_dict()
        return payload


CATALOG: dict[InterventionKind, Intervention] = {
    "tree_canopy": Intervention("tree_canopy", 0.15, 8.4, "Street trees and pocket forests"),
    "cool_roof": Intervention("cool_roof", 0.30, 3.2, "High-albedo cool roofs"),
    "green_roof": Intervention("green_roof", 0.18, 9.6, "Green roofs on suitable buildings"),
    "permeable_surface": Intervention(
        "permeable_surface", 0.20, 4.5, "Permeable public-realm surfaces"
    ),
    "water_corridor": Intervention(
        "water_corridor", 0.08, 14.0, "Blue corridor and water retention"
    ),
    "traffic_heat_reduction": Intervention(
        "traffic_heat_reduction",
        0.25,
        2.1,
        "Traffic and waste-heat reduction",
    ),
}


def apply_intervention(
    zone: ZoneFeatures,
    intervention: Intervention,
    model: HeatModel,
    rural_reference_c: float,
) -> InterventionResult:
    coverage = max(0.0, min(0.85, intervention.coverage_fraction))
    updated = _updated_zone(zone, intervention.kind, coverage)
    before = model.assess(zone, rural_reference_c)
    after = model.assess(updated, rural_reference_c)
    cost = zone.area_km2 * coverage * intervention.unit_cost_crore_per_km2
    return InterventionResult(
        intervention=replace(intervention, coverage_fraction=coverage),
        before=before,
        after=after,
        cooling_c=round(before.predicted_air_temp_c - after.predicted_air_temp_c, 2),
        heat_risk_reduction=round(before.heat_risk_score - after.heat_risk_score, 1),
        protected_population=max(0, before.exposed_population - after.exposed_population),
        cost_crore=round(cost, 2),
        updated_zone=updated,
    )


def _updated_zone(zone: ZoneFeatures, kind: InterventionKind, coverage: float) -> ZoneFeatures:
    if kind == "tree_canopy":
        canopy = _clip(zone.tree_canopy_fraction + 0.72 * coverage, 0.0, 0.72)
        ndvi = _clip(zone.ndvi + 0.46 * coverage, -0.2, 0.9)
        impervious = _clip(zone.impervious_fraction - 0.18 * coverage, 0.05, 0.98)
        wind = _clip(zone.wind_speed_ms - 0.08 * coverage, 0.2, 5.0)
        return replace(
            zone,
            tree_canopy_fraction=canopy,
            ndvi=ndvi,
            impervious_fraction=impervious,
            wind_speed_ms=wind,
            land_surface_temp_c=zone.land_surface_temp_c - 2.6 * coverage,
        )
    if kind == "cool_roof":
        return replace(
            zone,
            albedo=_clip(zone.albedo + 0.44 * coverage, 0.08, 0.65),
            land_surface_temp_c=zone.land_surface_temp_c - 3.5 * coverage,
            anthropogenic_heat_wm2=max(
                5.0, zone.anthropogenic_heat_wm2 - 5.5 * coverage
            ),
        )
    if kind == "green_roof":
        return replace(
            zone,
            ndvi=_clip(zone.ndvi + 0.30 * coverage, -0.2, 0.9),
            tree_canopy_fraction=_clip(
                zone.tree_canopy_fraction + 0.20 * coverage, 0.0, 0.75
            ),
            albedo=_clip(zone.albedo + 0.08 * coverage, 0.08, 0.65),
            land_surface_temp_c=zone.land_surface_temp_c - 2.9 * coverage,
        )
    if kind == "permeable_surface":
        return replace(
            zone,
            impervious_fraction=_clip(zone.impervious_fraction - 0.48 * coverage, 0.05, 0.98),
            ndvi=_clip(zone.ndvi + 0.12 * coverage, -0.2, 0.9),
            albedo=_clip(zone.albedo + 0.10 * coverage, 0.08, 0.65),
            land_surface_temp_c=zone.land_surface_temp_c - 1.8 * coverage,
        )
    if kind == "water_corridor":
        return replace(
            zone,
            water_fraction=_clip(zone.water_fraction + 0.65 * coverage, 0.0, 0.40),
            humidity_pct=_clip(zone.humidity_pct + 3.5 * coverage, 20, 85),
            land_surface_temp_c=zone.land_surface_temp_c - 3.4 * coverage,
        )
    if kind == "traffic_heat_reduction":
        return replace(
            zone,
            anthropogenic_heat_wm2=max(
                4.0, zone.anthropogenic_heat_wm2 * (1 - 0.52 * coverage)
            ),
            air_temp_c=zone.air_temp_c - 0.50 * coverage,
            land_surface_temp_c=zone.land_surface_temp_c - 0.65 * coverage,
        )
    raise ValueError(f"Unsupported intervention: {kind}")


def _clip(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))
