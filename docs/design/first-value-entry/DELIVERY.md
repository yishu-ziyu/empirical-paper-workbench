# 外部设计审阅交付

2026-09-08。Design-only Draft；未获外部设计批准，不实施官网、不合并。

设计 source SHA：`b132ff998cf2f2c94776f1056eba127b6a151eb8`。本次仅增加交付材料，原 HTML、文案、分镜、证据及旧截图保持不变。HTML 的 CSS/JS 全部内嵌，无外部运行资产；同目录 JSON 与 Markdown 为来源链接。

## 阅读入口

- [完整可离线打开的 HTML](index.html)、[产品说明](README.md)、[证据](evidence.md)、[分镜](storyboard.md)、[真人试用方案](user-study.md)。
- [自包含审阅包](first-value-entry-review.zip)：下载并解压，打开 `docs/design/first-value-entry/index.html`。包含本目录原件、26 张截图、渲染记录、能力清单与术语表；深层工程资料从 GitHub 仓库查看。无需服务器、安装依赖或业务凭证。
- [截图目录](../../acceptance/assets/first-value-entry-design/)；[12 组合实际输出](../../acceptance/assets/first-value-entry-design/render-matrix.json)；[历史交互结果](../../acceptance/assets/first-value-entry-design/interaction-checks.json)。
- [交付文件校验值](delivery-manifest.json)。包内 HTML 与上述设计 SHA 完全一致。

## 12 组合与实际结果

维度为 zh-CN / en × 1440×900 桌面 / 390×844 移动 × 01 / 02 / 03 分节，共 12 个。实际输出保留在原 `render-matrix.json`，每条均有 viewport、section、lang、width、height、scrollWidth、visibleSections、完整可见正文；12 条均无横向溢出且所选节正确。来源为上述 SHA 的设计，2026-09-08 既有 ego lite task 97 实测；本次没有重跑。

手工复现步骤：在浏览器打开 HTML，用开发者工具设定对应 CSS viewport；语言选择中文或 English，画幅保留自适应/桌面，依次选择 01、02、03，逐节滚动到底；第二节展开来源。桌面 390 审阅画幅是另一个已记录的控件检查，不代替 390 viewport 检查。

以下为按现有页面和先前 CDP 方法整理的复现命令（在 ego-browser 已获用户授权控制的设计页中运行；本次未执行这段整合命令，不能当作新增通过证据）：

```js
// ego-browser nodejs heredoc 内；先按当前 ownership 选择已授权任务与 HTML tab。
for (const [viewport,width,height] of [['desktop',1440,900],['mobile',390,844]]) {
  await cdp('Emulation.setDeviceMetricsOverride', {width,height,deviceScaleFactor:1,mobile:viewport==='mobile'});
  for (const lang of ['zh','en']) {
    await js(`document.querySelector('#lang').value='${lang}';document.querySelector('#lang').dispatchEvent(new Event('change'))`);
    for (const section of ['1','2','3']) {
      await js(`document.querySelector('#view').value='${section}';document.querySelector('#view').dispatchEvent(new Event('change'));window.scrollTo(0,0)`);
      cliLog(await js(`({lang:document.documentElement.lang,width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,visibleSections:[...document.querySelectorAll('[data-section]')].filter(e=>!e.classList.contains('hidden')).map(e=>e.dataset.section),body:document.querySelector('.shell').innerText})`));
      // Page.captureScreenshot 可保存当前视口；逐节滚动补图，不把整页压成拥挤长图。
      cliLog({viewport,section,screenshot:await cdp('Page.captureScreenshot',{format:'png'})});
    }
  }
}
```

## 截图覆盖与缺项

26 张图均已逐张检查，只含设计页和公开 Card 教学结果，无浏览器账户、凭证、私人数据或本机地址栏。`zh|en-01|02|03-desktop|mobile.png` 是分节首屏；`02-pair-mobile`、`02-sources-mobile`、`02-boundary-*`、`03-end-*` 补比较、来源、边界和末尾。`zh-02-sources-desktop` 补桌面展开来源；`zh-handoff-desktop` 仅证明原型交接弹窗，其背景是旧措辞，最终第三节以 `03-*` 与 HTML 为准。

**完整截图要求尚有缺口**：中英移动 01 的下半预览卡没有补图；英文移动 03 的中间自有数据限制段未完整覆盖；英文桌面 01 页尾也未入图。HTML 与渲染正文完整可读，但不以此声称截图完整。本次恢复 task 97 被工具以“user has taken control ... ended the task ... no longer assigned”拒绝，按浏览器控制规则停止，没有重试或换浏览器绕过。需用户明确恢复浏览器控制后补采。这不妨碍先推送可审阅原件。

## 按钮与验证边界

「真实案例」「当前范围」只在设计稿内切节；语言、画幅、整页/分节仅是审阅控件。「进入桌面工作台」/手机入口只打开交接说明，**没有任何按钮接入真实工作台或 API**。来源链接只打开去敏 JSON / Markdown。真实接线须另行批准。

本次检查：原设计 44 个变更文件的文本敏感模式扫描（私钥、provider token、长凭证赋值、本机用户路径）零命中；26 图逐张检查；HTML 原件保持；归档文件 SHA-256 与解压校验；`git diff --check`。原 validator ACCEPT 仅为历史客观设计检查，不能代替外部批准。本次不重跑引擎测试、真人试用或生产服务。
