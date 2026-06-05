// SystemStatusBar e2e: Task 41 行为 1 + 行为 2.
//
// 跑法:
//   1. 后端: PYTHONPATH=. python -m uvicorn Product.app:app --port 8765
//   2. 前端: cd Product/web-react && npm run dev -- --port 5173
//   3. e2e:  npx playwright test e2e/system-status-bar.spec.ts
//
// 此测试用 page.route 拦截 /api/system/status, 不依赖真实后端状态.
// 行为 1: 顶部常驻 4 个 pill
// 行为 2: 点击 pill 展开 4 个详情 section

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:5173/react/";

const FAKE_STATUS = {
  cap_count: 12,
  cost_total: 4.5,
  artifact_count: 7,
  obs_status: "completed",
  capabilities: [
    { id: "cap_statspai_ols", name: "ols", category: "Regression", risk_level: "low" },
    { id: "cap_statspai_did", name: "did", category: "Causal", risk_level: "medium" },
  ],
  artifacts: [
    { name: "paper.pdf", path: "Manuscripts/paper.pdf", size: 1024, created_at: "2026-06-05T10:00:00Z" },
  ],
  cost_breakdown: [{ service: "cap_statspai_ols", amount: 4.5 }],
};

test.describe("SystemStatusBar (Task 41)", () => {
  test("renders 4 pills and expands on click", async ({ page }) => {
    test.setTimeout(60_000);

    // Mock /api/system/status to return a known payload (don't depend on real backend state)
    await page.route("**/api/system/status", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(FAKE_STATUS),
      });
    });

    const resp = await page.goto(BASE_URL);
    expect(resp?.ok()).toBeTruthy();

    // Wait for intake → submit to land on brief tab (where status bar lives)
    await page.waitForSelector('textarea[aria-label="输入研究题目"]', { timeout: 30_000 });
    await page.locator('textarea[aria-label="输入研究题目"]').first().fill("测试 状态栏");
    await page.getByRole("button", { name: "开始研究" }).first().click();

    // 行为 1: 顶部常驻 4 个 pill
    const bar = page.getByTestId("system-status-bar");
    await expect(bar).toBeVisible({ timeout: 10_000 });

    const capCount = page.getByTestId("status-pill-cap-count");
    const costTotal = page.getByTestId("status-pill-cost-total");
    const artifactCount = page.getByTestId("status-pill-artifact-count");
    const obsGlyph = page.getByTestId("status-pill-obs-glyph");

    await expect(capCount).toHaveText("12", { timeout: 10_000 });
    await expect(costTotal).toHaveText("$4.50");
    await expect(artifactCount).toHaveText("7");
    await expect(obsGlyph).toHaveText("✓");

    // 行为 2: 点击 pill 展开 4 个详情 section
    await page.getByTestId("system-status-bar-toggle").click();
    await expect(page.getByTestId("system-status-bar-details")).toBeVisible();
    await expect(page.getByTestId("status-detail-capabilities")).toBeVisible();
    await expect(page.getByTestId("status-detail-cost")).toBeVisible();
    await expect(page.getByTestId("status-detail-artifacts")).toBeVisible();
    await expect(page.getByTestId("status-detail-obs")).toBeVisible();

    // Cost breakdown 数据透传
    const costDetail = page.getByTestId("status-detail-cost");
    await expect(costDetail).toContainText("cap_statspai_ols");
    await expect(costDetail).toContainText("$4.50");

    // 收起
    await page.getByTestId("system-status-bar-toggle").click();
    await expect(page.getByTestId("system-status-bar-details")).toBeHidden();
  });

  test("renders '—' for null fields (graceful degradation)", async ({ page }) => {
    test.setTimeout(60_000);

    await page.route("**/api/system/status", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          cap_count: null,
          cost_total: null,
          artifact_count: null,
          obs_status: "unknown",
        }),
      });
    });

    await page.goto(BASE_URL);
    await page.waitForSelector('textarea[aria-label="输入研究题目"]', { timeout: 30_000 });
    await page.locator('textarea[aria-label="输入研究题目"]').first().fill("测试 降级");
    await page.getByRole("button", { name: "开始研究" }).first().click();

    const capCount = page.getByTestId("status-pill-cap-count");
    const costTotal = page.getByTestId("status-pill-cost-total");
    const artifactCount = page.getByTestId("status-pill-artifact-count");
    await expect(capCount).toHaveText("—", { timeout: 10_000 });
    await expect(costTotal).toHaveText("—");
    await expect(artifactCount).toHaveText("—");
  });
});
