// Brief tab step-cards e2e: intake 输入题目 → 走到 brief tab → 点开始 →
// 看 4 个 card → step 3 点继续 → 看 final_brief.
//
// 跑法:
//   1. 后端: PYTHONPATH=. python -m uvicorn Product.app:app --port 8765
//      (后端应注入了 mock LLM fixture 替换 chat_completion_stream,
//       路径: Product/backend/wrapper/brief_stream_service.py —
//       patch brief_stream_service.chat_completion_stream 即可)
//   2. 前端: cd Product/web-react && npm run dev -- --port 5173
//   3. e2e:  npx playwright test e2e/brief-step-cards.spec.ts
//
// 用例假设后端注入了 mock LLM fixture. 若用真 LLM, 此测试需 ~30s 完成.

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:5173";

test.describe("Brief tab step-cards (Phase 1)", () => {
  test("happy path — intake → start → await step 3 → continue → final_brief", async ({
    page,
  }) => {
    await page.goto(BASE_URL);

    // 1. Intake 屏: 输入研究题目 (BriefPanel 不直接收 topic, 需先经 ResearchCommandInput)
    const topicInput = page.locator('textarea[aria-label="输入研究题目"]').first();
    await topicInput.fill(
      "工业机器人对城市制造业蓝领工资的影响——基于 CFPS 2010-2022"
    );

    // 2. 点 intake 的 "开始研究" 按钮 (IconButton label="开始研究")
    await page.getByRole("button", { name: "开始研究" }).first().click();

    // 3. 走到 brief tab 后, 点 brief-start 触发 /api/brief SSE
    await page.getByTestId("brief-start").click();

    // 4. 等步骤 1, 2 done (用 SSE 流式, 给足时间)
    await expect(page.getByTestId("step-card-1")).toHaveAttribute(
      "data-status",
      "done",
      { timeout: 30_000 }
    );
    await expect(page.getByTestId("step-card-2")).toHaveAttribute(
      "data-status",
      "done",
      { timeout: 30_000 }
    );

    // 5. 等步骤 3 抵达 awaiting
    await expect(page.getByTestId("step-card-3")).toHaveAttribute(
      "data-status",
      "awaiting",
      { timeout: 30_000 }
    );

    // 6. 看到 3 个按钮
    await expect(page.getByTestId("step-3-continue")).toBeVisible();
    await expect(page.getByTestId("step-3-modify")).toBeVisible();
    await expect(page.getByTestId("step-3-reselect")).toBeVisible();

    // 7. 点继续, 触发 /api/brief/resume
    await page.getByTestId("step-3-continue").click();

    // 8. 等步骤 4 done
    await expect(page.getByTestId("step-card-4")).toHaveAttribute(
      "data-status",
      "done",
      { timeout: 30_000 }
    );

    // 9. final_brief 显示
    await expect(page.getByTestId("brief-result")).toBeVisible({
      timeout: 30_000,
    });
    await expect(page.getByTestId("brief-verdict")).toContainText(
      /passed|failed/
    );
    await expect(page.getByTestId("brief-markdown")).toContainText("研究问题");
  });
});
