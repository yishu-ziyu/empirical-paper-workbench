# Handoff: F6 - 前端 UI/UX 打磨

## 目标
对 econpaper 前端进行 UI/UX 打磨，提升视觉品质和交互体验，贯彻 "Editorial Academic Refined" 设计美学方向。

## 背景
- 当前前端使用 Tailwind CSS，色板已定义（暖羊皮纸 + 墨黑 + 暗红强调）
- 字体为系统默认（system-ui），未使用设计规范中的思源宋体/Source Serif 4/JetBrains Mono
- 无动效库集成（Motion/Magic UI/GSAP 等均未安装）
- 无加载态、空态、过渡动画
- 三栏布局已实现但无视觉层次感
- 设计规范文件：`/Users/mahaoxuan/Documents/design-notes/DESIGN.md`

## 具体改动

### 1. 字体配置
- 安装思源宋体（Noto Serif SC）和 Source Serif 4 作为衬线字体
- 安装 JetBrains Mono 作为等宽字体
- 在 `index.css` 中通过 `@font-face` 或 CDN 引入
- 更新 `tailwind.config.cjs` 的 `fontFamily`：
  ```js
  fontFamily: {
    serif: ['"Source Serif 4"', '"Noto Serif SC"', 'Georgia', 'serif'],
    mono: ['"JetBrains Mono"', 'Menlo', 'monospace'],
    sans: ['system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
  }
  ```

### 2. 动效体系
- 安装 Motion 库（motion）：`npm install motion`
- 为三栏布局添加页面切换过渡动画（fade-in/slide-up）
- 为 Editor 流式输出添加打字机动效（新 chunk 淡入）
- 为 AgentPanel 状态变化添加脉冲动画（running 时闪烁）
- 为 ProgressBar 添加进度条缓动动画
- 动效需与写作节奏绑定：生成中波浪加速，暂停时几乎静止，完成时缓动结束

### 3. 加载态与空态
- **空态**：无 session 时显示引导提示"请上传 CSV 文件开始分析"
- **加载态**：上传 CSV 时按钮显示旋转指示器 + "上传中..."
- **WebSocket 连接中**：AgentPanel 显示 "连接中..." 脉冲文字
- **章节生成中**：Editor 显示占位渐变骨架屏
- **错误态**：统一的红色警告条（已有 uploadError，扩展为全局）

### 4. 视觉打磨
- 三栏布局增加分隔线阴影（`divide-x` 已用，加 `shadow-sm` 提升层次感）
- Header 加底部阴影，与主内容区分离
- 左侧 Outline 面板加章节状态 dot 指示器（灰色/绿色/黄色）
- 右侧 AgentPanel 加卡片分组，状态指示器用颜色编码
- 按钮 hover 状态加微过渡（`transition-colors duration-200`）
- 整体增加 `selection:bg-accent/20` 选择高亮色

### 5. 响应式考虑
- 三栏布局在窄屏（<1024px）时自动折叠左右栏为可切换面板
- 折叠按钮加在 Header 左右两侧

### 6. 测试
- 运行 `cd frontend && npm test` 确认所有 132 个测试通过
- 新增动效/空态/加载态测试（可选）

## 依赖
- 前置：无（独立任务，只涉及 frontend/ 目录）
- 不影响其他任务

## 验收标准
- [ ] 思源宋体 + Source Serif 4 + JetBrains Mono 字体正确加载
- [ ] Motion 库安装成功，三栏切换有过渡动画
- [ ] Editor 流式输出有打字机淡入效果
- [ ] AgentPanel 状态变化有脉冲动画
- [ ] 空态提示："请上传 CSV 文件开始分析"
- [ ] 上传按钮有加载态旋转指示器
- [ ] 所有 132 个前端测试仍然通过