from __future__ import annotations

from urban_heat.core import HeatModel
from urban_heat.data import generate_demo_city
from urban_heat.interventions import CATALOG, apply_intervention


def test_demo_city_is_reproducible() -> None:
    first = generate_demo_city(seed=2026)
    second = generate_demo_city(seed=2026)
    assert first == second
    assert len(first) == 48
    assert {zone.zone_id for zone in first} == {f"Z{i:02d}" for i in range(1, 49)}


def test_assessment_stays_within_operational_bounds() -> None:
    model = HeatModel()
    for zone in generate_demo_city():
        assessment = model.assess(zone, rural_reference_c=31.8)
        assert zone.air_temp_c - 1.2 <= assessment.predicted_air_temp_c <= zone.land_surface_temp_c
        assert 0 <= assessment.heat_risk_score <= 100
        assert 0.7 <= assessment.confidence <= 0.97
        assert assessment.exposed_population >= assessment.vulnerable_population >= 0


def test_each_intervention_has_non_negative_benefit() -> None:
    model = HeatModel()
    zone = max(generate_demo_city(), key=lambda item: model.assess(item, 31.8).heat_risk_score)
    for intervention in CATALOG.values():
        result = apply_intervention(zone, intervention, model, 31.8)
        assert result.cost_crore > 0
        assert result.cooling_c >= 0
        assert result.heat_risk_reduction >= 0
        assert result.protected_population >= 0


def test_cool_roofs_increase_albedo() -> None:
    model = HeatModel()
    zone = generate_demo_city()[18]
    result = apply_intervention(zone, CATALOG["cool_roof"], model, 31.8)
    assert result.updated_zone.albedo > zone.albedo
    assert result.updated_zone.land_surface_temp_c < zone.land_surface_temp_c
