// Brief tab mode-dispatch e2e (Task 42, ui-gap-fill)
//
// 验证 App.tsx 在 brief tab 根据 ResearchCommandInput 选择的 mode
// 真正分发到不同的子组件:
//   - codex-supervisor → SupervisorPlanReview 先渲染, 通过后 BriefPanel
//   - auto-research    → AutoResearchStream 渲染并自动跑 4 步
//   - human-review (默认) → BriefPanel 直接渲染
//
// 跑法:
//   1. 后端: PYTHONPATH=. python -m uvicorn Product.app:app --port 8765
//   2. 前端: cd Product/web-react && npm run dev -- --port 5173
//   3. e2e:  npx playwright test e2e/mode-dispatch.spec.ts
//
// 默认 mode 已切换为 human-review, 所以旧 brief-step-cards.spec.ts 不变;
// 这个 spec 显式点击 mode 下拉切换到另外 2 个 mode 来验证分支.

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:5173/react/";

const TOPIC = "工业机器人对城市制造业蓝领工资的影响——基于 CFPS 2010-2022";

async function openIntake(page: import("@playwright/test").Page) {
  await page.goto(BASE_URL);
  await page.waitForSelector('textarea[aria-label="输入研究题目"]', { timeout: 30_000 });
}

async function selectMode(page: import("@playwright/test").Page, modeLabel: string) {
  // The mode-selector trigger is the only button with the mode name in it.
  // Click it, then click the option with the matching name.
  await page.getByRole("button", { name: /半自动审阅|本地 Codex Supervisor|Auto Research/ }).first().click();
  await page.getByRole("option", { name: new RegExp(modeLabel) }).first().click();
}

async function fillTopicAndSend(page: import("@playwright/test").Page) {
  await page.locator('textarea[aria-label="输入研究题目"]').first().fill(TOPIC);
  await page.getByRole("button", { name: "开始研究" }).first().click();
  // After send, we land on brief tab. The mode label appears in the header.
  await page.waitForSelector('[data-testid="topic-slug"]', { timeout: 10_000 });
}

test.describe("Brief tab mode dispatch (Task 42)", () => {
  test("mode=human-review (default) → BriefPanel renders 4 step cards", async ({ page }) => {
    test.setTimeout(120_000);
    await openIntake(page);
    // No mode change: default is human-review
    await fillTopicAndSend(page);
    // BriefPanel should be visible with its step-cards container
    await expect(page.getByTestId("step-cards")).toBeVisible({ timeout: 10_000 });
    // SupervisorPlanReview (Plan Route Overview) must NOT be visible
    await expect(page.getByText("SupervisorPlan 决策中心")).toHaveCount(0);
    // AutoResearchStream must NOT be visible
    await expect(page.getByTestId("auto-research-stream")).toHaveCount(0);
  });

  test("mode=codex-supervisor → SupervisorPlanReview renders above", async ({ page }) => {
    test.setTimeout(120_000);
    await openIntake(page);
    await selectMode(page, "本地 Codex Supervisor");
    await fillTopicAndSend(page);
    // Plan header is visible
    await expect(page.getByText("SupervisorPlan 决策中心")).toBeVisible({ timeout: 10_000 });
    // Approve button is visible
    await expect(page.getByRole("button", { name: /批准路线并派发/ })).toBeVisible();
    // BriefPanel step-cards are NOT yet rendered (waiting for approve)
    await expect(page.getByTestId("step-cards")).toHaveCount(0);
    // AutoResearchStream must NOT be visible
    await expect(page.getByTestId("auto-research-stream")).toHaveCount(0);
  });

  test("mode=auto-research → AutoResearchStream auto-runs and advances to search", async ({ page }) => {
    test.setTimeout(120_000);
    await openIntake(page);
    await selectMode(page, "Auto Research");
    await fillTopicAndSend(page);
    // BDD §Task 42 behavior 2: auto-research auto-runs all 4 steps and lands
    // on the search tab WITHOUT user interaction. Because the synthetic backend
    // is very fast, the brief tab may already be gone by the time we assert.
    // We assert the post-condition (search tab active + brief saved) instead.
    await expect(page.getByRole("tab", { name: "递归搜索" })).toHaveAttribute(
      "aria-selected",
      "true",
      { timeout: 30_000 },
    );
    await expect(page.getByTestId("saved-brief-link")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByTestId("view-saved-brief")).toBeVisible();
  });
});
