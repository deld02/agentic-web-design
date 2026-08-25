# Learned Rules

Toda regla debe mantener `Scope`, `Confidence`, `Evidence` y `Review-by`.

## LR-001 — Mobile necesita composición propia
**Scope:** GLOBAL  
**Confidence:** HIGH  
**Evidence:** errores repetidos de clipping/jerarquía en composiciones desktop reducidas  
**Review-by:** 2027-02-19  
**Regla:** no aprobar una experiencia móvil que sea solo escalado/reflujo del desktop cuando jerarquía, asset principal o interacción requieran recomposición.

## LR-002 — Motion intent temprano, spec tras responsive
**Scope:** GLOBAL  
**Confidence:** HIGH  
**Evidence:** auditoría v1→v2 detectó dependencia circular Motion↔Mobile  
**Review-by:** 2027-02-19  
**Regla:** Art/UI definen motion intent/storyboard; Responsive fija constraints; Motion cierra timing, triggers, cleanup y reduced-motion después.

## LR-003 — No usar minimalismo como sustituto de dirección
**Scope:** GLOBAL  
**Confidence:** HIGH  
**Evidence:** decisiones globales D-001/D-002  
**Review-by:** 2027-02-19

## LR-004 — QA y Red Team no rediseñan
**Scope:** GLOBAL  
**Confidence:** HIGH  
**Evidence:** ownership contract del OS  
**Review-by:** 2027-02-19  
**Regla:** evidencian, clasifican y devuelven el finding al owner.
