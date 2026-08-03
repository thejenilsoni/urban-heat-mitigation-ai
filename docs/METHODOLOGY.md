# Methodology

## 1. Heat hotspot identification

Each zone combines land-surface temperature, near-surface air temperature, humidity, wind, vegetation, built-up intensity, albedo, imperviousness, tree canopy, water fraction, building density, and anthropogenic waste heat. The baseline constrains predicted air temperature to physically plausible bounds relative to input air and surface temperatures.

Apparent temperature is derived from predicted air temperature, humidity, and wind. Urban heat-island intensity is measured against a configurable rural reference. A composite risk score combines thermal stress, urban morphology, and social vulnerability.

## 2. Explainability

The deterministic baseline exposes the signed contribution of each heat driver. The interface reports dominant positive drivers for a selected zone. A trained production model should add model-specific explanations while retaining physics and monotonicity checks.

## 3. Cooling scenarios

| Intervention | Main modeled changes |
| --- | --- |
| Tree canopy | canopy and NDVI increase; imperviousness and LST decrease |
| Cool roofs | albedo increases; LST and cooling-related waste heat decrease |
| Green roofs | vegetation and albedo increase; roof-surface heating decreases |
| Permeable surfaces | imperviousness decreases; vegetation and reflectance rise |
| Blue corridors | water fraction rises; evaporative cooling lowers LST |
| Waste-heat reduction | anthropogenic heat and local temperature inputs decrease |

The model is rerun after each transformation. Reported temperature reduction, heat-risk reduction, protected population, and indicative cost are differences between baseline and scenario assessments.

## 4. Portfolio optimization

The optimizer enumerates intervention type and coverage candidates for every zone. Candidate utility combines local cooling, heat-risk reduction, avoided population exposure, social-vulnerability weighting, and intervention cost. A deterministic greedy allocator selects the highest benefit-per-cost options while respecting total budget and a diversity limit of two interventions per zone.

## 5. Evaluation protocol

A competition-grade evaluation should report temperature MAE, RMSE, and bias against held-out stations; hotspot precision, recall, F1, and spatial intersection-over-union; uncertainty coverage; cross-city and cross-season generalization; cooling-effect error against measured interventions; optimization sensitivity; and end-to-end latency.

Spatial leakage must be prevented by splitting entire locations and time periods, not random neighboring pixels. Synthetic metrics must always be labelled separately from field validation.
