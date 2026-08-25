# v2 → v2.1 · Three-Perspective Audit

**Date:** 2026-08-19  
**Scope:** core architecture, every registered agent, pipeline, gates, status semantics, project templates, CI and the then-included project skeleton.

## Executive result

v2 was structurally coherent but **not fail-closed**. It passed DAG/shape validation while allowing semantically impossible project states. It also lacked independent task validation and independent functional QA. v2.1 closes those gaps.

Final audited shape:

- 18 registered agents;
- 15 formal gates G0–G14;
- 28 stages/checkpoints;
- 0 dependency cycles;
- explicit semantic `entry_requires`;
- 12 mutation/lifecycle/security tests;
- JSON Schema validation for project status/config;
- independent Experience Validation + Functional QA;
- content finalization before implementation;
- machine-derived release eligibility.

---

# Perspective A — Agent architecture & governance

## Question

Can ownership, state and review logic prevent one agent from bypassing another or downstream work from starting on unapproved upstream work?

## Findings in v2

### A1 — DAG completion was confused with approval — CRITICAL

`depends_on` described execution order, but the system had no machine-readable condition saying “G5 must actually be APPROVED”. A DRS checkpoint could be `BLOCKED` while a later stage remained structurally reachable.

**Fix:** every stage now has `entry_requires.gates` and `entry_requires.checkpoints`. Validator rejects `ACTIVE/APPROVED` work whose semantic prerequisites are not satisfied.

### A2 — Reviewer checkpoints needed temporal semantics — HIGH

A first v2.1 draft required a reviewed gate to remain exactly `REVIEW`, which made a finished lifecycle inconsistent after the gate progressed to `APPROVED`.

**Fix:** reviewer checkpoints accept `REVIEW | APPROVED` as historical parent state, while gate approval invariants still prevent a gate becoming approved before its required checkpoints.

### A3 — Content had an initial owner but no finalization pass — HIGH

Late Red Team/design changes could leave final copy lengths/claims out of sync before implementation.

**Fix:** C01 gains `finalization`; frontend cannot begin until the checkpoint is approved.

### A4 — Scaling different project types was implicit — MEDIUM

Every project had the same apparent depth.

**Fix:** `config/profiles.json` adds `lean | standard | critical`. Core gates remain non-skippable; evidence depth scales. Critical requires observed-user validation.

## Governance verdict

**PASS after v2.1.** There is now a machine-enforced distinction between execution, review and approval. No registered downstream stage is allowed to begin merely because its predecessor ran.

---

# Perspective B — Real production / UX / conversion operation

## Question

If the documents are correct, can the system still ship something that looks good but fails as a real website?

## Findings in v2

### B1 — No independent experience validation — CRITICAL

03 designed flows and 11 challenged them intellectually, but there was no owner for task validation. The system could therefore prove internal coherence without proving that a user can understand/complete a critical task.

**Fix:** new `V01 · Experience Validation` before G10. It works from `ux/validation-plan.md` and explicitly labels evidence `HEURISTIC | OBSERVED_USER | BEHAVIORAL_DATA`.

Important safeguard: an AI walkthrough can never be called observed-user evidence.

### B2 — No independent functional QA — CRITICAL

09 implemented and self-tested; 10 was visual QA. A dead CTA, broken form, anchor or recovery state could theoretically pass the visual layer.

**Fix:** new `Q01 · Functional QA`. G11 remains in `REVIEW` until Q01 tests actual behavior; Visual QA cannot start until G11 + Q01 are approved.

### B3 — UX success criteria were not an explicit artifact — HIGH

V01 would otherwise have to infer tasks from flow diagrams.

**Fix:** G3 now requires `ux/validation-plan.md` with start, success, failure/recovery and priority.

### B4 — Project criticality was not tied to evidence quality — MEDIUM

**Fix:** critical delivery profile requires `experience_validation_target: observed-users`. If real sessions do not exist, the system blocks or requires explicit profile/target change; it cannot fake the evidence.

## Production verdict

**PASS for the core.** The system now independently validates four different things: intended UX (V01), functional behavior (Q01), rendered fidelity (10), and accessibility/performance (12). These are no longer conflated.

Residual external dependencies are explicit, not hidden defects: observed-user testing requires real participants; integrations require the corresponding extension/environment; browser QA requires a running build.

---

# Perspective C — Repository engineering, CI & maintainability

## Question

Does the repository actually detect corruption, or does it merely describe a good process?

## Destructive tests against v2

### C1 — Impossible release state passed validation — CRITICAL

Mutation used:

- all G0–G14 = `APPROVED`;
- zero real evidence;
- every checkpoint = `BLOCKED`;
- `release.eligible = true`.

**v2 result:** `OK` / exit 0.

**v2.1:** fails.

### C2 — Broken agent contract returned exit 0 — CRITICAL

Removed a required heading from UI agent.

**v2 result:** `audit_agents.py` printed `1 problems` but exited 0.

**v2.1:** exits non-zero; CI fails closed.

### C3 — JSON Schema existed but was not executed — HIGH

The repo contained a schema but validator only performed ad-hoc checks.

**Fix:** CI installs `jsonschema`; status and project config are validated against Draft 2020-12 schemas. Unknown top-level status/config fields are rejected.

### C4 — No regression tests for validator semantics — HIGH

**Fix:** `tests/test_semantics.py` now includes positive and negative lifecycle tests.

Current tests prove:

1. clean repo passes;
2. impossible release fails;
3. approved gate without evidence fails;
4. unsatisfied entry condition fails;
5. unknown schema field fails;
6. broken agent contract exits non-zero;
7. fully approved lifecycle through post-release Intelligence is representable;
8. critical profile without observed users fails;
9. a newly scaffolded project validates cleanly;
10. an active extension without a contract fails;
11. a DAG edge without a semantic entry condition fails.
12. GitHub Actions referenced by CI must be pinned to a full 40-character commit SHA.

### C5 — Extension IDs were free-form — MEDIUM

A project could name an extension that had no actual contract.

**Fix:** an active extension `"seo"` now requires `extensions/seo.md`; missing contracts fail validation.

### C6 — CI actions were referenced by movable major tags — MEDIUM

The workflow used `actions/checkout@v7` and `actions/setup-python@v7`. That is convenient but does not make the referenced code immutable.

**Fix:** external GitHub Actions are pinned to full commit SHAs, the validator rejects non-SHA action references, and Dependabot is configured to propose GitHub Actions updates.

## Engineering verdict

**PASS after v2.1.** The key improvement is that correctness claims are now tested adversarially. A green CI has materially stronger meaning than in v2.

---

# Agent-by-agent cross-check

| Agent | Architecture/governance | Production lens | Engineering / evidence lens | Verdict |
|---|---|---|---|---|
| 00 Orchestrator | Sole state owner; entry conditions enforced | release cannot bypass QA | derived eligibility + fail-closed | PASS |
| 01 Strategy | clear business ownership | protects priorities/claims | assumptions explicit | PASS |
| 02 Design Research | distinct from DRS | global evidence before design | provenance/confidence | PASS |
| 03 UX Architecture | owns structure, not copy/style | adds task validation plan | artifact now gate-required | PASS |
| C01 Content | explicit owner + finalization pass | prevents late placeholder/claim drift | checkpoint tracked | PASS |
| 04 Art Direction | visual owner clear | DRS formal reviewer | G5 checkpoint enforced | PASS |
| 05 Design System | foundation/stabilize split | avoids premature generic system | reopens G6 if material | PASS |
| 06 UI | composition ownership clear | real/representative content | DRS log required | PASS |
| DRS | transversal, not pseudo-owner | prevents generic/copied patterns | formal checkpoints + provenance | PASS |
| 08 Responsive | owns touch/recomposition | not desktop shrink | G8 before motion | PASS |
| 07 Motion | no circular dependency | reduced-motion/fallback | DRS+12+09 checkpoints | PASS |
| 09 Frontend | feasibility + implementation separated | cannot self-certify function | Q01 independently challenges build | PASS |
| V01 Experience Validation | independent from UX owner | task/evidence validation | checkpoint + target policy | PASS |
| 11 Design Critic | adversarial, no redesign | pre-code + build pass | critical findings block release | PASS |
| Q01 Functional QA | independent from implementer | tests actual actions/states | repro + closure evidence | PASS |
| 10 Visual QA | visual ownership isolated | real-browser render/regression | evidence-based closure | PASS |
| 12 A11y/Performance | shift-left + final gate | manual + measured limitations | dated standards/evidence | PASS |
| 13 Design Intelligence | cannot self-promote rules | learns without contaminating projects | scope/confidence/review-by | PASS |

---

# What “perfect” still cannot mean

No general web system can guarantee a perfect result independent of inputs and environment. v2.1 intentionally refuses to fake the following:

- real-user evidence without real users;
- production integration evidence without the actual integration;
- field performance data without field data;
- legal/privacy certainty without the appropriate specialist context;
- evergreen visual/technical research without freshness review.

These are boundary conditions, not silent holes. The system either asks for/activates the required evidence or records the limitation/blocker.

## Final judgment

**v2: NOT perfect / not safe enough.**  
**v2.1: structurally production-grade for the stated core, with explicit boundaries and no critical finding remaining from these three audits.**
