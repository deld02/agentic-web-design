# System audit — v6.4.2

Date: 2026-08-27
Scope: final typography, spacing and breathing review

## Finding

Typography and spatial rhythm were pressure-tested during visual design, but the final integrated build could change line metrics, wrapping and scene density. The registered polish capability was automatic in principle yet not a mandatory release condition.

## Correction

Agent 07 now runs `jakub-interface-polish` once in `FULL` mode on the final loaded-font desktop/mobile renders. `TEXT_SPACING_CRAFT` checks section breathing, hierarchy, paragraph measure/leading, mixed-type optical composition, wrapping, clipping and mobile recomposition. Evidence must name `SCN-*` locations and both viewports.

## KEEP

- The existing eight agents, six gates, thirteen stages and isolated build review.
- Project-specific typography and spacing decisions rather than fixed design tokens.
- One directed correction instead of an open-ended polish loop.

## IMPROVE

- Inspect the next real landing to calibrate whether scene-specific evidence is sufficiently precise for long editorial pages.

## ADD

- Mandatory final `FULL` craft-polish invocation.
- One blocking review axis and three adversarial regression tests.

## REMOVE

- Nominal “spacing is correct” approval without rendered locations.
- Reliance on pre-implementation typography evidence as final proof.

## Scenario verdicts

- Final render without the registered full polish: `BLOCKED`.
- Generic spacing claim without scene/viewport evidence: `BLOCKED`.
- Full render review with scene-specific desktop/mobile evidence: `SUPPORTED`.

## Verification

System, architecture, packaging, governance and semantic validators pass. All 150 tests pass, including the three new final text-spacing cases.

## Result

PASS. Final delivery now has a deterministic obligation to perform the visual spacing review while agent 07 retains the actual aesthetic judgement.

## Next review

After one real landing exposes dense paragraphs and a mixed-family headline across desktop and mobile.
