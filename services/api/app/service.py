from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache

from urban_heat.core import HeatModel, ZoneFeatures
from urban_heat.data import generate_demo_city
from urban_heat.interventions import CATALOG, apply_intervention
from urban_heat.optimizer import optimize_portfolio

RURAL_REFERENCE_C = 31.8


class UrbanHeatService:
    def __init__(self, seed: int = 2026) -> None:
        self.seed = seed
        self.model = HeatModel()
        self.zones = generate_demo_city(seed=seed)
        self.by_id = {zone.zone_id: zone for zone in self.zones}

    def city(self) -> dict[str, object]:
        assessments = [self.model.assess(zone, RURAL_REFERENCE_C) for zone in self.zones]
        hottest = max(
            zip(self.zones, assessments, strict=True),
            key=lambda pair: pair[1].heat_risk_score,
        )
        total_population = sum(assessment.exposed_population for assessment in assessments)
        total_vulnerable = sum(assessment.vulnerable_population for assessment in assessments)
        mean_air = sum(a.predicted_air_temp_c for a in assessments) / len(assessments)
        mean_uhi = sum(a.uhi_intensity_c for a in assessments) / len(assessments)
        return {
            "city": "Delhi demonstration grid",
            "data_status": "synthetic demonstration data",
            "model": self.model.version,
            "rural_reference_c": RURAL_REFERENCE_C,
            "grid": {"rows": 6, "columns": 8},
            "summary": {
                "mean_predicted_air_temp_c": round(mean_air, 2),
                "mean_uhi_intensity_c": round(mean_uhi, 2),
                "heat_exposed_population": total_population,
                "vulnerable_population": total_vulnerable,
                "highest_risk_zone": hottest[0].name,
                "highest_risk_score": hottest[1].heat_risk_score,
            },
            "zones": [
                {"features": asdict(zone), "assessment": assessment.to_dict()}
                for zone, assessment in zip(self.zones, assessments, strict=True)
            ],
        }

    def zone(self, zone_id: str) -> dict[str, object]:
        zone = self._zone(zone_id)
        return {
            "features": asdict(zone),
            "assessment": self.model.assess(zone, RURAL_REFERENCE_C).to_dict(),
        }

    def simulate(self, zone_id: str, intervention: str, coverage: float) -> dict[str, object]:
        zone = self._zone(zone_id)
        template = CATALOG[intervention]
        configured = type(template)(
            kind=template.kind,
            coverage_fraction=coverage,
            unit_cost_crore_per_km2=template.unit_cost_crore_per_km2,
            label=template.label,
        )
        result = apply_intervention(zone, configured, self.model, RURAL_REFERENCE_C)
        return result.to_dict()

    def optimize(
        self,
        budget_crore: float,
        allowed: list[str] | None,
        max_items_per_zone: int,
    ) -> dict[str, object]:
        plan = optimize_portfolio(
            self.zones,
            self.model,
            RURAL_REFERENCE_C,
            budget_crore,
            allowed=allowed,
            max_items_per_zone=max_items_per_zone,
        )
        return plan.to_dict()

    def _zone(self, zone_id: str) -> ZoneFeatures:
        try:
            return self.by_id[zone_id.upper()]
        except KeyError as exc:
            raise KeyError(f"Unknown zone: {zone_id}") from exc


@lru_cache(maxsize=8)
def get_service(seed: int = 2026) -> UrbanHeatService:
    return UrbanHeatService(seed=seed)
