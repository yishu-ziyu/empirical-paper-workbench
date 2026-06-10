from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_SRC = ROOT / "Product" / "web-react" / "src"


class WebReactApiBaseContractTests(unittest.TestCase):
    """BDD: React 工作台的阶段面板必须共用同一套本地 API 入口。"""

    def test_bdd_01_local_frontend_defaults_to_local_product_api(self) -> None:
        """Given 本地前端没有环境变量 When 发起阶段请求 Then 默认连接本地 Product API。"""

        helper = (WEB_REACT_SRC / "lib" / "apiBase.ts").read_text(encoding="utf-8")
        self.assertIn("http://127.0.0.1:8765", helper)
        self.assertIn("apiBase", helper)
        self.assertIn("apiUrl", helper)
        self.assertIn("__VITE_API_BASE_URL", helper)

    def test_bdd_03_url_api_base_overrides_env_for_live_acceptance(self) -> None:
        """Given 验收 URL 指定 api_base When 环境变量仍是旧端口 Then URL 必须优先。"""

        helper = (WEB_REACT_SRC / "lib" / "apiBase.ts").read_text(encoding="utf-8")
        query_index = helper.index("const queryBase = queryApiBase();")
        env_index = helper.index("const envBase = env[`VITE_${\"API_BASE_URL\"}`]?.trim();")

        self.assertLess(query_index, env_index)
        self.assertIn("if (queryBase) return queryBase;", helper)

    def test_bdd_04_recovery_keeps_current_local_api_base_before_default(self) -> None:
        """Given 当前页已经绑定本地后端 When 用户点击恢复 Then 不能强制写回默认端口。"""

        recovery = (WEB_REACT_SRC / "components" / "ServiceConnectionRecovery.tsx").read_text(
            encoding="utf-8"
        )
        app = (WEB_REACT_SRC / "App.tsx").read_text(encoding="utf-8")

        self.assertIn("preferredLocalApiBase", recovery)
        self.assertIn("setBrowserApiBase(preferredLocalApiBase)", recovery)
        self.assertIn("targetApiBase", app)
        self.assertIn('nextUrl.searchParams.set("api_base", targetApiBase)', app)

    def test_bdd_02_stage_panels_do_not_each_reimplement_api_base(self) -> None:
        """Given 多个阶段页面 When 请求后端 Then 不允许每个组件各自读取 env 拼地址。"""

        component_paths = [
            WEB_REACT_SRC / "App.tsx",
            WEB_REACT_SRC / "components" / "BriefPanel.tsx",
            WEB_REACT_SRC / "components" / "AutoResearchStream.tsx",
            WEB_REACT_SRC / "components" / "SearchPanel.tsx",
            WEB_REACT_SRC / "components" / "VariablesPanel.tsx",
            WEB_REACT_SRC / "components" / "DesignPanel.tsx",
            WEB_REACT_SRC / "components" / "ExecutionPanel.tsx",
            WEB_REACT_SRC / "components" / "IdentificationAuditPanel.tsx",
            WEB_REACT_SRC / "components" / "MethodsDrawer.tsx",
            WEB_REACT_SRC / "components" / "SystemStatusBar.tsx",
            WEB_REACT_SRC / "components" / "AgentTaskQueuePanel.tsx",
        ]
        for path in component_paths:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("lib/apiBase", source)
                self.assertNotIn('VITE_${"API_BASE_URL"}', source)


if __name__ == "__main__":
    unittest.main()
