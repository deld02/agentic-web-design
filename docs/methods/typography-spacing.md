# Composición tipográfica y ritmo

Este método evita que una landing tenga espacio vacío pero no respire. No prescribe una estética ni una escala fija: obliga a componer el espacio y la tipografía con el contenido real.

Antes del ajuste fino, las foundations tipográficas se comparan junto al sistema cromático/gráfico sobre el mismo contenido y escena mediante `docs/methods/material-decisions.md`. Este método pressure-tests la ganadora; no convierte el primer specimen correcto en selección.

## 1. Ritmo antes que padding

Cada escena define cuatro relaciones: `section`, `group`, `component` e `inline`. Debe cumplirse visualmente:

`section > group > component > inline`

No basta con aumentar márgenes. El espacio debe separar ideas, revelar jerarquía y permitir lectura. Es un fallo si existe una gran zona muerta mientras título, párrafo y CTA compiten dentro de un bloque comprimido.

Para cada escena se comprueban, como mínimo:

- entrada y salida de sección, incluida la relación con header y footer;
- título → apoyo → acción;
- separación entre filas o componentes repetidos;
- medida del texto, interlineado y densidad percibida;
- ausencia de clipping, colisiones y saltos accidentales.

Los valores pueden usar escalas fluidas y `clamp()`, pero sus mínimos y máximos se deciden por composición, no por costumbre.

## 2. Roles tipográficos, no métricas heredadas

Cada rol registra familia, peso, rango de tamaño, interlineado, tracking, medida, fallback y comportamiento responsive. Cambiar de familia exige recalibrar esas métricas: una tipografía alternativa nunca hereda automáticamente el tamaño o interlineado del body.

Como punto de comprobación, no como preset:

- el texto de lectura suele funcionar entre `45–75ch`; un apoyo breve puede ser más estrecho si no genera una columna entrecortada;
- el body necesita un interlineado coherente con su x-height y medida, normalmente en el entorno de `1.45–1.7`;
- una display puede ser más cerrada, pero nunca cortar ascendentes, descendentes, acentos o cursivas.

Las tipografías display se reservan para fragmentos que soporten su forma. Un párrafo en otra familia solo se aprueba tras revisar de nuevo medida, tamaño, peso, tracking e interlineado.

## 3. Titulares con varias tipografías

Un titular multifuente es una sola composición con roles distintos, no spans que comparten el mismo `font-size`.

1. Define qué fragmento lleva la tesis y cuál aporta contraste.
2. Ajusta cada fragmento por altura visual, peso, baseline, inclinación y overhang; igualdad numérica no implica igualdad óptica.
3. Da a cada rol su propia escala fluida, line-height y tracking cuando lo necesite.
4. Define saltos semánticos preferidos y una composición alternativa para anchos donde el gesto deja de funcionar.
5. Mantén el acento lo bastante breve para conservar intención. Si ocupa varias líneas, se rediseña su composición.
6. Evita viudas, palabras sueltas y finales residuales. `text-wrap: balance` puede mejorar el resultado, pero no sustituye los saltos diseñados ni su fallback.
7. Comprueba carga y fallback de fuentes para que el cambio métrico no recorte ni desmonte el titular.

Se permiten correcciones ópticas locales documentadas. Se rechazan cadenas frágiles de márgenes negativos o posiciones absolutas que solo funcionan en una captura.

## 4. Pressure test mínimo

Probar con contenido real en `320, 360, 390, 430, 768, 1024, 1280 y 1440 px`, más el ancho exacto donde cambie la composición. Repetir con texto al `80 %, 100 % y 130 %` de longitud y con las fuentes aún sin cargar.

En cada caso registrar `PASS | ADAPT | FAIL` para:

- respiración y jerarquía espacial;
- medida y ritmo de párrafos;
- saltos del titular multifuente;
- clipping, solapamiento y proximidad al viewport;
- relación entre contenido principal, CTA y elementos decorativos.

`FAIL` bloquea G3. `ADAPT` requiere una regla responsive explícita en `visual-system.md`.

## 5. Resolución del hero

El hero no se aprueba porque tenga título grande, dos columnas y espacio libre. Debe construir una primera impresión deliberada mediante relaciones entre copy, tipografía, media, color y mecanismo.

- La jerarquía tipográfica debe expresar la tesis, no solo ordenar tamaños. Puede usar una o varias familias, pero necesita contraste perceptible de voz mediante forma, ancho, peso, estilo, escala, ritmo o composición.
- Una sola familia es válida cuando su articulación aporta carácter. Añadir una serif, cursiva o mono como adorno tampoco demuestra dirección.
- El asset principal no puede comportarse como un rectángulo intercambiable colocado en la columna disponible: debe compartir estructura, tensión, continuidad, causa o respuesta con el mensaje.
- La profundidad puede ser espacial, material, tipográfica, cromática o interactiva; no exige 3D. Un hero plano es válido solo si la precisión de composición, imagen, contraste y detalle produce una intención equivalente.
- El primer viewport debe transmitir una cualidad concreta antes de leer toda la explicación. “Limpio”, “moderno” o “premium” no son cualidades suficientes.

G3 registra una prueba observable del hero. Una captura aislada puede demostrar composición estática; cualquier comportamiento elegido necesita además evidencia de interacción. El reviewer evalúa la imagen real, no acepta como prueba una descripción del owner.
