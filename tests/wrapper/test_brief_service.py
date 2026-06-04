"""任务书 (Brief) wrapper service BDD tests.

4 个 BDD 行为用例 (BDD ref: spec §6.1 row 1):
1. build_brief 返回包含 4 段 markdown 的字符串
2. write_brief 落盘到 Tasks/{topic_slug}/brief.md，附 provenance frontmatter
3. verify_brief 在 4 段齐全时返回 True
4. verify_brief 缺段时返回 False
"""
import tempfile
import unittest
from pathlib import Path

from Program.prompts.brief.v1 import load_prompt_v1

# NOTE: import the service module only inside test methods after conftest has
# installed the mock fixture. This avoids the cost of loading the (networked)
# LLM client at collection time on environments without a real key.
_brief_service = None


def _service():
    global _brief_service
    if _brief_service is None:
        from Product.backend.wrapper import brief_service
        _brief_service = brief_service
    return _brief_service


class BriefServiceTests(unittest.TestCase):

    def test_bdd_brief_build_returns_4_sections(self) -> None:
        """行为 1: build_brief 返回包含 4 段 markdown 的字符串."""
        svc = _service()
        result = svc.build_brief(
            topic="工业机器人对城市制造业就业结构的影响",
            prompt_loader=load_prompt_v1,
        )
        self.assertIn("研究问题", result)
        self.assertIn("边际贡献", result)
        self.assertIn("研究边界", result)
        self.assertIn("成功标准", result)

    def test_bdd_brief_write_creates_file_with_provenance(self) -> None:
        """行为 2: write_brief 落盘到 Tasks/{topic_slug}/brief.md，附 provenance frontmatter."""
        svc = _service()
        with tempfile.TemporaryDirectory() as tmp:
            path = svc.write_brief(
                content="# 研究问题\n...\n## 边际贡献\n...\n## 研究边界\n...\n## 成功标准\n...",
                topic="工业机器人对就业的影响",
                topic_slug="industrial-robots-employment",
                tasks_root=Path(tmp),
            )
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "brief.md")
            content = path.read_text(encoding="utf-8")
            self.assertIn("---", content)  # YAML frontmatter
            self.assertIn("model: MiniMax-M3", content)
            self.assertIn("topic: 工业机器人对就业的影响", content)

    def test_bdd_brief_verify_passes_when_4_sections_present(self) -> None:
        """行为 3: verify_brief 在 4 段齐全时返回 True."""
        svc = _service()
        content = (
            "## 研究问题\nx\n"
            "## 边际贡献\ny\n"
            "## 研究边界\nz\n"
            "## 成功标准\nw\n"
        )
        self.assertTrue(svc.verify_brief(content))

    def test_bdd_brief_verify_fails_when_section_missing(self) -> None:
        """行为 4: verify_brief 缺段时返回 False."""
        svc = _service()
        content = "## 研究问题\nx\n## 边际贡献\ny\n"
        self.assertFalse(svc.verify_brief(content))


if __name__ == "__main__":
    unittest.main()
