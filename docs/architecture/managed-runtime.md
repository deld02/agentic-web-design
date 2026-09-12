# Managed runtime: scope and acceptance

The existing pipeline remains authoritative. This adapter adds execution tools,
not new design roles or gates. Its supported build is static HTML or a static
export supplied by the frontend owner. It does not remotely run npm, arbitrary
shell commands, deployments or WordPress mutations.

## Server setup

- Python with Pillow available to the server interpreter.
- Node.js with Playwright resolvable by `require('playwright')`, and an installed
  Chromium browser. `AGENTIC_BROWSER_CHANNEL=msedge` supports installed Edge on Windows.
- `OPENAI_API_KEY`, `AGENTIC_IMAGE_MODEL` and `AGENTIC_REVIEW_MODEL` configured on
  the server. Select accessible models supporting image generation and visual
  Responses structured output respectively. Never paste credentials into a brief.
- An authenticated MCP connection from ChatGPT to this server; repository access
  alone is insufficient. See README for transports.

Call `runtime_status` first. Presence checks do not verify model access, billing,
browser launch or ChatGPT rendering of binary resources. `start_landing` refuses
to create a run when required local configuration is missing.

## Execution tools

Follow the returned specialist packet, then `advance_stage`; do not edit official
state. For visual work, use `generate_image`, `upload_image`, `read_image` and
`render_landing`. Imports never masquerade as server-observed generation.

`render_landing` captures desktop, mobile, declared scene anchors and optional
click, hover, keyboard-tab and reduced-motion states. Use relative asset URLs and
`data-scene-id="SCN-001"` anchors matching the content architecture. External
network requests are blocked: bundle assets into the static export. Captures of
an interaction are evidence to inspect, not proof of every possible behavior.

At review stages call `run_review` with actual images. A fresh Responses request
receives the relevant contract and artifacts, not the designing conversation.
The receipt records provider response ID and input hashes. Changed inputs require
another review; unchanged input returns the cached result. At most two provider
attempts per review stage prevent an unbounded paid correction loop. A REVISE
returns the preceding owner's correction packet without advancing the stage.
Local files are server-owned through MCP permissions, not cryptographically
protected against a hostile process with filesystem access.

Use `prepare_delivery` to package the static output and integrity manifest; this
does not approve it. Complete build/release checks and require `verify_run` to
return `verified: true`. `download_delivery` verifies ZIP contents against the
implementation and returns an MCP resource for archives up to 12 MiB. Client
download presentation must be tested; larger archives remain on the server.

## Acceptance before calling this production-ready

1. Run local unit tests and the optional real-browser smoke test.
2. Connect the intended ChatGPT client; test tool calls, physical generation,
   viewing images, one fresh provider review and delivery retrieval.
3. Complete one real landing through all stages, including master approval and
   final render comparison. Record latency, actual costs and any manual recovery.
4. Repeat with a distinct brief. Judge visual quality against the selected
   references, not the number of gates passed.

Current local tests exercise runtime behavior and a real static browser fixture.
Provider tests use simulated responses. They do not prove a live complete
landing, artistic excellence, or a working ChatGPT connection.

API contracts: [vision inputs](https://developers.openai.com/api/docs/guides/images-vision)
and [structured output](https://developers.openai.com/api/docs/guides/structured-outputs).
