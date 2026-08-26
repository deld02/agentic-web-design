# System audit — v6.3.3

Date: 2026-08-26
Scope: generated imagery execution and hero continuity

## Finding

The design OS produced image briefs but explicitly prohibited its production owner from invoking the final-image tools. The harness only verified generation during `creative-master`, so the actionable `IH-*` queue could remain outside execution. Separately, the artistic master could be mistaken for a promised hero even though G3 later created a different webpage composition.

## Correction

The image loop remains isolated from visual decision-making but now executes inside the existing `production-plan` stage. Each generated `IMG-*` needs a declared output, valid raster and real per-asset generation receipt. The `AM-*` is explicitly an art-direction source; the reviewed desktop/mobile hero `CMP-*` is the frozen implementation target. Final review compares that target with both final renders.

## KEEP

- Eight agents, six gates, thirteen stages and one user checkpoint.
- Scene-led decisions before asset production and one directed retry.
- Authentic-media and real 3D/video routes when generation is inappropriate.

## IMPROVE

- Evaluate visual similarity through the independent rendered review; deterministic code verifies evidence and execution, not aesthetic equivalence.

## ADD

- Per-asset `chat-image --asset-id` receipts during `production-plan`.
- Consistent implementation-root resolution for isolated harness runs.
- `HERO_TARGET_FIDELITY` in final visual review.

## REMOVE

- The dead external loop that no managed execution invoked.
- Ambiguous presentation of the artistic master as the final hero design.

## Scenario verdicts

- Generated conceptual hero/background production: `SUPPORTED` and enforced.
- Existing authentic media: `SUPPORTED` without false generation claims.
- Real 3D/video production: `SUPPORTED_WITH_EXTERNAL_RESOURCE`.
- Silent hero redesign after G3: `BLOCKED` by independent target comparison.

## Verification

All system, architecture and semantic validators pass. 138 tests cover production-image registration, undeclared-asset rejection, missing-receipt detection, hero-target evidence and the existing pipeline.

## Result

PASS. The system can no longer close its managed image stage on briefs alone, and the approved hero composition has explicit authority over implementation.

## Next review

After one real ChatGPT landing run with multiple generated scene assets and one responsive hero adaptation.
