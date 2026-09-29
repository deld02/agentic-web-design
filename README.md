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
5. Design the complete landing, not just the hero. Save whole-page desktop/mobile compositions and every section in visual-system.md as one construction blueprint; prototype only risky interactions.
6. Review the complete proposal independently, then obtain one user approval with confirm_design before construction. The master is an internal reference, not another stop. When spatial treatment is credible, compare media here before technology.
7. Choose the simplest suitable technology and build the complete structural landing.
8. Produce the planned assets through the separate image loop and integrate sections one at a time inside the shared page. Finish with a whole-page review of continuity, spacing, transitions, responsive behavior and fidelity. Existing runs retain their original checkpoint policy; do not silently migrate them.

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

The eight files in `agents/` define internal specialists, not eight separate conversations. Agent 00 is the orchestrator. The MCP returns an active `stage_packet` with the specialist contract, inputs, methods and capabilities. It owns state transitions and restores candidate state when validation rejects it. Agent 07 uses a fresh visual-review request (API or subscription-backed Codex) with physical evidence; a verdict written by the designing chat cannot approve a review.

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

El MCP implementa generación/importación de imágenes, revisión visual en contexto
separado, render de HTML estático/exportado y entrega verificada. El runtime se
comprueba antes de abrir un proyecto. **La integración completa con ChatGPT y los
proveedores debe probarse en un piloto real**; los tests locales no certifican
calidad artística ni conectividad externa. Configuración y límites:
[managed-runtime.md](docs/architecture/managed-runtime.md).

### Local con suscripción, sin clave API

```powershell
./tools/start-local.ps1 -Mode doctor
./tools/start-local.ps1 -Mode stdio
```

El lanzador usa `AGENTIC_AI_BACKEND=session`. En este PC ya está registrado el
MCP `agentic-web-design` en Codex por stdio: no usa túnel. Recarga los MCP o abre
una nueva sesión para que aparezca. La revisión automática necesita `codex login`
con tu cuenta ChatGPT; la sesión de la aplicación no implica una sesión CLI.
Consume los límites de la suscripción, no llamadas con una clave API propia.
Las imágenes se crean con la herramienta nativa de la sesión y se registran con
`register_session_image`, archivo real y referencia del resultado. El servidor
verifica el raster y su hash, pero declara esa procedencia como `CLIENT_ATTESTED`,
no como generación observada. Sin herramienta de imagen, se pausa la producción.
La revisión se ejecuta en una conversación nueva de Codex, no como autocrítica
del diseñador. No hay fallback silencioso a la API. Detalles y límites en
[managed-runtime.md](docs/architecture/managed-runtime.md).

### Alternativa API y ChatGPT web

El endpoint HTTP es `http://127.0.0.1:8765/mcp`. Para ChatGPT en developer mode,
la opción preferente es **Secure MCP Tunnel**: crea el túnel en OpenAI Platform y
ejecuta `tunnel-client` en el equipo con un perfil stdio cuyo `--mcp-command` sea
`python <repo>/tools/harness_mcp_server.py --transport stdio`. Es una conexión HTTPS
saliente; no exige publicar el ordenador. Mantén `tunnel-client run` activo mientras
se usa la app en ChatGPT. La alternativa pública sí requiere HTTPS, autenticación y
un origen permitido; el servidor se niega a enlazar una interfaz no local sin token.

Solo en esta alternativa, usa `-AIBackend api` y configura `OPENAI_API_KEY`, `AGENTIC_IMAGE_MODEL` y
`AGENTIC_REVIEW_MODEL`. Las llamadas de generación y revisión pueden tener coste
y deben conservar la aprobación del cliente MCP. Un ZIP o el conector de GitHub
por sí solos no ejecutan el sistema ni aportan el runtime.

El flujo MCP es `start_landing` → ejecutar únicamente el `stage_packet` →
`advance_stage`. Los especialistas no escriben `status.json`. En modo API, `creative-master` exige generación observada mediante `generate_image`; en modo sesión exige el resultado nativo físico registrado con su procedencia declarada.
`register_image` y `upload_image` acreditan archivos importados, no una llamada de generación. `production-plan` tampoco avanza si un `IMG-*` generado no ha
vuelto físicamente. CSS, SVG, círculos, diagramas o iconos improvisados no cuentan
como sustitutos de una imagen exigida. `verify_run` debe devolver `verified: true`
antes de afirmar que el sistema se ejecutó por completo.

En este adaptador, `implementation_root` debe ser `implementation`, una carpeta
dedicada dentro del proyecto gestionado. La elección tecnológica sigue siendo libre;
esta restricción protege el estado, no prescribe un framework. El render gestionado
acepta HTML estático/exportado; `build_frontend` permite Docker aislado o Node/npm
local sin Docker, con aprobación del código por el operador. La vía local no es
un sandbox. Configuración en `docs/architecture/managed-runtime.md`.
No soporta SSR ni servicios externos.
En el PC preparado, `./tools/start-local.ps1 -Mode doctor` comprueba el runtime
sin Docker. `./tools/connect-chatgpt.ps1` prepara la conexión privada cuando el
operador aporta su túnel, modelos y credenciales mediante entrada local oculta.
No incluye esos datos ni los binarios descargados en Git, y no equivale a una
conexión ChatGPT validada hasta probarla con la cuenta de destino.
`check_technology` expone esa compatibilidad antes de seleccionar. Un bloqueo
SQLite serializa los servidores cooperantes y un journal recupera transiciones
interrumpidas al reabrir el run. No es aislamiento frente a procesos locales hostiles
ni una garantía de durabilidad ante pérdida eléctrica.

Leer el repositorio no equivale a ejecutar el sistema. Desde ChatGPT conectado al
MCP, usa `start_landing`. La CLI siguiente es una entrada alternativa de bajo nivel
para entornos que ya disponen de runtime, no un sustituto de los servicios necesarios:

```text
python tools/evaluation_harness.py chat-start --brief-file <brief>
```

La respuesta debe exponer `execution_mode`, `run_id`, `run_dir`, `project_dir`, `stage`, `agent` y `mode`. Completa exclusivamente esa etapa y avanza con `chat-next`. `chat-image` registra una importación física; por sí solo no demuestra generación observada ni habilita una revisión independiente.

Para un ejecutor headless, usa `doctor`, `init` y `run`; `record` es instrumentación de bajo nivel y nunca sustituye una ejecución gestionada. Los seis escenarios y sus límites viven en `harness/scenarios.json`.

Una ejecución completa genera `execution-receipt.json`. Verifícala sin confiar en la declaración del modelo:

```text
python tools/verify_execution.py --receipt <run-dir>/execution-receipt.json
```

Sin un recibo válido, el resultado puede estar inspirado en la metodología, pero no puede presentarse como una ejecución completa de Agentic Web Design.

All writes stay in the local project and implementation roots supplied by the user. Publishing or writing to an external service requires an explicit request.
