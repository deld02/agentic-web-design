# System audit — v6.4.0

Date: 2026-08-27
Scope: evidence freshness, runtime continuity and causal reopening

## Finding

The system could verify complete tables, physical files and source references while still accepting stale screenshots, content drift, non-exercised interactions or downstream approvals whose causal inputs had changed.

## Correction

Agent 02 now freezes exact material strings in the existing content artifact. G4 records unique desktop/mobile runtime evidence for every scene. A release-integrity manifest hashes the implementation tree, causal artifacts and traversal files. Owner 00 can reopen one causal gate through a controlled command that invalidates every downstream gate and checkpoint.

## KEEP

- Eight agents, six gates, thirteen stages and twelve core project artifacts.
- Human visual judgement by isolated agent 07.
- Existing Experience Spine, creative-master, media-production and delivery contracts.

## IMPROVE

- Runtime evidence remains capture-based; a future real project should determine which complex mechanisms justify automated browser state assertions.
- Content lock intentionally covers material strings, not every editorial sentence.

## ADD

- `validation_release_integrity.py` for content parity, traversal coverage and SHA-256 freshness.
- `reopen_project.py` for owner-00-only causal invalidation.
- Four adversarial regression tests covering drift, stale/reused evidence and ownership.

## REMOVE

- The possibility of retaining a valid release review after implementation or upstream artifacts change.
- The possibility of silently preserving downstream approval after a causal gate reopens.

## Scenario verdicts

- Exact thesis/CTA survival through build: `SUPPORTED`.
- Per-scene desktop/mobile runtime traversal: `SUPPORTED`.
- Stale evidence after code, asset or artifact change: `BLOCKED`.
- Causal reopening by owner 00: `SUPPORTED`.
- Automatic semantic judgement of animation quality: `OUT_OF_SCOPE`; agent 07 retains judgement.

## Verification

All system, architecture, packaging, governance and semantic validators pass. The 142-test suite includes four new adversarial integrity tests.

## Result

PASS. Documentation can no longer remain authoritative after the implementation or its causal design inputs change.

## Next review

After one real landing with pinned or scroll-linked state reveals whether the runtime table should gain automated state probes in addition to physical evidence.
