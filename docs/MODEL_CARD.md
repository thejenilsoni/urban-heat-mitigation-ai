# Model card

**Name:** HeatShield physics-guided urban heat baseline  
**Version:** `physics-baseline-1.0`  
**Purpose:** hotspot screening, driver attribution, and cooling-scenario comparison

## Intended use

- prototype urban heat assessment;
- relative comparison of zones under a consistent input snapshot;
- transparent demonstration of intervention and optimization workflows;
- baseline against which trained models can be evaluated.

## Out-of-scope use

- real-time public-health warnings;
- engineering design values;
- claims that a specific intervention will cause the reported cooling;
- neighbourhood policy decisions without observed-data calibration;
- individual or household risk assessment.

## Inputs and outputs

The model consumes thermal, meteorological, land-cover, urban-form, population, and vulnerability features. It outputs predicted air temperature, apparent temperature, UHI intensity, heat-risk score, exposure estimates, confidence, and driver contributions.

## Limitations

The bundled city is synthetic. Coefficients encode plausible relationships but are not calibrated to a current Delhi campaign. Intervention transformations are scenario assumptions rather than causal-effect estimates. Vulnerability remains aggregate and contains no protected personal data.

## Required production validation

- geographically and temporally held-out observations;
- comparison against statistical and remote-sensing baselines;
- uncertainty and calibration analysis;
- subgroup and spatial-equity review;
- intervention-effect validation using measured before/after studies;
- independent domain and public-health review.
