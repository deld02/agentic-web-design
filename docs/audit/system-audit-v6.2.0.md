# System audit — v6.2.0

Date: 2026-08-24  
Scope: landing creation only

## Finding

The fail-closed v6.1.1 boundary correctly rejected false harness claims, but made ChatGPT-hosted execution impossible whenever the container had Python and project files but no invocable `codex` or `claude` CLI.

## Correction

The harness now supports two execution adapters over the same pipeline:

- `HEADLESS_MANAGED`: the existing external executor controlled by `run`.
- `CHAT_INTERACTIVE`: the current ChatGPT conversation controlled by `chat-start`, `chat-status`, `chat-image` and `chat-next`.

`chat-next` derives changed artifacts from the filesystem, validates the current stage and opens exactly one successor. It preserves the one-correction limit and user checkpoint. During `creative-master`, progression additionally requires `chat-image` to validate and register a physical raster inside the managed project.

## KEEP

- Eight owners, six gates and thirteen sequential stages.
- One authoritative pipeline and the same gate validators in both execution modes.
- The external final-image production loop.

## IMPROVE

- Exercise the complete interactive route with a real ChatGPT image-generation return.

## ADD

- A bounded in-chat executor adapter, not a new agent or workflow.
- Physical raster receipt before leaving `creative-master`.

## REMOVE

- The assumption that absence of a headless model CLI makes ChatGPT execution impossible.

## Scenario verdicts

- Headless CLI available: `SUPPORTED` through `run`.
- ChatGPT with Python and repository access: `SUPPORTED` through `CHAT_INTERACTIVE`.
- ChatGPT without local execution/file access: `BLOCKED`.
- Manual pipeline imitation or injected events: `BLOCKED`.

## Verification

The interactive runner opens one stage, rejects premature advancement and refuses image registration outside `creative-master`. The complete suite, system validator, state audit, agent audit and governance audit pass.

## Next review

After the first complete ChatGPT-interactive landing or earlier if a stage can be skipped or `creative-master` advances without a real raster receipt.
