// Component test for MethodsDrawer — Task 43 BDD (4 behaviors).
// We test the pure filter logic directly (no DOM renderer) to keep the
// test infra-light. The React component's render is verified separately
// by `npm run build` (vite + tsc) and the integration test that the
// drawer fetches /api/capabilities/methods on first open.
//
// Run with:
//   node --experimental-strip-types --test Product/web-react/tests/MethodsDrawer.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { filterMethods, type MethodItem } from "../src/components/MethodsDrawer";

const SAMPLE: MethodItem[] = [
  { id: "cap_statspai_did", name: "did", category: "causal", description: "Difference-in-Differences 2x2", risk_level: "high" },
  { id: "cap_statspai_bootstrap", name: "bootstrap", category: "inference", description: "Bootstrap standard errors", risk_level: "low" },
  { id: "cap_statspai_iv_bartik", name: "iv_bartik", category: "iv", description: "Bartik instrumental variable", risk_level: "medium" },
  { id: "cap_statspai_ols", name: "ols", category: "regression", description: "Ordinary least squares", risk_level: "low" },
  { id: "cap_statspai_event_study", name: "event_study", category: "causal", description: "Event-study coefficients", risk_level: "high" },
];

test("bdd_behavior_1: empty query + '全部' returns all", () => {
  const out = filterMethods(SAMPLE, "全部", "");
  assert.equal(out.length, SAMPLE.length);
});

test("bdd_behavior_2: filter by category 'causal' returns only causal items", () => {
  const out = filterMethods(SAMPLE, "causal", "");
  assert.equal(out.length, 2);
  assert.ok(out.every((m) => m.category === "causal"));
});

test("bdd_behavior_3: search 'did' returns name + description matches", () => {
  // 'did' matches: 'did' (name), 'Difference-in-Differences 2x2' (desc)
  // 'event_study' contains 's-t-u-d-y' not 'did', so it does NOT match.
  const out = filterMethods(SAMPLE, "全部", "did");
  const names = out.map((m) => m.name);
  assert.ok(names.includes("did"));
  assert.equal(out.length, 1);
});

test("bdd_behavior_3: search 'bartik' matches name 'iv_bartik'", () => {
  const out = filterMethods(SAMPLE, "全部", "bartik");
  assert.equal(out.length, 1);
  assert.equal(out[0].name, "iv_bartik");
});

test("bdd_behavior_3: search 'bootstrap' is case-insensitive", () => {
  const outLower = filterMethods(SAMPLE, "全部", "bootstrap");
  const outUpper = filterMethods(SAMPLE, "全部", "BOOTSTRAP");
  assert.equal(outLower.length, 1);
  assert.equal(outUpper.length, 1);
  assert.equal(outLower[0].name, "bootstrap");
});

test("bdd_behavior_3: category + query combine as AND", () => {
  const out = filterMethods(SAMPLE, "causal", "did");
  // causal filter + 'did' search = just 'did'
  assert.equal(out.length, 1);
  assert.equal(out[0].name, "did");
});

test("bdd_behavior_3: empty result for non-matching combo", () => {
  const out = filterMethods(SAMPLE, "causal", "bartik");
  // bartik is in 'iv' category, not 'causal'
  assert.equal(out.length, 0);
});

test("bdd_behavior_3: whitespace-only query is treated as empty", () => {
  const out = filterMethods(SAMPLE, "全部", "   ");
  assert.equal(out.length, SAMPLE.length);
});

test("filterMethods does not mutate the input array", () => {
  const before = JSON.stringify(SAMPLE);
  filterMethods(SAMPLE, "causal", "did");
  assert.equal(JSON.stringify(SAMPLE), before);
});
