# Medios de validación — Figma, navegador y alternativas

## Regla

No existe una herramienta universal para validar cualquier dirección. El OS elige el **medio mínimo capaz de demostrar la hipótesis**.

## Canvas / keyframes estáticos

Figma, SVG, imágenes, slides u otros canvases sirven bien para:

- explorar composición;
- tipografía/jerarquía;
- sistema visual;
- variantes;
- comparar direcciones;
- documentar handoff.

Figma es una opción, no una dependencia.

## Navegador / prototipo interactivo

El navegador u otro runtime representativo sirve para:

- responsive continuo;
- motion;
- scroll;
- input/touch;
- estados intermedios;
- canvas/WebGL/3D;
- performance;
- accesibilidad;
- comportamiento real de tipografía/assets.

Si la dirección depende de estos comportamientos, una captura estática no es evidencia suficiente.

## Storyboard / vídeo

Puede ser suficiente para validar narrativa, choreography o media temporal antes de invertir en runtime, siempre que no se use como prueba de interacción real.

## Media samples

Cuando fotografía, vídeo, 3D o generación visual define el concepto, debe probarse con muestras suficientemente representativas. Un rectángulo gris no demuestra una dirección image-led.

## Principio final

**Evidence-first, no Figma-first ni browser-first.**

Toda decisión compleja termina validándose en el medio correspondiente a su riesgo antes de release. El navegador real sigue siendo la referencia final de una web implementada.
