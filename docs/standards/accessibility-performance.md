# Accessibility & Performance Reference

**Checked:** 2026-08-20

Este archivo evita convertir thresholds externos en conocimiento eterno. 06/07 revisan estas referencias cuando un proyecto requiere precisión actual; el System Steward revisa su vigencia a nivel OS.

## Accessibility target base

- W3C WCAG 2.2 Recommendation: https://www.w3.org/TR/WCAG22/
- Quick Reference: https://www.w3.org/WAI/WCAG22/quickref/

Default del OS: **WCAG 2.2 AA** salvo requisito de proyecto más estricto o cambio del estándar registrado.

No confundir “pasar axe/Lighthouse” con conformidad completa: muchos criterios requieren evaluación humana.

## Core Web Vitals actuales en la fecha de revisión

Fuente: https://web.dev/articles/vitals

- LCP: <= 2.5 s
- INP: <= 200 ms
- CLS: <= 0.1
- Evaluación recomendada: percentil 75, segmentado mobile/desktop.

No inventar datos de campo. Si no existen RUM/CrUX adecuados, distinguir lab estimate de field data.

## Motion

- `prefers-reduced-motion`: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion

El reduced-motion equivalent debe conservar contenido/función; no basta con acelerar la misma animación si sigue causando el problema.

## Review policy

Actualizar `Checked` y referencias cuando:

- W3C publique un target nuevo relevante;
- cambien Core Web Vitals estables;
- el proyecto tenga obligación contractual/legal específica;
- una recomendación del repo se base materialmente en compatibilidad cambiante.
