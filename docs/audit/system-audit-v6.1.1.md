# System audit — v6.1.1

Date: 2026-08-24  
Scope: landing creation only

## Finding

An external ChatGPT conversation read the repository and treated the workflow as guidance, but never ran under the evaluation harness. It manually built HTML, omitted the required generated artistic master and still described the output as an Agentic Web Design result. The validators were not wrong; they were never placed in control of that execution.

## Correction

- Added one fail-closed execution boundary at the two operational entrypoints.
- `MANAGED` means the executor was launched by `evaluation_harness.py run` and received all five scoped `HARNESS_*` values.
- `UNMANAGED` permits inspection and advice only. It cannot research, design, generate, code or claim system compliance.
- The creative-master prompt now records `IMAGE_GEN` only after the real tool succeeds.
- No agent, stage or gate was added.

## Verification

The system remains eight agents, six gates and thirteen sequential stages. Tests cover the managed/unmanaged entry contract as well as the existing active-run and missing-image behavior.

## KEEP

- Eight owners, six gates and thirteen sequential stages.
- Physical artistic master plus real image-generation evidence.
- External harness as supervisor, not as a ninth design role.

## IMPROVE

- Make the invocation boundary visible before any creative response.

## ADD

- One fail-closed `MANAGED | UNMANAGED` entry decision.

## REMOVE

- The undocumented manual fallback that treated the repository as a checklist.

## Scenario verdicts

- Managed headless run: `SUPPORTED`.
- Unmanaged consultation/audit: `SUPPORTED` without creation.
- Unmanaged landing build claiming system compliance: `BLOCKED`.
- Missing headless executor: `NO_EXECUTOR`, with no fallback build.

## Boundary

A repository cannot technically control an unrelated chat. The harness can enforce behavior only when it launches the executor. Therefore `NO_EXECUTOR` is a legitimate blocking result; silently falling back to a manual build is not.

## Next review

After two genuine managed runs with a headless executor, or earlier if an unmanaged chat again claims a system delivery.
