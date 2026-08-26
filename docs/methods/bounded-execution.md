# Bounded execution

This method prevents silent retry loops without lowering design quality or imposing a fixed total project duration.

## Runtime budget

- Each stage gets one initial pass and at most one automatic corrective pass.
- The same material finding or blocker may trigger only one automatic retry. If it recurs, stop.
- A failed tool call may be retried once only when the failure is plausibly transient. A different tool or broader action is not a hidden extra retry.
- The artistic master gets at most one targeted edit/regeneration before its confirmation; a rejected G4 image output gets one directed regeneration inside the production subloop.
- Upstream work may reopen automatically once per causal change. A downstream failure must not restart the whole pipeline.

User-requested changes, genuinely new evidence and a user-authorized resumed pass start a new bounded run. They do not retroactively legitimize prior loops.

## Progress and inactivity

While work is active, provide a short progress update at least every ten minutes when the runtime permits it. A progress message names the current stage, newest material evidence and next expected output; activity logs or repeated plans are not progress.

If fifteen minutes pass without new material evidence—an artifact, render, decision, validated build or resolved finding—stop the current attempt. Do not keep browsing, regenerating or validating invisibly.

Waiting for the single visual confirmation is an explicit user pause, not active work. A delegated choice closes that pause and continues within the remaining budget.

## Exhaustion result

On exhaustion, preserve all valid work and return:

```text
RESULTADO: BLOCKED
STAGE / PASS:
ÚLTIMO AVANCE MATERIAL:
BLOQUEO REPETIDO O SIN PROGRESO:
ARTEFACTOS CONSERVADOS:
DECISIÓN O CAMBIO NECESARIO:
```

Do not claim completion, discard evidence, start another automatic pass or broaden scope. 00 records the blocker in existing status fields; no extra project artifact or checkpoint is created.
