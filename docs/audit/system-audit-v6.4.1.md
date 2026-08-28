# System audit — v6.4.1

Date: 2026-08-27
Scope: visual-production and motion escape hatches

## Finding

The system required media and effect records, but the model could manufacture `USER_EXPLICIT_TEXT_ONLY` in editable artifacts or use `STATIC_WINNER_REVIEWED` as a global escape. Criticism of one generated image or provider could therefore be overgeneralized into zero images and zero motion.

## Correction

Global visual waivers now require the same exact user quote in `brief.md`, `production-plan.md` and the immutable harness `scenario.json`. Provider-, style- and output-scoped rejections never qualify. G4 requires one selected non-static behavior and one implemented `FINAL` mechanism by default; a static winner remains valid for an individual scene. Delivery proof also checks that the referenced source contains a real motion or interaction signal.

The existing image decision method now preserves the scene's visual job after rejection: it permits one directed rebrief/regeneration or a suitable production-route change. It does not impose an asset quota or a particular animation library.

## KEEP

- Eight agents, six gates, thirteen stages and the current render-driven image loop.
- Per-project decisions for image count, format, effect type and implementation technology.
- Independent aesthetic judgement by agent 07.

## IMPROVE

- Observe a real landing run to confirm that the new invariant causes a better visual choice, not merely a technically present asset.

## ADD

- Immutable authority validation for global text-only and static-only exceptions.
- A motion-payload validator and five adversarial regression tests.

## REMOVE

- Self-authored visual waivers.
- The ability for a page-wide static result to pass through a scene-local static review.

## Scenario verdicts

- Provider-specific image rejection: `REBRIEF_OR_SWITCH_ROUTE`.
- Invented text-only/static-only marker: `BLOCKED`.
- Exact immutable user request for no imagery or motion: `SUPPORTED`.
- Ordinary premium landing with no primary media or implemented motion: `BLOCKED`.

## Verification

- System, architecture, packaging, governance and semantic validators pass.
- 147 tests pass.
- Five new adversarial tests cover invented waivers, provider-specific rejection, valid immutable authority and the global static escape.
- Existing end-to-end fixture proves a physical primary image and implemented motion can still pass.

## Result

PASS. A model can no longer interpret “do not use this image/tool/style” as “remove all imagery”, nor use a locally static scene to justify an entirely inert landing.

## Next review

After the next real landing execution, inspect whether the selected primary visual and motion mechanism improve the render; deterministic validation proves presence and authority, while agent 07 still owns aesthetic judgement.
