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

### Visual narrative verification

Review the final rendered page against `production-plan.md#Page visual narrative map`, not against asset count. Every axis must be `PASS`; `REVISE` blocks build review.

| Axis | Rendered evidence | Finding / correction owner | Verdict (`PASS | REVISE`) |
|---|---|---|---|
| WHOLE_PAGE_RHYTHM | | | REVISE |
| HERO_TARGET_FIDELITY | | | REVISE |
| EXPERIENCE_CONTINUITY | | | REVISE |
| ASSET_NECESSITY | | | REVISE |
| FORMAT_FIT | | | REVISE |
| MECHANISM_ELIGIBILITY | | | REVISE |
| TRANSITION_CONTINUITY | | | REVISE |
| MOBILE_FALLBACK | | | REVISE |

## Interaction, keyboard and reduced motion

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

## Design capability log

| Capability | Mode | Rule scope | Findings | Closure evidence |
|---|---|---|---|---|
