# Rejected / Suspicious Patterns

No son prohibiciones universales. Son patrones que requieren justificación fuerte porque suelen generar soluciones genéricas o frágiles.

## Hero formalmente completo pero plano

**Fallo observado:** hay titular grande, paleta contenida, asset, CTA y un `FX-*` nominal, pero el resultado sigue siendo intercambiable. Suele aparecer como cluster: neutro cálido, grotesca pesada, etiquetas mono, contornos finos, acento brillante y sombra desplazada; el gráfico ocupa la segunda columna sin relación causal con el mensaje.

**Por qué falla:** cada ingrediente se validó por separado; presencia se confundió con integración y familiaridad estética con dirección.

**Rechazar cuando:** sustituir color, asset o efecto no cambia la lógica del hero; la tipografía solo escala; el mecanismo es imperceptible, genérico o solo existe en el plan.

**Corrección:** ejecutar el stress test sobre el render, comparar la paleta con una alternativa plausible, integrar media y copy y exigir prueba física del mecanismo. No se corrige añadiendo automáticamente gradientes, 3D, más fuentes o más motion.

- glassmorphism por defecto;
- “AI blobs” y gradientes sin significado;
- tilt 3D aplicado a toda tarjeta/foto;
- parallax exagerado;
- cursor custom sin función;
- `scale(1.05)` como hover universal;
- motion permanente;
- WebGL/3D sin función;
- librerías pesadas para microefectos simples;
- todas las secciones con la misma card/grid y solo cambia el texto.
