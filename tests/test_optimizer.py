from __future__ import annotations

from urban_heat.core import HeatModel
from urban_heat.data import generate_demo_city
from urban_heat.optimizer import optimize_portfolio


def test_optimizer_respects_budget_and_diversity() -> None:
    plan = optimize_portfolio(generate_demo_city(), HeatModel(), 31.8, budget_crore=75)
    assert 0 < plan.committed_crore <= 75
    assert plan.expected_mean_cooling_c > 0
    assert plan.expected_protected_population >= 0
    counts: dict[str, int] = {}
    for item in plan.items:
        counts[item.zone_id] = counts.get(item.zone_id, 0) + 1
    assert max(counts.values()) <= 2


def test_larger_budget_never_spends_less() -> None:
    zones = generate_demo_city()
    model = HeatModel()
    smaller = optimize_portfolio(zones, model, 31.8, budget_crore=40)
    larger = optimize_portfolio(zones, model, 31.8, budget_crore=100)
    assert larger.committed_crore >= smaller.committed_crore
    assert larger.expected_protected_population >= smaller.expected_protected_population


def test_allowed_interventions_filter() -> None:
    plan = optimize_portfolio(
        generate_demo_city(),
        HeatModel(),
        31.8,
        budget_crore=40,
        allowed=["cool_roof"],
    )
    assert plan.items
    assert {item.intervention for item in plan.items} == {"cool_roof"}
