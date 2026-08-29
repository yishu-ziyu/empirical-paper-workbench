"""沙箱代码执行器测试（Phase A）。

覆盖两层：
1. ``run_sandboxed_python`` / ``SubprocessSession``（回退后端）：一次性
   subprocess，-I 隔离、超时杀进程、workdir 文件传递中间产物；
2. ``KernelSession``（dev 主后端）：持久 IPython 内核——变量/导入跨调用
   存活、最后表达式 repr、错误捕获、超时中断/重启恢复。

沙箱是 dev 级弱隔离（无网络/文件系统保证），本文件只验证行为契约。
"""
from __future__ import annotations

import os
import time

import pytest

from agent.engine.sandbox import (
    KernelSession,
    SandboxSession,
    SubprocessSession,
    open_session,
    run_sandboxed_python,
)


# ===========================================================================
# run_sandboxed_python：一次性便捷入口（任务要求的签名）
# ===========================================================================

def test_run_sandboxed_python_ok(tmp_path):
    result = run_sandboxed_python("print('hello sandbox')", str(tmp_path))
    assert result.ok is True
    assert result.error is None
    assert result.stdout.strip() == "hello sandbox"
    assert result.duration_s > 0


def test_run_sandboxed_python_empty_code(tmp_path):
    result = run_sandboxed_python("", str(tmp_path))
    assert result.ok is True
    assert result.stdout == ""


def test_run_sandboxed_python_nonzero_exit(tmp_path):
    code = "import sys; print('boom', file=sys.stderr); raise SystemExit(3)"
    result = run_sandboxed_python(code, str(tmp_path))
    assert result.ok is False
    assert "boom" in result.stderr
    assert result.error is not None and "3" in result.error


def test_run_sandboxed_python_uncaught_exception(tmp_path):
    result = run_sandboxed_python("1/0", str(tmp_path))
    assert result.ok is False
    assert "ZeroDivisionError" in result.stderr
    assert result.error


def test_run_sandboxed_python_timeout_kills_process(tmp_path):
    start = time.monotonic()
    result = run_sandboxed_python("import time; time.sleep(5)", str(tmp_path), timeout_s=1)
    duration = time.monotonic() - start
    assert result.ok is False
    assert result.error and "timeout" in result.error
    assert duration < 4  # 没有真等 5s


def test_run_sandboxed_python_cwd_is_workdir(tmp_path):
    result = run_sandboxed_python("import os; print(os.getcwd())", str(tmp_path))
    assert result.stdout.strip() == str(tmp_path)


# ===========================================================================
# -I 隔离行为（dev 级隔离的具体含义）
# ===========================================================================

def test_sandbox_does_not_see_arbitrary_env(tmp_path, monkeypatch):
    """子进程 env 精简：白名单之外的环境变量不透传。"""
    monkeypatch.setenv("ECONPAPER_SANDBOX_SECRET", "leak-me")
    result = run_sandboxed_python(
        "import os; print(os.environ.get('ECONPAPER_SANDBOX_SECRET'))", str(tmp_path)
    )
    assert result.stdout.strip() == "None"


def test_sandbox_workdir_not_on_sys_path(tmp_path):
    """-I 隔离：workdir 里的模块不会被自动 import（无隐式代码注入面）。"""
    (tmp_path / "helper.py").write_text("RAISED = True\n", encoding="utf-8")
    result = run_sandboxed_python("import helper", str(tmp_path))
    assert result.ok is False
    assert "helper" in (result.stderr + (result.error or ""))


def test_sandbox_rejects_bad_workdir():
    with pytest.raises(NotADirectoryError):
        SubprocessSession("/nonexistent/econpaper/sandbox/xyz")


# ===========================================================================
# SandboxSession 接口：SubprocessSession（回退后端）
# ===========================================================================

def test_subprocess_session_attempts_and_file_handoff(tmp_path):
    """attempt 之间通过 workdir 文件传递中间产物；attempts 计数递增。"""
    with SubprocessSession(str(tmp_path)) as session:
        assert isinstance(session, SandboxSession)
        first = session.run("with open('stage1.txt', 'w') as f: f.write('42')")
        assert first.ok is True
        assert session.attempts == 1
        second = session.run("print(open('stage1.txt').read())")
        assert second.ok is True
        assert second.stdout.strip() == "42"
        assert session.attempts == 2


def test_subprocess_session_repr_empty():
    session = SubprocessSession(os.getcwd())
    result = session.run("print(1)")
    assert result.result_repr == ""  # subprocess 后端没有最后表达式 repr


# ===========================================================================
# SandboxSession 接口：KernelSession（dev 主后端，持久内核）
# ===========================================================================

pytest.importorskip("ipykernel", reason="持久内核后端需要 ipykernel/jupyter_client")


@pytest.fixture
def kernel_session(tmp_path):
    session = KernelSession(str(tmp_path))
    yield session
    session.close()


def test_kernel_session_persists_state(kernel_session):
    """持久内核核心价值：变量/导入跨工具调用存活。"""
    assert kernel_session.run("a = 41").ok is True
    assert kernel_session.run("b = ['x'] * 3").ok is True
    out = kernel_session.run("print(a + 1, len(b))")
    assert out.ok is True
    assert out.stdout.strip() == "42 3"
    assert kernel_session.attempts == 3


def test_kernel_session_last_expression_repr(kernel_session):
    result = kernel_session.run("6 * 7")
    assert result.ok is True
    assert result.result_repr == "42"


def test_kernel_session_imports_survive(kernel_session):
    assert kernel_session.run("import statistics").ok is True
    result = kernel_session.run("statistics.mean([1, 2, 3])")
    assert result.result_repr == "2"


def test_kernel_session_error_capture(kernel_session):
    result = kernel_session.run("1/0")
    assert result.ok is False
    assert "ZeroDivisionError" in result.stderr
    assert result.error


def test_kernel_session_cwd_is_workdir(kernel_session):
    result = kernel_session.run("import os; print(os.getcwd())")
    assert result.stdout.strip() == kernel_session.workdir


def test_kernel_session_timeout_recovers(tmp_path):
    """超时先中断；中断后内核仍可用（不重启也能继续跑）。"""
    session = KernelSession(str(tmp_path))
    try:
        bad = session.run("import time; time.sleep(30)", timeout_s=2)
        assert bad.ok is False
        assert bad.error and "timeout" in bad.error
        good = session.run("40 + 2")
        assert good.ok is True
        assert good.result_repr == "42"
    finally:
        session.close()


def test_kernel_session_restart_clears_state(kernel_session):
    kernel_session.run("z = 1")
    kernel_session.restart()
    result = kernel_session.run("z")
    assert result.ok is False  # 变量随内核重启清空


def test_open_session_prefers_kernel(tmp_path):
    """dev 主后端：jupyter 依赖齐备时 open_session 默认给持久内核。"""
    session = open_session(str(tmp_path))
    try:
        assert isinstance(session, KernelSession)
    finally:
        session.close()


def test_open_session_falls_back_to_subprocess(tmp_path, monkeypatch):
    """依赖缺失/启动失败时回退一次性 subprocess，接口不变。"""
    monkeypatch.setattr(
        "agent.engine.sandbox.KernelSession",
        lambda _workdir: (_ for _ in ()).throw(RuntimeError("no jupyter here")),
    )
    session = open_session(str(tmp_path))
    try:
        assert isinstance(session, SubprocessSession)
        assert isinstance(session, SandboxSession)
        assert session.run("print('fallback ok')").stdout.strip() == "fallback ok"
    finally:
        session.close()


# ===========================================================================
# snapshot / restore（checkpoint↔内核对齐）
# ===========================================================================

def _kernel_session(tmp_path):
    from agent.engine.sandbox import KernelSession
    return KernelSession(str(tmp_path))


def test_kernel_snapshot_restore_roundtrip(tmp_path):
    """snapshot 后换一个全新内核 restore，变量原样回来（对齐 kernel-state.dill）。"""
    import pytest
    pytest.importorskip("ipykernel")
    s1 = _kernel_session(tmp_path)
    try:
        r = s1.run("import numpy as np\narr = np.array([3, 4])\narr.sum()")
        assert r.ok, r.error
        assert s1.snapshot(str(tmp_path / "kernel_state.dill"))
    finally:
        s1.close()

    s2 = _kernel_session(tmp_path)
    try:
        assert s2.restore(str(tmp_path / "kernel_state.dill"))
        r2 = s2.run("int(arr.sum() * 2)")
        assert r2.ok, r2.error
        assert r2.result_repr == "14"
    finally:
        s2.close()


def test_kernel_restore_missing_file_false(tmp_path):
    import pytest
    pytest.importorskip("ipykernel")
    s = _kernel_session(tmp_path)
    try:
        assert s.restore(str(tmp_path / "nope.dill")) is False
    finally:
        s.close()


def test_subprocess_snapshot_noop(tmp_path):
    """无内核后端：snapshot/restore 是诚实的 no-op（返回 False，不写文件）。"""
    from agent.engine.sandbox import SubprocessSession
    s = SubprocessSession(str(tmp_path))
    assert s.snapshot(str(tmp_path / "k.dill")) is False
    assert s.restore(str(tmp_path / "k.dill")) is False
    assert not (tmp_path / "k.dill").exists()
