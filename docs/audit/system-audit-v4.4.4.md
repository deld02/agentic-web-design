# System Audit — v4.4.4

**Date:** 2026-08-21  
**Auditor:** Design OS Auditor / System Steward  
**Verdict:** PASS

## Scope

Landing creation only. This correction closes the path that allowed an agent to avoid all image production by declaring a typography-led direction.

## Finding

Truth classes and per-image production were sound once an image existed, but no gate required the first substantial visual asset. Zero `IMG-*` records therefore escaped the contract.

## KEEP

- truthful media classes and per-image ownership;
- the existing eight agents, six gates, twelve stages and twelve project artifacts;
- flexible intake that does not require the user to arrive with photos.

## IMPROVE

- judge whether each asset is genuinely substantial and project-specific during 07 review;
- inspect real runs for decorative compliance that adds an asset without strengthening the landing.

## ADD

- one cross-gate `VISUAL_PAYLOAD_REQUIRED` invariant;
- semantic gate checks and regression coverage.

## REMOVE

- the image-led conditional loophole;
- typography-only fallback inferred by the agent;
- logos, gradients, patterns and placeholders as false evidence of visual payload.

## Correction

- G2 requires one project-specific visual sample per direction.
- G3 requires the selected payload integrated in desktop and mobile.
- G4 requires at least one substantial `IMG-*` in `FINAL` with usable output.
- Missing user media triggers representative, conceptual or decorative production without fabricating documentary evidence.
- Only an explicit user request recorded as `USER_EXPLICIT_TEXT_ONLY` can waive the invariant.

## Boundary verdict

PASS. No agent, gate, stage or project artifact was added. Existing artifacts and ownership now carry a single enforceable invariant.

## Scenario verdicts

| Scenario | Expected result |
|---|---|
| User has authentic media | evaluate and integrate the strongest suitable asset |
| User has no media | produce truthful representative/conceptual media |
| Documentary photo is unavailable | do not fabricate it; choose a non-documentary class |
| Typography leads the direction | keep typography primary and add a supporting substantial asset |
| User explicitly requests no images | record `USER_EXPLICIT_TEXT_ONLY` and preserve the exception |
| Agent simply prefers no images | block G2/G3/G4 |

## Next review

2026-11-19, or earlier after repeated visual-payload drift.
