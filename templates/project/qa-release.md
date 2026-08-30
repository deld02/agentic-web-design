# QA & Release

## Release evidence status

Every row must be `COMPLETE | NOT_APPLICABLE | ACCEPTED_RISK`. The latter two require rationale and owner.

| Area | Status | Rationale / owner |
|---|---|---|
| Objective and action | PENDING | |
| Content and assets | PENDING | |
| Visual direction | PENDING | |
| Responsive composition | PENDING | |
| Interaction and motion | PENDING | |
| Build fidelity | PENDING | |
| Functional delivery | PENDING | |
| Accessibility and performance | PENDING | |

## Build and run instructions

## Objective, action and functional delivery

## Visual and responsive verification

FINAL_RENDER_DESKTOP:
FINAL_RENDER_MOBILE:

FINAL_TEXT_SPACING_CAPABILITY: jakub-interface-polish
FINAL_TEXT_SPACING_MODE: FULL

### Visual narrative verification

Review the final rendered page against `production-plan.md#Page visual narrative map`, not against asset count. Every axis must be `PASS`; `REVISE` blocks build review.

| Axis | Rendered evidence | Finding / correction owner | Verdict (`PASS | REVISE`) |
|---|---|---|---|
| WHOLE_PAGE_RHYTHM | | | REVISE |
| HERO_TARGET_FIDELITY | | | REVISE |
| EXPERIENCE_CONTINUITY | | | REVISE |
| ASSET_NECESSITY | | | REVISE |
| FORMAT_FIT | | | REVISE |
| FOCAL_VISUAL_AUTHORITY | | | REVISE |
| MECHANISM_ELIGIBILITY | | | REVISE |
| TRANSITION_CONTINUITY | | | REVISE |
| MOBILE_FALLBACK | | | REVISE |
| TEXT_SPACING_CRAFT | | | REVISE |

## Interaction, keyboard and reduced motion

### Runtime traversal

Capture each scene in both desktop and mobile from the final implementation. Use a unique physical raster per row. For interactive scenes, describe the actual state change, not the intended effect. `Source digest` is the current `sha256:<digest>` of the complete implementation tree, produced by `tools/validation_release_integrity.py`.

| Scene ID | Viewport (`DESKTOP | MOBILE`) | Trigger / input | Expected state or transition | Observed result | Physical evidence relative to project | Verdict (`PASS | REVISE`) | Source digest |
|---|---|---|---|---|---|---|---|

### Spatial QA (conditional)

Complete only when G3 selected `RENDERED_3D` or `INTERACTIVE_3D`.

| Axis | Rendered/runtime evidence | Finding / correction owner | Verdict (`PASS | REVISE`) |
|---|---|---|---|

### Spatial state traversal (conditional)

For `INTERACTIVE_3D`, capture every approved `SPT-*` state on desktop and mobile. Evidence must be unique and tied to the current implementation digest.

| State ID | Scene ID | Viewport (`DESKTOP | MOBILE`) | Trigger / input | Expected camera/object/HTML state | Observed result | Physical evidence relative to project | Verdict (`PASS | REVISE`) | Source digest |
|---|---|---|---|---|---|---|---|---|

RELEASE_INTEGRITY_MANIFEST: evidence/release-integrity.json

## Accessibility, performance and asset verification

### Physical delivery proof

- `implementation_root`:
- command: `python tools/validate_delivery.py --project-dir <project-dir> --implementation-root <implementation-root>`
- result:
- `IMG ID → final file → implementation reference → desktop/mobile render evidence`:

## Evidence records

| ID | Method | Target | Result | Evidence | Owner | Status | Limitations |
|---|---|---|---|---|---|---|---|

## Findings

| ID | Severity | Evidence | Owner | Status |
|---|---|---|---|---|

## Deviations and accepted risks

## Design fingerprint

Record the finished landing in compact perceptual terms so a future project can detect accidental repetition without copying this implementation.

BACKGROUND_CHARACTER:
ACCENT_CHARACTER:
DISPLAY_TYPE_CHARACTER:
HERO_COMPOSITION:
HERO_MEDIA:
SIGNATURE_MECHANISM:
DEPTH_MEDIUM:
MOTION_INTENSITY:

## Release decision

## Final delivery contract

Complete this only after final review, following `docs/methods/final-delivery.md`. Existing final-render fields above remain the visual proof.

DELIVERY_STATUS: NOT_READY
LANDING_ENTRY:
RUN_COMMAND:
BUILD_COMMAND:
PREVIEW_TARGET:
DELIVERY_PACKAGE:
ASSET_COMPLETENESS: INCOMPLETE
LIMITATIONS:
HANDOFF_SUMMARY:

### Managed execution proof

These fields are written by the harness only after `release` completes and the full evaluation passes. Owners do not prefill or simulate them.

EXECUTION_MODE: UNMANAGED
HARNESS_RUN_ID: NOT_AVAILABLE
HARNESS_STATUS: NOT_COMPLETE
STAGES_COMPLETED: 0/13
VALIDATION_REPORT: NOT_RUN
EXECUTION_RECEIPT: NOT_AVAILABLE

## Design capability log

| Capability | Mode | Rule scope | Findings | Closure evidence |
|---|---|---|---|---|
