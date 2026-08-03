# API reference

The interactive OpenAPI explorer is available at `http://localhost:8000/docs`.

## Endpoints

- `GET /health` — service health.
- `GET /v1/city?seed=2026` — complete city assessment and summary.
- `GET /v1/zones/{zone_id}` — one zone with features and heat assessment.
- `POST /v1/scenarios/simulate` — run one cooling intervention.
- `POST /v1/portfolios/optimize` — allocate a budget across city zones.

## Scenario example

```json
{
  "zone_id": "Z30",
  "intervention": "tree_canopy",
  "coverage_fraction": 0.25
}
```

## Portfolio example

```json
{
  "budget_crore": 75,
  "allowed_interventions": ["tree_canopy", "cool_roof", "permeable_surface"],
  "max_items_per_zone": 2
}
```

The `seed` query parameter exists for deterministic demonstration datasets. A production deployment should replace it with an immutable observed-data snapshot identifier.
