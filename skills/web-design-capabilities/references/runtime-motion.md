# GSAP runtime implementation

Activate only when 06 has already selected GSAP as the simplest faithful runtime for an approved `FX-*`. GSAP does not decide that motion should exist.

Load only the installed official skills relevant to the implementation:

- `gsap-core` and `gsap-timeline` for sequencing;
- `gsap-scrolltrigger` for scroll-linked behavior;
- `gsap-react` or `gsap-frameworks` for lifecycle integration;
- `gsap-plugins` and `gsap-utils` only when the selected mechanism requires them;
- `gsap-performance` before build review.

06 must implement scoped selectors, cleanup, responsive `matchMedia` behavior, refresh after layout/media changes, transform/opacity-first animation, reduced-motion fallback and static continuity. 07 verifies behavior and performance from the executable landing.
