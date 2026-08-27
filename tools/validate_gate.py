#!/usr/bin/env python3
"""Preflight one project gate before 00 changes its state."""

from __future__ import annotations

from pathlib import Path
import argparse
import re
import sys

from project_validation import (
    ROOT,
    artistic_master_errors,
    image_handoff_errors,
    claim_errors,
    color_direction_errors,
    context_compiler_errors,
    design_fingerprint_errors,
    direction_divergence_errors,
    scene_color_map_errors,
    creative_master_errors,
    creative_master_confirmation_errors,
    creative_master_fidelity_errors,
    explicit_text_only,
    experience_spine_errors,
    final_render_errors,
    final_delivery_contract_errors,
    visual_narrative_review_errors,
    hero_stress_errors,
    load_json,
    markdown,
    nonempty_section,
    review_checkpoint_errors,
    reference_benchmark_errors,
    page_rhythm_errors,
    project_quality_bar_errors,
    scene_visual_errors,
    scene_outline,
    scene_grammar_errors,
    scene_strategy_errors,
    structure_challenge_errors,
    section,
    table_rows,
    technology_freshness_errors,
)
from validate_delivery import validate_delivery
from validation_project_paths import implementation_root_for
from validation_release_integrity import (
    content_lock_build_errors,
    content_lock_definition_errors,
    integrity_manifest_errors,
    runtime_traversal_errors,
)


def require_sections(errors: list[str], text: str, gate: str, headings: tuple[str, ...]) -> None:
    for heading in headings:
        if not nonempty_section(text, heading):
            errors.append(f"{gate} missing substantive content under {heading}")


def validate_gate(project_dir: Path, gate_id: str) -> list[str]:
    errors: list[str] = []
    gates = {item["id"]: item for item in load_json(ROOT / "config" / "gates.json")["gates"]}
    if gate_id not in gates:
        return [f"unknown gate {gate_id}"]
    gate = gates[gate_id]
    for name in gate["required_artifacts"]:
        if not (project_dir / name).is_file():
            errors.append(f"{gate_id} missing required artifact {name}")
    if errors:
        return errors

    config = load_json(project_dir / "project.config.json")
    status = load_json(project_dir / "status.json")
    errors.extend(review_checkpoint_errors(status))

    if gate_id == "G0":
        brief = markdown(project_dir, "brief.md")
        require_sections(errors, brief, "G0", (
            "## Intake summary", "## Objective, audience and primary action",
            "## Project type and provisional scope",
        ))
        if config.get("project_type") == "undetermined":
            errors.append("G0 project_type is undetermined")

    elif gate_id == "G1":
        research = markdown(project_dir, "research-strategy.md")
        content = markdown(project_dir, "content-architecture.md")
        require_sections(errors, research, "G1", (
            "## Facts, assumptions and preferences", "## Desired perception and anti-attributes",
            "## Opportunity, risks and open questions",
        ))
        require_sections(errors, content, "G1", (
            "## Primary journey and CTA", "## Sitemap / page or section outline",
            "## Content and copy", "## Media requirements",
        ))
        if len(table_rows(content, "## Narrative alternatives and decision evidence", "Candidate")) < 2:
            errors.append("G1 requires at least two narrative alternatives")
        errors.extend(claim_errors(project_dir))
        errors.extend(reference_benchmark_errors(project_dir))
        errors.extend(context_compiler_errors(project_dir))
        errors.extend(structure_challenge_errors(project_dir))
        _primary_scenes, outline_errors = scene_outline(project_dir)
        errors.extend(outline_errors)
        errors.extend(experience_spine_errors(project_dir))
        errors.extend(content_lock_definition_errors(project_dir))

    elif gate_id == "G2":
        text = markdown(project_dir, "creative-direction.md")
        divergence_checkpoint = status.get("checkpoints", {}).get("direction-divergence", {})
        direction_checkpoint = status.get("checkpoints", {}).get("direction-review", {})
        if divergence_checkpoint.get("status") != "APPROVED":
            errors.append("G2 requires approved direction-divergence checkpoint")
        if direction_checkpoint.get("status") != "APPROVED" or direction_checkpoint.get("review_context") != "ISOLATED":
            errors.append("G2 requires approved isolated direction-review checkpoint")
        require_sections(errors, text, "G2", ("## Project-specific quality bar", "## Artistic master", "## Creative master handoff"))
        errors.extend(project_quality_bar_errors(project_dir))
        errors.extend(direction_divergence_errors(project_dir))
        errors.extend(artistic_master_errors(project_dir))
        errors.extend(creative_master_confirmation_errors(project_dir))
        errors.extend(creative_master_errors(project_dir))

    elif gate_id == "G3":
        text = markdown(project_dir, "visual-system.md")
        if len(table_rows(text, "## Foundation alternatives and decision evidence", "Candidate system")) < 2 \
                and "ONLY_VIABLE:" not in section(text, "## Foundation alternatives and decision evidence"):
            errors.append("G3 requires two visual foundations or an evidenced ONLY_VIABLE exception")
        if not table_rows(text, "### Content-driven breakpoint evidence", "Range tested"):
            errors.append("G3 requires responsive failure/recomposition evidence")
        if not explicit_text_only(text) and not table_rows(text, "### Scene visual opportunities", "Scene"):
            errors.append("G3 requires visual payload integration on desktop and mobile")
        fx_rows = table_rows(text, "### Effect opportunity map", "Scene / opportunity")
        if not any(len(row) >= 6 and row[3] and row[4] and row[5] for row in fx_rows):
            errors.append("G3 requires a tested creative mechanism with responsive and reduced-motion behavior")
        errors.extend(hero_stress_errors(project_dir))
        errors.extend(creative_master_fidelity_errors(project_dir))
        errors.extend(color_direction_errors(project_dir))
        errors.extend(scene_color_map_errors(project_dir))
        errors.extend(scene_strategy_errors(project_dir))
        errors.extend(scene_grammar_errors(project_dir))
        errors.extend(scene_visual_errors(project_dir, config.get("delivery_profile", "focused")))
        errors.extend(page_rhythm_errors(project_dir))

    elif gate_id == "G4":
        production = markdown(project_dir, "production-plan.md")
        technology = markdown(project_dir, "technology-decision.md")
        final_assets = [
            row for row in table_rows(production, "## Asset inventory and readiness", "ID")
            if len(row) >= 6 and re.fullmatch(r"IMG-[0-9]{3,}", row[0]) and row[3].startswith("PRIMARY:") and row[4] == "FINAL" and row[5]
        ]
        if not explicit_text_only(production) and not final_assets:
            errors.append("G4 requires at least one scene-bearing PRIMARY FINAL IMG asset")
        errors.extend(image_handoff_errors(project_dir))
        errors.extend(final_render_errors(project_dir))
        errors.extend(visual_narrative_review_errors(project_dir))
        fx_rows = table_rows(production, "### Material effect decisions", "Effect ID / scene")
        if not any(len(row) >= 10 and row[6] and row[8] and row[9] in {"FINAL", "STATIC_WINNER_REVIEWED"} for row in fx_rows):
            errors.append("G4 requires a final creative mechanism or evidenced static winner")
        tech_rows = [row for row in table_rows(technology, "## Options compared", "Option") if len(row) >= 4 and all(row[:4])]
        if len(tech_rows) < 2:
            errors.append("G4 technology decision must compare at least two viable options")
        errors.extend(technology_freshness_errors())
        errors.extend(claim_errors(project_dir))
        if config.get("implementation_root") in {None, "", "undetermined"}:
            errors.append("G4 implementation_root is undetermined")
        else:
            implementation_root = implementation_root_for(project_dir, ROOT, config["implementation_root"])
            delivery_errors, _ = validate_delivery(project_dir, implementation_root)
            errors.extend(f"G4 delivery proof: {error}" for error in delivery_errors)
            errors.extend(content_lock_build_errors(project_dir, implementation_root))
            errors.extend(runtime_traversal_errors(project_dir, implementation_root))
            errors.extend(integrity_manifest_errors(project_dir, implementation_root))

    elif gate_id == "G5":
        qa = markdown(project_dir, "qa-release.md")
        baseline = table_rows(qa, "## Release evidence status", "Area")
        if len(baseline) < 8 or any(len(row) < 3 or row[1] not in {"COMPLETE", "NOT_APPLICABLE", "ACCEPTED_RISK"} for row in baseline):
            errors.append("G5 release evidence baseline is incomplete")
        if any(row[1] in {"NOT_APPLICABLE", "ACCEPTED_RISK"} and not row[2] for row in baseline if len(row) >= 3):
            errors.append("G5 exceptions require rationale and owner")
        if status.get("release", {}).get("eligible") is not True:
            errors.append("G5 release is not eligible")
        errors.extend(claim_errors(project_dir))
        implementation_root = implementation_root_for(project_dir, ROOT, config.get("implementation_root", "undetermined"))
        delivery_errors, _ = validate_delivery(project_dir, implementation_root)
        errors.extend(f"G5 delivery proof: {error}" for error in delivery_errors)
        errors.extend(final_render_errors(project_dir))
        errors.extend(visual_narrative_review_errors(project_dir))
        errors.extend(design_fingerprint_errors(project_dir))
        errors.extend(final_delivery_contract_errors(qa, ROOT, implementation_root))
        errors.extend(content_lock_build_errors(project_dir, implementation_root))
        errors.extend(runtime_traversal_errors(project_dir, implementation_root))
        errors.extend(integrity_manifest_errors(project_dir, implementation_root))

    return errors


def project_dirs(value: str | None, all_projects: bool) -> list[Path]:
    if all_projects:
        return sorted(path.parent for path in (ROOT / "projects").glob("*/status.json"))
    if not value:
        raise SystemExit("Provide --project-dir or --all-projects")
    path = Path(value).resolve()
    if not path.is_dir():
        raise SystemExit(f"Project directory does not exist: {path}")
    return [path]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gate", nargs="?", choices=[f"G{i}" for i in range(6)])
    parser.add_argument("--project-dir")
    parser.add_argument("--all-projects", action="store_true")
    parser.add_argument("--approved-only", action="store_true")
    args = parser.parse_args()
    failures: list[str] = []
    for project_dir in project_dirs(args.project_dir, args.all_projects):
        status = load_json(project_dir / "status.json")
        gate_ids = [args.gate] if args.gate else [f"G{i}" for i in range(6)]
        for gate_id in gate_ids:
            if args.approved_only and status["gates"][gate_id]["status"] != "APPROVED":
                continue
            for error in validate_gate(project_dir, gate_id):
                failures.append(f"{project_dir.name}:{error}")
    if failures:
        print("GATE VALIDATION FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("OK — requested project gates satisfy deterministic preflight checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
