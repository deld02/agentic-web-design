# Agentic Landing Design OS

A focused system for researching, art-directing, designing, building and reviewing one high-quality landing page. It does not own SEO, marketing operations, ecommerce or product development.

## Start

Ask one open question: what should be created, for whom and what should it achieve? Existing brand, copy, photos and references are welcome but optional. Ask only a follow-up that would materially change the result. If references are missing, research current competitors, strong category examples and relevant design galleries.

“Choose for me” delegates the preference; it does not skip research, comparison or review.

## Essential path

1. Define the objective and constraints.
2. Research the category, audience, existing identity and current references.
3. Compare content structures.
4. Define what premium means for this project, then generate one artistic master before composing the webpage.
5. Confirm that visual world once, then challenge every section for high-end value and translate the selected forms responsively.
6. Define the visual system and review it independently. When spatial treatment is credible, compare 2D/layers/rendered/interactive media here and freeze the least complex winner before technology.
7. Choose the simplest suitable technology and build the complete structural landing.
8. Render desktop/mobile, decide image presence and role per scene, send `IH-*` briefs to the separate image loop, then validate/integrate its returned files and review the final build.

The executable order and dependencies live only in [config/pipeline.json](config/pipeline.json). The runtime entry point is [skills/agentic-web-design/SKILL.md](skills/agentic-web-design/SKILL.md).

## Design rules

- Research informs choices but never selects them automatically.
- Color, typography, composition and media are judged together while translating the master into rendered scene alternatives.
- Documentary claims require authentic media. Conceptual, representative and decorative media may be requested from the external image loop when honestly framed.
- Every landing needs a substantial scene-bearing visual unless the user explicitly requests text only.
- Effects and depth are explored in context. A 3D decision follows the conditional spatial contract: G3 selects the medium, technology proves the runtime, G4 produces semantic states and QA traverses them. It requires an identified external model/scene/tool or runtime with rights, integration proof and fallback; CSS/SVG imitation is classified as 2D and cannot masquerade as 3D.
- A screenshot or composition study is evidence, not a shippable asset.
- Delivery is valid only when final media files exist inside the implementation and the code uses them.

## Roles

The eight files in `agents/` define ownership, not eight mandatory conversations. Only the active owner contract and its linked method should be loaded. Agent 07 reviews independently; findings return to the owner.

## Technology

HTML, Astro, component frameworks, visual platforms and custom creative stacks are options, never defaults. Agent 06 compares viable choices and always includes the simplest one capable of reproducing the approved design.

## Create and validate

```bash
python tools/new_project.py my-landing
python tools/validate_gate.py G2 --project-dir projects/my-landing
python tools/validate_system.py
python tools/audit_agents.py
python tools/validate_delivery.py --project-dir projects/my-landing --implementation-root path/to/site
python -m unittest discover -s tests -v
```

## Ejecución gestionada

Leer el repositorio no equivale a ejecutar el sistema. Para un proyecto real dentro de ChatGPT existe un único arranque canónico:

```text
python tools/evaluation_harness.py chat-start --brief-file <brief>
```

La respuesta debe exponer `execution_mode`, `run_id`, `run_dir`, `project_dir`, `stage`, `agent` y `mode`. Completa exclusivamente esa etapa y avanza con `chat-next`. Durante `creative-master` y la producción de imágenes finales, registra cada raster real con `chat-image`.

Para un ejecutor headless, usa `doctor`, `init` y `run`; `record` es instrumentación de bajo nivel y nunca sustituye una ejecución gestionada. Los seis escenarios y sus límites viven en `harness/scenarios.json`.

Una ejecución completa genera `execution-receipt.json`. Verifícala sin confiar en la declaración del modelo:

```text
python tools/verify_execution.py --receipt <run-dir>/execution-receipt.json
```

Sin un recibo válido, el resultado puede estar inspirado en la metodología, pero no puede presentarse como una ejecución completa de Agentic Web Design.

All writes stay in the local project and implementation roots supplied by the user. Publishing or writing to an external service requires an explicit request.
