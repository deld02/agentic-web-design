# State Machine v4

Ruta normal: `PENDING → ACTIVE → REVIEW → APPROVED`.

También: `ACTIVE → BLOCKED`, `REVIEW → ACTIVE`, `APPROVED → REVIEW` y `APPROVED → SUPERSEDED`.

Solo 00 cambia estado. Cada stage declara `depends_on` y `entry_requires`; el DAG no autoriza avanzar si el estado semántico no lo permite.

Una respuesta de usuario puede aportar una restricción, preferencia o delegar la elección, pero nunca ejecuta por sí sola una transición. La delegación conserva `active_stage`; el owner decide con la evidencia disponible y continúa hacia el review ya definido.

Los checkpoints obligatorios protegidos son:

- G1: research strategy;
- G2: independent direction review;
- G3: independent design review;
- G4: production plan, technology selection y independent build review.

Dentro de G4 el orden no es paralelo ni opcional: `technology-selection` incluye el build estructural y sus renders; `production-plan` depende de ese checkpoint; `implementation` depende de ambos y realiza integración/finalización; `build-review` depende de `implementation`. `config/pipeline.json` es la autoridad ejecutable.

Los tres reviews de 07 siguen `docs/architecture/review-isolation.md`. Un checkpoint de review no puede quedar `APPROVED` si `review_context` no es `ISOLATED`.

Un cambio reabre solo decisiones dependientes. `release.eligible` se deriva de G0–G4 aprobados.

Cada stage admite una pasada inicial y una corrección automática. La repetición del mismo bloqueo, un segundo fallo de herramienta o quince minutos sin evidencia material terminan en `BLOCKED` conservando artefactos. La reanudación autorizada inicia una nueva ejecución acotada; no borra el historial.
