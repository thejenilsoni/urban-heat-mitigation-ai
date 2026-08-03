"use client";

import { useMemo, useState, type CSSProperties } from "react";
import {
  buildDemoCity,
  citySummary,
  interventionCatalog,
  optimizePortfolio,
  simulateZone,
  type InterventionKind,
  type Zone,
} from "@/lib/heat-engine.mjs";

type Layer = "risk" | "temperature" | "canopy" | "vulnerability";
const interventions = Object.keys(interventionCatalog) as InterventionKind[];
const number = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });

export function HeatCommandCenter() {
  const zones = useMemo(() => buildDemoCity(), []);
  const [selectedId, setSelectedId] = useState("Z30");
  const [layer, setLayer] = useState<Layer>("risk");
  const [kind, setKind] = useState<InterventionKind>("tree_canopy");
  const [coverage, setCoverage] = useState(25);
  const [budget, setBudget] = useState(75);
  const [mode, setMode] = useState<"scenario" | "portfolio">("scenario");

  const selected = zones.find((zone) => zone.id === selectedId) ?? zones[0];
  const summary = useMemo(() => citySummary(zones), [zones]);
  const scenario = useMemo(
    () => simulateZone(selected, kind, coverage / 100),
    [selected, kind, coverage],
  );
  const portfolio = useMemo(() => optimizePortfolio(zones, budget), [zones, budget]);
  const hotspots = useMemo(
    () => [...zones].sort((a, b) => b.assessment.risk - a.assessment.risk).slice(0, 6),
    [zones],
  );
  const drivers = Object.entries(selected.assessment.contributions)
    .filter(([, value]) => value > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <div className="shell">
      <aside className="rail">
        <div className="logo">H<i /></div>
        <nav>{["Overview", "Map", "Scenarios", "Portfolio", "Reports"].map((item, index) => <button className={index === 0 ? "active" : ""} key={item} title={item}>{item.slice(0, 1)}</button>)}</nav>
        <div className="spacer" /><div className="avatar">JS</div>
      </aside>

      <main>
        <header>
          <div><p><span /> URBAN CLIMATE OPERATIONS</p><h1>HeatShield Command Center</h1></div>
          <div className="status">Synthetic demo city · 48 zones</div>
        </header>

        <section className="content">
          <div className="study-bar">
            <div><small>ACTIVE STUDY AREA</small><strong>Delhi metropolitan demonstration grid</strong><span>Physics-guided screening · peak summer afternoon</span></div>
            <div><small>RURAL REFERENCE</small><strong>31.8°C</strong></div>
            <div><small>MODEL</small><strong>Interpretable baseline</strong></div>
          </div>

          <div className="metrics">
            <Metric label="Mean predicted air" value={`${summary.predicted.toFixed(1)}°C`} detail="city-wide modeled" />
            <Metric label="Mean UHI intensity" value={`+${summary.uhi.toFixed(1)}°C`} detail="above rural reference" />
            <Metric label="Heat-exposed people" value={compact(summary.exposed)} detail={`${compact(summary.vulnerable)} vulnerable`} />
            <Metric label="Critical zones" value={String(summary.highRisk)} detail="risk score ≥ 70" />
          </div>

          <div className="map-layout">
            <section className="panel map-panel">
              <div className="panel-head"><div><small>SPATIAL INTELLIGENCE</small><h2>Urban heat risk surface</h2></div><div className="layers">{(["risk", "temperature", "canopy", "vulnerability"] as Layer[]).map((item) => <button className={layer === item ? "active" : ""} onClick={() => setLayer(item)} key={item}>{item}</button>)}</div></div>
              <div className="map-stage">
                <div className="map-grid">{zones.map((zone) => <button key={zone.id} className={selected.id === zone.id ? "zone selected" : "zone"} style={{ "--zone": zoneColor(zone, layer) } as CSSProperties} onClick={() => setSelectedId(zone.id)} title={`${zone.name}: ${layerValue(zone, layer)}`}><span>{zone.id}</span>{zone.water > 0.08 && <i />}</button>)}</div>
                <div className="confidence"><small>MODEL CONFIDENCE</small><strong>94%</strong></div>
                <div className="legend"><span>Lower</span><i /><span>Higher</span></div>
              </div>
              <footer><span>● Surface temperature</span><span>● Land cover</span><span>● Population vulnerability</span><em>Demonstration data, not current observations</em></footer>
            </section>

            <aside className="panel zone-panel">
              <div className="zone-title"><div className="zone-code">{selected.id}</div><div><small>SELECTED ZONE</small><h2>{selected.name}</h2><span>{selected.area.toFixed(1)} km² analysis area</span></div><b>{riskBand(selected.assessment.risk)} risk</b></div>
              <div className="risk-row"><div className="ring" style={{ "--score": `${selected.assessment.risk * 3.6}deg` } as CSSProperties}><div><strong>{Math.round(selected.assessment.risk)}</strong><span>/100</span></div></div><div><small>HEAT RISK SCORE</small><strong>{selected.assessment.heatIndex.toFixed(1)}°C apparent</strong><span>{selected.assessment.confidence * 100}% confidence</span></div></div>
              <div className="zone-stats"><Stat label="Predicted air" value={`${selected.assessment.predicted.toFixed(1)}°C`} /><Stat label="Surface temp" value={`${selected.lst.toFixed(1)}°C`} /><Stat label="UHI intensity" value={`+${selected.assessment.uhi.toFixed(1)}°C`} /><Stat label="Exposed" value={number.format(selected.assessment.exposed)} /></div>
              <h3>Dominant heat drivers</h3>
              <div className="drivers">{drivers.map(([name, value], index) => <div key={name}><span><b>{index + 1}</b>{name}</span><strong>{value.toFixed(1)}</strong><i><em style={{ width: `${Math.min(100, value * 3)}%` }} /></i></div>)}</div>
              <div className="cover"><Gauge label="Tree canopy" value={selected.tree} /><Gauge label="Impervious" value={selected.impervious} /><Gauge label="Albedo" value={selected.albedo} /></div>
            </aside>
          </div>

          <div className="planning-layout">
            <section className="panel planning-panel">
              <div className="panel-head"><div><small>COOLING STRATEGY LAB</small><h2>Mitigation planner</h2></div><div className="tabs"><button className={mode === "scenario" ? "active" : ""} onClick={() => setMode("scenario")}>Zone scenario</button><button className={mode === "portfolio" ? "active" : ""} onClick={() => setMode("portfolio")}>City portfolio</button></div></div>
              {mode === "scenario" ? <div className="scenario"><div className="controls"><label>Intervention</label><div className="interventions">{interventions.map((item) => <button className={kind === item ? "active" : ""} onClick={() => setKind(item)} key={item}>{interventionCatalog[item].short}</button>)}</div><div className="range-head"><label htmlFor="coverage">Implementation coverage</label><strong>{coverage}%</strong></div><input id="coverage" type="range" min="5" max="60" step="5" value={coverage} onChange={(event) => setCoverage(Number(event.target.value))} /><p className="note">Surface and morphology indicators are modified before the same heat model is rerun.</p></div><div className="result"><small>EXPECTED LOCAL COOLING</small><strong>-{scenario.cooling.toFixed(2)}°C</strong><span>{scenario.before.predicted.toFixed(1)}°C → {scenario.after.predicted.toFixed(1)}°C</span><div className="impact"><Stat label="People protected" value={number.format(scenario.protected)} /><Stat label="Indicative cost" value={`₹${scenario.cost.toFixed(1)} Cr`} /><Stat label="Risk reduction" value={`-${scenario.riskReduction.toFixed(1)} pts`} /></div></div></div> : <div className="portfolio"><div className="controls"><div className="range-head"><label htmlFor="budget">Available capital budget</label><strong>₹{budget} Cr</strong></div><input id="budget" type="range" min="20" max="250" step="5" value={budget} onChange={(event) => setBudget(Number(event.target.value))} /><div className="portfolio-metrics"><Stat label="Committed" value={`₹${portfolio.spent.toFixed(1)} Cr`} /><Stat label="Mean cooling" value={`${portfolio.cooling.toFixed(2)}°C`} /><Stat label="Protected" value={compact(portfolio.protected)} /></div></div><div className="portfolio-list">{portfolio.items.slice(0, 6).map((item, index) => <div key={`${item.zone.id}-${item.kind}`}><b>{index + 1}</b><span><strong>{item.zone.name}</strong><small>{interventionCatalog[item.kind].label} · {Math.round(item.coverage * 100)}%</small></span><em>-{item.cooling.toFixed(2)}°C</em><small>₹{item.cost.toFixed(1)} Cr</small></div>)}</div></div>}
            </section>

            <section className="panel hotspots"><div className="panel-head"><div><small>PRIORITY WATCHLIST</small><h2>Highest-risk zones</h2></div></div>{hotspots.map((zone) => <button onClick={() => setSelectedId(zone.id)} key={zone.id}><i style={{ background: zoneColor(zone, "risk") }} /><span><strong>{zone.name}</strong><small>{zone.id}</small></span><b>{Math.round(zone.assessment.risk)}</b><em>{zone.assessment.predicted.toFixed(1)}°</em><small>{compact(zone.assessment.exposed)}</small></button>)}<div className="equity"><strong>Equity weighting active</strong><p>Portfolio priority increases with vulnerable-population share.</p></div></section>
          </div>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) { return <article><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>; }
function Stat({ label, value }: { label: string; value: string }) { return <div className="stat"><span>{label}</span><strong>{value}</strong></div>; }
function Gauge({ label, value }: { label: string; value: number }) { return <div><span>{label}</span><strong>{Math.round(value * 100)}%</strong><i><em style={{ width: `${Math.min(100, value * 100)}%` }} /></i></div>; }
function riskBand(value: number) { return value >= 78 ? "critical" : value >= 65 ? "high" : value >= 48 ? "moderate" : "low"; }
function compact(value: number) { return value >= 1_000_000 ? `${(value / 1_000_000).toFixed(2)}M` : value >= 1000 ? `${Math.round(value / 1000)}K` : String(value); }
function layerValue(zone: Zone, layer: Layer) { return layer === "risk" ? `${zone.assessment.risk.toFixed(0)} risk` : layer === "temperature" ? `${zone.assessment.predicted.toFixed(1)}°C` : layer === "canopy" ? `${Math.round(zone.tree * 100)}% canopy` : `${Math.round(zone.vulnerableFraction * 100)}% vulnerable`; }
function zoneColor(zone: Zone, layer: Layer) { let value = zone.assessment.risk / 100; if (layer === "temperature") value = (zone.assessment.predicted - 37) / 8; if (layer === "canopy") value = 1 - zone.tree / 0.5; if (layer === "vulnerability") value = (zone.vulnerableFraction - 0.12) / 0.28; const t = Math.max(0, Math.min(1, value)); if (layer === "canopy") return `hsl(${145 - t * 105} 48% ${62 - t * 18}%)`; if (layer === "vulnerability") return `hsl(${265 - t * 42} 54% ${70 - t * 24}%)`; return `hsl(${48 - t * 42} ${70 + t * 15}% ${70 - t * 29}%)`; }
