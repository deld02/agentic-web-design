# Landing quality baseline

Este baseline cubre exclusivamente la creación de una landing. Se aplica con profundidad proporcional, sin convertir cada área en un proceso separado.

## Acceptance areas

1. **Objective and action** — la propuesta se entiende y la acción principal es clara.
2. **Content and assets** — el contenido usado es honesto; cada imagen tiene ID y decisión propia sobre representación, función, estilo, producción, derechos, responsive y fallback según `docs/methods/image-decisions.md`. La entrega comprueba archivo físico e integración; un prompt, placeholder o screenshot no es media final.
3. **Visual direction and scenes** — antes del master se define qué significa excelencia premium en este proyecto y qué baseline actual debe superar. El master debe demostrar ese umbral y la landing conservarlo. Cada sección contrasta su baseline con una oportunidad de producción de alto valor, separa ganancia real, equivalente simple y ruido caro, y adopta la forma mínima que preserve el valor. Las foundations se extraen de esas decisiones. El hero supera pruebas de integración, eliminación e intercambiabilidad; el cuerpo conserva el lenguaje sin repetir una receta. Todo elemento no textual que ocupe un área focal se juzga como media aunque sea CSS/SVG: debe superar en el render tanto su eliminación como una alternativa producida. Gradientes azul/morado, sans geométrica, hero centrado, pill CTA, tres icon cards, sombras difusas, blobs, grain, glows, círculos orbitales, diagramas falsos o iconos lineales son sospechosos cuando aparecen por defecto, pero nunca prohibiciones independientes del contexto.
4. **Responsive composition** — desktop y mobile conservan jerarquía, ritmo e intención; párrafos y titulares multifuente mantienen medida, saltos y respiración sin clipping ni colisiones.
5. **Rhythm, interaction and motion** — la secuencia completa alterna intensidad, descanso, densidad y escala con intención. Estados, touch, teclado y reduced motion funcionan; cada efecto material compara `NONE | SIMPLE | EXPRESSIVE`, tiene propósito y fallback, pertenece a una gramática común y existe realmente en la implementación. Un tratamiento genérico o imperceptible no se eleva artificialmente a mecanismo definitorio.
6. **Build fidelity** — la implementación reproduce el diseño aprobado sin desviaciones ocultas.
7. **Functional delivery** — navegación, CTA, enlaces y formularios incluidos en el alcance funcionan.
8. **Accessibility and performance** — se comprueban proporcionalmente semántica, contraste, foco, media, carga y estabilidad visual.

## Evidence status

Cada área termina en `COMPLETE | NOT_APPLICABLE | ACCEPTED_RISK`. Las dos últimas requieren razón y owner. `PENDING | MISSING | UNTESTED | UNKNOWN` bloquean release.

La evidencia registra `method | target | result | evidence | owner | status | limitations`. El validador comprueba estructura y estados; el review humano/visual decide si la calidad es suficiente.

Para G3, la evidencia de composición sigue `docs/methods/typography-spacing.md`. No se considera evidencia una captura de un único viewport.

La evidencia cromática sigue `docs/methods/scene-color-system.md` e incluye al menos la relación hero → escena siguiente y los estados materiales de cada modo utilizado.

## Explicit boundary

El OS no ofrece estrategia SEO, analytics, compliance, seguridad de aplicaciones, ecommerce, CMS, localización ni operación post-lanzamiento. Si una landing necesita servicios externos, se registran como dependencia/constraint y se entregan al especialista correspondiente; no se incorporan al sistema.
