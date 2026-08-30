# System audit — v6.7.0

Date: 2026-08-30
Scope: executable chat enforcement and focal visual authority

## Finding

The repository could prove whether a managed run completed, but an external chat
client still had to interpret CLI instructions. In observed use it designed HTML
manually, omitted project-specific image production and used CSS circles or small
diagrams where a substantial visual intervention was required.

## Resolution

- Added a thin MCP adapter over the existing harness state machine.
- Added short initialization instructions and a private Secure MCP Tunnel route so
  ChatGPT can reach the local executable instead of treating GitHub as a runtime.
- Restricted file writes to the active owner's artifact and canonical build stages.
- Added paid, approval-visible OpenAI raster generation at the two existing image
  stages, with immediate physical receipt registration.
- Kept the external `IH-*` production loop, asset count decisions and one artistic
  master checkpoint unchanged.
- Added blocking focal-visual review evidence on desktop and mobile. Primitive UI,
  SVG diagrams, orbit circles and remote URLs cannot satisfy a required focal job.
- Kept the final execution receipt as the only proof of complete execution.

## KEEP

- Eight agents, six gates, thirteen stages and one artistic-master checkpoint.
- One canonical pipeline and the separate bounded `IH-*` image-production loop.
- Render-led image quantity and medium decisions rather than fixed image counts.

## IMPROVE

- Exercise the HTTP transport through a real authenticated remote MCP client.
- Review image prompts and integrated outputs from the first complete external run.

## ADD

- One bounded MCP transport adapter.
- One blocking focal-visual authority axis using final desktop/mobile evidence.

## REMOVE

- No role, stage, gate, artifact or design decision.
- The practical ability to substitute prose compliance for an executable chat run.

## Security and scope

Stdio remains local. HTTP binds loopback by default, validates Origin and refuses a
non-loopback interface without a bearer token. The server exposes no arbitrary
filesystem or shell tool. It remains an adapter: eight agents, six gates, thirteen
stages and the verified-landing scope are unchanged.

## Scenario verdicts

- Manual HTML after reading the repo: `UNMANAGED`.
- Required image replaced by circles, CSS, SVG or amateur icon: `BLOCKED`.
- Generated `IMG-*` without a physical local raster receipt: `BLOCKED`.
- MCP run with incomplete stages or stale implementation: `UNVERIFIED`.
- Complete run with valid digest-bound receipt: `VERIFIED`.

## Verification

System, architecture, agent, packaging, semantic, MCP boundary and image-authority
tests pass. The Image API is mocked in tests; validation performs no paid call.

## Result

PASS. The most common external-client bypass now has an executable boundary rather
than another prose instruction.

## Next review

After the first complete remote MCP execution, review tool approvals, image quality,
production-loop ergonomics and receipt visibility without adding another pipeline.
