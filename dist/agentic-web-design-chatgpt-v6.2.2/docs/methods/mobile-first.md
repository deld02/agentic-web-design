# Método Mobile

Mobile no es una reducción matemática de desktop.

## Preguntas obligatorias
- ¿Cuál es la primera acción visible?
- ¿Qué información puede retrasarse?
- ¿Qué cambia de orden?
- ¿Qué interacción hover necesita alternativa touch?
- ¿Qué motion pierde sentido?
- ¿Qué imagen necesita otro encuadre o posición?
- ¿Qué título rompe antes de 320/360/390/430 px?
- Si el título mezcla fuentes, ¿cada rol conserva peso visual y tiene saltos o composición alternativa?
- ¿Qué ocurre con texto más largo?
- ¿El espacio sigue mostrando jerarquía entre sección, grupo, componente e inline?

## Matriz mínima sugerida
320, 360, 390, 430, 768, 1024, 1280, 1440 px + anchos intermedios críticos. Para tipografía y ritmo se aplica además `docs/methods/typography-spacing.md`.

Estos anchos son probes. Los breakpoints se crean donde una invariante de contenido o composición falla, no por clase de dispositivo. `visual-system.md` conserva el fallo/rango observado, la recomposición y el rango verificado según `docs/methods/material-decisions.md`; no se inventan candidates ni entradas centrales por breakpoint.
