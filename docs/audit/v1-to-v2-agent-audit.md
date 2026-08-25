# Auditoría profunda v1 → v2

**Fecha:** 2026-08-19  
**Scope:** arquitectura, agentes, ownership, pipeline, gates, templates, state, CI y proyecto de ejemplo.

## Resumen ejecutivo

El v1 tenía una base buena, pero no estaba listo como “OS” estable. Encontré problemas estructurales que podían producir trabajo contradictorio incluso si cada agente obedecía su propio prompt:

1. **Dependencia circular 07↔08:** Motion exigía mobile constraints y Mobile exigía motion spec.
2. **Red Team en dos posiciones incompatibles:** pipeline pre-code, pero DRS/micro-loop lo situaban post-QA.
3. **Copy sin owner:** UX detectaba gaps y UI exigía contenido real, pero nadie poseía copy/claims.
4. **Gate self-approval ambiguo:** agentes emitían APROBADO aunque 00 era owner del estado.
5. **Accessibility/Performance demasiado tardío:** la documentación decía “desde el principio” pero el pipeline real lo ejecutaba al final.
6. **Factibilidad técnica demasiado tardía:** Frontend aparecía cuando el diseño ya estaba cerrado.
7. **Design System prematuro:** podía sobreconstruir componentes antes de saber qué UI real existía.
8. **DRS con nomenclatura legacy y orden distinto al registry.**
9. **DRS podía convertirse en cuello de botella:** 3 fuentes nuevas para cada repetición del mismo patrón.
10. **DRS no trataba provenance/licencias de código/assets.**
11. **Status insuficiente:** gates eran strings sin evidence, owner, reviewers o blockers.
12. **Validator superficial:** comprobaba existencia/IDs, pero no ciclos, modes, gate contracts, templates o inconsistencias de versión.
13. **Release incompleto:** no bloqueaba explícitamente copy provisional, Red Team de build o desviaciones.
14. **Extensiones sin protocolo:** SEO/CMS/analytics/etc. podían entrar de forma ad hoc e invadir ownership.

v2 corrige estos puntos sin renumerar las conversaciones 00–13. Se añade C01 y DRS sigue transversal.

---

## 00 · Orchestrator

### v1 — Bien
- ownership del estado claro;
- reapertura downstream ya contemplada;
- prohibición de diseñar por sustitución.

### Problemas
- “aprobar” podía confundirse con validar la disciplina;
- status no guardaba evidencia suficiente;
- escalado humano poco definido;
- no distinguía resultado de agente de estado del gate.

### v2 — Corrección
- agentes entregan `READY_FOR_GATE | REVISE | BLOCKED`;
- solo 00 cambia gate state;
- gate decision exige owner + evidencia + reviewers;
- reapertura por impacto, no reset global;
- release valida provisional content, deviations y build findings.

**Resultado:** sólido.

---

## 01 · Web Strategy

### v1 — Bien
- objetivo, audiencia, propuesta, conversión y scope correctamente separados del diseño.

### Problemas
- no obligaba a separar hecho/supuesto;
- una hipótesis podía colarse como fundamento;
- success signals no exigían aclarar cómo se medirían.

### v2 — Corrección
- `assumptions-register.md` obligatorio;
- facts/assumptions/unknowns separados;
- métricas vanity prohibidas;
- success signals deben ser observables sin inventar datos.

**Resultado:** ownership limpio.

---

## 02 · Design Research

### v1 — Bien
- diferencia research global de DRS concreto;
- anti-copia y anti-genericidad correctos.

### Problemas
- provenance/freshness poco estructurados;
- competidor, inspiración y evidencia técnica podían mezclarse;
- no existía obligación clara de declarar sample limitations.

### v2 — Corrección
- matriz de fuentes tipada;
- access date + observation + confidence;
- afirma tendencias solo con evidencia suficiente;
- technical claims priorizan fuente primaria.

**Resultado:** más verificable y menos “moodboard”.

---

## 03 · UX Architecture

### v1 — Bien
- sitemap, journeys, CTA y estructura estaban bien delimitados.

### Problema principal
- detectaba content gaps pero no existía owner posterior capaz de resolverlos.

### v2 — Corrección
- UX produce `content-requirements.md`;
- no escribe copy final;
- entrega formal a C01;
- añade error/empty/alternate flows cuando aplican.

**Resultado:** UX deja de invadir contenido y UI.

---

## C01 · Content & Conversion — NUEVO

### Por qué era necesario
Sin este agente, UI tenía dos opciones malas: inventar copy o bloquearse esperando contenido externo sin contrato.

### Ownership
- message hierarchy;
- copy/microcopy;
- claims register;
- status FINAL/PROVISIONAL/MISSING;
- length bounds para stress-test responsive.

### Protección
- no inventa autoridad;
- no cambia UX/strategy silenciosamente;
- no activa SEO por defecto.

**Resultado:** cierra un hueco crítico del v1.

---

## 04 · Art Direction

### v1 — Bien
- idea dominante, atmósfera, image rules, anti-rules;
- “premium ≠ minimalismo”.

### Problema
- Motion estaba mencionado como parte temprana, pero el sistema no distinguía intención de spec, alimentando el ciclo 07↔08.

### v2 — Corrección
- 04 define **motion intent**;
- 07 no cierra timing hasta recibir responsive constraints;
- DRS entra como reviewer formal de G5 para que el lenguaje visual nuevo no pueda cerrarse sin contraste.

**Resultado:** mantiene creatividad temprana sin romper dependencias.

---

## 05 · Design System

### v1 — Riesgo
Se ejecutaba una sola vez antes de UI. Esto podía producir un design system teórico demasiado grande o exigir que UI se adaptara a primitives aún no probados.

### v2 — Corrección
Dos modos:
- `foundation`: tokens/primitives suficientes para empezar;
- `stabilize`: después de UI/Mobile/Motion consolida patrones reales.

Si stabilization cambia fundamentos, 00 reabre G6.

**Resultado:** sistema vivo, no biblioteca inventada por anticipado.

---

## 06 · UI Design

### v1 — Problemas
- se llamaba “composición visual final” antes de mobile/motion;
- dependía de copy real sin owner;
- DRS podía obligar a research repetitivo incluso en primitives ya aprobados.

### v2 — Corrección
- produce high-fidelity composition, no “final absoluto”;
- recibe G4 content contract;
- crea storyboard de motion intent;
- DRS usa fresh/cached tiers;
- stress-test de copy explícito.

- `design/asset-manifest.md` pasa a ser output obligatorio y elimina un input huérfano de Frontend.

**Resultado:** handoff mucho más implementable.

---

## 08 · Responsive & Mobile

### v1 — Problema crítico
Input obligatorio: motion spec. Pero 07 exigía mobile constraints. Ciclo imposible de satisfacer de forma estricta.

### v2 — Corrección
- 08 se ejecuta antes de 07;
- recibe motion intent/storyboard, no spec final;
- produce constraints móviles para 07;
- breakpoints responden a contenido, no a nombres de dispositivos.

**Resultado:** ciclo eliminado.

---

## 07 · Motion Design

### v1 — Problema crítico
Dependía de mobile constraints antes de que Mobile pudiera cerrar.

### v2 — Corrección
- el intent nace en 04/06;
- 08 fija mobile/touch;
- 07 especifica timing/easing/triggers/cleanup/reduced motion después;
- no-JS y reduced motion preservan función.

**Resultado:** orden lógico y compatible con storyboard temprano.

---

## 09 · Frontend

### v1 — Problema
Entraba demasiado tarde. Podía descubrir una inviabilidad después de G9.

### v2 — Corrección
Dos modos:
- `feasibility`: checkpoint tras foundation y tras motion;
- `implementation`: código final G11.

Frontend no puede vetar por preferencia de stack; debe explicar tradeoff/risk.

**Resultado:** menos sorpresas tardías sin dar poder creativo al implementador.

---

## 10 · Visual QA

### v1 — Bien
Render real, repro steps y severidad estaban correctamente enfocados.

### Problemas
- cierre de issue no exigía explícitamente closure evidence;
- baseline/cambio intencional/regresión no estaban diferenciados.

### v2 — Corrección
- issue solo cierra con evidencia de retest;
- distingue regression / accepted deviation / intentional change;
- baseline se actualiza solo con decisión registrada.

**Resultado:** QA reproducible.

---

## 11 · Design Critic / Red Team

### v1 — Problema crítico
`WORKFLOW.md` lo colocaba antes de Frontend, mientras el micro-loop/DRS lo colocaba después de Visual QA. Ambas posiciones tienen valor, pero el sistema fingía que era una sola.

### v2 — Corrección
Dos modos:
- `design-review` → G10 pre-code;
- `build-review` → checkpoint post-QA, crítico bloquea G14.

**Resultado:** contradicción convertida en feature explícita.

---

## 12 · Accessibility & Performance

### v1 — Contradicción
README decía que formaba parte del diseño “desde el principio”, pero pipeline lo ejecutaba casi al final.

### v2 — Corrección
- `design-advisory` tras G6 y G9;
- `production-audit` en G13;
- thresholds externos se guardan en documento fechado;
- no confunde automated scan con conformidad completa;
- distingue lab vs field data.

**Resultado:** shift-left real.

---

## 13 · Design Intelligence

### v1 — Bien
Evita convertir preferencias en reglas universales.

### Problema
No había política suficiente para promoción/deprecation.

### v2 — Corrección
- `PROJECT_ONLY | CANDIDATE | GLOBAL_PROPOSAL`;
- scope/confidence/evidence/review-by obligatorios;
- recurrencia entre proyectos o estándar fuerte antes de globalizar;
- deprecation, no borrado.

**Resultado:** aprendizaje controlado.

---

## DRS · Design Resource Scout

### v1 — Problemas
- conservaba roles legacy no registrados;
- su “loop” contradecía el pipeline del Red Team;
- 3 fuentes nuevas para cada decisión podía ser un cuello de botella;
- no había cache formal;
- no trataba licencia/provenance;
- source taxonomy técnica insuficiente.

### v2 — Corrección
- transversal puro y callers definidos en config;
- `fresh-research` vs `cached-contrast`;
- 3+ fuentes independientes en patrón nuevo/alto impacto;
- technical claims → fuente primaria cuando aplica;
- license/provenance como hard blocker cuando se reutiliza código/asset;
- no obliga a investigar primitives ya cubiertos sin razón nueva.

**Resultado:** mantiene el nivel de contraste sin convertir el OS en una máquina de research redundante.

---

# Auditoría transversal

## Ownership

No quedan gaps core importantes entre Strategy → UX → Content → Art → System → UI → Responsive → Motion → Frontend.

## Dependencias

`config/pipeline.json` es un DAG validado. 25 stages, 0 ciclos.

## Gates

15 gates G0–G14. Cada gate tiene owner, reviewers y required artifacts. Un formal stage por gate.

## State

`status.json` v2 guarda owner, reviewers, evidence, blockers y last decision por gate.

## Release

G14 bloquea por:
- gate anterior no aprobado;
- content missing/provisional no aceptado;
- critical build Red Team;
- QA severo;
- deviation no registrada;
- riesgo no aceptado;
- extension required incompleta.

## CI

Valida configs, DAG, modes, agent contract headings, project skeleton, status consistency, version sync y términos legacy. También regenera el contract audit y falla si el repo no está sincronizado.

## Límites que siguen siendo deliberados

El core **no finge cubrir todo tipo de web**. SEO, CMS/Divi, analytics, privacy/legal, ecommerce, localization y media production son extensions. Esto evita que el Orchestrator acabe con 30 agentes permanentes en cada proyecto.

# Veredicto

v1 era una buena especificación conceptual. v2 ya está estructurado como un sistema operativo agéntico mantenible: contracts + state + DAG + gates + evidence + controlled extensions.
