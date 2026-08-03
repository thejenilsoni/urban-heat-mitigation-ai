from __future__ import annotations

from dataclasses import asdict
from math import sin
from random import Random

from .core import ZoneFeatures


def generate_demo_city(rows: int = 6, columns: int = 8, seed: int = 2026) -> list[ZoneFeatures]:
    """Generate a reproducible Delhi-inspired demonstration grid.

    The data is synthetic and carries no claim of representing current observed
    conditions. Spatial gradients mimic common urban patterns: a dense hot core,
    lower vegetation in industrial zones, and stronger blue-green cooling near
    the river corridor and peripheral parks.
    """

    rng = Random(seed)
    zones: list[ZoneFeatures] = []
    center_r = (rows - 1) / 2
    center_c = (columns - 1) / 2
    names = [
        "Ridge Edge", "University", "Civil Lines", "Old City", "River East", "Mayur Vihar",
        "Noida Link", "Wetland Edge", "West Enclave", "Central Market", "Karol Bagh",
        "Civic Core", "ITO District", "Yamuna Bank", "East Delhi", "Green Belt",
        "Industrial West", "Pusa Campus", "Connaught Core", "Government District",
        "Pragati Maidan", "River Commons", "Residential East", "Transit Edge",
        "Dwarka North", "Airport Edge", "South Extension", "Lodhi District",
        "Defence Colony", "Okhla Industrial", "Jasola", "Floodplain South",
        "Dwarka South", "Vasant Kunj", "Mehrauli", "Saket", "Tughlakabad",
        "Badarpur", "Eco Park", "River South", "Peripheral West", "Aravalli Edge",
        "South Campus", "Green Reserve", "Urban Village", "Logistics South",
        "Peri-urban East", "Agricultural Edge",
    ]

    for row in range(rows):
        for column in range(columns):
            idx = row * columns + column
            radial = (((row - center_r) / max(1, center_r)) ** 2 + ((column - center_c) / max(1, center_c)) ** 2) ** 0.5
            core = max(0.0, 1.0 - radial / 1.45)
            river = max(0.0, 1.0 - abs(column - 4.75) / 1.35)
            ridge = max(0.0, 1.0 - abs(column - 0.4) / 1.5) * max(0.0, 1.0 - row / 5.5)
            industrial = 1.0 if (row, column) in {(2, 0), (2, 7), (3, 5), (4, 5)} else 0.0
            green = max(ridge, 0.65 if (row, column) in {(0, 0), (0, 1), (3, 3), (4, 2), (5, 3)} else 0.0)
            water = max(0.0, river * (0.09 + 0.08 * (1.0 - core)))
            tree = _clip(0.10 + 0.24 * green + 0.08 * (1.0 - core) - 0.05 * industrial + rng.uniform(-0.025, 0.025), 0.03, 0.46)
            impervious = _clip(0.42 + 0.40 * core + 0.20 * industrial - 0.20 * green - 0.12 * river + rng.uniform(-0.035, 0.035), 0.22, 0.94)
            ndvi = _clip(0.06 + 0.78 * tree + 0.42 * water - 0.24 * industrial + rng.uniform(-0.025, 0.025), -0.05, 0.72)
            ndbi = _clip(0.05 + 0.54 * impervious + 0.18 * industrial - 0.30 * tree + rng.uniform(-0.025, 0.025), -0.08, 0.65)
            albedo = _clip(0.13 + 0.07 * (1.0 - core) + 0.04 * industrial + rng.uniform(-0.012, 0.012), 0.10, 0.30)
            building = _clip(0.28 + 0.60 * core + 0.16 * industrial - 0.16 * green + rng.uniform(-0.03, 0.03), 0.14, 0.96)
            anthropogenic = 22 + 42 * core + 24 * industrial + rng.uniform(-4, 4)
            air_temp = 34.2 + 2.7 * core + 1.0 * industrial - 1.1 * green - 0.7 * river + rng.uniform(-0.35, 0.35)
            lst = air_temp + 4.8 + 4.7 * impervious + 2.4 * industrial - 3.2 * tree - 2.0 * water + rng.uniform(-0.55, 0.55)
            humidity = _clip(43 + 10 * river + 5 * water - 4 * industrial + rng.uniform(-2, 2), 32, 68)
            wind = _clip(1.1 + 1.15 * (1 - building) + 0.35 * river + rng.uniform(-0.18, 0.18), 0.45, 3.2)
            pop_density = 5200 + 22500 * core + 4200 * sin((idx + 3) * 0.47) + rng.uniform(-900, 900)
            vulnerable = _clip(0.16 + 0.12 * (1 - core) + 0.05 * industrial + rng.uniform(-0.018, 0.018), 0.12, 0.39)
            zones.append(
                ZoneFeatures(
                    zone_id=f"Z{idx + 1:02d}",
                    name=names[idx] if idx < len(names) else f"Zone {idx + 1}",
                    row=row,
                    column=column,
                    area_km2=round(rng.uniform(1.4, 3.8), 2),
                    land_surface_temp_c=round(lst, 2),
                    air_temp_c=round(air_temp, 2),
                    humidity_pct=round(humidity, 1),
                    wind_speed_ms=round(wind, 2),
                    ndvi=round(ndvi, 3),
                    ndbi=round(ndbi, 3),
                    albedo=round(albedo, 3),
                    impervious_fraction=round(impervious, 3),
                    tree_canopy_fraction=round(tree, 3),
                    water_fraction=round(water, 3),
                    building_density=round(building, 3),
                    anthropogenic_heat_wm2=round(anthropogenic, 1),
                    population_density_km2=round(max(2800, pop_density), 0),
                    vulnerable_fraction=round(vulnerable, 3),
                )
            )
    return zones


def city_payload(seed: int = 2026) -> dict[str, object]:
    return {
        "city": "Delhi demonstration grid",
        "data_status": "synthetic demonstration data",
        "seed": seed,
        "grid": {"rows": 6, "columns": 8},
        "zones": [asdict(zone) for zone in generate_demo_city(seed=seed)],
    }


def _clip(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))
