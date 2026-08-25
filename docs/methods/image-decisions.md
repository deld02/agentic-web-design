# Image decisions and external-production handoff

Images are a primary design medium, not a fallback or a documentation exercise. This method uses one approved visual master and one ordered decision/handoff map.

This is the single operational path for deciding and placing imagery. The scene method owns creative direction; 05 owns the specification and validation after the structural render. Final image creation runs in a separate external loop.

## 1. Create the visual master

After research, 03 defines what the visual world must make the visitor feel and understand, then invokes `CHATGPT_GENERATE` to create the physical `ARTISTIC_MASTER` (`AM-*`). Generated text is provisional. A prompt, landing screenshot, UI mockup, HTML, SVG, diagram, gradient or CSS composition does not count.

If a real person, place, product or result is claimed, use authentic documentary media. The later external loop may edit supplied material or create background, light, atmosphere, elements and layers without falsifying identity.

Show the resulting master once for user confirmation before frontend work.

## 2. Build the structural landing and inspect it

Inside `technology-selection`, 06 first selects the stack and then builds the complete semantic HTML/CSS structure with real copy, typography, color, grid, components, rhythm and deliberately reserved visual regions. It records representative desktop and mobile captures in `technology-decision.md#structural-build-handoff`. The checkpoint cannot close without them. These are diagnostic evidence, not final assets.

05 first reads the renders as one scroll experience, then scene by scene: presence, flatness, generic components, depth/material, transitions, scroll interest, text-safe space and whether an intervention is actually better than `NONE`. Layout or art-direction failures return to 04; media opportunities enter the existing map.

## 3. Build the page visual narrative

Before deciding assets, map every `SCN-*` as one visual beat: `ANCHOR | PROOF | SUPPORT | ATMOSPHERE | TRANSITION | REST | CLIMAX | CLOSURE`. Record its job, intensity relative to adjacent scenes, selected visual format, behavior, narrative trigger, decomposition, mobile/reduced fallback and transition onward.

The map must identify the minimum sufficient asset set, any long flat stretch and duplicate jobs removed. Count assets only after this map. A long page may need several visual beats; a compact page may need one dominant image and deliberate typographic rests. Neither receives an arbitrary quota.

Choose format and behavior independently:

- `BACKGROUND` when atmosphere should surround content without carrying documentary proof;
- `LATERAL | INLINE` when a specific visual explains nearby content;
- `FULL_BLEED` for a deliberate reset, entry or climax;
- `TRANSPARENT_OBJECT` when an object must participate in the composition;
- `TEXTURE` when material surface is needed but no narrative subject is required;
- `SEQUENCE | VIDEO | REAL_3D` only when transformation, time, matter or viewpoint is essential;
- `NONE` when type/layout is the stronger intentional rest.

Behavior rules are fail-closed: `STICKY | PINNED_SCROLL` needs a real sequence of related states; `PARALLAX` needs independently produced depth layers; `HOVER` needs an interactive/explorable target; `VIDEO_PLAYBACK` needs temporal content; `INTERACTIVE_3D` needs a real 3D source/runtime. Every non-static behavior needs mobile, reduced-motion and static fallback. Premium appearance alone is never a trigger.

## 4. Decide image presence and role per scene

For every `SCN-*`, 05 records `IMAGE | NO_IMAGE`. `IMAGE` identifies the actual role—background, lateral, inline, foreground, icon, texture or transition—and its perceptual/content job. `NO_IMAGE` states why typography, layout or existing media is stronger. This is a design decision, not a quota.

## 5. Convert selected needs into external handoffs

05 fills `Asset inventory and readiness` only from observed needs. One row per materially different output records:

- scene and perceptual job;
- production type: `SCENE_PLATE | TRANSPARENT_ELEMENT | TEXTURE | DEPTH_LAYERS | SECTION_ARTWORK | MASK_OR_SHAPE | MOTION_FRAMES | DOCUMENTARY_MEDIA`;
- representation and `DOCUMENTARY | REPRESENTATIVE | CONCEPTUAL | DECORATIVE` truth class;
- external-loop brief `IH-*`: subject/action, style, light/material, ratio, negative space, safe zones, inclusions/exclusions and continuity;
- exact integration: section, background/foreground/layer, position, crop, frame/mask, desktop/mobile behavior, effect or `NONE`, fallback and alt intent;
- route (`EXISTING` or `EXTERNAL:IH-*`), status and returned/final file.

The master directs the result but never predetermines the file type. Omit rows that do no real visual work.

## 6. Run image creation outside this system

The external image loop consumes one `IH-*` at a time. It may use ChatGPT image generation, another generator, photography, illustration, 3D or another appropriate production tool. That loop owns creation and its internal iterations; this OS does not invoke those tools.

The loop returns a web-ready file and production metadata. 05 validates the result against the brief and master. An unsuitable result returns to the external loop with one directed finding; it is never replaced with improvised HTML, SVG or prose. A returned file becomes `FINAL` only after 06 integrates it.

The ordered `IH-*` queue preserves continuity, but it is not an agent stage, gate or hidden generation instruction.

## 7. Integrate, render and correct once

06 follows the placement instruction in each row. Text and controls remain semantic HTML. The handoff requests separate background, foreground, mask or depth layers when responsive composition or effects require independence. A mobile asset may be separate when crop cannot preserve the subject and safe space.

Render desktop and mobile again. 07 compares the integrated scenes with the master and structural diagnosis. One directed correction may request a new external output, recrop, split layers, reduce intensity or remove a resource. It cannot restart the landing or accumulate effects.

Frames, masks, bleed, hover, reveal, parallax or 3D are chosen because they strengthen the image's job. If `NONE` is best, record it in the integration cell; no additional effect sheet is needed for ordinary image behavior.

## 8. Acceptance

Before `production-plan` begins, `technology-selection` must contain valid structural desktop/mobile renders. Before `implementation` begins, the page visual narrative covers every scene, its asset count and flat stretches are reasoned, every effect satisfies its trigger/decomposition/fallback rule, every scene has an image decision, every selected new image has an `EXTERNAL:IH-*` handoff, and every required handoff has returned a real web-ready file. Documentary assets remain authentic. Delivery still requires scene-bearing primary media unless the approved direction is explicitly typographic.

Delivery validation verifies that final files exist inside `implementation_root`, are valid media and are referenced by code. `PRIMARY` identifies scene-bearing media; `SUPPORTING` identifies auxiliary graphics. SVG/CSS may support the composition but cannot be its only primary visual.
