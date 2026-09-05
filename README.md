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

The eight files in `agents/` define internal specialists, not eight separate conversations. Agent 00 is the orchestrator. The MCP returns an active `stage_packet` with the specialist contract, inputs, methods and capabilities. It owns state transitions and restores candidate state when validation rejects it. Agent 07 requires a genuinely separate execution context; the current MCP adapter cannot dispatch that context and blocks review stages instead of granting a false approval.

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

El MCP del harness es un **adaptador parcial, no una ruta completa de producción
para ChatGPT**. Expone el pipeline existente, pero todavía faltan un ejecutor
de revisión aislada y operaciones gestionadas de build, render y entrega.
Se detiene en la primera revisión independiente: no basta con que el propio chat
escriba `PASS`. No lo uses para prometer una landing certificada de principio a fin.

```bash
# Codex/cliente local (stdio)
python tools/harness_mcp_server.py --transport stdio

# Desarrollo HTTP local
python tools/harness_mcp_server.py --transport http --host 127.0.0.1 --port 8765
```

El endpoint HTTP es `http://127.0.0.1:8765/mcp`. Para ChatGPT en developer mode,
la opción preferente es **Secure MCP Tunnel**: crea el túnel en OpenAI Platform y
ejecuta `tunnel-client` en el equipo con un perfil stdio cuyo `--mcp-command` sea
`python <repo>/tools/harness_mcp_server.py --transport stdio`. Es una conexión HTTPS
saliente; no exige publicar el ordenador. Mantén `tunnel-client run` activo mientras
se usa la app en ChatGPT. La alternativa pública sí requiere HTTPS, autenticación y
un origen permitido; el servidor se niega a enlazar una interfaz no local sin token.

Configura `OPENAI_API_KEY` para que `generate_image` produzca y registre el raster
físico con `gpt-image-2`. La llamada puede tener coste y debe conservar la aprobación
del cliente MCP. El ZIP o el conector de GitHub por sí solos no ejecutan nada: solo
son una ruta válida cuando el chat dispone realmente de Python, inicia `chat-start`
y muestra el preflight gestionado antes de investigar.

El flujo MCP es `start_landing` → ejecutar únicamente el `stage_packet` →
`advance_stage`. Los especialistas no escriben `status.json`. `creative-master` no avanza sin `generate_image` o
`register_image`; `production-plan` tampoco avanza si un `IMG-*` generado no ha
vuelto físicamente. CSS, SVG, círculos, diagramas o iconos improvisados no cuentan
como sustitutos de una imagen exigida. `verify_run` debe devolver `verified: true`
antes de afirmar que el sistema se ejecutó por completo.

En este adaptador, `implementation_root` debe ser `implementation`, una carpeta
dedicada dentro del proyecto gestionado. La elección tecnológica sigue siendo libre;
esta restricción protege el estado, no prescribe un framework. Ejecuta una sola
instancia de servidor por directorio de runs. Las operaciones se serializan en ese
proceso y una validación rechazada restaura el estado previo; esto no constituye
aislamiento frente a otros procesos locales ni recuperación ante un corte del proceso.

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
