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

## Criterio de selección visual

The selected thesis and identity guide design, not obedience to an artistic raster. AM/genome remains exploratory until tested on opening, explanation/proof and action/closure with real content in desktop/mobile. Approved CMPs establish build fidelity. SEMANTIC text may evolve with composition under independent meaning review; facts and explicitly fixed wording stay VERBATIM. Stillness may be the reviewed direction when motion adds no useful gain; neither an image nor an effect quota proves quality.

La conformidad técnica y documental es necesaria, pero no constituye aprobación estética. En direction-review y design-review, 07 debe poder elegir **ninguna** de las propuestas: ser la mejor de tres soluciones débiles no convierte a una en buena.

Juzga sobre imágenes visibles, junto a las referencias originales inspeccionadas, no sobre la persuasión del texto del owner. En el finding existente señala la escena y la relación observable que sostiene el veredicto: composición y tensión, oficio tipográfico, autoridad de la media, ritmo/continuidad y adecuación al público. No exige copiar una referencia ni superarla en todos los ejes, pero sí demostrar el nivel elegido en los rasgos relevantes para este proyecto. Si falta evidencia de comparación, pide evidencia; si la evidencia muestra una solución débil, devuelve REVISE al owner.

Una foto oscura con titular enorme, un color acento, bloques alternos o un selector básico no prueban autoría por sí solos. Pregunta si al sustituir nombre y texto el resultado seguiría funcionando igual para otros proyectos. Cuando esa intercambiabilidad domina las escenas principales, clasifica el fallo correspondiente y no apruebes por orden, honestidad, contraste o archivos completos.

La simplicidad gana solo si conserva la ganancia perceptiva definida y la demuestra en el render. No es obligatorio añadir 3D, animaciones, imágenes adicionales ni varias fuentes: tampoco se permite rebajar la intención a la opción más fácil de programar. Los descansos y escenas utilitarias pueden ser sencillos; el conjunto debe conservar una presencia específica y un recorrido diseñado. Si el prototipo no demuestra un efecto todavía, juzga únicamente lo observado, no su promesa.

Estas decisiones son juicio visual independiente, no una puntuación automática de belleza. Los scripts verifican evidencia y procedencia; nunca certifican por sí solos que la landing sea premium.

## Evidence status

Cada área termina en `COMPLETE | NOT_APPLICABLE | ACCEPTED_RISK`. Las dos últimas requieren razón y owner. `PENDING | MISSING | UNTESTED | UNKNOWN` bloquean release.

La evidencia registra `method | target | result | evidence | owner | status | limitations`. El validador comprueba estructura y estados; el review humano/visual decide si la calidad es suficiente.

Para G3, la evidencia de composición sigue `docs/methods/typography-spacing.md`. No se considera evidencia una captura de un único viewport.

La evidencia cromática sigue `docs/methods/scene-color-system.md` e incluye al menos la relación hero → escena siguiente y los estados materiales de cada modo utilizado.

## Explicit boundary

El OS no ofrece estrategia SEO, analytics, compliance, seguridad de aplicaciones, ecommerce, CMS, localización ni operación post-lanzamiento. Si una landing necesita servicios externos, se registran como dependencia/constraint y se entregan al especialista correspondiente; no se incorporan al sistema.
