from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

InterventionKind = Literal[
    "tree_canopy",
    "cool_roof",
    "green_roof",
    "permeable_surface",
    "water_corridor",
    "traffic_heat_reduction",
]


class ScenarioRequest(BaseModel):
    zone_id: str = Field(min_length=2, max_length=20)
    intervention: InterventionKind
    coverage_fraction: float = Field(ge=0.02, le=0.85)


class PortfolioRequest(BaseModel):
    budget_crore: float = Field(gt=0, le=5000)
    allowed_interventions: list[InterventionKind] | None = None
    max_items_per_zone: int = Field(default=2, ge=1, le=4)


class CityQuery(BaseModel):
    seed: int = Field(default=2026, ge=1, le=10_000_000)
