from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .schemas import PortfolioRequest, ScenarioRequest
from .service import get_service

app = FastAPI(
    title="HeatShield Urban Cooling API",
    version="1.0.0",
    description=(
        "Physics-aware urban heat screening, intervention simulation, and "
        "budget-constrained cooling portfolio optimization."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "heatshield-api"}


@app.get("/v1/city")
def city(seed: int = Query(default=2026, ge=1, le=10_000_000)) -> dict[str, object]:
    return get_service(seed).city()


@app.get("/v1/zones/{zone_id}")
def zone(zone_id: str, seed: int = Query(default=2026, ge=1, le=10_000_000)) -> dict[str, object]:
    try:
        return get_service(seed).zone(zone_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/v1/scenarios/simulate")
def simulate(
    request: ScenarioRequest,
    seed: int = Query(default=2026, ge=1, le=10_000_000),
) -> dict[str, object]:
    try:
        return get_service(seed).simulate(
            request.zone_id,
            request.intervention,
            request.coverage_fraction,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/v1/portfolios/optimize")
def optimize(
    request: PortfolioRequest,
    seed: int = Query(default=2026, ge=1, le=10_000_000),
) -> dict[str, object]:
    return get_service(seed).optimize(
        request.budget_crore,
        request.allowed_interventions,
        request.max_items_per_zone,
    )
