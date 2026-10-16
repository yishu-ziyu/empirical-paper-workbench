"""Capture and verify the local-only workspace relocation end to end."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".local" / "workspace-merge"
MOVES = {"经济学论文": "research", "empirical-paper-workbench-evidence": "evidence"}
EDITED = {"research/README.md", "research/AGENTS.md"}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def git(cwd, *args):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def inventory(base):
    entries = {}
    for parent, dirs, files in os.walk(base, followlinks=False):
        dirs[:] = [name for name in dirs if name != ".git"]
        for name in dirs + files:
            path = Path(parent) / name
            key = str(path.relative_to(base))
            if path.is_symlink():
                entries[key] = {"link": os.readlink(path)}
            elif path.is_file():
                entries[key] = {"sha256": sha(path)}
            else:
                entries[key] = {"directory": True}
    return entries


def estimate(environment):
    loader = """
from services.card_demo import load_card_extract
frame, _ = load_card_extract()
""" if environment == "backend" else """
import pandas as pd
from pathlib import Path
frame = pd.read_csv(Path(statspai.__file__).resolve().parents[2] / 'papers/data_card1995.csv')
frame = frame.drop(columns=[c for c in frame.columns if str(c).lower() in {'rownames', 'unnamed: 0'}])
"""
    code = """
import json, statspai
from agent.upstream import get_dependency_status
from agent.nodes.estimate import _estimate_ols
""" + loader + """
out = _estimate_ols(frame, {'method':'ols','treatment':'educ','controls':['exper','expersq','black','south','smsa']}, 'lwage ~ educ + exper + expersq + black + south + smsa')['estimate']
assert out['status'] == 'ok', out
assert out['estimator'].startswith('statspai.'), out
print(json.dumps({'source':statspai.__file__, 'dependency':get_dependency_status()['statspai'], 'rows':len(frame), 'columns':len(frame.columns), 'coef':out['coef'], 'estimator':out['estimator']}))
"""
    env = dict(os.environ, PYTHONPATH=f"{ROOT}:{ROOT / 'backend'}")
    # Exercise local estimation only; never load or change real login credentials.
    env["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
    env.pop("ECONPAPER_DEPENDENCY_ROOT", None)
    env.pop("ECONPAPER_CARD_CSV", None)
    env.pop("ECONPAPER_CARD_EXTRACT", None)
    result = subprocess.check_output([str(ROOT / environment / ".venv/bin/python"), "-c", code], cwd=ROOT, env=env, text=True)
    return json.loads(result.splitlines()[-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    STATE.mkdir(parents=True, exist_ok=True)
    manifest = STATE / "manifest.json"
    if args.capture:
        assert not manifest.exists(), "Refusing to overwrite migration baseline"
        data = {"trees": {}, "head": git(ROOT, "rev-parse", "HEAD"), "page_sha256": sha(ROOT / "frontend/public/_tmp-choice-progressive.html")}
        for old, new in MOVES.items():
            base = ROOT.parent / old
            assert base.is_dir() and not (ROOT / new).exists()
            data["trees"][new] = inventory(base)
        dependency = ROOT.parent / "经济学论文/dependencies/StatsPAI"
        data["dependency_refs"] = git(dependency, "for-each-ref", "--format=%(refname) %(objectname)")
        data["dependency_status"] = git(dependency, "status", "--porcelain")
        for name in ("README.md", "AGENTS.md"):
            (STATE / ("original-research-" + name)).write_bytes((ROOT.parent / "经济学论文" / name).read_bytes())
        data["estimates"] = {name: estimate(name) for name in ("backend", "agent")}
        manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        manifest.chmod(0o600)
        print(json.dumps({"captured": True, "entries": sum(map(len, data["trees"].values()))}))
        return
    data = json.loads(manifest.read_text())
    for old, new in MOVES.items():
        assert not (ROOT.parent / old).exists(), f"Old directory still exists: {old}"
        assert (ROOT / new).is_dir() and not (ROOT / new).is_symlink()
        current = inventory(ROOT / new)
        assert set(current) == set(data["trees"][new]), f"File inventory changed: {new}"
        for path, expected in data["trees"][new].items():
            if f"{new}/{path}" in EDITED:
                assert sha(STATE / ("original-research-" + path)) == expected["sha256"]
            else:
                assert current[path] == expected, f"Changed migrated content: {new}/{path}"
    dependency = ROOT / "research/dependencies/StatsPAI"
    assert git(dependency, "for-each-ref", "--format=%(refname) %(objectname)") == data["dependency_refs"]
    assert git(dependency, "status", "--porcelain") == data["dependency_status"]
    assert git(ROOT, "rev-parse", "HEAD") == data["head"]
    assert sha(ROOT / "frontend/public/_tmp-choice-progressive.html") == data["page_sha256"]
    for name in MOVES.values():
        assert git(ROOT, "check-ignore", f"{name}/.migration-probe") == f"{name}/.migration-probe"
        assert f"{name}/" in (ROOT / ".dockerignore").read_text().splitlines()
    estimates = {}
    for name, before in data["estimates"].items():
        after = estimate(name)
        assert Path(after["source"]).is_relative_to(dependency)
        assert after["dependency"]["installed"] and after["dependency"]["source_matches_repo"]
        assert {k: after[k] for k in ("rows", "columns", "coef", "estimator")} == {k: before[k] for k in ("rows", "columns", "coef", "estimator")}
        estimates[name] = after
    result = {"passed": True, "verified_entries": sum(map(len, data["trees"].values())), "estimates": estimates}
    (STATE / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
