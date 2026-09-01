import os
import subprocess
from pathlib import Path

from agent import upstream


def test_default_dependency_root_is_workspace_dependencies():
    assert upstream.DEPENDENCY_ROOT == upstream.WORKSPACE_ROOT / "dependencies"
    assert upstream.STATSPAI_REPO_PATH == upstream.DEPENDENCY_ROOT / "StatsPAI"


def test_dependency_root_can_be_configured(tmp_path):
    configured = tmp_path / "local dependencies"
    assert upstream._resolve_dependency_root(str(configured)) == configured.resolve()


def test_relative_dependency_root_is_workspace_relative(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert upstream._resolve_dependency_root("vendor") == (
        upstream.WORKSPACE_ROOT / "vendor"
    ).resolve()


def test_default_dependency_root_does_not_depend_on_cwd(tmp_path, monkeypatch):
    monkeypatch.delenv("ECONPAPER_DEPENDENCY_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    assert upstream._resolve_dependency_root() == upstream.WORKSPACE_ROOT / "dependencies"


def test_dependency_status_reports_actual_editable_source():
    status = upstream.get_dependency_status()
    statspai = status["statspai"]

    assert status["dependency_root"] == str(upstream.DEPENDENCY_ROOT)
    assert statspai["repo_exists"] is True
    assert statspai["installed"] is True
    assert Path(statspai["editable_source"]) == upstream.STATSPAI_REPO_PATH.resolve()
    assert statspai["source_matches_repo"] is True
    assert statspai["diagnostic"] is None


def test_make_install_honors_dependency_root_environment(tmp_path):
    dependency_root = tmp_path / "dependencies with spaces"
    env = os.environ.copy()
    env["ECONPAPER_DEPENDENCY_ROOT"] = str(dependency_root)

    result = subprocess.run(
        ["make", "-n", "install-agent"],
        cwd=upstream.PRODUCT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert f'pip install -e "{dependency_root}/StatsPAI"' in result.stdout
