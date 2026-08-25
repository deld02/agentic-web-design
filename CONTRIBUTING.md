# Contributing

## Antes de cambiar el core

1. Identifica owner y stage/gate afectados.
2. Registra por qué el cambio no debe quedarse `PROJECT_ONLY`.
3. Si altera pipeline, gates o state semantics, añade/actualiza un mutation test.
4. Si altera un agente, conserva el Agent Contract Standard.
5. No edites el audit generado a mano: ejecuta `tools/audit_agents.py`.

## Validación local

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_system.py
python tools/audit_agents.py
python -m unittest discover -s tests -v
```

Todos deben devolver exit code 0 y `git diff` no debe mostrar un audit generado desactualizado.

## Regla fail-closed

Si descubres un estado inválido que hoy pasa CI, primero añade un test que reproduzca el fallo; después corrige el validador. El test debe permanecer para evitar regresión.
