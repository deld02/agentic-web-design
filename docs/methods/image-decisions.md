# Image decisions and external-production handoff

Images are a primary design medium, not a fallback or a documentation exercise. This method uses one approved visual master and one ordered decision/handoff map.

This is the single operational path for deciding, producing and placing imagery. The scene method owns creative direction; 05 owns a bounded production subloop after the structural render. It remains separate from design decisions but is executed and supervised inside `production-plan`.

## 1. Create the visual master

After research, 03 defines what the visual world must make the visitor feel and understand, then invokes `CHATGPT_GENERATE` to create the physical `ARTISTIC_MASTER` (`AM-*`). Generated text is provisional. A prompt, landing screenshot, UI mockup, HTML, SVG, diagram, gradient or CSS composition does not count.

If a real person, place, product or result is claimed, use authentic documentary media. The later production subloop may edit supplied material or create background, light, atmosphere, elements and layers without falsifying identity.

Show the resulting master once for user confirmation before frontend work.

## 2. Build the structural landing and inspect it

Inside `technology-selection`, 06 first selects the stack and then builds the complete semantic HTML/CSS structure with real copy, typography, color, grid, components, rhythm and deliberately reserved visual regions. It records representative desktop and mobile captures in `technology-decision.md#structural-build-handoff`. The checkpoint cannot close without them. These are diagnostic evidence, not final assets.

05 first reads the renders as one scroll experience, then scene by scene: presence, flatness, generic components, depth/material, transitions, scroll interest, text-safe space and whether an intervention is actually better than `NONE`. Layout or art-direction failures return to 04; media opportunities enter the existing map.

## 3. Build the page visual narrative

Before deciding assets, map every `SCN-*` as one visual beat: `ANCHOR | PROOF | SUPPORT | ATMOSPHERE | TRANSITION | REST | CLIMAX | CLOSURE`. Record its job, intensity relative to adjacent scenes, selected visual format, behavior, narrative trigger, decomposition, mobile/reduced fallback and transition onward.

The map must identify the minimum sufficient asset set, any long flat stretch and duplicate jobs removed. Count assets only after this map. A long page may need several visual beats; a compact page may need one dominant image and deliberate typographic rests. Neither receives an arbitrary quota.

Choose format and behavior independently. This method owns the visual format:

- `BACKGROUND` when atmosphere should surround content without carrying documentary proof;
- `LATERAL | INLINE` when a specific visual explains nearby content;
- `FULL_BLEED` for a deliberate reset, entry or climax;
- `TRANSPARENT_OBJECT` when an object must participate in the composition;
- `TEXTURE` when material surface is needed but no narrative subject is required;
- `SEQUENCE | VIDEO | REAL_3D` only when transformation, time, matter or viewpoint is essential;
- `NONE` when type/layout is the stronger intentional rest.

`docs/methods/effect-selection.md#3-mechanism-eligibility` is the sole authority for behavior eligibility. Record the chosen behavior here, but do not restate or weaken those rules. Every accepted non-static behavior carries the evidence and fallbacks required by that method.

## 4. Decide image presence and role per scene

For every `SCN-*`, 05 records `IMAGE | NO_IMAGE`. `IMAGE` identifies the actual role—background, lateral, inline, foreground, icon, texture or transition—and its perceptual/content job. `NO_IMAGE` states why typography, layout or existing media is stronger. This is a design decision, not a quota.

## 5. Convert selected needs into production briefs

05 fills `Asset inventory and readiness` only from observed needs. One row per materially different output records:

- scene and perceptual job;
- production type: `SCENE_PLATE | TRANSPARENT_ELEMENT | TEXTURE | DEPTH_LAYERS | SECTION_ARTWORK | MASK_OR_SHAPE | MOTION_FRAMES | DOCUMENTARY_MEDIA`;
- representation and `DOCUMENTARY | REPRESENTATIVE | CONCEPTUAL | DECORATIVE` truth class;
- external-loop brief `IH-*`: subject/action, style, light/material, ratio, negative space, safe zones, inclusions/exclusions and continuity;
- exact integration: section, background/foreground/layer, position, crop, frame/mask, desktop/mobile behavior, effect or `NONE`, fallback and alt intent;
- route (`EXISTING` or `EXTERNAL:IH-*`), status and returned/final file.

The master directs the result but never predetermines the file type. Omit rows that do no real visual work.

## 6. Run the bounded image-production subloop

Consume one ordered `IH-*` at a time inside the existing `production-plan` stage. New representative or conceptual raster imagery defaults to real ChatGPT image generation. Authentic documentary media, licensed sources, video and real 3D use their appropriate real production route. The loop invokes the selected tool; a brief, prompt, CSS/SVG construction or declaration is not a produced asset.

Save every web-ready output at its declared `IMG-*` final path and record its production method. In interactive ChatGPT runs, call `chat-image --asset-id IMG-### --file <path>` immediately after successful generation. In headless runs, emit the image-generation receipt with the same `IMG-*` target. 05 validates the result against the brief, master and target composition. One rejected output may receive one directed regeneration; it is never replaced with improvised HTML, SVG or prose. 05 marks the physical output `FINAL`; 06 then integrates that exact file.

A rejection is scoped. “Do not use Magnific”, “this image is generic”, “no stock” or rejection of a style/provider/output invalidates only that route or result. It does not turn `IMAGE` into `NO_IMAGE`, remove the scene's visual job or authorize a text-only landing. Re-brief once, use ChatGPT generation or switch to suitable authentic/licensed production. `IMAGE → NO_IMAGE` is allowed only when the immutable user brief explicitly cancels imagery as a whole, or 07 compares physical before/after renders and finds that removing this specific asset improves the scene while another primary visual still carries the landing.

The ordered queue is not a new agent, stage or gate. `production-plan` cannot close while a required generated `IMG-*` lacks a physical file and a real generation receipt.

## 7. Integrate, render and correct once

06 follows the placement instruction in each row. Text and controls remain semantic HTML. The handoff requests separate background, foreground, mask or depth layers when responsive composition or effects require independence. A mobile asset may be separate when crop cannot preserve the subject and safe space.

Render desktop and mobile again. 07 compares the integrated scenes with the master and structural diagnosis. One directed correction may request a new external output, recrop, split layers, reduce intensity or remove a resource. It cannot restart the landing or accumulate effects.

Frames, masks, bleed, hover, reveal, parallax or 3D are chosen because they strengthen the image's job. If `NONE` is best, record it in the integration cell; no additional effect sheet is needed for ordinary image behavior.

## 8. Acceptance

Before `production-plan` begins, `technology-selection` must contain valid structural desktop/mobile renders. Before `implementation` begins, the page visual narrative covers every scene, its asset count and flat stretches are reasoned, every effect satisfies its trigger/decomposition/fallback rule, every scene has an image decision, every selected new image has an `EXTERNAL:IH-*` handoff, and every required handoff has returned a real web-ready file. Documentary assets remain authentic. Delivery still requires scene-bearing primary media unless an exact text-only user instruction is preserved in the immutable harness scenario and repeated verbatim in the brief and production plan.

Delivery validation verifies that final files exist inside `implementation_root`, are valid media and are referenced by code. `PRIMARY` identifies scene-bearing media; `SUPPORTING` identifies auxiliary graphics. SVG/CSS may support the composition but cannot be its only primary visual.
