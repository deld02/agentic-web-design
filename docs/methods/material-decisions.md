# Decisiones materiales

Este método evita dos fallos opuestos: elegir la primera solución razonable y documentar tanto que el proceso sustituya al diseño.

## Regla

La comparación vive donde se diseña. `decision-log.md` solo resume decisiones globales, transversales o costosas de revertir.

Una decisión es material si cambia la narrativa, dirección, foundation, verdad o método de media, mecanismo definitorio, composición responsive o arquitectura. Ajustes ópticos, espaciado local, estados comunes y variantes de una regla ya elegida son oficio del owner y no crean registros adicionales.

If research already evaluated material, downstream preserves the recorded decision or constraint and resolves only the uncertainty assigned to its owner. It does not silently choose again.

Identity authority is the strict case of this rule. G1 assigns stable `IDN-*` references to existing identity evidence and resolves each as `BINDING`, `EVOLVE_WITHIN_LIMITS` or `OPEN_TO_REPLACE`. G2 and G3 reference those IDs instead of restating or silently reinterpreting the brand. `NO_EXISTING_IDENTITY` closes the same question when no identity exists.

## Subdivisiones internas

Las áreas se organizan dentro de los artefactos existentes:

| Owner artifact | Subdivisiones |
|---|---|
| `content-architecture.md` | narrativa, contenido, CTA |
| `creative-direction.md` | conceptos, interacción, selección |
| `visual-system.md` | foundations, composición, responsive |
| `production-plan.md` | imágenes, tratamiento, efectos, producción |
| `technology-decision.md` | alternativas, arquitectura, operación |

No se crean subagentes, gates ni documentos por subdivisión.

## Bloque proporcional

Cuando exista una elección material, el artefacto owner demuestra:

1. pregunta o resultado que debe proteger;
2. alternativa base y challenger viables sobre el mismo contenido/contexto;
3. selección y motivo;
4. descarte relevante;
5. verificación proporcional al riesgo.

Puede ser una tabla, specimen, outline, storyboard o prototype. No necesita copiar una plantilla textual si la evidencia visual deja esos elementos inequívocos. `ONLY_VIABLE: motivo` se admite para una restricción real —verdad, derechos, identidad heredada válida o límite técnico—, no para evitar explorar.

Responsive es observacional: se registra dónde falla una invariante, qué recomposición lo resuelve y qué rango se verificó. No se inventan candidates ni se confunden viewports de prueba con breakpoints.

## Registro central

`decision-log.md` contiene solo decisiones que afectan varias fases o serían costosas de revertir; normalmente serán pocas. Ejemplos: dirección elegida, foundation principal, estrategia general de media, mecanismo definitorio y tecnología.

Campos: `ID | Scope | Decision | Evidence | Owner | Status`.

IDs: `PD-001`, `PD-002`… Estados: `DECIDED | VERIFIED | SUPERSEDED`. El detalle permanece en el artefacto enlazado y nunca se duplica por cada `IMG-*`, `FX-*` o breakpoint.

## Validación

Cada gate comprueba la comparación en su artefacto propietario. 07 juzga si las alternativas y la evidencia son reales; el validador solo protege mínimos estructurales que no añaden trabajo paralelo. G5 exige que las decisiones globales activas estén `VERIFIED`.
