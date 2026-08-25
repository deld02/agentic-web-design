# Uso con conversaciones/agentes — v4.5

## Activación obligatoria

Los archivos de referencia no sustituyen instrucciones de ejecución. En ChatGPT Projects, pega `CHATGPT-PROJECT-INSTRUCTIONS.md` en Project settings. En un runtime compatible con skills, activa `skills/agentic-web-design/SKILL.md`. Después carga únicamente el contrato del role activo.

No es necesario abrir ocho conversaciones. Carga únicamente el contrato del role activo junto a `SYSTEM.md`, configs, artefactos del proyecto y handoff vigente.

Secuencia habitual:

1. 00 define.
2. 01 investiga.
3. 02 estructura contenido y UX.
4. 03 explora direcciones; 07 revisa en contexto independiente.
5. 04 diseña la experiencia; 07 revisa.
6. 05 prepara motion/media y 06 selecciona tecnología en una wave proporcional.
7. 06 implementa; 07 prueba la build.
8. 00 libera.

Toda decisión material vuelve a uno de los 12 artefactos core. Las herramientas concretas se eligen por la evidencia que deben producir. Antes de afirmar que la landing está terminada, registra `implementation_root` y ejecuta `tools/validate_delivery.py`; si no puede ejecutarse o falla, el resultado es `REVISE | BLOCKED`.

El System Steward no se carga en conversaciones de proyecto. Se activa por release/cadencia para auditar el OS completo.

Cuando una fase usa capacidades de diseño, carga primero `skills/web-design-capabilities/SKILL.md` y después solo la referencia que su router indica. Registra uso y decisiones bajo `## Design capability log`; no copies la skill externa completa al contexto.
