# Runtime and Blender repairs — 2026-09-27

Scope: the eight findings in the local system audit. Existing 13-stage pipeline,
eight roles and six gates are unchanged. No deployment or GitHub push.

## Changes

| Finding | Repair |
|---|---|
| Missing 3D import through chat | Two bounded MCP operations: import_blender_file and inspect_blender_asset, only for declared custom Blender assets during production-plan. |
| Self-authored Blender success | Server-owned manifest and inspection paths; fixed inspector opens scene and GLB in fresh Blender processes. Embedded Python disabled; uploaded builder archived, never run. |
| Export differs from delivered model | Delivery path/hash bound to inspected bytes and a fresh desktop browser response hash. Static rebuilds preserve these assets and reject conflicts. |
| Provider failures consume design corrections | Separate counters: two completed reviews; three infrastructure failures. Legacy counters without a completed receipt retain failures but recover artistic allowance. |
| Misleading startup readiness | Session starts require CLI subscription reviewer readiness. Blender remains optional and separately reported. |
| Windows evidence corruption | Explicit UTF-8 on renderer subprocess; accented browser observations tested. |
| Stale registry and synthetic dates | Eight sources and licenses re-inspected, documented in capability-revalidation-20260927.md. Synthetic reference dates generated at test time. Freshness enforcement retained. |
| Tests duplicate installed Blender | Shared source-copy fixture excludes .harness, node_modules and generated exports. |

## Verification

Final run: **245 tests, 242 passed, 3 opt-in tests skipped, zero failures** in
65.538 seconds, with the real Blender/browser test enabled. The separate focused
live run passed all seven tests in 33.467 seconds.

The real integration probe imports the existing technical Blender fixture through
the production handlers, opens both scene and GLB with Blender 4.5.9 LTS, copies
the inspected model into the landing, and renders the Three.js viewer with Edge.
It asserts active WebGL, reduced-motion fallback, exact fetched hash, rebuild
preservation, collision rejection, tampered export rejection and invalid scene
rejection. This is a technical fixture, not a premium design assessment.

Local logs: `.harness/repair-tests-final-20260927.log` (full suite including real
Blender probe), `.harness/blender-repair-live-20260927.log` (focused live probe).
validate_system.py and audit_system.py passed; git diff --check found no whitespace
errors. The separate skill-creator quick validator could not run because its Python
environment lacks PyYAML; repository skill-contract and packaging tests passed.

## Operational limits

- Reload/restart the existing MCP server to expose the new tool names and code.
- No new completed 13-stage client landing or artistic approval is claimed.
- The native image-generation and subscription-review live tests were not rerun
  here; provider mocks do not certify current credentials or account access.
- External Blender production remains separate; the MCP imports and inspects,
  it does not silently install a plugin or execute an uploaded builder.
- Individual returned files are limited to 12 MiB; optimize larger exports.
- Blender parsing runs locally with disabled autoexec, not an OS sandbox. Server
  files are protected from MCP writes, not from administrators of the host.
- References were updated using the skill-creator guidance to keep one conditional
  procedure, rather than duplicating a new workflow in every agent.
