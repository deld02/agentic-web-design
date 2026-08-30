# Agents — ownership registry

| ID | Role | Owns |
|---|---|---|
| 00 | Orchestrator & Design Director | active-stage routing, project definition, state, gates and release |
| 01 | Strategy & Research | evidence, context, brand/category research and strategy |
| 02 | UX & Content | landing flow, hierarchy, copy and claims |
| 03 | Art Direction | divergent visual territories, selected generated artistic master and design genome |
| 04 | Visual & UI Design | typography, color, composition, responsive UI and visual system |
| 05 | Motion & Media | render audit, per-scene image decisions, external-production handoff, returned-media validation, effects and fallbacks |
| 06 | Frontend | technology, structural build, integration and final implementation |
| 07 | Critic & QA | independent rendered review and release findings |

## Operating rules

- Follow `config/pipeline.json` exactly. Only 00 writes official state.
- In managed chat execution, 00 is embodied by the harness: it supplies one complete specialist packet, owns `status.json`, validates the result and opens exactly one successor. Specialists never edit official state.
- The active owner decides and edits its artifact. A reviewer reports evidence and findings; it does not silently fix or redesign another owner's work.
- Use the active contract in `agents/` and only the method it links. Do not load every method or repeat global rules in project artifacts.
- Technology is selected for the project and always includes the simplest viable option in the comparison.
- G4 is sequential: technology plus structural build → image decisions and external-production handoff/return → integration → independent build review.
- The system ends at a verified landing. Work outside landing creation remains out of scope.
