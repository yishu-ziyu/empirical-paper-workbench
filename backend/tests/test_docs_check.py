"""scripts/check_docs.py must catch each class of documentation drift it claims to catch."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_docs.py"


@pytest.fixture
def cd(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("check_docs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    docs = tmp_path / "docs"
    (docs / "specs").mkdir(parents=True)
    (tmp_path / "README.md").write_text("[docs](docs/README.md)\n")
    (docs / "README.md").write_text("[specs](specs/README.md)\n")
    (docs / "specs" / "README.md").write_text("[a](a.md)\n")
    (docs / "specs" / "a.md").write_text("# A\n")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "DOCS", docs)
    monkeypatch.setattr(mod, "BASELINE", docs / ".doc-size-baseline")
    return mod


def test_clean_tree_passes(cd):
    files = cd.doc_files()
    assert cd.check_links(files) == []
    assert cd.check_orphans() == []
    assert cd.check_size(files) == ([], [])


def test_broken_link_is_reported(cd):
    (cd.DOCS / "specs" / "a.md").write_text("# A\n[gone](missing.md)\n")
    assert any("missing.md" in e for e in cd.check_links(cd.doc_files()))


def test_link_inside_code_fence_is_ignored(cd):
    (cd.DOCS / "specs" / "a.md").write_text("# A\n```\n[x](missing.md)\n```\n")
    assert cd.check_links(cd.doc_files()) == []


def test_unindexed_doc_is_orphan(cd):
    (cd.DOCS / "specs" / "b.md").write_text("# B\n")
    assert [o.split(":")[0] for o in cd.check_orphans()] == ["docs/specs/b.md"]


def test_oversized_living_doc_fails(cd):
    (cd.DOCS / "specs" / "a.md").write_text("x\n" * (cd.MAX_LINES + 1))
    errors, _ = cd.check_size(cd.doc_files())
    assert errors and "docs/specs/a.md" in errors[0]


def test_frozen_record_may_not_grow(cd):
    (cd.DOCS / "specs" / "a.md").write_text("x\n" * (cd.MAX_LINES + 5))
    cd.BASELINE.write_text(f"{cd.MAX_LINES + 5} docs/specs/a.md\n")
    assert cd.check_size(cd.doc_files())[0] == []
    (cd.DOCS / "specs" / "a.md").write_text("x\n" * (cd.MAX_LINES + 6))
    assert "grew" in cd.check_size(cd.doc_files())[0][0]


def test_code_change_without_doc_change_is_flagged(cd):
    assert cd.check_sync(["backend/routers/design.py"])
    assert cd.check_sync(["backend/routers/design.py", "docs/api/reference/02-endpoints.md"]) == []
    assert cd.check_sync(["agent/nodes/set_direction.py", "docs/contracts/infer-design-contract/03-x.md"]) == []
    assert cd.check_sync(["backend/tests/test_ws.py"]) == []
