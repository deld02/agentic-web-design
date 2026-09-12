# Learned Rules

Toda regla debe mantener `Scope`, `Confidence`, `Evidence` y `Review-by`.

Las entradas sin un caso reproducible enlazado son heurísticas de trabajo, no
resultados experimentales del sistema. Una política de ownership tampoco prueba
calidad estética. No usar estas entradas para declarar una landing premium.

## LR-001 — Mobile necesita composición propia
**Scope:** GLOBAL  
**Confidence:** HEURISTIC — pendiente de calibración con casos enlazados
**Evidence:** problemas de clipping/jerarquía comunicados; sin run y renders reproducibles enlazados aquí
**Review-by:** 2027-02-19  
**Regla:** no aprobar una experiencia móvil que sea solo escalado/reflujo del desktop cuando jerarquía, asset principal o interacción requieran recomposición.

## LR-002 — Motion intent temprano, spec tras responsive
**Scope:** GLOBAL  
**Confidence:** HEURISTIC — pendiente de evidencia reproducible
**Evidence:** atribuido a auditoría v1→v2; sin informe verificable enlazado aquí
**Review-by:** 2027-02-19  
**Regla:** Art/UI definen motion intent/storyboard; Responsive fija constraints; Motion cierra timing, triggers, cleanup y reduced-motion después.

## LR-003 — No usar minimalismo como sustituto de dirección
**Scope:** GLOBAL  
**Confidence:** HEURISTIC — criterio creativo, no resultado medido
**Evidence:** decisiones globales D-001/D-002 citadas históricamente; sin comparación de renders enlazada aquí
**Review-by:** 2027-02-19

## LR-004 — QA y Red Team no rediseñan
**Scope:** GLOBAL  
**Confidence:** HIGH  
**Evidence:** política explícita en `AGENTS.md` y `docs/architecture/review-isolation.md`, no evidencia de resultados visuales
**Review-by:** 2027-02-19  
**Regla:** evidencian, clasifican y devuelven el finding al owner.
