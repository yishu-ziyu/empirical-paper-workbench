# Product Surface Cleanup BDD

日期：2026-06-19

目标：把当前产品入口从历史 demo、P 阶段面板和旧静态前端里清出来。清理标准不是“文件少”，而是用户进入产品后只看到论文生产流水线，不再看到旧阶段名、旧 demo 工作台或内部调试入口。

## 行为 1：主入口只挂论文生产状态

Given 用户输入题目后进入 React 工作台
When App 渲染当前项目状态
Then 主入口必须挂载 `PaperProductionStatusPanel`
And 不得挂载 `ProductControlP0Panel`
And 不得在主入口显示 P0/P11/P17 这类内部阶段控制面板

验证的业务规则：用户路径只围绕论文生产流水线，不再从旧 P 阶段面板开始理解产品。

## 行为 2：旧静态工作台不再作为运行入口存在

Given `/legacy` 已经重定向到 `/`
When 检查仓库运行源码
Then `Product/web/index.html`、`Product/web/assets/app.js` 和对应静态 CSS 不应继续作为可服务源码存在
And FastAPI 不应挂载 `Product/web/assets`

验证的业务规则：旧工作台不能继续吸引后续开发或验收；历史记录留在 docs/Tasks，不留在运行入口。

## 行为 3：产品地图只能声明一个当前入口

Given 后续 Agent 阅读产品地图
When 它查找当前工作台入口
Then 文档必须声明 React shell 是唯一当前产品壳
And `Product/web` 只能被描述为已移除的历史入口

验证的业务规则：后续开发不会再把静态 legacy 工作台当成当前产品。

## 行为 4：保留后端能力，不保留用户面噪声

Given P0/P1/P2 旧阶段后端和测试仍有历史价值
When 本轮清理运行面
Then 不删除后端服务、结果产物和历史测试
And 只从主 React 入口摘掉旧聚合面板

验证的业务规则：清理不等于毁掉可复用能力；被清理的是用户面噪声和旧入口。

## 边界

- 本轮不删除 `Product/backend/*` 的旧阶段服务。
- 本轮不删除旧 `Tasks/`、`docs/superpowers/` 或历史验收记录。
- 本轮不删除 `ProductControlP0Panel.tsx` 文件本体；它暂时作为历史源码留存，后续需要单独归档其依赖测试。
- 本轮不新增论文流水线功能。
