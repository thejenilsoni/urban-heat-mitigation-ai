from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from itertools import product
from typing import Iterable

from .core import HeatModel, ZoneFeatures
from .interventions import (
    CATALOG,
    InterventionKind,
    InterventionResult,
    apply_intervention,
)


@dataclass(frozen=True, slots=True)
class PlanItem:
    zone_id: str
    zone_name: str
    intervention: InterventionKind
    coverage_fraction: float
    cooling_c: float
    protected_population: int
    heat_risk_reduction: float
    cost_crore: float
    priority_score: float


@dataclass(frozen=True, slots=True)
class OptimizationPlan:
    budget_crore: float
    committed_crore: float
    expected_mean_cooling_c: float
    expected_protected_population: int
    expected_risk_reduction: float
    items: tuple[PlanItem, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def optimize_portfolio(
    zones: Iterable[ZoneFeatures],
    model: HeatModel,
    rural_reference_c: float,
    budget_crore: float,
    allowed: Iterable[InterventionKind] | None = None,
    max_items_per_zone: int = 2,
) -> OptimizationPlan:
    """Select a transparent, budget-constrained cooling portfolio.

    Candidates are ranked by avoided exposure, risk reduction, cooling, and
    social vulnerability per unit cost. A local diversity constraint limits
    over-concentration in any one zone.
    """

    allowed_kinds = tuple(allowed or CATALOG.keys())
    candidates: list[tuple[float, ZoneFeatures, InterventionResult]] = []
    coverages = (0.10, 0.20, 0.30, 0.40)

    for zone, kind, coverage in product(zones, allowed_kinds, coverages):
        template = CATALOG[kind]
        intervention = replace(template, coverage_fraction=coverage)
        result = apply_intervention(zone, intervention, model, rural_reference_c)
        if result.cooling_c <= 0 or result.cost_crore <= 0:
            continue
        vulnerability_weight = 1.0 + 1.8 * zone.vulnerable_fraction
        population_benefit = result.protected_population / 1000.0
        score = (
            2.8 * result.cooling_c
            + 0.22 * result.heat_risk_reduction
            + 0.15 * population_benefit
        ) * vulnerability_weight / result.cost_crore
        candidates.append((score, zone, result))

    candidates.sort(
        key=lambda item: (
            item[0],
            item[2].protected_population,
            item[2].cooling_c,
        ),
        reverse=True,
    )

    spent = 0.0
    selected: list[PlanItem] = []
    zone_counts: dict[str, int] = {}
    zone_interventions: set[tuple[str, InterventionKind]] = set()

    for score, zone, result in candidates:
        key = (zone.zone_id, result.intervention.kind)
        if key in zone_interventions:
            continue
        if zone_counts.get(zone.zone_id, 0) >= max_items_per_zone:
            continue
        if spent + result.cost_crore > budget_crore + 1e-9:
            continue
        selected.append(
            PlanItem(
                zone_id=zone.zone_id,
                zone_name=zone.name,
                intervention=result.intervention.kind,
                coverage_fraction=result.intervention.coverage_fraction,
                cooling_c=result.cooling_c,
                protected_population=result.protected_population,
                heat_risk_reduction=result.heat_risk_reduction,
                cost_crore=result.cost_crore,
                priority_score=round(score, 3),
            )
        )
        spent += result.cost_crore
        zone_counts[zone.zone_id] = zone_counts.get(zone.zone_id, 0) + 1
        zone_interventions.add(key)

    total_cost = sum(item.cost_crore for item in selected)
    weighted_cooling = sum(item.cooling_c * item.cost_crore for item in selected)
    mean_cooling = weighted_cooling / total_cost if total_cost else 0.0
    return OptimizationPlan(
        budget_crore=round(budget_crore, 2),
        committed_crore=round(total_cost, 2),
        expected_mean_cooling_c=round(mean_cooling, 2),
        expected_protected_population=sum(item.protected_population for item in selected),
        expected_risk_reduction=round(sum(item.heat_risk_reduction for item in selected), 1),
        items=tuple(selected),
    )
