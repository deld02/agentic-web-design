# System audit — v6.2.1

Date: 2026-08-25  
Scope: landing creation only

## Finding

The media stage could complete a per-scene `IMAGE | NO_IMAGE` table without first understanding the landing as a visual narrative. That encouraged arbitrary asset counts, repeated image jobs, flat scroll stretches and effects selected for premium appearance rather than narrative necessity.

## Correction

Agent 05 now creates one `Page visual narrative map` inside the existing production plan before asset handoffs. It covers every G1 scene, defines the page beat, visual job, relative intensity, format, behavior, narrative trigger, decomposition, mobile/reduced fallback and transition. Asset count is derived only after this map.

Mechanism eligibility is explicit: sticky/pinned needs related state progression, parallax needs independent depth layers, hover needs an explorable target, playback needs temporal content and interactive 3D needs real spatial value plus real 3D media. Agent 07 repeats a compact whole-page review on final desktop/mobile renders.

## KEEP

- Eight roles, six gates, thirteen stages and one production plan.
- Separate external image-production loop.
- Static and `NO_IMAGE` decisions remain valid when intentional.

## IMPROVE

- Observe the quality of asset-count reasoning in the next complete landing.

## ADD

- Page-level visual rhythm before per-scene image decisions.
- Deterministic format/behavior compatibility checks.
- Final rendered review of asset necessity, format fit, transitions and fallbacks.

## REMOVE

- Image quotas and effects justified only by an expensive or premium appearance.

## Scenario verdicts

- One strong hero plus deliberate typographic rests: `SUPPORTED`.
- Multiple scene-specific assets with distinct jobs: `SUPPORTED`.
- Parallax on one flat photograph: `BLOCKED`.
- Sticky/pinned decoration without state progression: `BLOCKED` by contract/review.
- Real 3D selected for material or viewpoint value: `SUPPORTED` with provenance and fallback.

## Verification

The gate tests prove that missing scene coverage blocks G4 and parallax without independent layers fails. The full suite and all system, state, agent and governance audits pass.

## Next review

After two complete landings with materially different media needs, or earlier if a repeated effect passes without a project-specific narrative trigger.
