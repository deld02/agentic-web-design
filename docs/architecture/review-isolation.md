# Independent review isolation

`07` is independent only when it runs in a fresh context. A textual role switch inside the owner's conversation is not independent review.

The review packet contains only:

- brief and approved upstream decisions;
- the owner artifact under review;
- gate criteria and relevant project constraints;
- physical direction compositions or final desktop/mobile renders, plus the executable build when relevant;
- open risks explicitly recorded in the artifact.

It excludes hidden reasoning, persuasive summaries and informal owner justifications. The reviewer returns findings and a verdict; it does not edit the owner artifact. Using a different model/provider can increase diversity but is optional and never substitutes context isolation.

The harness attaches the existing FRONTIER, SIMPLE and SATURATED benchmark captures from research in the same review call. The reviewer first distinguishes visible excellence from generic risk, then compares candidate craft and identity under `reference_calibration` and `artistic_authority`. These are review axes, not new gates. A comparison must name both reference and candidate evidence; missing or weak benchmarks return to research instead of lowering the bar. This per-project calibration is not proof that the critic has been empirically validated: a labelled benchmark evaluation with known excellent and mediocre outcomes is still needed to measure false approvals. No verdict may claim that evaluation happened merely because the axes exist.

The review result has one root `correction_kind`: `NONE` for PASS; otherwise `CRAFT`, `CONCEPT` or `REFERENCE`. Findings state the visible cause and required observable gain, not a replacement design. CRAFT preserves a viable thesis and repairs execution. CONCEPT reopens the visual relationship in the same owner stage; margins or explanatory labels alone do not prove conceptual repair. REFERENCE escalates to 00 for research correction; the owner cannot silently rewrite upstream decisions. Mixed failures use the earliest material cause, retaining all findings. This adds no stage, resets no correction allowance and does not authorize new direction after approval.

Evaluate the complete composition, not literal exclusivity of an image. Nonliteral media may communicate through identity, content, framing and behavior; depicting the category is neither necessary nor sufficient. Interchangeability must be demonstrated at that relationship level. Compare craft where audience, action, trust and available proof/media make it transferable. A studio portfolio is not a requirement to invent a portfolio for a consultant. An irrelevant benchmark returns REFERENCE, not a demand for decoration.

The protected review checkpoints in `status.json` use `review_context`:

- `PENDING` before the isolated execution;
- `ISOLATED` only after a fresh-context review using the packet above;
- `EXCEPTION_RECORDED` when isolation was impossible. This state cannot approve the checkpoint.
