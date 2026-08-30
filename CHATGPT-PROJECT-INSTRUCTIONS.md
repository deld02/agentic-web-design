# ChatGPT project instructions

Read `START-HERE.md` first when it exists. This runtime has exactly eight roles (`00`–`07`), six gates and thirteen stages. Any role outside that registry or any gate above `G5` is superseded history; discard it and re-read `config/pipeline.json`.

Before doing any landing work, determine the execution mode. When the Agentic Web Design MCP tools are available, call `start_landing` first and use only those bounded tools; this is the preferred chat mode. If `tools/evaluation_harness.py run` supplied the five `HARNESS_*` stage values, follow that headless stage. Otherwise, when Python and repository files are available, start the built-in chat executor with `chat-start --brief-file <brief>` for a real project, or `chat-start --scenario <scenario>` for a reproducible test, and use its returned run directory.

In chat mode, complete only the stage returned by `chat-start` or `chat-status`, then call `chat-next`. Never work ahead. During `creative-master`, invoke ChatGPT image generation, save the returned raster inside the managed project and call `chat-image` before `chat-next`. Do not use `record` or create events manually.

In MCP mode, complete only the `stage_packet` returned by `start_landing`, `get_stage` or `advance_stage`. That packet is the orchestrator handoff: it includes the active specialist contract, required inputs, current artifact, stage-specific guidance and automatic capabilities. Use `get_guidance` only for a conditional capability whose stated trigger is present. Use `write_file` only for the packet's writable files; never edit `status.json`, which belongs to the harness. During `creative-master`, use `generate_image` (or `register_image` for a raster already produced) and then request the one user checkpoint with `confirm_master`. During `production-plan`, every declared generated `IMG-*` must be produced and registered before advancing. Never replace required project imagery with CSS geometry, SVG diagrams, orbit circles, amateur icons or a remote URL. End only after `verify_run` returns `verified: true`.

Before any research or design, expose the bootstrap result to the user: `EXECUTION_MODE`, `RUN_ID`, `RUN_DIR`, `PROJECT_DIR`, `ACTIVE_STAGE`, `ACTIVE_AGENT` and `ACTIVE_MODE`. The equivalent MCP response fields are valid evidence. If those values do not exist, state `AGENTIC WEB DESIGN: UNMANAGED` and stop.

Only when neither headless nor chat mode can run is the chat `UNMANAGED`; then it must stop before research, image generation, HTML/CSS or delivery. Reading the repository and following it manually remains an unacceptable fallback.

A GitHub connector, repository URL or uploaded ZIP is not execution evidence. A ZIP is usable only when the current chat has a real Python/filesystem runtime, successfully runs `chat-start` and exposes the managed preflight before any design work. Never ask for a ZIP as if possession of files alone solved the runtime boundary. Prefer the connected harness MCP, including a private Secure MCP Tunnel, when available.

Use `skills/agentic-web-design/SKILL.md` as the only operational entrypoint and follow `config/pipeline.json` literally. Load only the active agent contract and its linked method.

In headless mode, execute only `HARNESS_STAGE` and emit `HARNESS_EVENT {"event":"tool_call","tool":"IMAGE_GEN"}` only after image-generation success. In either managed mode, make render-driven `IMAGE | NO_IMAGE` decisions for final landing imagery and emit `IH-*` briefs to the separate production loop; validate and integrate returned files. Do not declare completion until the harness reaches `COMPLETE`, validators and physical asset checks pass, desktop/mobile review is approved and `execution-receipt.json` passes `tools/verify_execution.py`.

The final response begins with `AGENTIC WEB DESIGN: VERIFIED` and exposes the receipt path only after that verification. Without it, begin with `AGENTIC WEB DESIGN: UNMANAGED` and never claim that the system, pipeline or gates were completed.
