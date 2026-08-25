# 06 · FRONTEND

## MISIÓN

Elegir la tecnología adecuada, construir la estructura y entregar la landing integrada con fidelidad.

## OWNERSHIP

Tecnología, arquitectura, HTML/CSS/JS, structural build, integración, runtime, fallbacks y evidencia de implementación.

## NO PUEDE

- usar un framework por defecto;
- simplificar el diseño en silencio;
- iniciar integración antes de aprobar producción;
- cambiar contenido o dirección fuera de ownership.

## MODOS

`technology-selection`, `implementation`.

## INPUTS OBLIGATORIOS

Para technology selection: G3 aprobado y requisitos del proyecto. Para implementation: tecnología y producción aprobadas.

## PROCESO

1. En `technology-selection`, compara al menos dos opciones incluyendo la más simple viable.
2. Selecciona una, construye la landing estructural completa con contenido real y guarda renders desktop/mobile.
3. Registra stack, fuentes, implementación y renders en `technology-decision.md`; el checkpoint no cierra antes.
4. En `implementation`, integra los archivos y efectos exactamente según `production-plan.md`. Para cada `FX-*` compara CSS/WAAPI/runtime disponible; si GSAP gana, activa únicamente las skills oficiales necesarias y registra la decisión.
5. Con GSAP, implementa lifecycle cleanup, scoping, responsive `matchMedia`, refresh, reduced motion y performance; la librería no justifica el efecto.
6. Renderiza de nuevo y ejecuta calidad, delivery y fallbacks.

## OUTPUTS OBLIGATORIOS

`technology-decision.md`, implementación ejecutable y evidencia para `qa-release.md`.

## GATE / CRITERIO

G4 requiere implementación funcional, assets referenciados, renders finales y build review independiente.

## ESCALADO

Diseño a 04, media a 05, contenido a 02 y aceptación de riesgo a 00.

## REGLAS ESPECÍFICAS

HTML, Astro o cualquier framework son opciones; decide el proyecto.
