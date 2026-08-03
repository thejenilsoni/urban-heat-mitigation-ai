# Data integration guide

## Bundled demonstration data

The fixed-seed generator produces 48 synthetic zones so every workflow is reproducible. Generated output must not be represented as observed Delhi temperature or population data.

```bash
PYTHONPATH=ml python scripts/generate_demo_data.py
```

## Recommended observed-data categories

| Category | Typical variables | Processing requirement |
| --- | --- | --- |
| Thermal remote sensing | LST, emissivity, cloud mask | atmospheric correction, temporal compositing |
| Multispectral land cover | NDVI, NDBI, NDWI, albedo | harmonized projection and resolution |
| Meteorology | air temperature, humidity, wind, radiation | station quality control and interpolation |
| Urban morphology | buildings, height, density, roads, imperviousness | vector/raster aggregation by zone |
| Blue-green assets | canopy, parks, water, soil permeability | seasonal and maintenance-aware inventory |
| Human exposure | population, age, health and socioeconomic vulnerability | privacy-preserving zonal aggregation |
| Intervention economics | capex, maintenance, suitability, land ownership | local authority validation |

## Canonical zone schema

The Python `ZoneFeatures` dataclass is the authoritative feature contract. Fractions use 0–1, temperature uses degrees Celsius, area uses square kilometres, population density uses people per square kilometre, wind uses metres per second, and anthropogenic heat uses watts per square metre.

## Reproducibility and provenance

Every production record should carry source, acquisition time, processing version, quality flags, spatial resolution, and licence metadata. Model outputs should preserve the input snapshot identifier so a scenario can be reconstructed and audited later.
