# Revisión de arquitectura, QA y dirección de arte

Revisión del código local a partir de `7ddbe50`. Arquitectura y dirección de arte
se revisaron en contextos separados, sin editar; QA, reproducciones e implementación
se realizaron en el contexto coordinador. Estos revisores no son agentes añadidos
al pipeline de creación de landings.

## Resultado

### Seguimiento de implementación — 2026-09-12

Los hallazgos de la tabla siguiente describen la auditoría inicial. Desde entonces:

- Headless aplica las transiciones mediante el harness y rechaza/restaura cambios
  del ejecutor en `status.json`; la fixture ya no aprueba su propio estado.
- El MCP dispone de generación/importación/lectura de raster, render estático
  desktop/móvil y por escenas, revisión visual en una petición API nueva y
  empaquetado/descarga con comprobación de integridad.
- SQLite serializa servidores cooperantes. El journal restaura metadatos tras una
  interrupción del proceso al reabrir el run. No protege frente al administrador
  local ni promete recuperación de un fallo eléctrico.
- La revisión guarda hashes, rechaza evidencia obsoleta, reutiliza resultados sin
  cambios y limita intentos. Un resultado REVISE devuelve el paquete del owner
  anterior para corregir, sin abrir una etapa nueva.
- Se ha probado un navegador Edge real con una fixture estática, desktop/móvil,
  scroll por escenas, click y movimiento reducido. Las respuestas del proveedor
  se han simulado en los tests: no son una revisión artística real.

Pendiente para aceptación: configurar proveedor/modelos en el servidor, conectar
ChatGPT y completar un piloto real con generación, revisión y descarga. No se
han configurado credenciales ni publicado servicios durante esta intervención.
El validador auxiliar `skill-creator/quick_validate.py` no pudo arrancar por faltar
PyYAML en los intérpretes disponibles; los validadores propios del repositorio sí
han comprobado la estructura de la skill y del sistema.

### Auditoría inicial

El sistema todavía no está demostrado como una ruta completa de producción desde
ChatGPT. La corrección de bugs y los tests automáticos no certifican calidad estética.

| Prioridad | Hallazgo | Evidencia y actuación |
|---|---|---|
| P1 | Investigación vacía aprobada | Reproducido por MCP: después de una definición válida, `advance_stage` devolvía `content-architecture` sin editar la plantilla de research. Corregido: se ejecutan al salir de research las mismas comprobaciones de investigación que usa G1. |
| P1 | Recuperación parcial de una transición | El journal y `run.json` podían avanzar aunque `status.json` se restaurase. Corregido para excepciones en el proceso: recuperación conjunta de metadatos, incluida activación y construcción del siguiente paquete. Pruebas inyectan fallos en snapshot, activación y paquete. No es una transacción durable ante corte eléctrico ni una barrera contra otros procesos locales. |
| P1 | Headless contradice ownership | `run_active` valida estados APPROVED después del especialista, pero no aplica las transiciones de 00. La fixture feliz escribe el estado desde el ejecutor. Pendiente: unificar la transición de owner y separar el resultado del reviewer, sin autorizar al especialista a escribir estado. |
| P1 | MCP incompleto | La revisión aislada sigue bloqueada explícitamente; faltan build/render/entrega gestionados. No se ha ocultado el bloqueo ni fabricado una revisión. |
| P2 | Divergencia comprobada tarde | La integridad de los tres territorios se comprobaba en G2, después de su selección. Corregido: comprobar territorios al salir de divergence, sin exigir todavía una selección que pertenece al reviewer. G2 conserva la comprobación completa. |
| P2 | IDs de run colisionan | Dos arranques dentro del mismo segundo podían dar `FileExistsError`. Reproducido por las pruebas nuevas; IDs automáticos ahora incluyen un sufijo aleatorio. Los IDs explícitos conservan rechazo de duplicados. |
| P2 | Heurísticas presentadas como aprendizaje verificado | El catálogo no enlaza casos físicos para varias afirmaciones HIGH. Corregido el alcance de esas afirmaciones; no se inventaron referencias. |
| P2 | Presupuesto documental contradictorio | El método negaba una duración total fija mientras el harness configura 75 minutos. Aclarado: el presupuesto limita un intento, no define calidad ni garantiza acabar. No se amplió el tiempo automáticamente. |

## Criterio de dirección de arte

Se conservan los requisitos solicitados de imágenes sustanciales, movimiento y
ausencia de sustitutos amateurs. No se relajan para hacer pasar el validador.
Sin embargo, su presencia es una condición de entrega, no una medida de excelencia.
Un archivo raster, un efecto implementado o tres boards diferentes no demuestran
que el conjunto tenga buena composición, jerarquía o personalidad.

No se encontró una ejecución local terminada con evidencia visual suficiente para
comparar resultados. El diagnóstico disponible era incompleto; no se ha juzgado
una landing que no se haya visto. Tampoco se generó una landing manual para
presentarla como prueba del harness.

## Próximo trabajo, por orden

1. Completar un único mecanismo de transición para chat y headless, con recuperación
   durable y rechazo de escrituras de estado del especialista.
2. Conectar revisión realmente aislada y operaciones de build/render/entrega con
   permisos acotados. Comprobar capacidades antes de consumir tiempo de diseño.
3. Ejecutar una landing real desde el cliente objetivo: aprobación del master,
   imágenes integradas, escritorio/móvil e interacciones comprobadas. Comparar
   master, implementación y referencias con un reviewer que no haya construido la web.

No añadir más roles, gates o cuotas mientras esta prueba de extremo a extremo
no pueda completarse. Los dos primeros puntos son trabajo de runtime; el tercero
es la prueba necesaria de utilidad y calidad, no otro documento obligatorio por landing.

## Verificación de esta revisión

- Batería general: 189 tests, OK (144,5 segundos).
- Dos tests de frontera divergence/reviewer añadidos después: OK.
- `validate_system.py`, `audit_agents.py` y `git diff --check`: OK.
- Las pruebas de fallos tardíos simulan excepciones dentro del proceso; no cortes
  eléctricos. El test de frontera de selección simula la comprobación física para
  aislar ownership; no demuestra la calidad de tres diseños.
- No se hizo una ejecución real completa desde ChatGPT, ni generación pagada,
  ni certificación visual, ni publicación de una landing.
