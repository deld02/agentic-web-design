# Craft polish capability

Use `quick` during iteration. `full` is mandatory once on the final integrated desktop/mobile renders before G4/G5 approval; record it as `TEXT_SPACING_CRAFT` in `qa-release.md`.

Inspect evidence, not vibes:

- typography wrapping, line length, per-family metrics, fallback shift and rendering;
- mixed-type headline roles, optical baseline/scale, preferred breaks and alternate responsive composition;
- spatial hierarchy (`section > group > component > inline`) and dead-space/compressed-cluster imbalance;
- optical alignment and icon/text weight;
- nested radii, borders, shadows and surface separation;
- semantic color roles, scene-mode continuity and deliberate transitions between high-expression and reading surfaces;
- rendered hero resolution: typographic voice, palette interchangeability, media/copy integration, mechanism salience and depth/rhythm/detail;
- hit areas, hover, active, focus and disabled states;
- interruptible state transitions and sensible transform origins;
- touch behavior, reduced motion and responsive edge cases;
- layout/paint cost of animated properties.

Return prioritized findings with exact location, current behavior, proposed change, reason, verification and owner. Preserve the selected identity and styling system. Do not introduce a paid font, new palette, component library or motion language during polish.

Do not accept nominal completeness. A second-column asset, offset shadow, mono label or generic reveal counts only when it contributes to the hero thesis; repeat the removal/swap countertest when the composition feels polished but interchangeable.

Write findings into `visual-system.md` or `qa-release.md`.

The final `full` pass inspects the entire scroll with loaded fonts and real copy. It cannot pass from tokens or source CSS alone. Name affected scenes and verify section breathing, paragraph measure/leading, mixed-family optical composition, wrapping and mobile recomposition. “Looks balanced” without rendered locations is not evidence.
