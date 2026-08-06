# Evolution Landscape · OpenEvolve / ShinkaEvolve / EvoAgentX

Date: 2026-08-06  
Scope: evaluator-driven evolve loops for **empirical-paper-workbench**  
Related: `runtime/full_pipeline.py`, `runtime/continuous_loop.py`, H8 Continuous evolution (structure audit)

## One-line recommendation

**第一刀不要装整套外框。** 在本仓做 **custom OpenEvolve-style loop**：genome = 可演化工件（写作/策略/配置），fitness = `full_pipeline` 复合分（repro + quality + latex/pdf）。Shinka / EvoAgentX 作后续可选升级，不是首嵌。

```text
  外部框架                    本仓现状                    第一刀
  ────────                    ────────                    ──────
  OpenEvolve  ──风格──►  continuous_loop + quality  ──►  custom score loop
  ShinkaEvolve ──重引擎──► (未接)                     ──►  第二阶段可选
  EvoAgentX    ──工作流进化──► (未接)                  ──►  多 agent 拓扑后再说
```

---

## 1. Three systems at a glance

| | **OpenEvolve** | **ShinkaEvolve** | **EvoAgentX** |
|--|----------------|------------------|---------------|
| Origin | Open AlphaEvolve-style coding agent | SakanaAI; sample-efficient program evolution (ICLR 2026) | Self-evolving agent **workflows** |
| Mutates | Code (file / function / island MAP-Elites) | Programs (archive + island; local/Slurm jobs) | Prompts, tools, **workflow topology** |
| Fitness | User `evaluate(program_path) → metrics` | User `evaluate.py` job + validator | Task metrics (F1, pass@1, …) + TextGrad/AFlow/MIPRO |
| Best for | Single-program optimization with a hard score | Scientific code with verifiers; high sample efficiency | Multi-agent workflow auto-build + optimize |
| Fit to this repo | **High as pattern** (eval-first code loop) | High if later evolving estimation/do-files | Medium; different unit of evolution |
| Install tax | Low | Medium (Hydra/jobs/async) | Medium-high (full agent platform) |

Sources (public):

- OpenEvolve: <https://github.com/algorithmicsuperintelligence/openevolve> (also historical `codelion/openevolve`)
- ShinkaEvolve: <https://github.com/SakanaAI/ShinkaEvolve> · blog <https://sakana.ai/shinka-evolve/>
- EvoAgentX: <https://github.com/EvoAgentX/EvoAgentX> · arXiv:2507.03616

---

## 2. Minimal install / API (copy-paste surface)

### 2.1 OpenEvolve

```bash
pip install openevolve
# Python 3.10+; any OpenAI-compatible LLM
export OPENAI_API_KEY="..."   # Gemini/OpenAI/local proxy all use this env name often
```

**CLI shape** (seed program + evaluator + yaml):

```bash
python openevolve-run.py \
  path/to/initial_program.py \
  path/to/evaluator.py \
  --config path/to/config.yaml \
  --iterations 50
```

**Library shape** (no external files required for smoke):

```python
from openevolve import run_evolution, evolve_function

result = run_evolution(
    initial_program="""
def search(...):
    ...
""",
    evaluator=lambda path: {"score": float(...)},  # path → metrics dict
    iterations=100,
)
# or
result = evolve_function(fn, test_cases=[...], iterations=50)
print(result.best_code)
```

**Evaluator contract** (examples return metrics; newer builds may wrap `EvaluationResult`):

```python
def evaluate(program_path: str) -> dict:
    # load program_path, run, return numeric metrics
    return {
        "score": 0.85,           # primary fitness (higher better, by convention)
        "value_score": 0.9,
        "distance_score": 0.7,
        # optional side metrics for MAP-Elites feature dims
    }
```

**Config knobs** (yaml): `llm.primary_model` / `api_base`, `database.population_size` / `num_islands`, `evaluator.timeout` / `parallel_evaluations`, `diff_based_evolution`.

**What to steal for this repo:** (1) `evaluate(path) → metrics` hard contract; (2) island/archive optional later; (3) cascade early-fail on broken candidates; (4) LLM only as mutation operator, never as score.

### 2.2 ShinkaEvolve

```bash
pip install shinka-evolve
# import name: shinka
# or: uv pip install shinka-evolve
shinka_launch variant=circle_packing_example
```

**Python API** (unified runner):

```python
from shinka.core import ShinkaEvolveRunner, EvolutionConfig
from shinka.database import DatabaseConfig
from shinka.launch import LocalJobConfig  # also SlurmCondaJobConfig, SlurmDockerJobConfig

job_conf = LocalJobConfig(eval_program_path="evaluate.py")
db_conf = DatabaseConfig()
evo_conf = EvolutionConfig(init_program_path="initial.py")

runner = ShinkaEvolveRunner(
    evo_config=evo_conf,
    job_config=job_conf,
    db_config=db_conf,
    max_evaluation_jobs=2,
    max_proposal_jobs=3,
    max_db_workers=4,
)
runner.run()
```

**Eval pattern** (circle packing example): wrapper around `run_shinka_eval` + `adapted_validate_packing` → valid/invalid + metric (e.g. sum of radii). Jobs can be local process or Slurm.

**Agent skills** (optional, for Claude/Codex): `npx skills add SakanaAI/ShinkaEvolve --skill '*' ...` → setup / convert / run / inspect.

**When to pull in:** sample-efficient archive search over **code that has a cheap verifier** (e.g. estimation script correctness + speed). **Not** first embed for full paper pipeline (too slow, job graph mismatch).

### 2.3 EvoAgentX

```bash
pip install evoagentx
# or: pip install git+https://github.com/EvoAgentX/EvoAgentX.git
export OPENAI_API_KEY=...
```

**Minimal workflow generate + run:**

```python
from evoagentx.models import OpenAILLMConfig, OpenAILLM
from evoagentx.workflow import WorkFlowGenerator, WorkFlow
from evoagentx.agents import AgentManager
import os

cfg = OpenAILLMConfig(
    model="gpt-4o-mini",
    openai_key=os.getenv("OPENAI_API_KEY"),
    stream=True,
    output_response=True,
)
llm = OpenAILLM(config=cfg)

goal = "Generate html code for the Tetris game"
graph = WorkFlowGenerator(llm=llm).generate_workflow(goal)
mgr = AgentManager()
mgr.add_agents_from_workflow(graph, llm_config=cfg)
wf = WorkFlow(graph=graph, agent_manager=mgr, llm=llm)
print(wf.execute())
```

**Evolution layer** (not the first API you call): TextGrad, MIPRO, AFlow, EvoPrompt - optimize prompts / structure of multi-agent graphs against benchmark datasets.

**When to pull in:** if product goal becomes “evolve the multi-agent paper workflow graph itself.” Current workbench already has a fixed 10-step spine + L8; importing EvoAgentX as outer OS is high thrash.

---

## 3. Fit to empirical-paper-workbench

### What already exists (do not reinvent)

| Piece | Path / symbol | Role in evolve loop |
|-------|---------------|---------------------|
| 10-step E2E | `runtime/full_pipeline.py` `FullPaperPipeline` | **Run** candidate end-to-end |
| L8 evaluate | `runtime/continuous_loop.py` `evaluate_after_pipeline` | Verdict / repro / green check |
| Learn plan | `build_learn_plan` | Maps reds → rewrite/degrade/halt |
| Quality report | `Program.workbench.paper_quality` via step_07 | Structured quality JSON |
| REPRO | step_09 prints `REPRO_OK` | Hard bit in fitness |
| Continuous loop | `ContinuousEmpiricalLoop` | Outer rounds with max_rounds fuse |
| CLI | `Product.cli continuous-loop` | Human entry |

Audit residual (from `02_L8_IMPLEMENTATION.md`): **H8 cross-run evolution 未接** - this document is the materials for that next structure, not a claim that H8 is done.

### Why not `pip install openevolve` as the product loop

1. OpenEvolve assumes **mutating a program file** and scoring a **fast numeric bench**. Our unit is a **paper run** (data gate → OLS → write → quality → repro → optional latex), minutes not milliseconds.
2. MAP-Elites island DB is overkill until we have a stable scalar fitness and a clear genome.
3. LLM provider in this repo is already MiniMax/Grok/Pi-shaped; bolting OpenEvolve’s yaml LLM stack duplicates cost control and keys.
4. Integrity rules (no fake citations, OLS ≠ causal) must stay **inside evaluator**, not hope the evolver “learns” honesty.

### Why OpenEvolve-**style** is still the right first embed

```text
  OpenEvolve core (steal)
  ─────────────────────
  genome  →  mutate with LLM
  run     →  isolated candidate
  score   →  pure evaluator (no LLM in score if possible)
  select  →  keep best / archive
  stop    →  max_iter or threshold

  Map onto workbench
  ──────────────────
  genome  →  writing strategy / section draft / pipeline flags / prompt cards
  run     →  FullPaperPipeline.run(...)  (or only_steps tail)
  score   →  score_full_pipeline(...) = repro + quality + latex_pdf
  select  →  best-so-far under continuous_loop fuse
  stop    →  max_rounds / completed_green / halted_honest
```

Shinka = later if genome is **scientific code** with a tight verifier.  
EvoAgentX = later if genome is **agent graph topology**.

---

## 4. Recommended fitness: `full_pipeline` composite score

Primary scalar for evolution (higher = better). All terms must be **machine-checkable**.

| Component | Weight (v0) | Source | Pass semantics |
|-----------|-------------|--------|----------------|
| **repro** | 0.40 | step_09: exit 0 and `REPRO_OK` in stdout; coef match main_results | 0 or 1 |
| **quality** | 0.40 | `*_full_pipeline_quality.json` verdict | mapped float |
| **latex_pdf** | 0.20 | `paper.tex` / `paper.pdf` size + compile success (xelatex/pdflatex) | 0 or 1 (or partial) |

### Quality mapping (v0, explicit)

```text
ready_for_review (and no blocking)     → 1.00
soft-only residual                     → 0.65
blocking but completed pipeline        → 0.35
pipeline failed / repro fail           → 0.00 (or hard abort before quality)
```

Blocking set (align `continuous_loop.BLOCKING_VERDICTS`):

- `too_thin`, `missing_sections`, `section_length_gate_required`
- `evidence_integrity_blocked`, `format_gate_required`

Soft set: `needs_literature_review`, `method_gate_required`, `needs_review_loop`, `evidence_integrity_needs_review`.

### Optional sub-metrics (log only; do not replace scalar until calibrated)

- `char_count` / section lengths (anti-too_thin)
- `citation.verified_count` (currently often 0 - must not invent bib to game score)
- `claim_bind_ok` (when bind-or-block lands)
- wall-clock cost / token cost (budget pressure)

### Integrity floor (non-negotiable)

If quality report or integrity audit flags fabrication patterns, **fitness = 0** regardless of length.  
Never reward “fake verified bibliography” or causal language on OLS-only runs.

---

## 5. Genome choices for v0 (keep one)

| Genome | Mutate | Eval cost | Recommend |
|--------|--------|-----------|-----------|
| **A. Writing / expand prompts + paper draft** | LLM rewrite of `Manuscripts/generated/*_paper.md` or step_06 prompts | 1× write + quality + (optional full) | **Yes - first** |
| **B. Pipeline policy** | flags: `expand_mode`, degrade, method list, control sets | full or partial steps | Second |
| **C. Estimation code** | `replication/*.py` / adapter snippets | repro + numerical | Shinka later |
| **D. Multi-agent graph** | node/edge of agent workflow | whole product | EvoAgentX later |

v0 = **A**: continuous_loop already rewrites via expand/degrade (+ optional Pi). Evolution adds **multi-candidate archive** + **scalar selection** across rounds/runs (true H8), not only single-line rewrite.

---

## 6. Concrete Python skeleton (custom OpenEvolve-style)

Path suggestion (not created by this materials note):  
`runtime/evolution/pipeline_evolve.py`  
Optional CLI later: `python -m Product.cli evolve-pipeline --max-gen 5`

```python
"""OpenEvolve-style loop around FullPaperPipeline composite score.

v0 genome: paper draft text (or writing prompt card).
v0 fitness: repro + quality + latex/pdf (see evolution_landscape.md §4).

No dependency on pip install openevolve required.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from runtime.full_pipeline import FullPaperPipeline, ROOT, _now, _write_json
from runtime.continuous_loop import (
    BLOCKING_VERDICTS,
    SOFT_VERDICTS,
    evaluate_after_pipeline,
)

# ── Fitness ──────────────────────────────────────────────────────────────────

BLOCKING = BLOCKING_VERDICTS
SOFT = SOFT_VERDICTS


@dataclass
class Fitness:
    score: float
    repro: float
    quality: float
    latex_pdf: float
    verdict: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def as_metrics(self) -> dict[str, float]:
        """OpenEvolve-compatible metrics dict."""
        return {
            "score": self.score,
            "repro": self.repro,
            "quality": self.quality,
            "latex_pdf": self.latex_pdf,
        }


def map_quality(verdict: list[str], *, pipeline_ok: bool, repro_ok: bool) -> float:
    if not pipeline_ok or not repro_ok:
        return 0.0
    v = set(verdict or [])
    if v & BLOCKING:
        return 0.35
    if v & SOFT:
        return 0.65
    if not v or v <= {"ready_for_review"}:
        return 1.0
    return 0.5


def check_latex_pdf(root: Path = ROOT) -> float:
    """1.0 if usable PDF; 0.5 if tex only; 0.0 if neither."""
    pdf = root / "paper.pdf"
    tex = root / "paper.tex"
    # also accept Manuscripts/generated artifacts if present
    candidates = [
        pdf,
        root / "Manuscripts" / "generated" / "paper.pdf",
        root / "output" / "paper.pdf",
    ]
    for p in candidates:
        if p.exists() and p.stat().st_size > 1000:
            return 1.0
    if tex.exists() and tex.stat().st_size > 200:
        # try one compile (best-effort; do not fail fitness hard on tool missing)
        try:
            r = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", tex.name],
                cwd=str(tex.parent),
                capture_output=True,
                text=True,
                timeout=120,
            )
            out_pdf = tex.with_suffix(".pdf")
            if out_pdf.exists() and out_pdf.stat().st_size > 1000:
                return 1.0
            if r.returncode == 0:
                return 0.7
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return 0.5
        return 0.5
    return 0.0


def score_after_pipeline(pipe: FullPaperPipeline, *, w_repro=0.4, w_q=0.4, w_pdf=0.2) -> Fitness:
    ev = evaluate_after_pipeline(pipe)
    repro = 1.0 if ev.get("repro_ok") else 0.0
    pipeline_ok = ev.get("pipeline_status") == "completed"
    q = map_quality(list(ev.get("verdict") or []), pipeline_ok=pipeline_ok, repro_ok=bool(ev.get("repro_ok")))
    pdf = check_latex_pdf()
    # integrity floor: evidence_integrity_blocked → zero
    if "evidence_integrity_blocked" in (ev.get("verdict") or []):
        total = 0.0
    else:
        total = w_repro * repro + w_q * q + w_pdf * pdf
    return Fitness(
        score=round(total, 4),
        repro=repro,
        quality=q,
        latex_pdf=pdf,
        verdict=list(ev.get("verdict") or []),
        details=ev,
    )


# ── Genome / population ──────────────────────────────────────────────────────

@dataclass
class Individual:
    id: str
    genome: dict[str, Any]  # e.g. {"paper_path": "...", "expand": True, "notes": "..."}
    fitness: Fitness | None = None
    pipeline_run_id: str | None = None


Mutator = Callable[[Individual, int], Individual]
# mutator(parent, generation) -> child with new genome (LLM rewrite, flag flip, ...)


def default_mutator(parent: Individual, generation: int) -> Individual:
    """Stub: flip expand/degrade and attach learn notes. Replace with LLM/Pi rewrite."""
    g = dict(parent.genome)
    g["expand"] = True
    g["degrade"] = True
    g["notes"] = f"evolve gen={generation} from={parent.id}"
    # optional: copy paper to a gen-specific path so runs do not clobber
    return Individual(id=f"gen{generation}_{int(time.time())}", genome=g)


def run_individual(ind: Individual, *, use_llm: bool = False) -> Individual:
    """One FullPaperPipeline evaluation for this genome."""
    only = ind.genome.get("only_steps")  # None = full 10; or REWRITE_TAIL
    pipe = FullPaperPipeline(
        use_llm=use_llm,
        run_id=f"evolve_{ind.id}",
        expand_mode=bool(ind.genome.get("expand")),
        degrade_mode=bool(ind.genome.get("degrade")),
        learn_notes=str(ind.genome.get("notes") or ""),
    )
    # If genome points at a candidate paper, ensure pipeline ctx sees it
    paper = ind.genome.get("paper_path")
    if paper:
        pipe.ctx["paper_path"] = str(paper)
    record = pipe.run(only_steps=only)
    ind.pipeline_run_id = record.run_id
    ind.fitness = score_after_pipeline(pipe)
    return ind


# ── Evolution loop ───────────────────────────────────────────────────────────

@dataclass
class EvolveConfig:
    max_generations: int = 5
    population_size: int = 1          # v0: (1+1)-ES; raise when eval is cheaper
    elite_k: int = 1
    use_llm: bool = False
    score_threshold: float = 0.95     # stop early if score >= this and ready_for_review
    work_dir: Path = field(default_factory=lambda: ROOT / "state" / "runs" / "evolve")


@dataclass
class EvolveResult:
    best: Individual
    history: list[dict[str, Any]]
    status: str  # completed_threshold | max_generations | failed


def evolve(
    seed: Individual,
    *,
    mutate: Mutator = default_mutator,
    cfg: EvolveConfig | None = None,
) -> EvolveResult:
    cfg = cfg or EvolveConfig()
    cfg.work_dir.mkdir(parents=True, exist_ok=True)
    history: list[dict[str, Any]] = []

    # evaluate seed
    pop = [run_individual(seed, use_llm=cfg.use_llm)]
    best = pop[0]
    _checkpoint(cfg.work_dir, 0, pop, best)

    for gen in range(1, cfg.max_generations + 1):
        children: list[Individual] = []
        for _ in range(cfg.population_size):
            child = mutate(best, gen)
            child = run_individual(child, use_llm=cfg.use_llm)
            children.append(child)

        candidates = sorted(
            [best, *children],
            key=lambda x: (x.fitness.score if x.fitness else -1.0),
            reverse=True,
        )
        best = candidates[0]
        pop = candidates[: max(cfg.elite_k, 1)]
        history.append(
            {
                "gen": gen,
                "best_score": best.fitness.score if best.fitness else None,
                "best_id": best.id,
                "verdict": best.fitness.verdict if best.fitness else [],
                "metrics": best.fitness.as_metrics() if best.fitness else {},
            }
        )
        _checkpoint(cfg.work_dir, gen, pop, best)

        if (
            best.fitness
            and best.fitness.score >= cfg.score_threshold
            and set(best.fitness.verdict or []) <= {"ready_for_review", ""}
        ):
            return EvolveResult(best=best, history=history, status="completed_threshold")

    status = "max_generations"
    if best.fitness is None:
        status = "failed"
    return EvolveResult(best=best, history=history, status=status)


def _checkpoint(work_dir: Path, gen: int, pop: list[Individual], best: Individual) -> None:
    payload = {
        "gen": gen,
        "updated_at": _now(),
        "best": {
            "id": best.id,
            "genome": best.genome,
            "pipeline_run_id": best.pipeline_run_id,
            "fitness": asdict(best.fitness) if best.fitness else None,
        },
        "population": [
            {
                "id": i.id,
                "score": i.fitness.score if i.fitness else None,
                "verdict": i.fitness.verdict if i.fitness else None,
            }
            for i in pop
        ],
    }
    _write_json(work_dir / f"gen_{gen:03d}.json", payload)
    _write_json(work_dir / "latest.json", payload)


# ── Optional: OpenEvolve bridge (if installed) ────────────────────────────────

def openevolve_evaluator_bridge(program_path: str) -> dict[str, float]:
    """If you later wire openevolve CLI: program mutates a strategy file;
    this evaluator runs one pipeline and returns metrics dict.
    """
    # program_path would load strategy → Individual.genome
    # then run_individual + return fitness.as_metrics()
    raise NotImplementedError("bridge only after custom loop is green")


if __name__ == "__main__":
    seed = Individual(
        id="seed",
        genome={
            "expand": False,
            "degrade": False,
            "notes": "seed",
            "only_steps": None,  # full pipeline first generation
        },
    )
    result = evolve(seed, cfg=EvolveConfig(max_generations=3, population_size=1, use_llm=False))
    print(result.status, result.best.fitness)
    print("history:", json.dumps(result.history, ensure_ascii=False, indent=2))
```

### How this relates to `ContinuousEmpiricalLoop`

| | Continuous loop | Evolve skeleton |
|--|-----------------|-----------------|
| Rounds | Sequential rewrite of **one** lineage | Population + **select best** |
| Stop | green / honest halt / max_rounds | threshold / max_gen |
| Score | verdict sets (discrete) | **scalar** composite (+ archive) |
| H8 | L8 present; cross-run archive weak | Explicit checkpoint archive under `state/runs/evolve/` |

Practical merge path:

1. Land `score_after_pipeline` + unit tests on existing quality JSON fixtures.  
2. Run evolve with `population_size=1` (same as continuous loop, but score-logged).  
3. Raise population when write-only eval is cheap enough.  
4. Optional: wrap `score_after_pipeline` as OpenEvolve/Shinka evaluator **without** replacing product CLI.

---

## 7. Decision table (when to adopt what)

| Stage | Action | Done when |
|-------|--------|-----------|
| **Now** | Custom OpenEvolve-style loop + composite score | `evolve` writes `state/runs/evolve/latest.json`; score moves on real runs |
| **Next** | Archive best paper drafts across days; compare scores | H8 cross-run evolution visible in audit |
| **Later** | `pip install openevolve` only if mutating pure code modules | evaluator is <30s and fully isolated |
| **Later** | Shinka for estimation/replication code search | domain verifier stable (REPRO + numerical gates) |
| **Later** | EvoAgentX if product owns multi-agent topology search | fixed 10-step spine no longer SSOT |

---

## 8. Non-goals / risks

- Do **not** evolve fake literature into the score.  
- Do **not** let LLM self-grade quality without the structured quality report.  
- Do **not** run unbounded parallel full pipelines (cost, data clobber); isolate run_id and paper paths.  
- Do **not** replace `continuous_loop` SSOT until evolve is proven; keep evolve as additive H8 module.  
- PDF weight 0.20 is provisional; if latex is flaky on CI, temporarily set `w_pdf=0` and keep check as soft metric.

---

## 9. Sources (landscape)

| System | Install | Primary API | Notes |
|--------|---------|-------------|-------|
| OpenEvolve | `pip install openevolve` | `run_evolution` / `openevolve-run.py` + `evaluate(path)` | MAP-Elites, islands, OpenAI-compatible LLM |
| ShinkaEvolve | `pip install shinka-evolve` | `ShinkaEvolveRunner` + `LocalJobConfig(eval_program_path=...)` | `import shinka`; Hydra `shinka_launch` |
| EvoAgentX | `pip install evoagentx` | `WorkFlowGenerator` + TextGrad/AFlow/MIPRO optimizers | Workflow/agent evolution, not single-file fitness |

Local anchors:

- `runtime/full_pipeline.py` - 10-step run + REPRO_OK  
- `runtime/continuous_loop.py` - evaluate / learn / package  
- `docs/structure-audit/02_L8_IMPLEMENTATION.md` - H8 still open  

---

## 10. Next concrete action

Implement `runtime/evolution/score.py` with `score_after_pipeline` + one fixture test on an existing `Results/json/*_full_pipeline_quality.json`, then wire a dry-run evolve (`max_generations=1`, `use_llm=False`) that only scores the last full_pipeline package without mutating. That proves the fitness contract before any LLM mutation spend.
