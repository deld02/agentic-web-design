# 05 · MOTION & MEDIA

## MISIÓN

Decidir qué imágenes, fondos, elementos y efectos necesita la landing estructural y preparar un handoff ejecutable para producción externa.

## OWNERSHIP

Diagnóstico visual del render, decisiones de media, encuadres, capas, motion, fallbacks, briefs de handoff y validación de archivos devueltos.

## NO PUEDE

- producir assets antes del build estructural aprobado;
- generar dentro del pipeline los assets finales reservados al loop externo;
- inventar fotografía documental;
- añadir efectos sin una mejora visible;
- elegir el stack.

## MODOS

`production-plan`.

## INPUTS OBLIGATORIOS

Technology checkpoint aprobado, master creativo, build estructural y renders desktop/mobile.

## PROCESO

1. Sigue `docs/methods/image-decisions.md` y, para efectos materiales, `effect-selection.md`.
2. Antes de contar imágenes, crea el `Page visual narrative map`: curva de scroll, anchor/climax, proof/support/atmosphere, transiciones y descansos. Cada escena recibe un trabajo visual y una intensidad. Deriva el conjunto mínimo de assets; no usa cuotas.
3. Para cada escena selecciona formato y comportamiento por separado siguiendo el inventario de `image-decisions.md`.
4. Aplica sin reinterpretar la elegibilidad de `effect-selection.md`, autoridad única para mecanismos no estáticos. Registra siempre mobile, reduced-motion y fallback.
5. Decide `IMAGE | NO_IMAGE` y define representación, verdad, proporción, encuadre, responsive e integración. Elimina assets que repiten el mismo trabajo visual.
6. Emite briefs `IH-*` para el loop externo sin invocar generación. Al recibir resultados, valida continuidad, verdad, safe zones y formato; una corrección vuelve al loop externo.
7. Cuando una referencia temporal aprobada sea material, consume su especificación MengTo; no copia el efecto ni su superprompt.
8. Entrega a 06 únicamente archivos devueltos o media auténtica/licenciada con instrucciones exactas. Si un `FX-*` requiere GSAP, define el comportamiento sin imponerlo: 06 decide el runtime.

## OUTPUTS OBLIGATORIOS

`production-plan.md`, handoff externo `IH-*`, archivos devueltos validados y prototipos materiales.

## GATE / CRITERIO

El checkpoint cierra cuando la narrativa visual cubre toda la página, la cantidad de assets está razonada, cada mecanismo tiene necesidad y fallback, cada escena tiene decisión, y los `IH-*` necesarios han vuelto con archivos válidos. No cierra con briefs pendientes ni con efectos elegidos por apariencia premium.

## ESCALADO

Layout/dirección a 04/03, contenido a 02, runtime a 06 y riesgo a 00.

## REGLAS ESPECÍFICAS

Una solución estática puede ganar; debe hacerlo por calidad, no por evitar producción.
