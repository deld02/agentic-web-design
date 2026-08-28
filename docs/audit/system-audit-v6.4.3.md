# System audit — v6.4.3

Date: 2026-08-27
Scope: design-capability routing and stage enforcement

## Finding

The capability registry correctly classified core and conditional skills, but `automatic` was descriptive. The harness supplied the agent contract and pipeline without requiring the capability router, and gates checked only that a capability-log heading existed.

## Correction

Both headless prompts and interactive `chat-status` now supply the router, required core references and conditional candidates for the exact active stage. Stage readiness and gate validation require capability ID plus exact stage mode in the owned artifact. Registered local fallbacks preserve offline execution without turning omission into compliance.

Material non-static motion activates Emil. A structured craft classification activates Impeccable. Immersive, lookup, reference extraction and GSAP retain their narrow triggers; “premium” alone grants none of them.

## KEEP

- Eight agents, six gates, thirteen stages and existing project artifacts.
- One central capability registry and one router.
- Conditional capabilities that do not inflate every landing.

## IMPROVE

- Review the first complete ChatGPT execution packet to confirm capability findings are substantive rather than nominal log rows.

## ADD

- `validation_capability_activation.py` as the single runtime authority for routing receipts.
- Harness injection, stage/gate enforcement and five regression tests.

## REMOVE

- Automatic capability declarations without runtime consequence.
- The ability to substitute an improvised challenger while claiming the registered skill ran.

## Scenario verdicts

- Missing Hallmark/Anthropic/Taste/Jakub/Vercel at an allowed automatic stage: `BLOCKED`.
- Material motion without Emil: `BLOCKED`.
- Classified flat/generic result without Impeccable: `BLOCKED`.
- Immersive requested only by generic premium language: `NOT_ACTIVATED`.

## Verification

System, architecture, packaging, governance and semantic validators pass. All 155 tests pass, including five new capability-routing cases.

## Result

PASS. Core automatic skills are now part of the executable stage contract rather than optional documentation.

## Next review

After one complete managed landing run provides real capability logs and isolated review evidence.
