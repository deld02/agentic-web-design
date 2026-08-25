# Dirección cromática

Este método ocurre en G3 antes de `scene-color-system.md`. No tokeniza una paleta ni intenta calcular si es bella: obliga a diseñar color sobre una interfaz real, comparar alternativas y someter la ganadora a revisión visual independiente.

No añade fase ni artefacto. Las evidencias `CLR-*` y la decisión viven en `visual-system.md`.

## 1. Misma composición, tres territorios

04 aplica sobre el mismo hero, copy, media, layout y viewport tres territorios físicos:

- `BASELINE` — solución directa, sobria y profesional;
- `BRAND_LED` — desarrolla identidad, materiales o señales existentes sin heredarlos automáticamente;
- `CHALLENGER` — busca una percepción más distintiva sin sacrificar acción, lectura ni autenticidad.

Cada territorio se guarda como render `CLR-*`. No se comparan listas HEX, moodboards ni composiciones diferentes: cambiar cualquier variable ajena al color invalida la comparación.

## 2. Jerarquía y presencia

Cada territorio define y estima la presencia visible de `dominant`, `background`, `foreground`, `support` y `accent`. Los porcentajes son estimaciones compositivas, no métricas de píxel. Sirven para comprobar jerarquía: un accent no compite con dominant sin una razón perceptiva o funcional explícita.

## 3. Procedencia no es calidad

`COLOR_PROVENANCE` pregunta de dónde procede la dirección y por qué pertenece al proyecto. Asociaciones como “verde = sostenibilidad” solo son hypotheses de procedencia; nunca demuestran craft ni calidad.

`COLOR_COMPOSITION` juzga sobre el render: `LUMINANCE`, `CHROMA`, `TEMPERATURE`, relación `DOMINANT_ACCENT`, calidad de `NEUTRALS`, compatibilidad con `MEDIA`, comportamiento en `LARGE_SURFACES`, efecto `PERCEPTION` y accesibilidad de texto, estados y foco.

Después de elegir, `scene-color-system.md` aplica la dirección por escenas y roles semánticos.

## 4. Challenge independiente

07 recibe el hero elegido y crea una única lámina física `CLR-*` que muestra sobre esa misma composición: accent eliminado, neutralización y paleta plausible/típica de la categoría. Registra qué pierde o mejora cada counterfactual. Si la elegida no mejora claramente percepción y dirección, devuelve `REVISE` a 04. Un `PASS` escrito sin lámina física no cuenta.

## 5. Límites

- Los validadores comprueban archivos, estructura, jerarquía declarada, contraste registrado y revisión; no deciden belleza.
- No existe color obligatorio ni paleta prohibida.
- Existing identity informs the brand-led option, but research may change or reject it when it conflicts with the current objective.
- Los tres territorios son variantes del mismo hero, no tres nuevas direcciones creativas.
