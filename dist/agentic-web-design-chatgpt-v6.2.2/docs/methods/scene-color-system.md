# Sistema cromático por escenas

Este método aplica por escenas la dirección elegida previamente mediante `docs/methods/color-direction.md`. No inventa ni selecciona la paleta.

Una paleta define la identidad cromática de la landing; no obliga a usar el mismo fondo, contraste o intensidad en todas las secciones. El color se diseña en tres capas: primitives de marca, modos semánticos y asignación por escena.

Antes de definir primitives o modos finales, la foundation cromática se compara junto a tipografía y lenguaje gráfico sobre la misma escena mediante `docs/methods/material-decisions.md`. Los tokens representan la opción elegida; no la eligen.

## 1. Primitives y roles

Las primitives registran los colores disponibles y su procedencia. Los componentes no consumen primitives directamente: usan roles semánticos por modo, como mínimo cuando sean materiales:

`background | foreground | muted | accent | surface | border | link | focus | positive | negative`

Esto permite que un mismo componente funcione sobre un hero expresivo y sobre una sección de lectura sin duplicar su identidad ni fijar `white` o `black` dentro del componente.

## 2. Modos por función

Cada escena elige intensidad y contraste por el trabajo que realiza. Los nombres siguientes son funcionales, no presets obligatorios:

- `SIGNATURE` — máxima expresión de la tesis; habitual en hero o escena memorable.
- `READING` — baja interferencia y alta comodidad para explicación, servicios o contenido denso.
- `CONTRAST` — cambio de ritmo, prueba, CTA o momento que necesita separación clara.
- `UTILITY` — formularios, FAQ, navegación o contenido donde previsibilidad y estados dominan.

Una landing puede usar uno, dos o más modos. No se añade un modo si no mejora jerarquía, lectura o narrativa. `READING` puede ser blanco, claro, oscuro o tintado: lo decide la tipografía, el contenido y el contexto, no una convención.

## 3. Mapa de escenas

Para cada sección registrar:

- trabajo narrativo y densidad;
- modo elegido y razón;
- asignaciones concretas de `background`, `foreground`, `accent` y `surface`; no basta con nombrar el modo;
- media y componentes que cruzan el cambio;
- transición desde/hacia la escena vecina;
- contraste, foco y estados interactivos dentro del modo.

El hero puede usar un mecanismo espectacular y las siguientes escenas adoptar un fondo claro y calmado. La continuidad se conserva mediante al menos dos invariantes deliberados —por ejemplo tipografía, accent, geometría, grid, tratamiento de imagen o ritmo—, no repitiendo obligatoriamente el fondo del hero.

El mapa usa los mismos `SCN-*` de la arquitectura. Todas las escenas tienen fila: una escena `UTILITY` puede heredar un modo de otra, pero debe declarar la herencia, las asignaciones resultantes y sus transiciones. Así la elección de paleta global nunca sustituye la decisión cromática de cada sección.

## 4. Transiciones

Cada cambio de modo elige una transición consciente:

- `CUT` — corte claro entre capítulos;
- `BRIDGE` — elemento, color o media atraviesa ambas escenas;
- `OVERLAP` — una superficie introduce el siguiente modo;
- `BLEND` — transición gradual justificada;
- `STATE_CHANGE` — el fondo o chrome cambia durante scroll con fallback estable.

No alternar fondos para decorar ni usar un degradado para ocultar una relación mal resuelta. Un cambio fuerte debe coincidir con un cambio narrativo o perceptivo; un cambio suave debe preservar separación suficiente.

## 5. Pressure test

Antes de G3 comprobar:

- hero aislado y hero → primera escena de lectura;
- una sección densa, CTA, formulario/FAQ y footer cuando existan;
- texto, enlaces, controles, borders, focus y media en cada modo;
- desktop, mobile y estados de transición;
- experiencia sin efectos o scroll-driven color changes;
- consistencia de identidad al capturar cualquier escena fuera del contexto del hero.

Falla si el hero funciona como pieza aislada pero el resto parece una plantilla genérica; si la paleta obliga a una lectura incómoda; si los componentes llevan colores hardcoded que rompen al cambiar de modo; o si la alternancia cromática no tiene lógica narrativa.

### Prueba de intercambiabilidad cromática

La procedencia o armonía de una paleta no demuestra que tenga dirección. En la escena `SIGNATURE`, 04 compara la opción elegida con una neutralización rápida o una paleta plausible de la categoría. Si el cambio no altera percepción, jerarquía ni significado, el color es utility y no puede presentarse como rasgo distintivo; la identidad debe recaer de forma consciente en otros elementos.

No se prohíben beige, blanco, negro, naranja, gradientes ni ninguna combinación. Se rechaza el **cluster genérico**: varios códigos muy frecuentes —por ejemplo fondo cálido neutro, sans grotesca pesada, mono técnico, acento brillante, contorno fino y sombra desplazada— usados juntos sin una relación demostrable con el sujeto. La combinación puede aprobarse si research y la materialización muestran por qué pertenece al proyecto y qué decisión evita que sea intercambiable.
