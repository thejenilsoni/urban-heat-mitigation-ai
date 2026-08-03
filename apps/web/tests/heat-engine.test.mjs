import test from "node:test";
import assert from "node:assert/strict";
import {
  buildDemoCity,
  citySummary,
  optimizePortfolio,
  simulateZone,
} from "../lib/heat-engine.mjs";

test("demo city contains a stable 6x8 grid", () => {
  const zones = buildDemoCity();
  assert.equal(zones.length, 48);
  assert.equal(zones[0].id, "Z01");
  assert.equal(zones.at(-1).id, "Z48");
  assert.deepEqual(buildDemoCity(), zones);
});

test("tree scenario cools the selected zone", () => {
  const zone = buildDemoCity().find((item) => item.id === "Z30");
  assert.ok(zone);
  const result = simulateZone(zone, "tree_canopy", 0.25);
  assert.ok(result.cooling > 0);
  assert.ok(result.after.risk <= result.before.risk);
  assert.ok(result.cost > 0);
});

test("portfolio respects its budget", () => {
  const result = optimizePortfolio(buildDemoCity(), 75);
  assert.ok(result.items.length > 0);
  assert.ok(result.spent <= 75);
  assert.ok(result.cooling > 0);
});

test("city summary exposes key indicators", () => {
  const summary = citySummary(buildDemoCity());
  assert.ok(summary.predicted > 30);
  assert.ok(summary.uhi > 0);
  assert.ok(summary.exposed > 0);
  assert.ok(summary.highRisk > 0);
});
