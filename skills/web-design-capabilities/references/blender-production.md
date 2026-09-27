# Conditional Blender production

Use only after G3 selected real 3D and 05 chose custom Blender authoring in the
existing `3D production provenance` table. No new stage or user checkpoint.
G3 owns suitability; this capability cannot choose 3D or change the master.

## Execution

Check the installed Blender executable/version and available execution route.
Blender Agent Studio is an optional MIT companion, not an assumed installed
tool. Its plugin requires Blender and Bun; local Blender Python scripts are a
valid alternative without MCP, Docker or a model API key. Never install software
silently or claim plugin use when only the local fallback was used.

`tools/start-local.ps1 -BlenderPath <executable>` exposes `BLENDER_EXECUTABLE`
to its child runtime; this is optional and never blocks non-3D work. For a real
local smoke test run `python tools/blender_smoke.py --blender <executable>
--output <new-test-directory>`. It performs CPU rendering, GLB export, fresh
import in a second process with bounded timeouts. It does
not test a browser or certify aesthetic quality, and refuses an existing output
directory. Keep these technical samples separate from project artwork.

05 gives the existing production loop the selected reference, proportions,
camera, materials, semantic states, budget and expected exports. Inspect a
graybox before expensive detail. Produce the editable scene and reproducible
builder, then beauty views. Interactive delivery also exports a GLB and checks
it by fresh import. Keep stable part names/pivots for required motion. The
browser owns interaction and lighting; Blender simulations do not automatically
survive export. Inspect scripts before execution, write only to project output,
and use the normal bounded retry policy.

06 integrates the approved result with accessible HTML and the already selected
runtime. 07 compares the result to the approved reference, reviews material/light
quality, traverses existing spatial states and tests the existing fallback and
device budget. Reuse those reviews; do not add a second spatial QA checklist.
If production fails, retain the approved direction and report the blocker or
return to its owner for a reviewed alternative, never substitute faux 3D.

## Returned evidence

During `production-plan`, declare the custom Blender FX in the existing provenance
table, then call `import_blender_file` once per role: `scene` (uncompressed .blend),
`builder` (.py, archived only), `preview` (.png), and `export` (.glb) for interactive
3D. Each request carries `run_id`, `fx_id`, `role`, `data_base64`; limit 12 MiB per
file. Larger files require an optimized export, not bypassing the import boundary.

Call `inspect_blender_asset` with `run_id` and `fx_id`. The server opens the scene
and GLB in fresh Blender processes using its own inspector, with embedded Python
disabled. It never executes the returned builder. Missing Blender or failed import
blocks acceptance and preserves logs. No client-authored inspection receipt is accepted.

The tool maintains `BLENDER_HANDOFF: evidence/blender/handoff.json` and returns
`delivery.path`. 06 must load that exact asset, then call `render_landing`. Delivery
checks bind the inspected hash, deployed bytes and current desktop browser fetch.
07 still judges appearance, meaningful interaction and fallback: a successful
import or network fetch is not proof that the model looks good. Local filesystem
administrators remain inside the trust boundary; these receipts are not signed
attestation against an operator who can rewrite server files.

## Sources and rights

Source and MIT license inspected 2026-09-25:
https://github.com/ifBars/blender-agent-studio
https://github.com/ifBars/blender-agent-studio/blob/main/LICENSE

No upstream code or assets are vendored here. The independently authored workflow
above may use Blender Python without that companion. `cth9191/blender-to-web`
is a research reference only: its README currently reserves reuse rights for
authored code/assets. Do not install, copy or redistribute that material as an
OS dependency without suitable permission. Recheck upstream terms before use.
