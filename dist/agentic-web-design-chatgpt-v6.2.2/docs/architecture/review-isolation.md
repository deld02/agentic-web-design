# Independent review isolation

`07` is independent only when it runs in a fresh context. A textual role switch inside the owner's conversation is not independent review.

The review packet contains only:

- brief and approved upstream decisions;
- the owner artifact under review;
- gate criteria and relevant project constraints;
- physical direction compositions or final desktop/mobile renders, plus the executable build when relevant;
- open risks explicitly recorded in the artifact.

It excludes hidden reasoning, persuasive summaries and informal owner justifications. The reviewer returns findings and a verdict; it does not edit the owner artifact. Using a different model/provider can increase diversity but is optional and never substitutes context isolation.

The protected review checkpoints in `status.json` use `review_context`:

- `PENDING` before the isolated execution;
- `ISOLATED` only after a fresh-context review using the packet above;
- `EXCEPTION_RECORDED` when isolation was impossible. This state cannot approve the checkpoint.
