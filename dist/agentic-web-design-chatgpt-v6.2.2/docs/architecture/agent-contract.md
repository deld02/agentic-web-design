# Agent Contract Standard

Todo agente core debe contener, como mínimo:

1. MISIÓN
2. OWNERSHIP
3. NO PUEDE
4. MODOS
5. INPUTS OBLIGATORIOS
6. PROCESO
7. OUTPUTS OBLIGATORIOS
8. GATE / CRITERIO
9. ESCALADO
10. REGLAS ESPECÍFICAS

## Resultado

Los agentes no cambian state. Entregan:

`READY_FOR_GATE | REVISE | BLOCKED`

## Handoff

Un handoff válido identifica from/to, stage/gate, inputs canónicos, artefactos, evidencia, criterio de aceptación, blockers y owner de retorno.
