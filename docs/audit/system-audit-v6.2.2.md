# System audit — v6.2.2

Date: 2026-08-25  
Scope: ChatGPT runtime integrity for landing creation

## Finding

A ChatGPT execution described obsolete roles and gates even though the active system contains only agents `00`–`07` and gates `G0`–`G5`. Repository search exposed historical audits and a stale audit index, allowing retrieval to mix retired architectures with the current pipeline. The same chat then built manually and admitted that the harness had not governed the work.

## Correction

The repository keeps its history, but ChatGPT no longer receives the entire repository. `tools/build_chatgpt_pack.py` creates a current-only runtime directory and ZIP containing the active entrypoint, agents, pipeline, methods, templates, validators and interactive harness. It excludes historical audits, changelog, decision history and tests, writes `START-HERE.md`, records file hashes and fails if known legacy architecture tokens leak into the package.

## KEEP

- Historical audits remain available to maintainers in the source repository.
- Eight active roles, six gates and thirteen stages.
- `CHAT_INTERACTIVE` as the supported ChatGPT execution adapter.

## IMPROVE

- Replace the ChatGPT Project files whenever the runtime version changes; do not append new ZIPs beside old ones.

## ADD

- A reproducible clean runtime pack and ZIP.
- Automated legacy-token and current-version tests.

## REMOVE

- Historical architecture from the context supplied to ChatGPT Projects.
- The stale audit pointer to v4.17.

## Scenario verdicts

- Source repository maintenance: `SUPPORTED`, including history.
- ChatGPT Project using the generated runtime pack: `SUPPORTED`.
- ChatGPT Project using the full historical repository: `UNSUPPORTED` due to context contamination.
- Manual build outside `chat-start/chat-next`: `BLOCKED` by current entry contract.

## Verification

The pack tests prove that current runtime files and the interactive harness are present, historical audits are absent, the embedded version matches the system and forbidden legacy identifiers do not appear. The full suite and governance validators pass.

## Next review

After the next real ChatGPT Project run using only the v6.2.2 package, or earlier if it cites a role outside `00`–`07`.
