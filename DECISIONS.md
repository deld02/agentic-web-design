# DECISION LOG — System

No borrar decisiones revertidas.

## D-085 — La ejecución completa necesita un recibo externo verificable

**Fecha:** 2026-08-30
**Contexto:** conversaciones externas leían la metodología, construían manualmente y solo al ser interrogadas admitían que el harness nunca había gobernado el trabajo. La documentación fail-closed no permitía al usuario distinguirlo al recibir la landing.
**Decisión:** el arranque canónico de ChatGPT es `chat-start`; antes del diseño se exponen sus valores gestionados. Tras `release`, el harness crea un recibo ligado a secuencia, gates, reviews, master, informe, contrato y build. Sin verificación, la respuesta debe declararse `UNMANAGED`.
**Enforcement:** ambos adaptadores gestionados producen `execution-receipt.json`; `tools/verify_execution.py` recalcula todos los digests y bloquea secuencias incompletas, recibos alterados y builds posteriores. No añade agentes, gates, stages ni checkpoints.
**Estado:** ACTIVE desde v6.6.0.

## D-084 — El medio espacial se decide antes del runtime

**Fecha:** 2026-08-28
**Contexto:** el sistema distinguía 2D y 3D real, pero podía terminar escogiendo la modalidad después de tecnología y no disponía de un contrato entre dirección, estados espaciales e inspección runtime.
**Decisión:** 04 compara modalidades y congela el medio en G3; 06 prueba y elige runtime solo si gana `INTERACTIVE_3D`; 05 define estados semánticos `SPT-*` y producción; 07 verifica cada estado. `spatial-experience.md` es la única autoridad condicional y la procedencia 3D existente sigue siendo la única fuente de assets, derechos e integración.
**Enforcement:** el harness enruta el método en ambos modos, valida G3/G4 tras sus reviews y bloquea comparación, spike, storyboard, fallbacks o traversal incompletos. No se añaden agentes, gates, stages ni artefactos.
**Estado:** ACTIVE desde v6.5.0.

## D-083 — `automatic` significa activación comprobada por stage

**Fecha:** 2026-08-27
**Contexto:** el registro declaraba capacidades core automáticas, pero el harness no cargaba el router ni los gates comprobaban su uso. Un ejecutor podía omitir Anthropic, Taste, Hallmark, Jakub o Vercel y aun cerrar el pipeline.
**Decisión:** el harness inyecta router, referencias core y candidatas condicionales en cada stage. El artifact registra capability ID y Mode igual al stage. Las core automáticas son obligatorias; las condicionales conservan su trigger.
**Enforcement:** `validation_capability_activation.py` bloquea cada stage y gate si falta una activación automática, exige Emil ante motion material e Impeccable ante un finding tipado. El fallback local registrado permite continuar cuando una fuente externa no está disponible.
**Estado:** ACTIVE desde v6.4.3.

## D-082 — La respiración tipográfica se revisa sobre el producto final

**Fecha:** 2026-08-27
**Contexto:** el método tipográfico se probaba en G3, pero fuentes reales, copy, media e interacción podían alterar la geometría durante la implementación y llegar a release con párrafos comprimidos, huecos muertos o titulares multifuente rotos.
**Decisión:** 07 ejecuta exactamente una revisión `jakub-interface-polish` `FULL` sobre los renders finales desktop/mobile. No crea un agente, stage ni gate nuevo.
**Enforcement:** `TEXT_SPACING_CRAFT` bloquea G4/G5 sin evidencia que nombre escenas y ambos viewports; también se verifican capability y modo. Tres pruebas cubren ausencia de la skill, evidencia nominal y ejecución completa.
**Estado:** ACTIVE desde v6.4.2.

## D-081 — Rechazar una solución visual no autoriza a eliminar el medio

**Fecha:** 2026-08-27
**Contexto:** después de recibir una crítica sobre imágenes genéricas o una herramienta concreta, el agente podía inventar una marca `USER_EXPLICIT_TEXT_ONLY` o declarar `STATIC_WINNER_REVIEWED` y entregar una landing sin imágenes ni efectos.
**Decisión:** las excepciones globales de imagen y motion requieren una cita exacta del usuario, repetida en brief/plan y verificada contra el escenario inmutable del harness. La crítica a un output, estilo o proveedor conserva el trabajo visual y obliga a rebrief o cambio de ruta. Una escena puede ser estática, pero no convierte toda la landing en estática.
**Enforcement:** G4 exige un `PRIMARY FINAL IMG`, un comportamiento no estático seleccionado, un `FX-* FINAL` y señal física de implementación, salvo la autoridad inmutable correspondiente. Cinco pruebas adversariales cubren falsas excepciones y el escape estático.
**Estado:** ACTIVE desde v6.4.1.

## D-080 — La evidencia de release debe pertenecer al build exacto

**Fecha:** 2026-08-27
**Contexto:** una landing podía conservar gates aprobados después de cambiar copy, código, assets o artefactos; las capturas representativas tampoco demostraban el recorrido temporal completo.
**Decisión:** 02 congela tesis/CTA en `Content lock`; 06/07 recorren cada escena desktop/mobile con evidencia física única; un manifiesto SHA-256 liga traversal, implementación y artefactos causales. Si un input cambia, 00 reabre el gate causal y todos sus consumidores pierden aprobación.
**Enforcement:** G1 bloquea un lock incompleto; G4/G5 bloquean copy ausente/reintroducido, escena o viewport sin traversal, captura reutilizada, digest obsoleto y manifest desactualizado. `reopen_project.py` rechaza cualquier owner distinto de 00.
**Estado:** ACTIVE desde v6.4.0.

## D-079 — El loop de imágenes debe ejecutarse y el hero aprobado debe sobrevivir

**Fecha:** 2026-08-26
**Contexto:** 05 emitía `IH-*` pero tenía prohibido invocar generación; el harness solo registraba el master. Además, `AM-*` podía percibirse como propuesta de hero aunque G3 implementase luego otra composición.
**Decisión:** el loop de producción sigue separado de la decisión visual, pero se ejecuta de forma acotada dentro del stage `production-plan`. Cada raster conceptual/representativo generado requiere archivo y recibo `IMG-*`. `AM-*` es fuente artística; el hero `CMP-*` revisado en G3 es el target congelado para 06.
**Enforcement:** el harness bloquea `production-plan` ante briefs pendientes, archivos generados inválidos o recibos ausentes. G4/G5 requieren `HERO_TARGET_FIDELITY` comparando `CMP-*` con renders finales desktop/mobile.
**Estado:** ACTIVE desde v6.3.3.

## D-078 — La entrega es un producto físico, no una afirmación

**Fecha:** 2026-08-26
**Contexto:** G5 podía probar revisión y renders sin definir con precisión qué debía recibir el usuario ni dónde encontrarlo.
**Decisión:** 00 completa un único `Final delivery contract` en `qa-release.md`. Debe identificar landing ejecutable, entry point, comandos, preview, paquete limpio, assets, estado, limitaciones y resumen; reutiliza los renders ya exigidos.
**Enforcement:** G5 bloquea `NOT_READY`, rutas inexistentes, entry points fuera del implementation root, paquetes sucios o inválidos, assets incompletos e incoherencias de estado.
**Estado:** ACTIVE desde v6.3.2.

## D-077 — La experiencia es una columna vertebral, no seis agentes

**Fecha:** 2026-08-26  
**Contexto:** faltaba explicitar qué debe comprender, sentir y decidir el visitante a lo largo del recorrido, pero repartirlo entre seis roles nuevos duplicaría ownership de 00, 02, 03, 05 y 07.  
**Decisión:** 02 crea una única `Experience Spine` por escena dentro de `content-architecture.md`. 03 la traduce a dirección, 04 a composición, 05 a comportamiento justificado y 07 revisa su continuidad final. No se añaden agentes, gates, etapas ni artefactos.  
**Enforcement:** G1 bloquea filas incompletas, inválidas, duplicadas o ausentes; G4/G5 requieren `EXPERIENCE_CONTINUITY: PASS` con evidencia desktop/mobile.  
**Estado:** ACTIVE desde v6.3.1.

## D-076 — Autoridades únicas y ratchets de arquitectura

**Fecha:** 2026-08-25  
**Contexto:** el runtime, los validadores y la documentación repetían inventarios, helpers y reglas semánticas. Las pruebas comprobaban el resultado funcional, pero no impedían que la organización volviera a degradarse.  
**Decisión:** `config/runtime-files.json` es la única lista de contenido runtime; `validation_common.py` es el único propietario de parsing y firmas compartidas; `effect-selection.md` es la única autoridad de elegibilidad no estática. El CLI queda separado del motor del harness. `code_quality.py` bloquea duplicación, dependencias inversas y crecimiento de módulos críticos.  
**Límite:** los presupuestos de tamaño son ratchets de transición, no una declaración de que los módulos grandes ya tengan el tamaño ideal. Solo pueden bajar mediante extracción responsable.  
**Estado:** ACTIVE desde v6.3.0.

## D-070 — El harness debe ejecutar, no simular

**Fecha:** 2026-08-24  
**Decisión:** `run` invoca un executor headless por etapa, instrumenta escrituras, valida estado/gate y limita tiempo/correcciones. `doctor` bloquea la falsa suposición de que la app desktop es una CLI. `execute` queda como primitive de bajo nivel.  
**Límite:** el harness no contiene un modelo ni puede automatizar una aplicación empaquetada que Windows no permite invocar; necesita un runner headless real.

## D-071 — Capacidades nuevas como adapters sin autoridad

**Fecha:** 2026-08-24  
**Decisión:** añadir Hallmark solo como reto estructural, MengTo solo para referencias temporales/HTML, Impeccable solo tras findings tipificados y GSAP solo tras selección del runtime. Los controles UI Craft se traducen en evidencia determinista; nunca puntúan belleza ni sustituyen a 07.

## D-069 — Núcleo creativo adaptativo sin ampliar el sistema

**Fecha:** 2026-08-23  
**Decisión:** conservar ocho agentes, seis gates, los artefactos actuales y un único checkpoint humano. Divergencia creativa, selección independiente y producción del master pasan a ser etapas ejecutables separadas; contexto, genome, gramática de escenas y memoria viven como secciones estructuradas dentro de artefactos existentes.  
**Enforcement:** G1 exige contexto y cinco lentes actuales; G2 exige tres `DIR-*`, selección aislada, trazabilidad del `AM-*` y genome; G3 exige gramática por cada `SCN-*`; G5 exige fingerprint.

## D-068 — La producción final de imágenes vive en un loop externo

**Fecha:** 2026-08-23  
**Contexto:** pedir a 05 que diagnosticara, generara, corrigiera y aprobara imágenes dentro del mismo pipeline mezclaba decisión de diseño con ejecución de una herramienta y favorecía iteraciones largas o sustitutos pobres.  
**Decisión:** el OS conserva únicamente la generación del `AM-*` de dirección en G2. Para la landing final, 05 decide `IMAGE | NO_IMAGE` por escena y define rol, representación, verdad, composición, responsive, efecto e integración. Toda creación nueva sale como `EXTERNAL:IH-*` a un loop separado, que devuelve archivos para validación e integración.  
**Enforcement:** G4 bloquea escenas sin decisión, rutas externas sin handoff/retorno coincidente y archivos sin integración. Delivery rechaza `CHATGPT_GENERATE` como método final directo dentro del pipeline y acepta `EXTERNAL_IMAGE_LOOP`.  
**Límite:** el loop externo puede usar ChatGPT, fotografía, ilustración, 3D u otra herramienta; esa elección y sus iteraciones no añaden stages, agentes o prompts ocultos al OS.  
**Estado:** ACTIVE desde v5.8.0.

## D-067 — El 3D debe ser real o la dirección debe declararse 2D

**Fecha:** 2026-08-23  
**Contexto:** sombras, gradientes, perspectiva CSS y rectángulos superpuestos podían producir una apariencia de objeto volumétrico barato y aun describirse como profundidad o 3D premium.  
**Decisión:** todo mecanismo final declara `FLAT_2D`, `LAYERED_2D`, `RENDERED_3D` o `INTERACTIVE_3D`. Si se selecciona 3D, se produce mediante un recurso, herramienta o runtime externo identificable y registra asset/scene, derechos, integración y fallback. Si no, se resuelve como diseño 2D deliberado, sin imitar un objeto 3D pobre.  
**Enforcement:** delivery bloquea medios ausentes, 3D sin procedencia y CSS/SVG usado como prueba 3D. La revisión aislada de 07 incluye integridad del medio y rechaza el falso volumen que el código no puede juzgar estéticamente.  
**Límite:** profundidad visual no implica 3D; fotografía, composición, capas o contraste pueden producirla. No se obliga WebGL ni complejidad externa cuando una solución 2D es mejor.  
**Estado:** ACTIVE desde v5.7.0.

## D-066 — El sistema se prueba desde fuera del pipeline

**Fecha:** 2026-08-23  
**Contexto:** los validadores internos comprobaban contratos y artefactos, pero no podían demostrar que una ejecución siguiera el orden, usara realmente generación visual, terminara dentro de límites o llegara a una revisión visual independiente. Añadir otro agente habría aumentado el mismo andamiaje que se quería evaluar.  
**Decisión:** un harness externo crea runs aislados sobre seis escenarios, registra eventos, aplica watchdogs y reutiliza el estado y los gates oficiales. La calidad estética sigue perteneciendo a 07 sobre un snapshot físico e inmutable de masters, referencias y renders.  
**Enforcement:** se bloquean ownership incorrecto, saltos, repetición, exceso de correcciones, timeouts y comienzo de G3 sin una llamada registrada de generación de imagen en G2. Un run no pasa sin release completo y review aislado con evidencia por eje.  
**Límite:** el log prueba lo observado, no sandboxea por sí solo un ejecutor externo ni convierte Python en juez artístico. No añade agente, gate, stage, checkpoint ni artefacto de proyecto.  
**Estado:** ACTIVE desde v5.6.0.

## D-065 — Cada sección explora valor de producción sin confundirlo con coste

**Fecha:** 2026-08-23  
**Contexto:** concentrar toda la ambición en el hero dejaba el cuerpo correcto pero plano. Preguntar solo por efectos también empujaba hacia complejidad técnica sin valor.  
**Decisión:** cada `SCN-*` compara un baseline directo con la intervención específica que podría justificar una producción de alto nivel. La evaluación separa `HIGH_VALUE`, `SIMPLIFY` y `EXPENSIVE_NOISE`, y selecciona la implementación más sencilla que preserve la ganancia.  
**Proporcionalidad:** las escenas `UTILITY` responden brevemente y pueden conservar el baseline. La pregunta es obligatoria; producir un asset, 3D o efecto no lo es.  
**Enforcement:** G3 bloquea si falta cualquier escena, si baseline y oportunidad son iguales o si no se distinguen valor, simplificación y ruido caro.  
**Límite:** €10K es una provocación de ambición, no un presupuesto, score ni requisito de complejidad. No añade agente, artefacto, gate, stage ni checkpoint.  
**Estado:** ACTIVE desde v5.5.0.

## D-064 — “Premium” se define para el proyecto antes de generar

**Fecha:** 2026-08-23  
**Contexto:** un master artístico podía ser ambicioso pero irrelevante si el agente no había definido primero qué calidad debía demostrar para esa audiencia, categoría e identidad. “Premium” como adjetivo general no proporciona dirección ni umbral.  
**Decisión:** antes de invocar generación, 03 registra en `creative-direction.md` qué significa premium aquí, qué baseline actual debe superar, qué necesita autoría, qué debe evitar, qué debe probar el master y qué debe preservar la landing.  
**Enforcement:** G2 bloquea si falta un campo, si el bloque aparece después del master o si una respuesta contiene únicamente etiquetas genéricas. 07 juzga el significado visual; G3/G4 conservan el umbral durante traducción e implementación.  
**Límite:** no es un score universal ni una pregunta adicional al usuario. No añade agente, documento, gate, checkpoint ni taxonomía de estilos.  
**Estado:** ACTIVE desde v5.4.1.

## D-063 — El master artístico se valida antes de diseñar la web

**Fecha:** 2026-08-23  
**Contexto:** G2 permitía que capturas de landings convencionales compitieran como dirección creativa. Elegir la mejor de varias webs correctas no demostraba una visión artística y adelantaba layout, efectos y UI antes de fijar el mundo visual.  
**Decisión:** tras G1, 03 genera exactamente un `AM-*` mediante `CHATGPT_GENERATE`. Es un styleframe de atmósfera, materia, luz, color, profundidad, geometría y tensión compositiva; no es una captura de web ni un asset final. El único checkpoint del usuario valida, ajusta una vez o delega ese master. G3 traduce después el master a escenas web mediante baseline/challenger.  
**Simplificación:** desaparecen de G2 las múltiples direcciones de web, el mínimo por perfil, el torneo de efectos y el registro duplicado de payloads. No se añade agente, gate, stage, checkpoint ni artefacto.  
**Enforcement:** G2 exige un único `AM-*` físico, generado, grounded, confirmado y enlazado al handoff; G3 debe usar el mismo `AM-*` como fuente y demostrar su traducción responsive.  
**Límite:** Python verifica identidad, método, archivo, orden y handoff; 07 inspecciona visualmente que el master no sea UI disfrazada ni una imagen genérica.  
**Estado:** ACTIVE desde v5.4.0.

## D-062 — Una paleta global no decide el color de las secciones

**Fecha:** 2026-08-23  
**Contexto:** G3 comparaba territorios cromáticos y documentaba un mapa por escenas, pero el validador solo exigía la elección global. Un agente podía aprobar una paleta y omitir cómo funcionaba realmente en las secciones.  
**Decisión:** cada `SCN-*` de G1 recibe en G3 una asignación concreta de `background`, `foreground`, `accent` y `surface`, además de transición de entrada/salida, invariantes y resultado de contraste/estados. Las escenas utilitarias pueden heredar, pero no quedar implícitas.  
**Enforcement:** G3 bloquea si falta cualquier escena, si se usa un ID ajeno al outline, si se duplica, si los roles son abstractos o si falta `IN`/`OUT`. El mapa debe aparecer después de seleccionar dirección cromática y modos semánticos.  
**Límite:** el código verifica decisiones observables, no si la composición cromática es artísticamente buena; esa valoración sigue perteneciendo a 07 sobre renders.  
**Estado:** ACTIVE desde v5.3.1.

## D-061 — Las escenas primarias originan el sistema visual

**Fecha:** 2026-08-23  
**Contexto:** diseñar primero una paleta, una tipografía y un catálogo de componentes podía producir una landing consistente pero genérica. Añadir otro agente o documento habría aumentado el andamiaje sin asegurar decisiones mejores.  
**Decisión:** G1 distingue escenas `PRIMARY` y `UTILITY`. En G3, cada escena primaria compara la misma composición/contenido mediante un baseline profesional y un challenger específico del proyecto; la selección precede a las foundations. Después se extraen las reglas compartidas y se revisa el ritmo global antes de declarar intención de motion, 3D o media.  
**Enforcement:** G1 bloquea sin mapa válido o escena primaria. G3 bloquea si falta una estrategia primaria, las alternativas son iguales, la estrategia aparece después de las foundations o faltan las cuatro decisiones de ritmo global.  
**Límite:** no se añaden agente, gate, stage, artefacto ni catálogo de escenas. G3 decide la forma; G4 sigue produciendo assets finales desde el render estructural.  
**Estado:** ACTIVE desde v5.3.0.

## D-060 — “Premium” se recalibra con la web actual en cada proyecto

**Fecha:** 2026-08-22  
**Contexto:** una definición interna de calidad envejece y la memoria del modelo tiende a promediar patrones históricos. Guardar referencias sin caducidad tampoco demuestra que sigan representando la ejecución contemporánea.  
**Decisión:** G1 vuelve a explorar la web viva en cada proyecto. Conserva como mínimo una referencia directa o adyacente, una frontera contemporánea y una solución simple excelente; cada una registra fuente de descubrimiento, URL original, fecha y captura física. La evidencia caduca a los 30 días.  
**Límite:** las galerías descubren, pero la evidencia procede de la web original. La exploración se detiene cuando los carriles están cubiertos y nuevas referencias no cambian las direcciones; no existe navegación infinita ni un estilo premium universal.  
**Estado:** ACTIVE desde v5.2.0.

## D-059 — El gusto se desafía pronto y siempre sobre evidencia visible

**Fecha:** 2026-08-22  
**Contexto:** v5.0 exigía composiciones físicas y reviews visuales, pero el challenger de gusto seguía siendo condicional; G1 tampoco demostraba físicamente qué webs se habían inspeccionado y G4 no validaba las capturas finales.  
**Decisión:** Taste pasa a core automático antes de seleccionar G2 y aplica un challenge contextual de intercambiabilidad, eliminación e integración. G1 exige URLs originales con capturas válidas; G4/G5 exigen renders finales desktop/mobile para 07.  
**Límite:** patrones frecuentes de IA son sospechosos, no prohibiciones universales. No se imponen tipografías, escalas, acentos saturados, grids, 3D ni motion. Taste recomienda `KEEP | ITERATE | KILL`; 07 conserva la autoridad de review.  
**Estado:** ACTIVE desde v5.1.0.

## D-058 — El runtime deja de gobernarse por terminología

**Fecha:** 2026-08-21  
**Contexto:** las reglas se repetían con nombres propios en agentes, métodos, skills y plantillas. Varios tests solo comprobaban que esas palabras existieran, creando apariencia de enforcement y aumentando el drift del LLM.  
**Decisión:** `config/pipeline.json` es la única autoridad de orden. El runtime carga solo el artefacto activo, su owner y el método enlazado. Python comprueba estados y evidencia física; 07 juzga calidad. Se eliminan las taxonomías globales de autoridad, delegación y oportunidad perceptiva, además de cualquier bypass aprobado por una frase Markdown.  
**Invariantes:** siguen siendo obligatorios el research, las alternativas visuales físicas, una composición artística generada, una confirmación, la construcción estructural, la producción derivada del render, la integración y el review independiente. Publicar fuera del workspace requiere autorización explícita.  
**Estado:** ACTIVE desde v5.0.0; supersede las partes operativas incompatibles de D-052, D-053 y D-055 sin borrar su historial.

## D-057 — El pipeline es autoridad ejecutable y su camino crítico es único

**Fecha:** 2026-08-21  
**Contexto:** el flujo visual correcto estaba descrito, pero el DAG permitía iniciar `production-plan` antes del build estructural y trataba `implementation` como una fase interrumpible. Con un único `active_stage`, el agente podía bloquearse o reordenar por interpretación.  
**Decisión:** G4 sigue exclusivamente `technology-selection + structural build → production-plan → implementation → build-review`. Cada stage depende formalmente del anterior y el validador compara el camino crítico exacto, además de comprobar el DAG.  
**Invariantes:** `config/pipeline.json` gobierna ejecución; solo 00 cambia estado; technology selection no aprueba sin build, fuentes y renders; implementation no comienza sin producción final; no se añade agente, gate, stage ni artefacto.  
**Estado:** ACTIVE desde v4.17.0.

## D-056 — La producción visual se decide sobre el render estructural

**Fecha:** 2026-08-21  
**Contexto:** G4 exigía aprobar producción antes de permitir implementación. Fondos, elementos y capas se generaban sin conocer geometría, copy, zonas seguras, crops o ritmo reales; el master artístico se confundía con un asset web.  
**Decisión:** tras technology selection, 06 construye y renderiza la landing estructural. 05 audita sus escenas, convierte gaps visibles en tipos de salida web y produce en contexto. 06 integra y renderiza de nuevo; 07 permite una corrección dirigida.  
**Invariantes:** el master sigue precediendo al build; build review sigue bloqueado hasta producción aprobada; al menos un primary generado final; media documental auténtica; una sola corrección; sin agentes, gates, stages ni artefactos nuevos.  
**Estado:** ACTIVE desde v4.16.0.

## D-055 — Una sola orden gobierna creación e integración de imágenes

**Fecha:** 2026-08-21  
**Contexto:** el sistema podía completar fichas, generar un SVG o una captura HTML y aprobar el visual payload sin invocar generación de imágenes. La fragmentación entre master, inventario, efectos e implementación favorecía cumplimiento documental y landings tipográficas/genéricas.  
**Decisión:** `IMAGE_CREATION_FLOW` une el recorrido operativo: G2 crea el master mediante `CHATGPT_GENERATE`; tras la única confirmación, 05 produce un mapa secuenciado con brief y ubicación exacta; ejecuta cada fila; 06 integra los archivos finales. G4 exige al menos un primary generado.  
**Invariantes:** la imagen no falsifica identidad documental; texto y controles siguen siendo semánticos; una corrección máxima por candidato; prompts, HTML, SVG, CSS y capturas no sustituyen generación; no se añade agente, gate, stage, checkpoint ni artefacto.  
**Estado:** ACTIVE desde v4.15.0.

## D-054 — La ejecución automática siempre tiene límite y salida recuperable

**Fecha:** 2026-08-21  
**Contexto:** una prueba superó noventa minutos sin progreso visible. El pipeline definía estados y gates, pero no acotaba reintentos de herramientas, regeneraciones, correcciones ni reaperturas. Un agente podía interpretar `REVISE` como permiso para repetir indefinidamente.  
**Decisión:** `BOUNDED_EXECUTION` concede a cada stage una pasada inicial y una corrección automática; una herramienta transitoria y un candidato visual se reintentan una vez. Un blocker repetido o quince minutos sin evidencia material detienen la ejecución, conservan artefactos y devuelven `BLOCKED`.  
**Invariantes:** el límite controla repetición, no ambición ni calidad; una reanudación del usuario inicia otra ejecución acotada; no se borra trabajo; no se amplía scope; no se añade gate, stage, agente, checkpoint ni artefacto de proyecto.  
**Estado:** ACTIVE desde v4.14.0.

## D-053 — La exploración artística se crea antes de poder descartarse

**Fecha:** 2026-08-21  
**Contexto:** G1 obligaba al estudio y G2 a producir carga visual, pero un resultado `LOW` permitía evitar una composición artística completa. El agente podía decidir de antemano que una solución directa era suficiente y nunca mostrar el potencial visual del proyecto.  
**Decisión:** después de G1, todo proyecto salvo `USER_EXPLICIT_TEXT_ONLY` produce una `ARTISTIC_DIRECTION_COMPOSITION` física, ambiciosa y fundada en research. Se muestra y compara dentro de G2; puede ser rechazada si otra dirección resuelve mejor el objetivo.  
**Invariantes:** crear no significa seleccionar; “artística” no significa maximalista; un prompt o decoración genérica no cuenta; Python valida existencia y anclaje, 07 juzga calidad; no se añade gate, stage, agente, documento ni tabla.  
**Estado:** ACTIVE desde v4.13.0.

## D-052 — Un único visto bueno visual antes de fijar el master

**Fecha:** 2026-08-21  
**Contexto:** el sistema podía seleccionar una composición coherente y convertirla en master sin dar al usuario un punto claro y barato para confirmar si esa expresión le representa. Añadir preguntas en cada fase haría el proceso rígido y volvería a sobredimensionarlo.  
**Decisión:** G2 contiene una sola `CREATIVE_MASTER_CONFIRMATION` después de materializar/comparar visuales y antes de fijar el master. El usuario puede `USER_APPROVED`, pedir una ronda concreta `ITERATE` o delegar mediante `PREFERENCE_DELEGATED`; la delegación previa cierra el punto sin repreguntar.  
**Invariantes:** se presenta evidencia real, no prompts; la selección registrada coincide con el candidato confirmado/delegado; `ITERATE` reutiliza el mismo punto; la preferencia no sustituye a 07; no se añade gate, stage, agente, documento ni formulario.  
**Estado:** ACTIVE desde v4.12.0.

## D-051 — La composición elegida gobierna el desarrollo posterior

**Fecha:** 2026-08-21  
**Contexto:** una composición artística podía ganar G2 y después quedar reducida a inspiración informal. 04 podía recomenzar tipografía, color, composición y media por separado, produciendo una landing correcta pero distinta o un hero aislado de un cuerpo genérico.  
**Decisión:** el `CMP-*` seleccionado se promueve a `CREATIVE_MASTER`. 03 extrae tesis, anti-reglas, riesgos e invariantes `TYPE | COLOR | COMPOSITION | MEDIA | SPACE | DEPTH | MOTION`; 04 registra conservación, desviaciones deliberadas y traducción hero/cuerpo; 07 revisa `DIRECTION_FIDELITY`; 06 compara el build con master y G3.  
**Invariantes:** el master no tiene que ser maximalista; no se rasteriza ni sustituye interfaz real; no obliga a copiar píxeles; una restricción real puede justificar una desviación; no se añade render, fase, gate, agente, artefacto ni tabla de inventario.  
**Estado:** ACTIVE desde v4.11.0.

## D-050 — La procedencia cromática no demuestra composición cromática

**Fecha:** 2026-08-21  
**Contexto:** 04 podía inventar una paleta, asociar sus colores con valores del proyecto y aprobar G3 sin demostrar que la combinación funcionaba en superficies reales. El significado escrito se confundía con oficio cromático.  
**Decisión:** antes de `scene-color-system`, 04 renderiza `BASELINE | BRAND_LED | CHALLENGER` sobre el mismo hero, declara jerarquía/proporciones y evalúa `COLOR_COMPOSITION` aparte de `COLOR_PROVENANCE`. 07 crea una lámina física con accent eliminado, neutralización y paleta típica de categoría.  
**Invariantes:** Python prueba archivos y estructura, no belleza; los tres territorios no son tres direcciones creativas nuevas; no se prohíbe ninguna paleta; accesibilidad no sustituye craft; semántica como “verde = sostenibilidad” nunca cierra calidad; no se añade gate, agente, fase ni artefacto.  
**Estado:** ACTIVE desde v4.10.0.

## D-049 — Un asset auxiliar no puede hacerse pasar por carga visual principal

**Fecha:** 2026-08-21  
**Contexto:** un agente produjo un SVG propio, lo registró como `IMG-* FINAL` y superó los checks aunque la dirección pedía escenas de cereal, biomaterial, transformación y laboratorio. Optimizó para el validador porque todos los formatos finales tenían la misma autoridad.  
**Decisión:** el inventario existente clasifica cada asset `PRIMARY:<método> | SUPPORTING:<método>`. Al menos un primary scene-bearing debe ser final. En proyectos `MATERIAL`, SVG/vector no puede ser el único primary salvo `VECTOR_PRIMARY_REVIEWED` tras comparación renderizada independiente.  
**Invariantes:** no se obliga a usar ChatGPT Images, raster, vídeo o 3D cuando otra solución gana; no se prohíbe ilustración vectorial; supporting sigue permitido; no se añade gate, agente, fase, documento ni tabla; facilidad técnica y “pasa el validador” no son evidencia de calidad.  
**Estado:** ACTIVE desde v4.9.2.

## D-048 — La evidencia visual se reutiliza y escala por perfil

**Fecha:** 2026-08-21  
**Contexto:** D-047 hizo la composición verificable, pero duplicó registros en G2/G3 y aplicó al perfil `focused` casi la misma producción de escenas que a `standard`. El sistema conservaba pocos agentes, pero empezaba a administrar evidencia en vez de diseñar.  
**Decisión:** G2 usa un único registro por dirección que sirve a la vez como muestra visual y `CMP-*`; G3 usa una única tabla de escenas para composición e integración. `focused` reutiliza el hero seleccionado y solo añade otra escena cuando su trabajo visual es materialmente distinto; `standard/extended` mantienen hero y body.  
**Invariantes:** se mantienen ocho owners, seis gates, doce stages y doce artefactos; no baja el mínimo de direcciones; prompts no cuentan; mobile sigue siendo obligatorio para el hero; `CMP-*` no se entrega; la simplificación elimina duplicación, no diseño.  
**Estado:** ACTIVE desde v4.9.1.

## D-047 — Componer visualmente antes de descomponer para producción

**Fecha:** 2026-08-21  
**Contexto:** el sistema podía exigir imágenes y mecanismos, pero un agente aún podía diseñar cada elemento por separado y obtener una landing formalmente completa pero visualmente plana. Generar una imagen de la escena completa permite explorar fondos, capas, profundidad y relaciones que el diseño por inventario no descubre.  
**Decisión:** cuando `PERCEPTUAL_OPPORTUNITY=MATERIAL`, G2 exige una composición física `CMP-*` del hero por dirección y G3 exige hero más una escena corporal distinta en desktop/mobile. La composición se descompone en HTML/contenido, CSS/layout, `IMG-*` y `FX-*`; nunca se entrega como sección rasterizada.  
**Invariantes:** no se añade gate, stage, rol ni artefacto; no se obliga a generar imágenes cuando CSS/prototipo/Figma resuelve mejor; un prompt no es evidencia; texto y controles esenciales no se hornean; 05 produce las capas finales y 06 conserva semántica, responsive y accesibilidad.  
**Estado:** ACTIVE desde v4.9.0.

## D-046 — La ambición expresiva se decide por trabajo perceptivo, no por sector

**Fecha:** 2026-08-21  
**Contexto:** el sistema podía exigir calidad y detectar un hero plano, pero no decidía de forma general cuándo una solución directa era insuficiente para la percepción necesaria. Convertir listas como “consultor = artístico” en reglas habría creado presets y sesgo estilístico.  
**Decisión:** G1 aplica `PERCEPTUAL_OPPORTUNITY = LOW | MATERIAL` mediante seis lentes cualitativas sin scoring. `MATERIAL` obliga a G2 a comparar un baseline `DIRECT` excelente con un `PERCEPTUAL_CHALLENGER` materializado y a registrar ganancia, autenticidad, claridad/acción y coste/robustez.  
**Invariantes:** categoría y gusto no deciden; el baseline no puede ser strawman; explorar no significa seleccionar; `LOW` no reduce craft ni prohíbe expresión; cada gesto challenger debe proceder de evidencia del proyecto; no se añade gate, stage, role ni artefacto.  
**Estado:** ACTIVE desde v4.8.0.

## D-045 — La presencia de ingredientes no demuestra resolución premium

**Fecha:** 2026-08-21  
**Contexto:** un hero contenía titular, CTA, asset, paleta y un mecanismo nominal, pero seguía siendo plano e intercambiable: tipografía basada solo en escala, neutro cálido genérico, gráfico aparcado en la segunda columna y ningún comportamiento perceptible. Los controles verificaban cada ingrediente por separado.  
**Decisión:** G3 incorpora un stress test renderizado de seis ejes y pruebas de intercambio/eliminación. G4/G5 exigen que un `FX-* FINAL` señale código real mediante `source/file#marker`.  
**Invariantes:** no se obliga a usar varias fuentes, 3D, gradientes o motion; una solución sobria o estática puede ganar si demuestra voz, integración, procedencia, tensión y detalle; ningún color concreto queda prohibido; un cluster frecuente sin relación con el sujeto bloquea; no se añade fase ni artefacto.  
**Estado:** ACTIVE desde v4.7.0.

## D-044 — Los gates críticos se prueban; el review se aísla

**Fecha:** 2026-08-21  
**Contexto:** varias reglas ya tenían validación parcial, pero no existía un preflight dirigido que 00 pudiera ejecutar antes de aprobar cada gate. Además, llamar “07” al mismo contexto no eliminaba el sesgo del owner y los claims dependían de una norma narrativa.  
**Decisión:** añadir `tools/validate_gate.py`, `tools/audit_state.py`, un ledger de claims verificable y `review_context: ISOLATED` para los tres checkpoints de 07. CI ejecuta preflight sobre gates aprobados y auditoría de estado.  
**Invariantes:** JSON Schema se reserva para JSON; Markdown se valida por estructura y evidencia; un modelo/proveedor distinto es opcional pero el contexto nuevo es obligatorio; SQLite, commits por transición y nuevos artefactos no se incorporan sin evidencia de concurrencia real; las taxonomías con semánticas distintas no se fusionan artificialmente.  
**Estado:** ACTIVE desde v4.6.0.

## D-043 — La entrega se prueba sobre archivos reales

**Fecha:** 2026-08-21  
**Contexto:** un agente conocía la política de imágenes, pero construyó una landing sin producirlas y solo reconoció el fallo al ser preguntado. Los gates validaban declaraciones en Markdown; no demostraban que el asset existiera, estuviera incluido o fuese usado por el código. En ChatGPT Projects, además, archivos e instrucciones ocupan superficies distintas.  
**Decisión:** introducir `DELIVERY_PROOF_REQUIRED`, un punto de entrada skill, instrucciones específicas para ChatGPT Projects y `tools/validate_delivery.py`. G4/G5 requieren `implementation_root`; cada `IMG-* FINAL` debe ser un archivo visual válido dentro de esa raíz y estar referenciado por la implementación.  
**Invariantes:** si `CHATGPT_GENERATE` gana se invoca la herramienta; un prompt no es un asset; screenshots QA no son media; si la prueba no puede ejecutarse o falla, no se declara terminado; no se añade agente, gate, stage ni artefacto de proyecto.  
**Estado:** ACTIVE desde v4.5.0.

## D-042 — Explorar mecanismos antes de elegir una landing estática

**Fecha:** 2026-08-21  
**Contexto:** el OS especificaba correctamente motion, efectos y fallbacks después de seleccionarlos, pero “cuando sea material” permitía declarar cero oportunidades. El booster immersive explicit-only reforzaba además la falsa idea de que todo 3D necesitaba una experiencia inmersiva.  
**Decisión:** `CREATIVE_MECHANISM_REQUIRED` obliga a cada dirección a materializar un `FX-*` con base estática y candidatos simple/expresivo, usando anclas de webs reales, laboratorios, bancos de elementos o fuentes 3D. G3 prueba el ganador y G4 exige `FINAL` o `STATIC_WINNER_REVIEWED`.  
**Invariantes:** no se fuerza espectáculo; `NONE` necesita comparación visible y review; 3D acotado puede usarse fuera de immersive cuando producto, material, espacio, transformación o perspectiva lo justifican; fuentes descubren y prueban, no conceden identidad o licencia; no se añade agente, gate, stage ni artefacto.  
**Estado:** ACTIVE desde v4.4.5.

## D-041 — Toda landing necesita carga visual sustancial

**Fecha:** 2026-08-21  
**Contexto:** las reglas de verdad y producción operaban solo después de que una dirección se declarase image-led. Un agente podía elegir typography-only, crear cero IDs y aprobar el proceso sin activar ninguna obligación de producción.  
**Decisión:** `VISUAL_PAYLOAD_REQUIRED` exige al menos un asset visual sustancial, específico y funcional: muestra por dirección en G2, integración desktop/mobile en G3 y un `IMG-* FINAL` con salida utilizable en G4. La falta de material activa producción no documental honesta.  
**Invariantes:** logo, iconos, blobs, gradientes, patrones genéricos, placeholders y tipografía grande no cuentan por sí solos; el agente no puede inventar la excepción; solo una petición explícita `USER_EXPLICIT_TEXT_ONLY` la permite; no se añade agente, gate, stage ni artefacto.  
**Estado:** ACTIVE desde v4.4.4.

## D-040 — Descubrir no concede autoridad automática

**Fecha:** 2026-08-21  
**Contexto:** el problema parecía cromático, pero la causa era general: research podía encontrar un logo, CSS, tokens, componentes, layout o referencia y downstream podía heredarlo por existir o ignorarlo sin explicar. Crear reglas separadas por color, logo o CSS habría fragmentado el sistema.  
**Decisión:** `EVIDENCE_AUTHORITY` evalúa todo hallazgo material como `ADOPT | ADAPT | REJECT` según el objetivo actual y transfiere su autoridad como `DECIDED | BOUNDED | OPEN`. Research puede cerrar cualquier decisión respaldada por evidencia, limitarla o pasarla abierta al owner adecuado.  
**Invariantes:** procedencia no demuestra fit; no hay cuotas por disciplina; downstream verifica `DECIDED`, explora dentro de `BOUNDED` y resuelve `OPEN`; una decisión solo se reabre mediante finding al owner causal; ni material propio ni referencia externa se heredan automáticamente.  
**Estado:** ACTIVE desde v4.4.3.

## D-039 — Delegar preferencia no delega el pipeline

**Fecha:** 2026-08-21  
**Contexto:** ante “haz tu propuesta”, un agente abandonó la ejecución de G2, sustituyó la evidencia visual por prosa y afirmó que podía cerrar la dirección. El sistema regulaba preguntas y ownership, pero no definía qué autoridad transfería esa respuesta.  
**Decisión:** clasificar “haz tu propuesta”, “elige tú” y equivalentes como `PREFERENCE_DELEGATED`. El owner puede seleccionar la alternativa mejor sustentada o una síntesis coherente, pero conserva brief, stage, artefactos, evidencia y reviewer. Solo 00 cambia estado.  
**Invariantes:** delegación no es aprobación; no reabre el brief ni autoriza brainstorming libre; no elimina outputs del stage; no permite preguntar otra vez la misma preferencia; si todas las alternativas fallan se reexplora dentro del mismo stage; solo una preferencia irreducible, cambio de objetivo o riesgo factual/legal vuelve al usuario.  
**Estado:** ACTIVE desde v4.4.2.

## D-038 — Subdividir conocimiento, no proceso

**Fecha:** 2026-08-21  
**Contexto:** D-037 corrigió decisiones sin comparación, pero convirtió `decision-log.md` en una matriz obligatoria de once columnas para G1–G5 y duplicó cada imagen, efecto y breakpoint. La arquitectura seguía compacta, pero la ejecución volvía a ser administrativa.  
**Decisión:** conservar el protocolo común y mover toda comparación al artefacto del owner. Las subdivisiones son secciones internas —narrativa/contenido/CTA, foundations/composición/responsive, imágenes/tratamiento/efectos—, no nuevos agentes o gates. El registro central usa seis campos y solo resume decisiones globales, transversales o costosas de revertir.  
**Invariantes:** una base y un challenger siguen siendo necesarios cuando la elección es material; `ONLY_VIABLE` necesita motivo real; responsive sigue siendo observacional; `IMG-*`, `FX-*` y breakpoints no se duplican; G5 verifica únicamente decisiones globales activas.  
**Estado:** ACTIVE desde v4.4.1.

## D-037 — Un protocolo común hace verificables las decisiones materiales

**Fecha:** 2026-08-21  
**Contexto:** narrativa, foundations, media, efectos y responsive tenían buenos criterios especializados, pero salvo tecnología/dirección el sistema podía aprobar artefactos largos sin demostrar alternativas comparables, selección o rechazo. Añadir un proceso por área habría vuelto a sobredimensionar el OS.  
**Decisión:** usar un único contrato `docs/methods/material-decisions.md` y convertir el `decision-log.md` existente en índice vivo desde G1. El detalle queda en el artefacto owner. Cada elección material compara una base y un challenger, o justifica `ONLY_VIABLE`; responsive registra fallo observado en vez de candidates ficticios.  
**Invariantes:** no hay nuevo agente, gate, stage ni artefacto; microdecisiones de oficio no se registran; tokens y capability logs no prueban selección; el validador comprueba proceso/cobertura, nunca calidad estética; owner y reviewer no coinciden; G5 exige decisiones activas `VERIFIED`.  
**Estado:** SUPERSEDED por D-038; el protocolo permanece, el índice exhaustivo no.

## D-036 — Los efectos se comparan antes de especificarse

**Fecha:** 2026-08-21  
**Contexto:** el sistema exigía propósito, estados y fallback después de escoger un efecto, pero no gobernaba la elección. Un agente podía adoptar el primer hover atractivo, repetirlo globalmente o elegir `NONE` sin explorar.  
**Decisión:** toda oportunidad material se clasifica `DEFINING | STRUCTURAL | FEEDBACK | AMBIENT` y compara candidates `NONE | SIMPLE | EXPRESSIVE` en contexto. Se elige por meaning, direction fit, claridad, control, responsive, viabilidad y, al final, diferenciación.  
**Invariantes:** cero o un defining mechanism normalmente; más requiere una lógica común; `NONE` es candidato, no escape; referencias descubren mecanismos pero no seleccionan; los efectos elegidos comparten gramática y fallback.  
**Estado:** ACTIVE.

## D-035 — La paleta se aplica por modos de escena

**Fecha:** 2026-08-21  
**Contexto:** tratar la paleta como un fondo global puede forzar toda la landing a mantener la intensidad del hero o, en el extremo contrario, hacer que las secciones claras posteriores parezcan una plantilla sin relación.  
**Decisión:** separar primitives de identidad, roles semánticos y modos por función (`SIGNATURE | READING | CONTRAST | UTILITY`). Cada escena elige modo y transición; los componentes consumen roles, no colores hardcoded.  
**Invariantes:** el número de modos no es fijo; claro/oscuro no se prescriben; el hero puede ser espectacular y el cuerpo calmado; la continuidad se demuestra mediante invariantes de identidad y no por repetir un fondo; los cambios cromáticos necesitan función narrativa.  
**Estado:** ACTIVE.

## D-034 — Producir media no es inventar evidencia

**Fecha:** 2026-08-21  
**Contexto:** la regla “no inventar assets” fue interpretada por un agente externo como prohibición de generar recursos visuales cuando no existían fotos reales. El resultado protegía la autenticidad, pero dejaba incompleta una dirección que necesitaba imagen.  
**Decisión:** sustituir esa regla por clases de verdad `DOCUMENTARY | REPRESENTATIVE | CONCEPTUAL | DECORATIVE`. Solo `DOCUMENTARY` exige material real verificable. Las demás clases pueden producirse o generarse si no crean una atribución factual falsa. La media necesaria ausente pasa a `NEEDS_PRODUCTION`, no a prohibición.  
**Invariantes:** no se genera una falsa persona, taller, producto o resultado real; una dirección image-led necesita muestras representativas antes de G3; 05 debe resolver cada necesidad mediante producción, generación, encargo o eliminación razonada.  
**Estado:** ACTIVE.

## D-033 — Las referencias web se eligen por el problema del proyecto

**Fecha:** 2026-08-20  
**Contexto:** buscar “webs modernas” o usar solo galerías premiadas confunde novedad con adecuación y puede imponer una estética antes de comprender la landing.  
**Decisión:** 01 deriva un `reference search brief` del objetivo, audiencia, acción, categoría, percepción, material y constraints. Contrasta referencias `DIRECT | ADJACENT | FRONTIER | SIMPLE`, inspecciona la web original y extrae principios por alcance en vez de seleccionar una plantilla ganadora.  
**Invariantes:** galerías descubren pero no prueban; la alternativa simple viable siempre se considera; premio/popularidad no determinan fit; Pinterest es secondary discovery y exige fuente original; los territorios finales combinan principios sin copiar una web completa.  
**Estado:** ACTIVE.

## D-032 — Cada imagen es una decisión independiente

**Fecha:** 2026-08-20  
**Contexto:** una dirección genérica de “usar fotos” o “generar imágenes” no define qué debe comunicar cada asset y permite que piezas atractivas, inconsistentes o equivocadas lleguen al build.  
**Decisión:** toda imagen y variante material recibe ID, representación, función, estilo, composición, continuidad, restricciones, uso, método, tratamiento estático, comportamiento, provenance y aceptación propios dentro de `production-plan.md`. Para nueva imagen raster conceptual/editorial se evalúa siempre `CHATGPT_GENERATE`, sin convertirlo en default cuando otra vía preserva mejor autenticidad, precisión o control.  
**Invariantes:** una biblia visual común no sustituye briefs individuales; marco, hover y efectos necesitan razón por ID; `NONE` es válido; no se fija un modelo o versión permanente; frontend solo integra assets `FINAL`.  
**Estado:** ACTIVE.

## D-027 — v4 compacta el sistema alrededor del diseño

**Fecha:** 2026-08-20  
**Contexto:** v3 protegía bien la calidad, pero 23 agentes, 16 gates, 41 stages y más de 50 artefactos convertían proyectos pequeños en procesos administrativos.  
**Decisión:** conservar todas las fases del diseño agrupadas en 8 roles, 6 gates y 12 stages. Strategy/Research, UX/Content, Visual Identity/System/UI/Responsive y Critic/QA se consolidan por continuidad de decisión.  
**Tecnología:** toda producción requiere comparar al menos dos opciones, incluida la solución más simple viable. HTML, Astro, frameworks full-stack, CMS y custom son candidates, no defaults.  
**Estado:** ACTIVE desde v4.

## D-028 — Capacidades externas mediante slots y adapters

**Fecha:** 2026-08-20  
**Contexto:** varias skills externas mejoran dirección, polish, motion y auditoría, pero cargarlas juntas crea solapamiento, defaults estéticos y dependencia externa.  
**Decisión:** v4.1 introduce un router local con progressive disclosure y slots `direction-primary | direction-challenger | knowledge-lookup | craft-polish | motion-craft | interface-audit | immersive-booster`.  
**Invariantes:** un primary; challenger limitado; lookup sin autoridad; experimental no automático; immersive explicit-only; source/license/fallback trazables; capability log en G2–G4.  
**Estado:** ACTIVE desde v4.1.

## D-029 — Intake progresivo y referencias por descubrimiento

**Fecha:** 2026-08-20  
**Contexto:** pedir objetivo, audiencia, alcance, identidad, contenido, assets, referencias, integraciones y restricciones de una vez convierte el inicio en un formulario y penaliza a quien todavía no tiene ejemplos o materiales.
**Decisión:** empezar con una sola invitación abierta, extraer antes de preguntar y limitar cada ronda a dos preguntas que cambien una decisión material. Fotos, copy y referencias son inputs opcionales. Su ausencia activa una ruta `DISCOVER` de investigación contemporánea, fechada y trazable, con pocos territorios para reacción y reglas anti-copia.
**Invariantes:** no preguntar stack durante intake; unknown reversible no bloquea; no inventar material; solo bloquean decisiones que redefinen el proyecto o riesgos factuales, legales o irreversibles.
**Estado:** ACTIVE desde v4.1.

## D-030 — Gobierno del OS y assurance proporcional

**Fecha:** 2026-08-20  
**Contexto:** v4.1 era fuerte en diseño y consistencia del pipeline, pero no tenía owner para auditar el propio sistema, confundía soporte nominal con cobertura especializada y había perdido validación observada, release/operations assurance y controles efectivos de vigencia al compactar versiones anteriores.
**Decisión:** v4.2 añade un `Design OS Auditor / System Steward` fuera de los ocho roles operativos; incorpora experience validation como checkpoint de 02, un baseline corporativo de diez áreas, ocho extension packs reales, risk flags y validación temporal de fuentes/capacidades.
**Proporcionalidad:** `focused` admite heurística documentada; `standard` requiere feedback representativo o limitación explícita; `extended` exige usuarios observados o aceptación humana del riesgo. Especialidad se activa por proyecto/tipo/riesgo, no globalmente.
**Invariantes:** un test estructural no prueba calidad; AI no es usuario observado; legal/security assurance requiere evidencia competente; permitir un project type no implica soporte sin packs; el Steward no cambia estado de proyectos.
**Estado:** SUPERSEDED por D-031; amplió el scope más allá de landings.

## D-031 — Scope estricto: creación de landings

**Fecha:** 2026-08-20  
**Contexto:** v4.2 reaccionó a una auditoría añadiendo disciplinas de producto, comercio, compliance y operación. Aunque eran condicionales, convertían un sistema de diseño de landings en una plataforma web general y reintroducían burocracia.
**Decisión:** v4.3 acepta únicamente `project_type: landing`. Elimina extension packs, risk flags, experience-validation formal y baselines ajenos. Conserva intake, research, content/UX, dirección, visual/UI, responsive, motion/media, selección tecnológica, implementación y crítica/QA.
**Boundary:** SEO strategy, analytics, legal/privacy, application security, commerce, CMS strategy, localization y post-launch operations no son ownership del OS. Pueden aparecer solo como constraint o integración externa de la landing.
**Gobierno:** System Steward permanece fuera del pipeline con mandato explícito de impedir scope creep.
**Estado:** ACTIVE desde v4.3.

## D-001 — Efectos específicos, no ausencia de efectos
**Estado:** ACTIVE. Evitar clichés significa diseñar efectos específicos, no reducir efectos por defecto.

## D-002 — Premium no equivale a minimalismo
**Estado:** ACTIVE.

## D-003 — Red Team no rediseña
**Estado:** ACTIVE.

## D-004 — Visual y técnico son gates independientes
**Estado:** ACTIVE.

## D-005 — Motion nace en storyboard, se especifica tras responsive
**Anterior:** Motion y Mobile se necesitaban mutuamente.  
**Nueva:** Art/UI crean intent/storyboard → Responsive fija constraints → Motion cierra timing/behavior.  
**Estado:** ACTIVE desde v2.

## D-006 — Diferenciación entre escenas
**Estado:** ACTIVE.

## D-007 — Contenido requiere owner explícito
C01 posee copy/claims/microcopy. UI no inventa contenido para resolver layout.  
**Estado:** ACTIVE desde v2.

## D-008 — No autoaprobación de agentes
Agentes entregan `READY_FOR_GATE`; 00 cambia estado oficial.  
**Estado:** ACTIVE desde v2.

## D-009 — Red Team en dos pasadas
Design review antes de frontend + build review después de Visual QA.  
**Estado:** ACTIVE desde v2.

## D-010 — Shift-left técnico y accesible
09/12 actúan como advisors antes de sus gates finales.  
**Estado:** ACTIVE desde v2.

## D-011 — DRS admite cache trazable
Fresh research 3+ fuentes para patrón nuevo/alto impacto; cached contrast para el mismo mecanismo vigente. Para identity foundations v3, fresh research es obligatorio.  
**Estado:** ACTIVE desde v2; ampliado en v3.

## D-012 — Ejecución no equivale a aprobación
Cada stage declara `entry_requires`; downstream no puede activarse por mera precedencia del DAG.  
**Estado:** ACTIVE desde v2.1.

## D-013 — Validación de experiencia independiente
V01 valida tareas y declara el nivel real de evidencia. Una simulación no puede etiquetarse como usuario observado.  
**Estado:** ACTIVE desde v2.1.

## D-014 — QA funcional independiente de Frontend
Q01 valida comportamiento real antes de Visual QA y participa en la aprobación de G12/G13.  
**Estado:** ACTIVE desde v2.1; numeración actualizada en v3.

## D-015 — Contenido se finaliza antes de implementación
C01 vuelve tras G11 para resolver estados `MISSING/PROVISIONAL`, claims y cambios de longitud/jerarquía antes de G12.  
**Estado:** ACTIVE desde v2.1; numeración actualizada en v3.

## D-016 — CI debe fallar ante estados imposibles
La validación del sistema es fail-closed y se protege con mutation/lifecycle tests.  
**Estado:** ACTIVE desde v2.1.

## D-017 — CI usa referencias inmutables para Actions
Las Actions externas del workflow se fijan a SHA completo. El validador rechaza tags móviles y Dependabot propone las actualizaciones.  
**Estado:** ACTIVE desde v2.1.

## D-018 — Una dirección no se aprueba sin competición visual/experiencial
04 explora varias direcciones materializadas; V00 valida comparativamente después de DRS/CT01/M01. La primera propuesta razonable no puede convertirse por inercia en Design System/UI. El mínimo depende del delivery profile.  
**Estado:** ACTIVE desde v2.2.

## D-019 — Creative Technology es core y tool-agnostic
CT01 posee mecanismos técnicos creativos, prototipos de riesgo y fallbacks. CSS/JS/SVG/canvas/WebGL/3D/librerías son opciones según la experiencia, no estándares globales ni señales automáticas de calidad.  
**Estado:** ACTIVE desde v2.2.

## D-020 — Media & Asset Production es core y provider-agnostic
M01 posee estrategia/readiness/finalización de media/assets. En v3 también revisa compatibilidad entre media real e identity foundation.  
**Estado:** ACTIVE desde v2.2; ampliado en v3.

## D-021 — Ninguna herramienta concreta es requisito del OS
Figma, navegador/prototipo, Blender, Spline, GSAP, Three.js u otras herramientas/proveedores pueden usarse cuando resuelvan una necesidad. El core exige evidencia/contrato, no una cuenta o stack concreto.  
**Estado:** ACTIVE desde v2.2.

## D-022 — Visual Identity es una fase core independiente
**Contexto:** v2.2 permitía pasar de una dirección G5 directamente a Design System. Eso podía convertir principios cromáticos/tipográficos insuficientemente investigados en tokens y dar apariencia de rigor a una mala foundation.  
**Decisión:** introducir VI01 + IV01 y G6 Visual Identity entre Direction Selection y Design System.  
**Impacto:** Design System pasa a G7; release pasa a G15; UI y producción consumen identity foundations aprobadas.  
**Estado:** ACTIVE desde v3.

## D-023 — Research visual foundational es obligatorio
**Decisión:** G2 debe investigar externamente identidad existente, categoría, competencia, typography/color/media landscape y referencias adyacentes/materiales. Para primary typeface, brand color system o nuevo graphic language, DRS exige `fresh-research`; `NO_EXTERNAL_RESOURCE_REQUIRED` no es válido.  
**Estado:** ACTIVE desde v3.

## D-024 — Art Direction no cierra fuente ni paleta final
**Decisión:** 04 puede definir type/color territories para comunicar una dirección, pero VI01 posee family/pairing/color foundation real. V00 valida experiencia; IV01 valida identity.  
**Estado:** ACTIVE desde v3.

## D-025 — Identity se valida con pressure tests comparables
**Decisión:** cada candidate G6 se prueba sobre el mismo layout/copy/media base en escenas representativas antes de tokenizar. El profile fija mínimo 2/3/4 candidates. IV01 devuelve `KEEP | ITERATE | KILL` y escala preferencia humana irreducible.  
**Estado:** ACTIVE desde v3.

## D-026 — Color y tipografía necesitan provenance de proyecto
**Decisión:** color psychology genérica y categorías estéticas (`serif=premium`, `azul=confianza`) no son rationale suficiente. Tipografía requiere source/foundry, licencia web, charset y comportamiento real; color requiere relación contextual con equity/producto/material/media/categoría/cultura o necesidad funcional documentada.  
**Estado:** ACTIVE desde v3.

### D-072 — La creación falla cerrada fuera del harness
Fecha: 2026-08-24  
Scope: GLOBAL  
Contexto: una conversación externa leyó el repositorio, omitió el runner y entregó HTML sin el master generado.  
Decisión anterior: el harness se describía como evaluación reproducible, pero la entrada no impedía usar el pipeline manualmente.  
Nueva decisión: solo un proceso lanzado por `evaluation_harness.py run` puede crear y declarar una landing del sistema. Sin las cinco variables `HARNESS_*`, la sesión se limita a inspección y debe detenerse antes de diseñar.  
Motivo/evidencia: un validador no puede hacer cumplir una ejecución que nunca lo invoca.  
Impacto: entrada fail-closed; no añade agentes, gates ni stages.  
Agentes/gates afectados: entrada global; `creative-master`.  
Estado: ACTIVE  
Review-by: tras dos ejecuciones reales con un executor headless.

### D-073 — ChatGPT puede ser el ejecutor bajo control local
Fecha: 2026-08-24  
Scope: GLOBAL  
Contexto: ChatGPT dispone de Python y archivos, pero no puede invocar otro modelo mediante `codex` o `claude`.  
Decisión anterior: v6.1.1 detenía toda creación sin un executor headless externo.  
Nueva decisión: el mismo harness admite `CHAT_INTERACTIVE`; el chat trabaja una etapa y `chat-next` valida antes de abrir la siguiente. `chat-image` exige el raster físico del master.  
Motivo/evidencia: el controlador y el ejecutor no necesitan ser procesos distintos si el controlador sigue gobernando el orden y los gates.  
Impacto: hace viable ChatGPT sin duplicar pipeline, roles o validadores.  
Agentes/gates afectados: todos, sin cambio de ownership.  
Estado: ACTIVE  
Review-by: primera landing interactiva completa.

### D-074 — Los assets se derivan de una narrativa visual de página
Fecha: 2026-08-25  
Scope: GLOBAL  
Contexto: decidir `IMAGE | NO_IMAGE` localmente no determinaba cantidad, fondos, ritmo ni elegibilidad de sticky/parallax/3D.  
Decisión anterior: 05 auditaba escenas directamente después del render estructural.  
Nueva decisión: 05 mapea primero todos los beats visuales y deriva el conjunto mínimo de assets. Formato y comportamiento se eligen por separado; los mecanismos expresivos requieren trigger, descomposición y fallback verificables.  
Motivo/evidencia: las decisiones locales podían ser correctas de forma aislada y producir una landing globalmente plana o arbitraria.  
Impacto: un nuevo bloque dentro de `production-plan.md`, sin nuevo artefacto, agente, gate o stage.  
Agentes/gates afectados: 05, 07 y G4.  
Estado: ACTIVE  
Review-by: tras dos landings completas con necesidades visuales distintas.

### D-075 — ChatGPT recibe solo el runtime vigente
Fecha: 2026-08-25  
Scope: GLOBAL  
Contexto: la búsqueda del repositorio mezcló auditorías v1/v2 con el pipeline actual y ChatGPT citó roles retirados.  
Decisión anterior: el repositorio completo se utilizaba también como paquete de ejecución.  
Nueva decisión: el repositorio conserva la historia, pero ChatGPT Projects utiliza únicamente el ZIP generado por `tools/build_chatgpt_pack.py`.  
Motivo/evidencia: las instrucciones de prioridad no impiden que retrieval recupere documentos históricos semánticamente similares.  
Impacto: distribución limpia y verificable; sin cambios de agentes, gates o pipeline.  
Agentes/gates afectados: entrada global.  
Estado: ACTIVE  
Review-by: siguiente ejecución real en ChatGPT.

## Plantilla

```text
### D-XXX — Título
Fecha:
Scope: GLOBAL | PROJECT
Contexto:
Decisión anterior:
Nueva decisión:
Motivo/evidencia:
Impacto:
Agentes/gates afectados:
Estado: ACTIVE | REVERSED | SUPERSEDED
Review-by:
```
