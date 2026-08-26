# System audit — v6.3.1

Date: 2026-08-26  
Scope: experience construction before visual design

## Finding

The system defined content flow and later visual rhythm, but did not require one explicit causal account of how every scene changes the visitor's understanding, confidence or intent. Adding six specialist agents would have duplicated existing ownership and increased handoffs without guaranteeing continuity.

## Correction

Agent 02 now owns one Experience Spine inside the existing content architecture. It records entry state, active question, meaning, proof, desired shift, next tension/action and narrative function for every outlined scene. Agents 03, 04 and 05 consume it at their existing stages. Agent 07 must verify `EXPERIENCE_CONTINUITY` on final desktop and mobile renders.

## KEEP

- Eight agents, six gates, thirteen stages and one human creative-master checkpoint.
- Existing project artifacts and the separation between semantic, visual and interaction decisions.
- Independent rendered review by 07.

## IMPROVE

- Evaluate causal quality visually and editorially; deterministic validation only proves coverage and structure.
- Refine the spine from real project failures rather than adding speculative fields.

## ADD

- `docs/methods/experience-spine.md` as the single method authority.
- Exact per-scene G1 validation in `tools/validation_experience.py`.
- Final `EXPERIENCE_CONTINUITY` review evidence.

## REMOVE

- The need for proposed agents 03A, 03B, 03C, 03D, 06A and 10A.
- Premature visual and interaction prescriptions during semantic architecture.

## Scenario verdicts

- Experience construction before art direction: `SUPPORTED` in G1.
- Visual translation of the selected experience: `SUPPORTED` in existing G2/G3 ownership.
- Interaction and final continuity review: `SUPPORTED` in existing G4 ownership.
- Additional experience-agent hierarchy: `REJECTED` as duplicate architecture.

## Verification

All validators, architecture ratchets, runtime-pack checks and 130 unit tests pass. The pipeline remains eight agents, six gates and thirteen stages.

## Next review

After the next real project reveals whether the Experience Spine produces observable continuity rather than merely complete rows.
