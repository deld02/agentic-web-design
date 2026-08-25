# Resource Selection v4

01, 03, 04, 05 y 06 pueden consultar el Creative Resource Registry cuando una referencia, librería, herramienta o asset pueda cambiar una decisión material.

Orden: problem match → reuse safety → stack fit → performance/accessibility → cost/availability → freshness → novelty.

Máximo tres familias por decisión. La presencia en el registro nunca concede derechos de reutilización. Licencia, términos, provenance y vigencia se verifican al usar.

La selección tecnológica usa `config/technology-options.json`; el Creative Resource Registry no sustituye la comparación de arquitectura.

## Benchmarking de webs según el proyecto

Antes de buscar, 01 convierte el brief en un `reference search brief`:

- trabajo principal de la landing y acción esperada;
- audiencia, categoría, mercado/idioma y nivel de conocimiento;
- percepción que debe crear y códigos que debe evitar;
- contenido, prueba y media disponibles;
- ambición visual/interactiva y restricciones reales.

No pregunta estos campos de nuevo si ya pueden extraerse. Con ellos construye consultas específicas como:

`[categoría/oferta] + [audiencia/mercado] + [acción] + website/landing`

`[reto de persuasión] + [dirección perceptiva] + website`

Las galerías sirven para descubrir; la búsqueda web general encuentra marcas, competidores y casos que no aparecen en ellas.

### Calibración contemporánea

Se ejecuta de nuevo para cada proyecto. La memoria del agente y el registro de fuentes sirven para formular la búsqueda, no para declarar qué aspecto tiene una web actual. Una referencia inspeccionada hace más de 30 días debe abrirse y capturarse de nuevo.

### Set de contraste

La búsqueda reúne tres webs originales como mínimo y cubre:

1. `DIRECT` — misma categoría, audiencia u objetivo; revela expectativas y saturación.
2. `ADJACENT` — sustituye o complementa a `DIRECT` cuando otra categoría resuelve mejor el mismo problema de confianza, explicación, deseo o acción.
3. `FRONTIER` — ejecución actual de alto nivel relevante para la ambición visual o interactiva; amplía posibilidades sin convertirse en default.
4. `SIMPLE` — solución contenida y excelente que cumple el objetivo con menos mecanismos; evita confundir complejidad con calidad.

El set válido contiene `DIRECT` o `ADJACENT`, además de `FRONTIER` y `SIMPLE`. Se detiene al cubrirlos con evidencia útil; no crea un moodboard infinito.

### Qué se inspecciona

Cada candidate se abre en su web original y se observa, proporcionalmente, en desktop y mobile:

- tesis del hero y tiempo hasta comprender la propuesta;
- orden narrativo, densidad y transiciones entre escenas;
- relación entre tipografía, imagen, color y espacio;
- CTA, prueba y tratamiento de objeciones;
- interacción/motion y qué ocurre sin ellos;
- consistencia responsive, coste aparente y viabilidad para este proyecto.

No se asigna una nota universal. Se compara `OBJECTIVE_FIT | AUDIENCE_FIT | CLARITY | DISTINCTIVENESS | TRANSFERABILITY | FEASIBILITY` y se decide `ADOPT_PRINCIPLE | ADAPT | REJECT`. Una referencia principal puede existir solo con alcance declarado —por ejemplo `structure`, `imagery` o `motion`—, nunca como plantilla completa.

El resultado es un conjunto corto de principios y dos o tres territorios contrastados, incluyendo la alternativa simple viable. El usuario reacciona a territorios, no a una pared de enlaces.

### Dónde busca

Fuentes de primera consulta según la incertidumbre:

- búsqueda web general y webs oficiales: categoría, competidores y realidad actual;
- `siteinspire` y `one-page-love`: landings reales, estructura, composición y categorías;
- `awwwards`: dirección expresiva y mecanismos de alto impacto, nunca como prueba automática de usabilidad;
- `pinterest`: descubrimiento visual secundario cuando faltan palabras para estilo, atmósfera, materialidad o composición; todo pin material debe rastrearse hasta su fuente original;
- `are-na` e `its-nice-that`: investigación visual adyacente, fotografía, ilustración y art direction;
- `codrops-creative-hub` / `codrops-demos`: comportamiento de imagen y mecanismo técnico concreto.

### Ruta para efectos, interacción y 3D

Para un `FX-*`, no se hace una búsqueda abierta de “efectos modernos”. Se elige una fuente por carril relevante:

| Carril | Pregunta | Fuentes iniciales |
|---|---|---|
| `LIVE_EXECUTION` | ¿Cómo funciona dentro de una web completa? | competidores/web oficial, SiteInspire, One Page Love, Awwwards, Godly |
| `MECHANISM_LAB` | ¿Cómo se comporta y cuánto cuesta? | Codrops Creative Hub/Demos, Motion, GSAP, Three.js Examples |
| `ELEMENT_BANK` | ¿Qué variantes existen para este tipo de elemento? | Aceternity UI, Magic UI, Motion Primitives, React Bits |
| `3D_MATERIAL` | ¿Qué lenguaje espacial/material es viable? | Spline/Community, Three.js Examples, Poly Haven, ambientCG, Sketchfab |

La consulta se formula como `[elemento/escena] + [trabajo perceptivo] + [trigger] + [dirección material]`, por ejemplo `product image + reveal construction + scroll + layered paper`. Se abre la web o demo original. Cada ancla registra carril, URL, mecanismo transferible, lo que no debe copiarse, stack/licencia y limitación mobile/performance.

Cada referencia registra URL original, autor/estudio cuando exista, fecha, rol en el set, observación, principio transferible, anti-copia, limitaciones y una captura física guardada como evidencia del estado realmente inspeccionado. Un proyecto puede usar hasta tres familias de fuente por decisión; popularidad o premio no equivalen a fit.

Pinterest nunca ocupa por sí solo el rol `DIRECT`, no demuestra que una web funcione y no se usa como fuente de un asset. Si el pin no permite localizar la publicación, proyecto o autor original, se descarta de la evidencia aunque pueda orientar términos de búsqueda posteriores.

## Referencias para una imagen concreta

Después del benchmark general, una imagen puede necesitar una búsqueda más precisa:

`categoría/sujeto + acción/contexto + lenguaje visual + composición/efecto`

Se etiqueta `SUBJECT_TRUTH | ART_DIRECTION | COMPOSITION | EFFECT | MATERIAL_LIGHT` según `docs/methods/image-decisions.md`. Esta búsqueda amplía el benchmark solo para resolver el ID; no reabre toda la dirección.
