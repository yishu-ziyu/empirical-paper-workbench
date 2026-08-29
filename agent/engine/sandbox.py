"""沙箱代码执行器（Phase A：给 LLM 装上"手"）。

隔离级别说明（重要）：本地 dev 级弱隔离，不是安全边界。
- SubprocessSession：``python -I -B -c <code>`` 一次性执行。``-I``（isolated）
  忽略用户 site-packages / PYTHON* 环境变量、不把当前目录放进 sys.path，
  但**没有网络、文件系统或进程级隔离**。
- KernelSession：本地 IPython 内核（jupyter_client + ipykernel），连 ``-I``
  等价物都没有（内核需要完整 site-packages 才能跑 pandas/statsmodels），
  仅以"会话级 workdir"收拢读写。生产部署必须换 E2B 等真正的远程沙箱，
  本模块的接口即为该替换预留的槽位。

槽位设计（参考 Prime Agent / Prime Intellect 的架构调研）：持久 Python 内核
（变量/导入/中间产物跨工具调用存活）比一次性 subprocess 更适合研究迭代。
因此抽象出 ``SandboxSession`` 接口：

- 主后端 ``KernelSession``：一个会话 = 一个内核进程，``run`` 即 execute 一格，
  返回 stdout/stderr + 最后表达式 repr；超时先中断、探针失败则重启内核
  （``restart``），内核随会话存活。
- 回退后端 ``SubprocessSession``：jupyter 依赖缺失或内核启动失败时使用，
  每次 ``run`` 起一个一次性子进程；中间产物通过 workdir 里的文件在
  attempt 之间传递（工作目录文件持久，两个后端语义一致）。

未来换持久内核托管（本地 Jupyter server / E2B）时只需新增一个
``SandboxSession`` 实现，调用方（engine.estimate_agent）只依赖接口。
"""
from __future__ import annotations

import abc
import logging
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# 剥掉 IPython traceback 里的 ANSI 颜色码，别把控制符喂给 LLM
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


@dataclass
class SandboxResult:
    """一次沙箱执行的完整产物。"""

    ok: bool                       # 退出码 0 且无异常 traceback
    stdout: str
    stderr: str
    error: Optional[str]           # 超时 / 非零退出 / 异常摘要；成功为 None
    duration_s: float
    result_repr: str = ""          # 最后表达式 repr（KernelSession 专属；subprocess 后端为空）


class SandboxSession(abc.ABC):
    """沙箱会话接口：estimate_agent 只依赖本抽象，不感知后端细节。

    约定：
    - 同一会话内 ``workdir`` 不变，attempt 之间通过 workdir 里的文件传递
      中间产物（持久内核里变量/导入也跨调用存活）。
    - ``run`` 永不抛异常，失败信息一律装进 ``SandboxResult.error``。
    """

    workdir: str
    attempts: int

    @abc.abstractmethod
    def run(self, code: str, timeout_s: int = 30) -> SandboxResult:
        """执行一段 Python 代码，返回 (stdout, stderr, error, 耗时)。"""

    def restart(self) -> None:
        """重启会话（清空变量/导入）。无内核的后端为 no-op。"""

    def snapshot(self, path: str) -> bool:
        """把会话命名空间快照到 path（对齐 Prime Agent 的 kernel-state.dill）。

        无内核的后端不支持（变量本就不存活），返回 False。
        """
        return False

    def restore(self, path: str) -> bool:
        """从 path 恢复命名空间。文件不存在或后端不支持时返回 False。"""
        return False

    def close(self) -> None:
        """释放会话资源。无内核的后端为 no-op。"""

    def __enter__(self) -> "SandboxSession":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        self.close()
        return False


# ---------------------------------------------------------------------------
# 主后端：持久 IPython 内核（jupyter_client + ipykernel）
# ---------------------------------------------------------------------------

# 超时恢复：先 SIGINT 中断，再用探针验证；探针失败才重启内核
_PROBE_TIMEOUT_S = 5
_KERNEL_READY_TIMEOUT_S = 30


class _OutputSink:
    """收集一格 iopub 输出：stream -> stdout/stderr，execute_result -> repr。"""

    def __init__(self) -> None:
        self.stdout: list[str] = []
        self.stderr: list[str] = []
        self.result_repr: str = ""
        self.error: list[str] = []

    def __call__(self, msg: dict) -> None:
        msg_type = msg["header"]["msg_type"]
        content = msg["content"]
        if msg_type == "stream":
            name = content.get("name")
            text = _ANSI_RE.sub("", str(content.get("text") or ""))
            if name == "stdout":
                self.stdout.append(text)
            else:
                self.stderr.append(text)
        elif msg_type == "execute_result":
            data = content.get("data") or {}
            self.result_repr = _ANSI_RE.sub("", str(data.get("text/plain") or ""))
        elif msg_type == "error":
            traceback = "\n".join(content.get("traceback") or [])
            self.error.append(_ANSI_RE.sub("", traceback) or f"{content.get('ename')}: {content.get('evalue')}")

    @property
    def stdout_text(self) -> str:
        return "".join(self.stdout)

    @property
    def stderr_text(self) -> str:
        return "".join(self.stderr)

    @property
    def error_text(self) -> Optional[str]:
        return "\n".join(self.error) if self.error else None


class KernelSession(SandboxSession):
    """持久 IPython 内核会话（dev 主后端）。

    内核进程的 cwd 即 ``workdir``（相对路径读写全部落在数据目录）；
    变量、import、写盘的中间产物跨 ``run`` 存活。超时先 interrupt，
    探针仍无响应则 ``restart_kernel``（变量会丢，cwd 由本类重新落位）。

    线程模型：jupyter_client 的 blocking API 依赖"调用线程当前的事件循环"，
    直接在调用方线程执行会被外层 loop（FastAPI / pytest / anyio）污染。
    因此本类所有内核交互都经由 ``_call_isolated`` 在专用隔离线程里跑，
    与调用方的事件循环状态完全解耦。
    """

    # 隔离线程兜底等待：execute_interactive 自带 timeout，这里再留裕量
    _JOIN_GRACE_S = 15.0

    def __init__(self, workdir: str) -> None:
        from jupyter_client.manager import start_new_kernel  # noqa: PLC0415 — 依赖缺失时推迟报错

        self.workdir = os.path.abspath(str(workdir))
        if not os.path.isdir(self.workdir):
            raise NotADirectoryError(f"sandbox workdir 不存在: {self.workdir}")
        self.attempts: int = 0
        self._start_new_kernel = start_new_kernel
        self._km: Any = None
        self._kc: Any = None
        self._lock = threading.Lock()  # 会话内串行：同一内核一次跑一格

    # -- 隔离线程执行 ------------------------------------------------------

    def _call_isolated(self, fn: Callable[[], Any], join_timeout: Optional[float] = None) -> Any:
        """在专用隔离线程里执行一次 jupyter blocking 调用。

        新线程没有事件循环，jupyter_core 的 wrapped 会走
        ensure_event_loop + run_until_complete 的确定路径，不碰调用方的 loop。
        ``join_timeout`` 仅供兜底（正常路径下 blocking API 自带超时）。
        """
        box: dict[str, Any] = {}

        def _target() -> None:
            try:
                box["value"] = fn()
            except BaseException as exc:  # noqa: BLE001 — 原样带回调用线程
                box["exc"] = exc

        thread = threading.Thread(target=_target, name="sandbox-kernel-call", daemon=True)
        thread.start()
        thread.join(join_timeout)
        if thread.is_alive():
            raise TimeoutError(f"sandbox kernel call 隔离线程超过 {join_timeout}s 未返回")
        if "exc" in box:
            raise box["exc"]
        return box.get("value")

    # -- 内核生命周期 ------------------------------------------------------

    def _start(self) -> None:
        """启动内核，内核进程 cwd = workdir（起完立即 chdir 回父进程）。"""
        cwd0 = os.getcwd()

        def _spawn() -> None:
            try:
                os.chdir(self.workdir)
                self._km, self._kc = self._start_new_kernel(kernel_name="python3")
            finally:
                os.chdir(cwd0)

        self._call_isolated(_spawn)

    def _ensure_started(self) -> None:
        if self._km is None or self._kc is None:
            self._start()

    def restart(self) -> None:
        """重启内核：变量/导入清空，cwd 重新落回 workdir。"""
        if self._km is None:
            return

        def _restart() -> None:
            cwd0 = os.getcwd()
            try:
                os.chdir(self.workdir)
                self._km.restart_kernel()
            finally:
                os.chdir(cwd0)
            self._kc.wait_for_ready(timeout=_KERNEL_READY_TIMEOUT_S)

        with self._lock:
            self._call_isolated(_restart)

    def snapshot(self, path: str) -> bool:
        """把内核用户命名空间 dill 序列化到 path（对齐 Prime Agent kernel-state.dill）。

        用于 LangGraph 断点续跑：graph checkpoint 记下这个路径，新进程 restore 后
        变量/导入原样回来。逐键试 pickle 过滤——IPython 注入的机器对象（get_ipython、
        In/Out、sqlite 连接等）跳过并在 stdout 报告。执行失败或文件未生成返回 False。
        """
        code = (
            "import dill as _dill, pickle as _pickle\n"
            "_skip = {'In', 'Out', 'get_ipython', 'exit', 'quit', 'open', '_i', '_ii', '_iii', '_oh'}\n"
            "_ns = {k: v for k, v in globals().items() if not k.startswith('_') and k not in _skip}\n"
            "_ok, _bad = {}, []\n"
            "for _k, _v in _ns.items():\n"
            "    try:\n"
            "        _pickle.dumps(_v)\n"
            "        _ok[_k] = _v\n"
            "    except Exception:\n"
            "        _bad.append(_k)\n"
            f"_dill.dump(_ok, open({path!r}, 'wb'))\n"
            "print('快照变量:', sorted(_ok) or '(空)', '| 跳过不可序列化:', sorted(_bad) or '(无)')\n"
            "del _ns, _ok, _bad, _skip, _dill, _pickle\n"
        )
        result = self.run(code, timeout_s=60)
        if result.stdout.strip():
            logger.info("kernel snapshot: %s", result.stdout.strip())
        return bool(result.ok and os.path.exists(path))

    def restore(self, path: str) -> bool:
        """从 path 恢复命名空间到当前内核。文件不存在或恢复失败返回 False。"""
        if not os.path.exists(path):
            return False
        code = (
            "import dill as _dill\n"
            f"globals().update(_dill.load(open({path!r}, 'rb')))\n"
            "del _dill\n"
        )
        result = self.run(code, timeout_s=60)
        return bool(result.ok)

    def close(self) -> None:
        if self._km is None:
            return
        logger.info("sandbox kernel 关闭（workdir=%s）", self.workdir)

        def _shutdown() -> None:
            self._km.shutdown_kernel(now=True)

        try:
            self._call_isolated(_shutdown)
        except Exception:  # pragma: no cover — 关闭失败不影响主流程
            logger.warning("sandbox kernel 关闭失败", exc_info=True)
        self._km = None
        self._kc = None

    # -- 执行 --------------------------------------------------------------

    def run(self, code: str, timeout_s: int = 30) -> SandboxResult:
        with self._lock:
            return self._run_locked(code, timeout_s)

    def _run_locked(self, code: str, timeout_s: int = 30) -> SandboxResult:
        self._ensure_started()
        self.attempts += 1
        started = time.monotonic()
        sink = _OutputSink()
        try:
            reply = self._call_isolated(
                lambda: self._kc.execute_interactive(code, timeout=timeout_s, output_hook=sink),
                join_timeout=timeout_s + self._JOIN_GRACE_S,
            )
        except TimeoutError:
            duration = time.monotonic() - started
            self._recover()
            return SandboxResult(
                ok=False,
                stdout=sink.stdout_text,
                stderr=sink.stderr_text,
                error=f"timeout after {timeout_s}s（内核已中断/重启，变量丢失）",
                duration_s=duration,
            )
        duration = time.monotonic() - started
        status = (reply or {}).get("content", {}).get("status", "error")
        error = sink.error_text
        if status != "ok" and error is None:
            error = f"kernel execute status={status}"
        stderr = sink.stderr_text
        if error:
            # traceback 同时进 stderr（错误现场）与 error（结构化摘要）
            stderr = f"{stderr}\n{error}".strip() if stderr else error
        return SandboxResult(
            ok=status == "ok" and error is None,
            stdout=sink.stdout_text,
            stderr=stderr,
            error=error,
            duration_s=duration,
            result_repr=sink.result_repr,
        )

    def _recover(self) -> None:
        """超时恢复：SIGINT -> 探针 -> 仍卡死才重启。"""
        try:
            self._call_isolated(self._km.interrupt_kernel)
        except Exception:  # pragma: no cover
            logger.warning("interrupt_kernel 失败", exc_info=True)
        try:
            self._call_isolated(
                lambda: self._kc.execute_interactive(
                    "None", timeout=_PROBE_TIMEOUT_S, output_hook=lambda _msg: None
                )
            )
            return  # 中断生效，内核还活着
        except Exception:
            pass
        try:
            self.restart()
        except Exception:
            logger.warning("sandbox kernel 重启失败", exc_info=True)


# ---------------------------------------------------------------------------
# 回退后端：一次性 subprocess
# ---------------------------------------------------------------------------

# 子进程只继承白名单 env（-I 已忽略 PYTHON*，这里再收掉 PATH 之外的杂音）
_SANDBOX_ENV_KEYS = (
    "PATH",
    "LANG",
    "LC_ALL",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
)


class SubprocessSession(SandboxSession):
    """一次性 subprocess 回退后端。

    每次 ``run`` 以 ``[sys.executable, "-I", "-B", "-c", code]`` 起一个子进程，
    cwd=workdir、精简 env、超时杀进程。会话本身无状态，attempt 之间只靠
    workdir 文件传递中间产物。
    """

    def __init__(self, workdir: str) -> None:
        self.workdir = os.path.abspath(str(workdir))
        if not os.path.isdir(self.workdir):
            raise NotADirectoryError(f"sandbox workdir 不存在: {self.workdir}")
        self.attempts: int = 0

    def _child_env(self) -> dict:
        env = {key: os.environ[key] for key in _SANDBOX_ENV_KEYS if os.environ.get(key)}
        env.setdefault("HOME", self.workdir)  # 个别库（matplotlib 等）依赖 HOME
        return env

    def run(self, code: str, timeout_s: int = 30) -> SandboxResult:
        if timeout_s <= 0:
            raise ValueError(f"timeout_s 必须为正数，收到 {timeout_s}")
        self.attempts += 1
        started = time.monotonic()
        proc = subprocess.Popen(  # noqa: S603 — 固定解释器 + -I 隔离，无 shell
            [sys.executable, "-I", "-B", "-c", code],
            cwd=self.workdir,
            env=self._child_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            return SandboxResult(
                ok=False,
                stdout=stdout or "",
                stderr=stderr or "",
                error=f"timeout after {timeout_s}s（子进程已被杀死）",
                duration_s=time.monotonic() - started,
            )
        duration = time.monotonic() - started
        returncode = proc.returncode
        return SandboxResult(
            ok=returncode == 0,
            stdout=stdout or "",
            stderr=stderr or "",
            error=None if returncode == 0 else f"子进程退出码 {returncode}",
            duration_s=duration,
        )


# ---------------------------------------------------------------------------
# 工厂 + 任务要求的一次性便捷入口
# ---------------------------------------------------------------------------

def open_session(workdir: str, *, prefer_kernel: bool = True) -> SandboxSession:
    """按 dev 主后端（持久内核）优先开一个会话，失败回退一次性 subprocess。

    ``prefer_kernel=False``（或 jupyter 依赖缺失 / 内核启动失败）时直接用
    ``SubprocessSession``。estimate_agent 只经由本工厂拿会话。
    """
    if prefer_kernel:
        try:
            return KernelSession(workdir)
        except Exception as exc:
            logger.warning("持久内核会话启动失败，回退一次性 subprocess 沙箱: %s", exc)
    return SubprocessSession(workdir)


__all__ = [
    "SandboxResult",
    "SandboxSession",
    "KernelSession",
    "SubprocessSession",
    "open_session",
]
