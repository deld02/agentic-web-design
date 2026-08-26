# System audit — v6.3.0

Date: 2026-08-25  
Scope: source organization and runtime integrity for landing creation

## Finding

The system behaved correctly but repeated the runtime inventory, common validator helpers and effect eligibility across several files. Two critical modules remained large, and CI could not prevent those boundaries from degrading again.

## Correction

One declarative runtime inventory now drives both source validation and ChatGPT packaging. Shared parsing/media primitives have one owner, the harness CLI is separated from its execution engine, and effect eligibility has one documentary authority. A dependency-free architecture check enforces unique ownership, forbidden import edges, runtime integrity and line-count ratchets in CI.

## KEEP

- Eight operational roles, six gates and thirteen ordered stages.
- Existing public harness commands and deterministic project validators.
- Historical audit and decision evidence outside the ChatGPT runtime context.

## IMPROVE

- Continue lowering the line budgets of `evaluation_harness.py`, `project_validation.py` and `test_semantics.py` through cohesive extractions.
- Add new architecture rules only for observed failure modes, not speculative abstractions.

## ADD

- `config/runtime-files.json` as runtime authority.
- `tools/validation_common.py`, `tools/harness_cli.py` and `tools/code_quality.py`.
- A maintenance map and CI architecture test.

## REMOVE

- Duplicate runtime inventories and duplicate Markdown/media helper implementations.
- Repeated effect-eligibility rules outside their owning method.
- Generated distribution output from version-controlled source state.

## Scenario verdicts

- Source repository maintenance: `SUPPORTED` with enforced boundaries.
- ChatGPT Project using the generated v6.3.0 runtime pack: `SUPPORTED`.
- Existing landing pipeline and external image loop: `UNCHANGED`.
- Arbitrary growth of critical modules or duplicated helpers: `BLOCKED` by CI.

## Verification

All system validators, governance audits, the clean-pack checks and 126 unit tests pass. The runtime package retains the same public entrypoint and excludes maintenance-only safety and quality configuration.

## Next review

After the next real ChatGPT Project run using only the v6.3.0 package, or earlier if an architecture ratchet needs to be raised rather than lowered.
