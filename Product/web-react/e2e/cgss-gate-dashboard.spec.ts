import { expect, test } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:5173/react/";

function cgssUrl() {
  const url = new URL(BASE_URL);
  url.searchParams.set("topic", "CGSS 互联网使用与主观幸福感");
  url.searchParams.set("mode", "human-review");
  return url.toString();
}

test.describe("CGSS read-only Gate Dashboard", () => {
  test("shows evidence-chain status before writing or PDF-first UI", async ({ page }) => {
    await page.goto(cgssUrl());

    const dashboard = page.getByTestId("cgss-gate-dashboard");
    await expect(dashboard).toBeVisible();
    await expect(dashboard.getByText("mixed existing workspace")).toBeVisible();
    await expect(dashboard.getByRole("heading", { name: "Current strongest allowed claim: descriptive" })).toBeVisible();
    await expect(dashboard.getByText("First failing gate").first()).toBeVisible();
    await expect(dashboard.getByText("MethodGate").first()).toBeVisible();
    await expect(dashboard.getByRole("button", { name: /DataContract evidence panel/ })).toBeVisible();
    await expect(dashboard.getByRole("button", { name: /SampleAudit evidence panel/ })).toBeVisible();
    await expect(dashboard.getByRole("button", { name: /MeasurementAudit evidence panel/ })).toBeVisible();
    await expect(dashboard.getByText("Blocked claims")).toBeVisible();
    await expect(dashboard.getByText("Number mismatches")).toBeVisible();
    await expect(dashboard.getByText("Replication readiness")).toBeVisible();

    await expect(dashboard).not.toContainText("paper completion percent");
    await expect(dashboard).not.toContainText("P0-P18");
    await expect(dashboard).not.toContainText("pipeline complete");
    await expect(dashboard).not.toContainText("AI checked");
    await expect(dashboard).not.toContainText("PDF hero");
    await expect(dashboard).not.toContainText("word count");

    await expect(dashboard.getByTestId("cgss-primary-cta")).toHaveCount(1);
    await expect(dashboard.getByTestId("cgss-primary-cta")).toContainText("Confirm cluster level");
  });

  test("opens artifact evidence panel with claim consequence", async ({ page }) => {
    await page.goto(cgssUrl());

    const dashboard = page.getByTestId("cgss-gate-dashboard");
    await dashboard.getByRole("button", { name: /SampleAudit/ }).click();

    const panel = dashboard.getByTestId("cgss-evidence-panel");
    await expect(panel).toBeVisible();
    await expect(panel).toContainText("SampleAudit");
    await expect(panel).toContainText("cluster level");
    await expect(panel).toContainText("claim consequence");
  });

  test("shows claim downgrade, number mismatch, and replication not-ready state", async ({ page }) => {
    await page.goto(cgssUrl());

    const dashboard = page.getByTestId("cgss-gate-dashboard");
    await expect(dashboard.getByText("Internet use improves subjective happiness.")).toBeVisible();
    await expect(dashboard.getByText("Internet use is associated with higher subjective happiness in the current CGSS sample.")).toBeVisible();
    await expect(dashboard.getByText("Claim C-003 cites 0.083, but ResultObject R-007 records 0.071.")).toBeVisible();
    await expect(dashboard.getByRole("heading", { name: "clean_rerun_required" })).toBeVisible();
  });
});
