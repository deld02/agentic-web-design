# Managed runtime: scope and acceptance

The existing pipeline remains authoritative. This adapter adds execution tools,
not new design roles or gates. Its supported build is static HTML or a static
export. Optional Docker or explicitly trusted local adapters install locked npm
dependencies and build frontend exports. Only Docker isolates project code. Neither adapter
deploys, mutates WordPress or verifies backend services.

## AI execution provider

`start-local.ps1` defaults to `AGENTIC_AI_BACKEND=session`: no API keys, no tunnel.
The Codex client calls the local MCP over stdio. Python direct launches retain
the API default for existing integrations; select the session backend explicitly.
The run records its backend and rejects implicit provider switches.

- Generation: `generate_image` returns NEEDS_NATIVE_IMAGE plus prompt/output path;
  this is a production request, **not a successful generation**. The client calls
  its real native image tool, saves the raster and calls `register_session_image`
  with the actual tool-result reference. Missing tool means pause, not SVG fallback.
- Provenance: raster decoding and hashes are checked. Native tool origin is
  client-attested and disclosed in `verify_run` and the execution receipt. It is
  not cryptographic proof of a tool invocation. Imported bytes alone do not qualify.
- Review: `run_review` starts a fresh `codex exec` conversation with attached
  evidence and structured output. No resume, no owner conversation, no user config,
  read-only sandbox. It requires ChatGPT CLI login, strips API-key variables, and
  forces ChatGPT authentication. The server records the actual completed thread
  ID, validates findings and hashes, and keeps existing retry limits. This is
  conversation separation, not isolation from all readable host files.
- Missing CLI login blocks review. Run `codex login` interactively; never extract
  the desktop app's credentials. Subscription usage/limits still apply.
- API generation/review remains opt-in via `-AIBackend api`. The no-key mode never
  silently falls back to it. ChatGPT **web** connection instructions below belong
  to that separate API/tunnel alternative, not to local Codex.

The local adapter tests simulate Codex review responses. A subscription-authenticated
review and full landing still need live acceptance after CLI login.

## Frontend execution

Call `check_technology` before selection. `static-html` uses the existing renderer;
`npm-static-export` needs an enabled local Node/npm or Docker backend. `server-runtime` or required
external services return BLOCKED. Do not downgrade them silently.
Record `EXECUTION_PROFILE` and `REQUIRED_EXTERNAL_SERVICES` in the existing
technology decision. Stage-exit validation independently rejects unsupported
profiles and required services even when the capability tool was skipped.

### Local Windows execution without Docker

On the prepared Windows workstation, run `./tools/start-local.ps1 -Mode doctor`.
The launcher resolves the bundled Python/Node and the project-local npm installation;
it changes only its process environment, not Windows settings. `-Mode stdio` starts
the MCP server; `-Mode http` binds only to loopback. Override `-PythonPath`,
`-NodePath` and `-NpmCli` on another computer. Runtime downloads under `.harness/`
are ignored by Git and are **not** shipped in the repository/package.

Set these variables in the terminal that starts the MCP server:

```powershell
$env:AGENTIC_BUILD_BACKEND = 'local'
$env:AGENTIC_ENABLE_BUILDS = '1'
$env:AGENTIC_NODE = 'C:/path/to/node.exe'
$env:AGENTIC_NPM_CLI = 'C:/path/to/npm/bin/npm-cli.js'
```

The first build request returns the source SHA256 without executing anything.
Review that project's source, then set `AGENTIC_LOCAL_APPROVED_SHA256` to that
exact digest and restart the server from that terminal. Any source change needs
fresh approval. Chat tools cannot set this operator environment variable.

This is **trusted host execution, not a sandbox**. Scripts and dependencies can
access files and network with your account's permissions despite the clean child
environment. Use a non-administrator account; never approve untrusted projects.
Provider keys are not passed to npm, but this does not prevent host file access.
Installation lifecycle hooks and pre/post build scripts are disabled. Each command
has a 180-second timeout; Windows timeout handling attempts to stop its process tree.
There are no local CPU, memory, disk or network isolation guarantees. Failed work
and prior exports are preserved. Do not automatically enable install hooks when a
dependency fails. Existing pipeline, media and review checks remain unchanged.

Connecting ChatGPT web still requires a separately configured authenticated connection;
enabling local compilation does not establish that connection or configure model keys.

The prepared workstation also has the official tunnel client in `.harness/runtime/`.
To connect, obtain a tunnel associated with your ChatGPT workspace and runtime
permissions from [Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels).
Then run:

```powershell
./tools/connect-chatgpt.ps1 -TunnelId tunnel_YOUR_ID -ImageModel YOUR_IMAGE_MODEL -ReviewModel YOUR_REVIEW_MODEL
```

Use model IDs available to your API account. The script requests missing keys via
hidden local input, never chat or a tracked file. `CONTROL_PLANE_API_KEY` needs
Tunnels Read + Use; `OPENAI_API_KEY` is for generation/review, whose API usage can
incur charges. It creates a local profile without overwriting an existing one,
checks it, and runs the official outbound tunnel in the foreground. Keep that
terminal open. In ChatGPT developer app setup select Connection → Tunnel and the
same ID. Actual account access and end-to-end calls must still be verified.
See [official connection instructions](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

Local acceptance: npm 12.0.2 and the Windows tunnel client 0.0.14 were downloaded
from their official distributions and verified against published SHA512/SHA256.
The opt-in `test_local_build_live.py` successfully compiled a real Vite 7.1.7
fixture with Node 24.19.0. This proves this static build, not every framework,
provider credentials, or the complete ChatGPT flow. Live-test work is preserved
in an `awd-vite-*` temporary directory for inspection.

### Isolated Docker alternative

The operator explicitly enables `AGENTIC_ENABLE_BUILDS=1`, leaves
`AGENTIC_BUILD_BACKEND=docker`, and provisions
`AGENTIC_BUILD_IMAGE` as a local Linux Node/npm image pinned by `@sha256:...`.
No automatic image pull or privileged execution is allowed. Presence is not a
successful framework test. The image must support a non-root user, npm, sh and cp.

06 writes editable source and package-lock.json in `frontend/`, including
`runtime.json` with `{"target":"static","external_services":[]}` only when true.
The build script must export to `dist` or `out`; call `build_frontend` with that
directory. A Next.js static export, React/Vite or Astro static build can be
candidates; compatibility must be demonstrated, not inferred from the name.

Source is mounted read-only; writable container space is bounded tmpfs. Install
uses public-registry lock entries with lifecycle scripts disabled and network
enabled. Network is disconnected before the build script executes; pre/post
scripts remain disabled. Dependencies requiring install scripts or build-time
network may fail: do not weaken these controls automatically. The container has
CPU, memory, process and command-time limits and is removed on completion/failure.
Four build attempts per project bound accumulation. Status logs omit arbitrary
stdout/stderr; failures may require operator diagnosis in an isolated environment.

Only bounded regular export files return. Successful output replaces
`implementation/` while retaining the previous version. Failed work is preserved
outside the project and requires operator cleanup; credentials are never mounted.
Then use the same render, media integration and review tools. A subsequent source
change requires rebuilding, rerendering and reintegrating any media absent from
the rebuilt export. Root-relative framework assets are supported by the renderer.

Delivery ZIP remains the deployable static export, not an editable source bundle.
`frontend/` and the lockfile remain available on the server. SSR, authenticated
backend flows and publishing require separate adapters and explicit access.
This adapter has mocked lifecycle tests; a live Docker framework pilot remains
required before claiming that a particular stack works end-to-end.

Implementation references: [Docker execution constraints](https://docs.docker.com/reference/cli/docker/container/run/)
and [Next.js static export boundaries](https://nextjs.org/docs/app/guides/static-exports).

## Server setup

- Python with Pillow available to the server interpreter.
- Node.js with Playwright resolvable by `require('playwright')`, and an installed
  Chromium browser. `AGENTIC_BROWSER_CHANNEL=msedge` supports installed Edge on Windows.
- API backend only: `OPENAI_API_KEY`, `AGENTIC_IMAGE_MODEL` and `AGENTIC_REVIEW_MODEL` configured on
  the server. Select accessible models supporting image generation and visual
  Responses structured output respectively. Never paste credentials into a brief.
- A local stdio MCP connection for Codex session mode, or an authenticated connection from ChatGPT web; repository access
  alone is insufficient. See README for transports.

Call `runtime_status` first. Presence checks do not verify model access, billing,
browser launch or ChatGPT rendering of binary resources. `start_landing` refuses
to create a run when required local configuration is missing.

## Execution tools

Follow the returned specialist packet, then `advance_stage`; do not edit official
state. For visual work, use `generate_image`, `upload_image`, `read_image` and
`render_landing`. Imports never masquerade as server-observed generation.

During `research-strategy`, use `upload_image` to preserve captured reference
rasters under `evidence/`, then cite the returned path, original URL, inspection
date and observations in `research-strategy.md`. Research imports reject
production asset IDs and retain `EXTERNAL_IMPORT` provenance. A screenshot shown
in chat is not yet an archived reference, and a content/HTML export is not a
screenshot. If the client cannot persist or transfer capture bytes, report that
specific transport limitation; do not approve research using URLs alone.

`render_landing` captures desktop, mobile, declared scene anchors and optional
click, hover, keyboard-tab and reduced-motion states. Use local asset URLs and
`data-scene-id="SCN-001"` anchors matching the content architecture. External
network requests are blocked: bundle assets into the static export. Captures of
an interaction are evidence to inspect, not proof of every possible behavior.

At review stages call `run_review` with actual images. A fresh Responses request
(API backend) or a fresh Codex conversation (session backend) receives the relevant
contract and artifacts, not the designing conversation. The receipt records the
provider response or thread ID and input hashes. Changed inputs require
another review; unchanged input returns the cached result. At most two completed
design reviews and three infrastructure failures per stage bound the loop. Failed
authentication, timeout, malformed output or stale input do not spend a design review.
Exhausted infrastructure retries require operator recovery after repairing the cause.
A REVISE
returns the preceding owner's correction packet without advancing the stage.
Local files are server-owned through MCP permissions, not cryptographically
protected against a hostile process with filesystem access.

Custom Blender returns use `import_blender_file` and `inspect_blender_asset` in
the existing production stage. The complete conditional procedure and limits live
in [Blender production](../../skills/web-design-capabilities/references/blender-production.md).
Blender is optional in runtime readiness; the subscription reviewer is not optional
for session-mode starts. Static rebuilds preserve the inspected 3D asset bytes and
reject conflicting output. The renderer records successful local asset response
hashes; final validation binds these to the inspected export and current source.

Use `prepare_delivery` to package the static output and integrity manifest; this
does not approve it. Complete build/release checks and require `verify_run` to
return `verified: true`. `download_delivery` verifies ZIP contents against the
implementation and returns an MCP resource for archives up to 12 MiB. Client
download presentation must be tested; larger archives remain on the server.

## Acceptance before calling this production-ready

1. Run local unit tests and the optional real-browser smoke test.
2. Connect the intended ChatGPT client; test tool calls, physical generation,
   viewing images, one fresh provider review and delivery retrieval.
3. Complete one real landing through all stages, including complete-proposal approval and
   final render comparison. Record latency, actual costs and any manual recovery.
4. Repeat with a distinct brief. Judge visual quality against the selected
   references, not the number of gates passed.

Current local tests exercise runtime behavior and a real static browser fixture.
On 2026-09-20, the opt-in subscription review smoke test also passed with a real
ChatGPT-authenticated Codex conversation, an attached synthetic raster and a
structured review response (`AGENTIC_RUN_SESSION_TESTS=1`,
`tests/test_session_backend.py`: seven passing tests). No API key was used.
This proves the subscription review path, not native image generation through
MCP, a complete landing, artistic excellence, or a ChatGPT web connection.

API contracts: [vision inputs](https://developers.openai.com/api/docs/guides/images-vision)
and [structured output](https://developers.openai.com/api/docs/guides/structured-outputs).
