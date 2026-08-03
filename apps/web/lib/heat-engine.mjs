const names = [
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
];

export const interventionCatalog = {
  tree_canopy: { label: "Tree canopy", short: "Trees", cost: 8.4, accent: "leaf" },
  cool_roof: { label: "Cool roofs", short: "Roofs", cost: 3.2, accent: "roof" },
  green_roof: { label: "Green roofs", short: "Green roof", cost: 9.6, accent: "green" },
  permeable_surface: { label: "Permeable surfaces", short: "Permeable", cost: 4.5, accent: "water" },
  water_corridor: { label: "Blue corridors", short: "Blue", cost: 14, accent: "blue" },
  traffic_heat_reduction: { label: "Waste-heat reduction", short: "Waste heat", cost: 2.1, accent: "traffic" },
};

function seeded(index, salt = 0) {
  const value = Math.sin((index + 1) * 12.9898 + salt * 78.233) * 43758.5453;
  return value - Math.floor(value);
}

function clip(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function buildDemoCity() {
  const zones = [];
  const rows = 6;
  const columns = 8;
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const idx = row * columns + column;
      const radial = Math.sqrt(((row - 2.5) / 2.5) ** 2 + ((column - 3.5) / 3.5) ** 2);
      const core = Math.max(0, 1 - radial / 1.45);
      const river = Math.max(0, 1 - Math.abs(column - 4.75) / 1.35);
      const ridge = Math.max(0, 1 - Math.abs(column - 0.4) / 1.5) * Math.max(0, 1 - row / 5.5);
      const industrial = [[2, 0], [2, 7], [3, 5], [4, 5]].some(([r, c]) => r === row && c === column) ? 1 : 0;
      const park = [[0, 0], [0, 1], [3, 3], [4, 2], [5, 3]].some(([r, c]) => r === row && c === column) ? 0.65 : 0;
      const green = Math.max(ridge, park);
      const water = Math.max(0, river * (0.09 + 0.08 * (1 - core)));
      const tree = clip(0.10 + 0.24 * green + 0.08 * (1 - core) - 0.05 * industrial + (seeded(idx, 1) - 0.5) * 0.05, 0.03, 0.46);
      const impervious = clip(0.42 + 0.40 * core + 0.20 * industrial - 0.20 * green - 0.12 * river + (seeded(idx, 2) - 0.5) * 0.07, 0.22, 0.94);
      const ndvi = clip(0.06 + 0.78 * tree + 0.42 * water - 0.24 * industrial + (seeded(idx, 3) - 0.5) * 0.05, -0.05, 0.72);
      const ndbi = clip(0.05 + 0.54 * impervious + 0.18 * industrial - 0.30 * tree + (seeded(idx, 4) - 0.5) * 0.05, -0.08, 0.65);
      const albedo = clip(0.13 + 0.07 * (1 - core) + 0.04 * industrial + (seeded(idx, 5) - 0.5) * 0.024, 0.10, 0.30);
      const building = clip(0.28 + 0.60 * core + 0.16 * industrial - 0.16 * green + (seeded(idx, 6) - 0.5) * 0.06, 0.14, 0.96);
      const anthropogenic = 22 + 42 * core + 24 * industrial + (seeded(idx, 7) - 0.5) * 8;
      const airTemp = 34.2 + 2.7 * core + industrial - 1.1 * green - 0.7 * river + (seeded(idx, 8) - 0.5) * 0.7;
      const lst = airTemp + 4.8 + 4.7 * impervious + 2.4 * industrial - 3.2 * tree - 2 * water + (seeded(idx, 9) - 0.5) * 1.1;
      const humidity = clip(43 + 10 * river + 5 * water - 4 * industrial + (seeded(idx, 10) - 0.5) * 4, 32, 68);
      const wind = clip(1.1 + 1.15 * (1 - building) + 0.35 * river + (seeded(idx, 11) - 0.5) * 0.36, 0.45, 3.2);
      const populationDensity = Math.max(2800, 5200 + 22500 * core + 4200 * Math.sin((idx + 3) * 0.47) + (seeded(idx, 12) - 0.5) * 1800);
      const vulnerableFraction = clip(0.16 + 0.12 * (1 - core) + 0.05 * industrial + (seeded(idx, 13) - 0.5) * 0.036, 0.12, 0.39);
      zones.push({
        id: `Z${String(idx + 1).padStart(2, "0")}`,
        name: names[idx], row, column,
        area: 1.4 + seeded(idx, 14) * 2.4,
        lst, airTemp, humidity, wind, ndvi, ndbi, albedo, impervious, tree,
        water, building, anthropogenic, populationDensity, vulnerableFraction,
      });
    }
  }
  return zones.map((zone) => ({ ...zone, assessment: assessZone(zone) }));
}

export function assessZone(zone) {
  const contributions = {
    "Surface heating": 0.54 * zone.lst,
    "Background air": 0.42 * zone.airTemp,
    "Humidity": 0.018 * zone.humidity,
    "Ventilation": -0.46 * zone.wind,
    "Vegetation": -2.45 * zone.ndvi - 2.70 * zone.tree,
    "Built form": 1.72 * zone.ndbi + 2.18 * zone.impervious + 0.92 * zone.building,
    "Reflectance": -2.85 * zone.albedo,
    "Blue infrastructure": -1.85 * zone.water,
    "Anthropogenic heat": 0.018 * zone.anthropogenic,
  };
  let predicted = 5.15 + Object.values(contributions).reduce((sum, value) => sum + value, 0);
  predicted = clip(predicted, zone.airTemp - 1.2, zone.lst - 0.3);
  const vaporPressure = (zone.humidity / 100) * 6.105 * Math.exp((17.27 * predicted) / (237.7 + predicted));
  const heatIndex = predicted + 0.33 * vaporPressure - 0.70 * zone.wind - 4;
  const thermal = 1 / (1 + Math.exp(-(heatIndex - 35) / 3.2));
  const morphology = 0.55 * zone.impervious + 0.45 * zone.building;
  const risk = clip(100 * (0.62 * thermal + 0.22 * morphology + 0.16 * zone.vulnerableFraction), 0, 100);
  const population = Math.round(zone.populationDensity * zone.area);
  return {
    predicted: round(predicted), heatIndex: round(heatIndex), uhi: round(Math.max(0, predicted - 31.8)),
    risk: round(risk, 1), exposed: heatIndex >= 38 ? population : Math.round(population * thermal),
    vulnerable: Math.round(population * zone.vulnerableFraction * Math.max(0.35, thermal)),
    confidence: 0.94, contributions,
  };
}

export function simulateZone(zoneWithAssessment, kind, coverage) {
  const zone = { ...zoneWithAssessment };
  delete zone.assessment;
  const c = clip(coverage, 0.02, 0.85);
  if (kind === "tree_canopy") {
    zone.tree = clip(zone.tree + 0.72 * c, 0, 0.72); zone.ndvi = clip(zone.ndvi + 0.46 * c, -0.2, 0.9);
    zone.impervious = clip(zone.impervious - 0.18 * c, 0.05, 0.98); zone.lst -= 2.6 * c;
  } else if (kind === "cool_roof") {
    zone.albedo = clip(zone.albedo + 0.44 * c, 0.08, 0.65); zone.lst -= 3.5 * c; zone.anthropogenic -= 5.5 * c;
  } else if (kind === "green_roof") {
    zone.ndvi = clip(zone.ndvi + 0.30 * c, -0.2, 0.9); zone.tree = clip(zone.tree + 0.20 * c, 0, 0.75);
    zone.albedo = clip(zone.albedo + 0.08 * c, 0.08, 0.65); zone.lst -= 2.9 * c;
  } else if (kind === "permeable_surface") {
    zone.impervious = clip(zone.impervious - 0.48 * c, 0.05, 0.98); zone.ndvi = clip(zone.ndvi + 0.12 * c, -0.2, 0.9);
    zone.albedo = clip(zone.albedo + 0.10 * c, 0.08, 0.65); zone.lst -= 1.8 * c;
  } else if (kind === "water_corridor") {
    zone.water = clip(zone.water + 0.65 * c, 0, 0.4); zone.humidity = clip(zone.humidity + 3.5 * c, 20, 85); zone.lst -= 3.4 * c;
  } else if (kind === "traffic_heat_reduction") {
    zone.anthropogenic = Math.max(4, zone.anthropogenic * (1 - 0.52 * c)); zone.airTemp -= 0.5 * c; zone.lst -= 0.65 * c;
  }
  const after = assessZone(zone);
  const before = zoneWithAssessment.assessment;
  const cost = zone.area * c * interventionCatalog[kind].cost;
  return {
    zone, before, after, kind, coverage: c, cost: round(cost), cooling: round(before.predicted - after.predicted),
    riskReduction: round(before.risk - after.risk, 1), protected: Math.max(0, before.exposed - after.exposed),
  };
}

export function optimizePortfolio(zones, budget, enabledKinds = Object.keys(interventionCatalog)) {
  const candidates = [];
  for (const zone of zones) {
    for (const kind of enabledKinds) {
      for (const coverage of [0.1, 0.2, 0.3, 0.4]) {
        const result = simulateZone(zone, kind, coverage);
        if (result.cooling <= 0 || result.cost <= 0) continue;
        const score = (2.8 * result.cooling + 0.22 * result.riskReduction + 0.15 * (result.protected / 1000)) * (1 + 1.8 * zone.vulnerableFraction) / result.cost;
        candidates.push({ ...result, score });
      }
    }
  }
  candidates.sort((a, b) => b.score - a.score || b.protected - a.protected);
  const selected = [];
  const zoneCount = new Map();
  const selectedKey = new Set();
  let spent = 0;
  for (const candidate of candidates) {
    const key = `${candidate.zone.id}:${candidate.kind}`;
    if (selectedKey.has(key) || (zoneCount.get(candidate.zone.id) || 0) >= 2) continue;
    if (spent + candidate.cost > budget) continue;
    selected.push(candidate); spent += candidate.cost; selectedKey.add(key);
    zoneCount.set(candidate.zone.id, (zoneCount.get(candidate.zone.id) || 0) + 1);
  }
  const weightedCooling = selected.reduce((sum, item) => sum + item.cooling * item.cost, 0);
  return {
    items: selected,
    spent: round(spent),
    cooling: spent ? round(weightedCooling / spent) : 0,
    protected: selected.reduce((sum, item) => sum + item.protected, 0),
    riskReduction: round(selected.reduce((sum, item) => sum + item.riskReduction, 0), 1),
  };
}

export function citySummary(zones) {
  const mean = (key) => zones.reduce((sum, zone) => sum + zone.assessment[key], 0) / zones.length;
  return {
    predicted: round(mean("predicted")), uhi: round(mean("uhi")),
    exposed: zones.reduce((sum, zone) => sum + zone.assessment.exposed, 0),
    vulnerable: zones.reduce((sum, zone) => sum + zone.assessment.vulnerable, 0),
    highRisk: zones.filter((zone) => zone.assessment.risk >= 70).length,
  };
}

function round(value, digits = 2) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}
