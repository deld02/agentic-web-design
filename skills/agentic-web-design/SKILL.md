---
name: agentic-web-design
description: Research, design and build a distinctive landing through the repository's enforced pipeline, including a generated artistic master, render-driven image decisions, external-production handoff and verified delivery. Use for landing creation or redesign, not SEO or product operations.
---

# Agentic Web Design

## Execution lock — check before any design work

Landing creation is valid only in one of two harness-managed modes:

- `HEADLESS_MANAGED`: `tools/evaluation_harness.py run` launched the executor and exposes `HARNESS_RUN_DIR`, `HARNESS_PROJECT_DIR`, `HARNESS_STAGE`, `HARNESS_AGENT` and `HARNESS_MODE`.
- `CHAT_INTERACTIVE`: when the current ChatGPT environment has Python/files but no invocable model CLI, run `chat-start`, complete only the returned stage and call `chat-next` before doing anything from the next stage. The harness validates and advances the same pipeline; do not use `record` or fabricate events.

If neither mode is active, the session is `UNMANAGED`. You may inspect, explain or audit, but must not build HTML, generate a substitute design manually or describe the result as an Agentic Web Design execution. If Python execution is available, start `CHAT_INTERACTIVE` instead of stopping merely because an external CLI is unavailable.

During `creative-master`, invoke real image generation. In headless mode emit the required `HARNESS_EVENT` only after success. In chat mode save the returned raster inside the managed project and immediately run `chat-image --file <path>`; `chat-next` blocks without it. A manually drawn SVG, CSS composition, prompt or declaration is not equivalent. The `AM-*` is an art-direction source, not a promised hero layout; the actual implementation target is the reviewed hero `CMP-*` created in G3.

Use `config/pipeline.json` as the execution authority. Create a project with `tools/new_project.py` when needed, then load only its current artifacts, the active agent contract and the method linked there. Do not reconstruct the whole system in context.

The essential path is:

1. Compile the project context before looking for a style: business, action, audience sophistication, trust, human presence, authority/warmth, technicality, experimental tolerance, locality, proof, narrative, emotion and mobile importance. Recalibrate visual quality from current live websites for every project using five physical lenses: direct, adjacent, frontier, strong simple and saturated/overused. Evidence older than 30 days is stale. Compare prior design fingerprints when available.
2. Define at least two content/landing flows, then run the structural interchangeability challenge before selection. Reject the default category sequence when sections could be exchanged without changing meaning. For the selected flow, build the per-scene Experience Spine in `content-architecture.md`; it defines the visitor's semantic progression without prescribing visuals or effects.
3. Define from G1 what “premium” means here, then create exactly three physically visible `DIR-*` territories that differ in at least four art-direction dimensions. 07 compares them in isolated context against the compiled constraints and saturated codes and selects one or returns `REVISE`; 03 never approves its own route.
4. From only the selected territory, invoke ChatGPT image generation to create one project-specific artistic master (`AM-*`). It is a styleframe for atmosphere, material, light, color, depth and composition—not a landing screenshot, UI mockup or final asset. Show it once; the user may approve, request one focused adjustment or delegate. Extract a binding genome: invariants, flex, contextual decisions, relational scene grammar and one signature mechanism.
5. Translate the confirmed genome into the landing. For every section, define dominant, counterpoint, tension, signal, rest, transition and adaptation; then compare a direct baseline with the most valuable treatment that could justify a €10K bespoke budget. Separate real value, a simpler equivalent and expensive noise. Derive typography, color, grid, components and responsive rules. Assign actual color roles and transitions to every scene, then review whole-page rhythm.
6. Select technology and build the complete structural landing with real content. Record desktop/mobile renders.
7. Audit those renders first as one scroll narrative and then by scene. Agent 05 derives the minimum sufficient asset set with `image-decisions.md`, decides `IMAGE | NO_IMAGE` and writes ordered `IH-*` briefs. It then runs a bounded image-production subloop inside `production-plan`: new representative/conceptual raster work defaults to real ChatGPT image generation; authentic media, licensed resources, video and real 3D use their appropriate route. In chat mode register every generated `IMG-*` with `chat-image --asset-id IMG-### --file <path>`; the stage cannot close on briefs alone.
8. Validate every produced asset against its brief, master and intended hero/body composition, then integrate approved media, render again and run independent review. One directed regeneration per rejected asset is allowed. 07 compares the final hero with the reviewed G3 hero `CMP-*`; unrecorded divergence returns to 04/06. When 07 classifies another rendered failure as generic, flat, safe, overdesigned, weak-hierarchy or interchangeable, 04 may apply exactly one matching craft-correction lens before re-review.
9. When a reference depends on video/HTML interaction, use the installed MengTo extraction skill and translate only its observed temporal principle. When 06 has selected GSAP, use only the relevant installed official GSAP skills for implementation and performance; neither capability chooses the design or runtime.
10. Before delivery, run the gate/state checks, deterministic UI scan and `tools/validate_delivery.py`, then record the finished design fingerprint and complete `qa-release.md#Final delivery contract` with `docs/methods/final-delivery.md`. Return concrete package, entry/preview and final-render paths plus status, exact commands and limitations. Internal process documents are not the delivered product; do not claim completion when files or evidence are missing.

Images representing real people, premises, clients or results require authentic supplied media. Generated imagery may represent concepts, atmosphere, materials and non-documentary scenes without pretending to be evidence.

When a tool or correction fails twice, stop with valid work preserved and explain what is needed to continue.

Write only inside the user-approved local project and implementation roots. Publishing, pushing or writing to GitHub or any external service requires an explicit user request.

For a headless executor use `doctor`, `init` and active `run`. Inside ChatGPT without an external CLI use `chat-start`, `chat-status`, `chat-image` and `chat-next`. Never treat an initialized folder or manually injected event log as an executed test.
