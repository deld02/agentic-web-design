# Maintenance map

This directory is for maintainers. It is deliberately excluded from the ChatGPT runtime pack.

## Authorities

- `config/pipeline.json`: execution order and ownership.
- `config/runtime-files.json`: runtime-pack contents and critical runtime inventory.
- `tools/validation_common.py`: shared Markdown/JSON/media primitives.
- `docs/methods/image-decisions.md`: visual formats, image roles and external handoff.
- `docs/methods/effect-selection.md#3-mechanism-eligibility`: sole authority for non-static behavior eligibility.
- `repo-manifest.json`: system version mirrored by versioned runtime configurations and checked by `validate_system.py`.

Agent contracts route work to these authorities; they do not restate their rules. Reviewers report findings and do not edit another owner's artifact.

## Repository layers

1. Runtime: files selected by `config/runtime-files.json` and copied to the clean ChatGPT package.
2. Verification: `tools/`, `tests/` and CI. Deterministic checks validate structure and evidence; rendered design quality remains an independent 07 judgment.
3. History: `CHANGELOG.md`, `DECISIONS.md` and `docs/audit/`. These explain evolution and never enter the runtime context.
4. Generated output: `.harness/` and `dist/`. Both are reproducible and ignored by version control.

## Change procedure

1. Change the narrowest authority; update routing text only when its interface changes.
2. Do not add a second inventory, helper implementation or mechanism rule.
3. Lower code-quality budgets after extracting a responsibility; never raise them merely to make CI green.
4. Run `python tools/code_quality.py`, system validators and the full test suite.
5. Build a fresh ChatGPT package and inspect its runtime manifest.
