# ChatGPT project instructions

Read `START-HERE.md` first when it exists. This runtime has exactly eight roles (`00`–`07`), six gates and thirteen stages. Any role outside that registry or any gate above `G5` is superseded history; discard it and re-read `config/pipeline.json`.

Before doing any landing work, determine the execution mode. If `tools/evaluation_harness.py run` supplied the five `HARNESS_*` stage values, follow that headless stage. Otherwise, when Python and repository files are available, start the built-in chat executor with `chat-start --brief-file <brief>` for a real project, or `chat-start --scenario <scenario>` for a reproducible test, and use its returned run directory.

In chat mode, complete only the stage returned by `chat-start` or `chat-status`, then call `chat-next`. Never work ahead. During `creative-master`, invoke ChatGPT image generation, save the returned raster inside the managed project and call `chat-image` before `chat-next`. Do not use `record` or create events manually.

Before any research or design, expose the bootstrap result to the user: `EXECUTION_MODE`, `RUN_ID`, `RUN_DIR`, `PROJECT_DIR`, `ACTIVE_STAGE`, `ACTIVE_AGENT` and `ACTIVE_MODE`. If those values do not exist, state `AGENTIC WEB DESIGN: UNMANAGED` and stop.

Only when neither headless nor chat mode can run is the chat `UNMANAGED`; then it must stop before research, image generation, HTML/CSS or delivery. Reading the repository and following it manually remains an unacceptable fallback.

Use `skills/agentic-web-design/SKILL.md` as the only operational entrypoint and follow `config/pipeline.json` literally. Load only the active agent contract and its linked method.

In headless mode, execute only `HARNESS_STAGE` and emit `HARNESS_EVENT {"event":"tool_call","tool":"IMAGE_GEN"}` only after image-generation success. In either managed mode, make render-driven `IMAGE | NO_IMAGE` decisions for final landing imagery and emit `IH-*` briefs to the separate production loop; validate and integrate returned files. Do not declare completion until the harness reaches `COMPLETE`, validators and physical asset checks pass, desktop/mobile review is approved and `execution-receipt.json` passes `tools/verify_execution.py`.

The final response begins with `AGENTIC WEB DESIGN: VERIFIED` and exposes the receipt path only after that verification. Without it, begin with `AGENTIC WEB DESIGN: UNMANAGED` and never claim that the system, pipeline or gates were completed.
