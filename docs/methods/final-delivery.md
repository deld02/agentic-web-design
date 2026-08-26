# Final delivery

Use this method only after the independent final review. The product is the working landing, not the process documentation.

## Required handoff

Complete `qa-release.md#Final delivery contract` with:

- an honest status: `READY`, `READY_WITH_LIMITATIONS` or `NOT_READY`;
- the real entry file inside `implementation_root`;
- exact run and build commands (`NOT_REQUIRED` is valid only for build);
- a real preview target and a physical clean delivery folder or ZIP;
- confirmation that every required final asset is integrated;
- a short project-specific summary and explicit limitations.

The existing `FINAL_RENDER_DESKTOP` and `FINAL_RENDER_MOBILE` fields are the visual proof; do not duplicate them in this contract.

## Status semantics

- `READY`: the landing is executable, reviewed and complete; `LIMITATIONS` must be `NONE`.
- `READY_WITH_LIMITATIONS`: the landing is executable and reviewed, and the stated limitation does not invalidate its primary objective.
- `NOT_READY`: any missing file, pending media, broken primary behavior, absent render, unresolved blocking finding or non-executable handoff. G5 must remain blocked.

## Clean package

The delivery package contains only what the recipient needs to run, build or inspect the landing. Exclude harness state, audits, tests, caches, repository metadata, dependency folders and internal design-process evidence. Source files and licenses actually required by the landing remain included.

## User-facing completion

The final response must expose concrete paths or URLs for the package, entry/preview and both final renders, plus the status, commands and limitations. Never say “delivered” while making the user search for the product.
