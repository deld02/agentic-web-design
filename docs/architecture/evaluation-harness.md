# Evaluation harness

The harness actively supervises the operating system from outside its eight project roles. It does not add a pipeline stage or decide design quality by code.

## Contract

- The harness is fail-closed. A managed design execution is either launched by `run` or advanced stage-by-stage through `CHAT_INTERACTIVE`; reading the repository or merely initializing a run does not authorize a manual build.
- `harness/scenarios.json` defines reproducible briefs, risk focus and bounded execution limits.
- `doctor` proves whether a headless executor can actually start. The desktop application alone is not a CLI executor.
- `init` creates an isolated project run and a pending visual-review form.
- `run` invokes the supplied executor once per pipeline stage, passes a bounded stage prompt through stdin/environment, detects artifact writes, validates the resulting gate/checkpoint and performs at most one correction.
- `chat-start` and `chat-next` provide the same sequential control when the current ChatGPT conversation is itself the executor and cannot spawn another model CLI.
- `run` stops as `NEEDS_USER`, `FAILED`, `PARTIAL` or `COMPLETE`; it never spins indefinitely or silently simulates work.
- An executor may emit `HARNESS_EVENT {...}` lines for otherwise unobservable tool calls. Physical artifacts and gate validators remain authoritative.
- `evaluate` checks pipeline order, ownership, time/correction limits, physical master evidence, project state, approved gates and deterministic implementation defects.
- `capture` can create desktop/mobile browser evidence with a local Chrome/Edge binary.
- `packet` snapshots artifacts and physical evidence for an isolated agent-07 review.

The event log is diagnostic evidence, not authority. Project files, state, physical media, gate validators and the independent rendered review remain authoritative.

## Execution boundary

The repository cannot control an unrelated conversation unless it opts into the local controller. Enforcement begins either when `run` launches the model process or when ChatGPT starts `CHAT_INTERACTIVE` and advances exclusively through `chat-next`. An unmanaged chat may diagnose the system, but it cannot create a landing and claim harness compliance.

This boundary prevents the invalid fallback of reading the rules, writing HTML manually and later explaining which stages should have happened. `NO_EXECUTOR` blocks headless mode only; when local Python execution is available, ChatGPT can use `CHAT_INTERACTIVE` without installing another agent.

## Minimal use

```text
python tools/evaluation_harness.py doctor -- <executor> --help
python tools/evaluation_harness.py init --scenario institutional-event
python tools/evaluation_harness.py run --run-dir <run> -- <headless-executor-command>
python tools/evaluation_harness.py packet --run-dir <run>
```

ChatGPT-hosted execution without an external model CLI:

```text
python tools/evaluation_harness.py chat-start --scenario institutional-event
python tools/evaluation_harness.py chat-start --brief-file brief.txt
python tools/evaluation_harness.py chat-status --run-dir <run>
python tools/evaluation_harness.py chat-image --run-dir <run> --file <generated-master.png>
python tools/evaluation_harness.py chat-next --run-dir <run>
```

`chat-next` derives artifact writes from filesystem changes, validates the current owner, gate and checkpoint, and opens exactly one successor. It permits the same single correction and user checkpoint as `run`. `chat-image` works only during `creative-master`, requires a valid raster inside the managed project and records the generation receipt; without it, progression is blocked.

The harness sets `HARNESS_RUN_DIR`, `HARNESS_PROJECT_DIR`, `HARNESS_SCENARIO`, `HARNESS_STAGE`, `HARNESS_AGENT`, `HARNESS_MODE` and `HARNESS_PROMPT_FILE`. The stage prompt is also sent through stdin. `execute` remains available only as a low-level uninstrumented primitive; use `run` for an actual evaluation.

If `doctor` returns `NO_EXECUTOR`, use `CHAT_INTERACTIVE` when the current chat has Python and repository-file access. Otherwise install or provide a headless agent CLI. A packaged desktop application that Windows refuses to invoke cannot be driven by Python; the harness reports that limitation instead of pretending an external execution started.

## Deterministic UI checks

At evaluation, `tools/ui_quality_scan.py` inspects the configured implementation for observable defects such as removed focus without replacement, missing image alternatives, placeholder copy and layout-shift risks. Critical correctness defects block. AI-template signals such as `transition: all` or bounce easing remain advisory for 07; Python never declares a design beautiful or generic.

## Final visual review

`visual-review.json` is completed by agent 07 in isolated context after inspecting the executable landing, master, current references, responsive renders and interaction evidence. Every configured axis needs `PASS | REVISE`, concrete evidence and findings. A `PASS` with missing evidence or blocking findings is invalid.

Generated runs live under `.harness/runs/` and remain untracked. Each review packet is a physical snapshot so later file changes cannot silently alter the evidence that was judged.
