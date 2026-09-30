# Progressive intake

El inicio es una conversación breve para conseguir dirección, no un cuestionario que el usuario deba completar antes de recibir valor.

## Primera intervención

Usar una sola invitación abierta:

> Cuéntame qué quieres crear, para quién y qué debería conseguir. Si ya tienes una web, marca, textos, fotos o referencias, compártelos; si no, no pasa nada.

No preguntar por Astro, HTML, Next, CMS ni otra tecnología en este momento. La tecnología se deriva más tarde de la experiencia, las funciones, la edición y el mantenimiento necesarios.

## Extracción antes de preguntar

00 extrae de la respuesta todo lo que ya pueda clasificar como `FACT | ASSUMPTION | PREFERENCE | UNKNOWN`. No vuelve a preguntar información disponible en la conversación, archivos o enlaces entregados.

Después decide entre tres acciones:

- `ADVANCE`: hay dirección suficiente para redactar el brief y avanzar;
- `ASK`: falta una decisión que cambia materialmente objetivo, audiencia, acción, alcance o restricciones;
- `DISCOVER`: faltan referencias visuales o el usuario delega la exploración al sistema.

## Regla de repregunta

Hacer como máximo dos preguntas en una ronda. Cada pregunta debe poder cambiar una decisión material. Prioridad:

1. qué resultado debe producir el proyecto y cuál es la acción principal;
2. para quién se diseña;
3. alcance o función que cambia el tipo de proyecto;
4. hechos, derechos, plazo o restricciones que impiden avanzar con seguridad.

Marca, copy, fotos, ejemplos, integraciones, mantenimiento y presupuesto se preguntan solo cuando sean materiales. Se aceptan respuestas parciales. Un `UNKNOWN` no bloquea G0 si puede convertirse en una hipótesis reversible y explícita.

## Material aportado

Adjuntar material es opcional y nunca se presenta como una lista de deberes. Si existe, se registra según su estado:

- identidad: `AVAILABLE | PARTIAL | MISSING`;
- contenido: `FINAL | PROVISIONAL | MISSING`;
- media: `AVAILABLE | INSUFFICIENT | MISSING | RIGHTS_UNKNOWN | NEEDS_PRODUCTION`;
- referencias: `PROVIDED | DISCOVER | HYBRID | NOT_MATERIAL`.

Solo se solicita un archivo concreto cuando utilizarlo o no utilizarlo cambia la dirección. No se falsifican logos, testimonios, métricas, claims ni fotografías documentales. La media artística ausente se marca `NEEDS_PRODUCTION`: puede producirse o generarse conforme a `docs/methods/image-decisions.md` sin atribuirla a una persona, lugar, producto o resultado real.

## Descubrimiento de referencias

No tener ejemplos es una ruta normal. `DISCOVER` se activa si las referencias faltan, son vagas, están desactualizadas, se contradicen o el usuario pide que el sistema proponga.

01 realiza una calibración web contemporánea y fechada al inicio de cada proyecto, aunque el usuario aporte referencias. No reutiliza una definición histórica de “premium”. Busca un contraste pequeño:

- categoría directa: códigos que la audiencia ya reconoce y oportunidades de diferenciación;
- referencias adyacentes: soluciones de otros sectores con principios transferibles;
- ejecución actual de alto nivel: composición, tipografía, imagen, interacción o motion relevante.
- ejecución simple de alta calidad: el mismo objetivo resuelto con menos mecanismos.

El mínimo operativo son tres webs originales: realidad directa o adyacente, frontera contemporánea y una solución simple excelente. Las galerías sirven para descubrir; cada resultado se abre en su web original. Por cada referencia se registra fuente de descubrimiento, URL original, fecha, captura física, observación, principio transferible y anti-copia. Una inspección de más de 30 días se considera caducada y se repite. La búsqueda termina cuando los tres carriles están cubiertos y nueva exploración deja de cambiar las direcciones candidatas.

La devolución al usuario es una selección corta, normalmente de dos o tres territorios contrastados, para que pueda reaccionar con `me atrae | no me atrae | exploraría`. No se le exige conocer terminología de diseño.

La fecha de una captura no demuestra excelencia. Inspecciona la web original completa: hero, al menos una escena de cuerpo y su transición, y móvil cuando esté disponible. Si se adopta un comportamiento, obsérvalo funcionando. Una portada de galería o un screenshot antiguo puede orientar la búsqueda, pero no sustenta una decisión sobre ritmo o interacción. Si el acceso falla, sustituye la referencia o declara exactamente lo que no se pudo observar; no la presentes como inspeccionada.

Dentro de las observaciones existentes, vincula cada principio seleccionado con una decisión concreta y su escena de destino: qué relación visual aporta, qué se conserva y qué no se copia. No añadas un registro separado. Una referencia directa mediocre sirve para comprender la categoría, no para fijar el techo de calidad. La referencia SIMPLE solo cuenta como excelente cuando muestra oficio visible en composición, tipografía y media; tener pocos elementos no basta.

## Equivalencia antes de inspiración

Prioriza referencias que resuelven un problema comparable de audiencia, acción, confianza y contenido/media disponibles; no solo el mismo sector o las más premiadas. En `Fit and limitation` de la tabla existente identifica esa equivalencia y la diferencia que no se transfiere. DIRECT/ADJACENT calibran el trabajo real; FRONTIER/SIMPLE, el oficio transferible. Un portfolio excepcional puede aportar encuadre o tipografía, pero sus obras no son una exigencia para una landing sin casos. Si las referencias no sostienen ambas comparaciones, sustitúyelas dentro del presupuesto de investigación; no explores indefinidamente ni rebajes el umbral.

## Traducción de lenguaje ambiguo

Palabras como “moderno”, “premium”, “limpio” o “impactante” son señales, no una dirección. El sistema propone interpretaciones contrastadas en lenguaje perceptivo —por ejemplo sobrio/expresivo, cálido/preciso, editorial/tecnológico o calmado/energético— y valida la diferencia con referencias visibles.

## Preferencia delegada

“Haz tu propuesta”, “elige tú”, “confío en tu criterio” y equivalentes delegan la preferencia entre soluciones válidas. No aprueban un gate, no cambian objetivo o alcance y no autorizan a abandonar el stage activo.

El owner:

1. conserva brief, research, constraints, estado y artefactos vigentes;
2. selecciona la alternativa mejor sustentada —o sintetiza elementos compatibles bajo una sola tesis— usando la comparación del stage;
3. explica la elección y descartes de forma breve dentro del artefacto owner;
4. completa la evidencia exigida, la entrega al reviewer y continúa sin volver a pedir la misma preferencia;
5. deja que 00 cambie el estado únicamente después del review requerido.

La delegación no convierte una respuesta en brainstorming libre ni permite sustituir hero, navegación, escena de contenido, CTA, mobile o media representativa por una descripción en prosa. Si todas las alternativas fallan, el owner reabre exploración dentro del mismo stage. Solo pregunta de nuevo ante preferencia humana irreducible, cambio material de objetivo o riesgo factual/legal.

## Cierre de G0

El brief resume:

- lo entendido;
- la acción y audiencia principales;
- el tipo y alcance provisional;
- material disponible y estado;
- ruta de referencias;
- restricciones conocidas;
- hechos, preferencias, hipótesis y unknowns;
- qué podría cambiar materialmente el resultado.

Antes de avanzar, 00 presenta un resumen corto. Solo bloquea si falta una decisión que redefiniría el proyecto o existe un riesgo factual, legal o irreversible. El resto viaja como hipótesis trazable hacia research.
