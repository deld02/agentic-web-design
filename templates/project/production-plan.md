# Production Plan

## Material media and effect decisions

Keep media/effect comparisons here. Add to `decision-log.md` only a direction that affects multiple phases or is expensive to reverse.

## Render diagnosis and external handoff

05 completes this map only after inspecting the approved structural-build evidence in `technology-decision.md#structural-build-handoff`.

VISUAL_DIAGNOSIS: <!-- where the real render loses presence, rhythm, depth, continuity or specificity -->

## Page visual narrative map

Decide primero el ritmo visual completo; no cuentes imágenes por sección. `Page beat`: `ANCHOR | PROOF | SUPPORT | ATMOSPHERE | TRANSITION | REST | CLIMAX | CLOSURE`. `Format`: `NONE | BACKGROUND | LATERAL | INLINE | FOREGROUND | TEXTURE | FULL_BLEED | TRANSPARENT_OBJECT | SEQUENCE | VIDEO | REAL_3D`. `Behavior`: `STATIC | HOVER | STICKY | PARALLAX | PINNED_SCROLL | VIDEO_PLAYBACK | INTERACTIVE_3D`.

ASSET_SET_RATIONALE:
FLAT_STRETCH_CHECK:
DUPLICATE_JOB_CHECK:

<!-- Explain why this is the minimum sufficient asset set, where scroll interest drops and which duplicate visual jobs were removed. -->

| Scene ID | Page beat | Visual job | Intensity / relation to adjacent scenes | Selected format | Selected behavior | Narrative trigger / why this behavior | Asset decomposition | Mobile / reduced-motion fallback | Transition onward |
|---|---|---|---|---|---|---|---|---|---|

This is the single ordered image decision and production map. Every used image or materially different responsive variant has its own row. `Final file / fallback` is a real produced path, never a prompt. Required generation is executed during this stage.

## Scene image decisions

Every outlined `SCN-*` receives one decision. Roles: `BACKGROUND | LATERAL | INLINE | FOREGROUND | ICON | TEXTURE | TRANSITION | NONE`.

| Scene ID | Decision (`IMAGE | NO_IMAGE`) | Role | What it must represent / why none | Truth or source constraint | Desktop/mobile placement and behavior | Production route (`EXISTING | EXTERNAL:IH-### | NONE`) |
|---|---|---|---|---|---|---|

`SUPPORTING` assets are auxiliary. SVG/CSS can support a scene but cannot replace its scene-bearing primary visual.

## Asset inventory and readiness

| ID | Scene + observed render need | Production type + representation/truth class | Payload role / selected method | Status | Final file / fallback | External loop handoff (`IH-*`) + production brief | Exact integration in landing |
|---|---|---|---|---|---|---|---|

Each row answers only what production and frontend need:

- `Production type`: `SCENE_PLATE | TRANSPARENT_ELEMENT | TEXTURE | DEPTH_LAYERS | SECTION_ARTWORK | MASK_OR_SHAPE | MOTION_FRAMES | DOCUMENTARY_MEDIA`.
- `External loop handoff`: stable `IH-*`, subject/action, art direction, light/material, ratio, safe zones, must include/avoid and continuity with the master.
- `Exact integration`: section, background/foreground/layer, position, crop, frame/mask, desktop/mobile behavior, effect or `NONE`, reduced-motion/static fallback and alt intent.

Use `PRIMARY:EXTERNAL_IMAGE_LOOP` or `SUPPORTING:EXTERNAL_IMAGE_LOOP` for new generated production. Status moves `NEEDS_PRODUCTION → RETURNED → FINAL`; 05 marks the output `FINAL` after validating the real file, and 06 must integrate that exact file. In ChatGPT, every generated row requires `chat-image --asset-id IMG-### --file <path>`.

## Responsive media, ratios and safe zones

## Motion choreography and reduced motion

### Interaction grammar

- Interaction thesis / spatial metaphor:
- Defining mechanism (zero or one normally):
- Shared duration, easing, distance and transform-origin rules:
- Repetition / interruption rules:
- Touch, keyboard, reduced-motion and static fallback grammar:

### Material effect decisions

Use stable `FX-*` IDs for material mechanisms; they remain in this artifact unless globally consequential.

For `FINAL`, implementation proof is `source/file#marker`: both must exist in `implementation_root`. For `STATIC_WINNER_REVIEWED`, use `STATIC:<evidence>` and record why visible candidates weakened the rendered hero.

| Effect ID / scene | Opportunity level | Static candidate | Simple candidate | Expressive candidate | Source anchors / transfer | Evaluation / winner | Prototype evidence | Fallback / owner | Status (`FINAL | STATIC_WINNER_REVIEWED`) | Implementation proof | Delivered medium (`FLAT_2D | LAYERED_2D | RENDERED_3D | INTERACTIVE_3D`) |
|---|---|---|---|---|---|---|---|---|---|---|---|

### 3D production provenance

Complete only for a selected `RENDERED_3D` or `INTERACTIVE_3D` mechanism. CSS/SVG perspective, gradients and shadows are `FLAT_2D` or `LAYERED_2D`, never proof of 3D.

| FX ID | Medium | External source / authoring tool | Asset / runtime | License or rights | Integration proof (`source/file#marker`) | Static / reduced-motion fallback |
|---|---|---|---|---|---|---|

## Creative mechanisms and risk prototypes

## Loading, performance and fallbacks

## Acceptance criteria

Authentic documentary media remains valid. New atmosphere, backgrounds, elements or layers are specified through `IH-*` and produced with the selected real tool; they are never replaced by improvised CSS/SVG pretending to be imagery.

## Design capability log

| Capability | Mode | Activation evidence | Adopted / rejected mechanisms | Fallback / kill criterion |
|---|---|---|---|---|
