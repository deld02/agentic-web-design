"""Opt-in real Blender smoke test. No network, installs or API credentials."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def build(output: Path) -> None:
    import bpy
    from mathutils import Vector

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 8
    scene.render.resolution_x = 640
    scene.render.resolution_y = 480
    scene.render.resolution_percentage = 100
    material = bpy.data.materials.new("Copper")
    material.diffuse_color = (0.45, 0.16, 0.06, 1)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = material.diffuse_color
    shader.inputs["Metallic"].default_value = 0.7
    shader.inputs["Roughness"].default_value = 0.3
    for name, radius, depth, z in [("Base", .65, .12, .06), ("Stem", .065, 1.6, .9), ("Shade", .5, .18, 1.8)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=(0, 0, z))
        obj = bpy.context.object
        obj.name = name
        obj.data.materials.append(material)
        bevel = obj.modifiers.new("Edge bevel", "BEVEL")
        bevel.width = .035
        bevel.segments = 3
    bpy.ops.mesh.primitive_plane_add(size=200)
    bpy.context.object.name = "Ground"
    for position, energy, size in [((2, -3, 5), 1000, 4), ((-3, 1, 3), 700, 3)]:
        bpy.ops.object.light_add(type="AREA", location=position)
        light = bpy.context.object
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.rotation_euler = (Vector((0, 0, 1)) - light.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.camera_add(location=(3.5, -5, 3))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, .95)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.lens = 55
    scene.camera = camera
    scene.world = bpy.data.worlds.new("Studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.12, .12, .12, 1)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "sample.blend"), compress=False)
    scene.render.filepath = str(output / "preview.png")
    bpy.ops.render.render(write_still=True)
    bpy.ops.object.select_all(action="DESELECT")
    for name in ("Base", "Stem", "Shade"):
        bpy.data.objects[name].select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(output / "sample.glb"), export_format="GLB", use_selection=True)


def inspect(output: Path) -> None:
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(output / "sample.glb"))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    assert {"Base", "Stem", "Shade"}.issubset({obj.name for obj in meshes})
    assert all(len(obj.data.vertices) > 0 for obj in meshes)
    (output / "inspection.json").write_text(json.dumps({
        "blender_version": bpy.app.version_string,
        "command": subprocess.list2cmdline(sys.argv),
        "exit_code": 0, "fresh_import": True,
        "meshes": [{"name": obj.name, "vertices": len(obj.data.vertices)} for obj in meshes],
    }, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    executable = args.blender.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    script = output / "builder.py"
    shutil.copyfile(__file__, script)
    for mode in ("build", "inspect"):
        command = [str(executable), "--background", "--factory-startup", "--python-exit-code", "1", "--python", str(script), "--", mode, str(output)]
        result = subprocess.run(command, capture_output=True, timeout=180)
        (output / f"{mode}.log").write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(f"Blender {mode} failed: see {output / (mode + '.log')}")
    files = {}
    for role, name in {"scene": "sample.blend", "builder": "builder.py", "preview": "preview.png", "export": "sample.glb", "inspection": "inspection.json"}.items():
        data = (output / name).read_bytes()
        files[role] = {"path": name, "sha256": hashlib.sha256(data).hexdigest()}
    (output / "handoff.json").write_text(json.dumps({"assets": [{"fx_id": "FX-001", "files": files}]}, indent=2), encoding="utf-8")
    (output / "production-plan.md").write_text(
        "### 3D production provenance\n\n"
        "| FX ID | Medium | External source / authoring tool | Asset / runtime | License or rights | Integration proof | Fallback |\n"
        "|---|---|---|---|---|---|---|\n"
        "| FX-001 | INTERACTIVE_3D | Blender / CUSTOM | sample.glb | Original test | NOT_INTEGRATED_SMOKE_ONLY | preview.png |\n\n"
        "BLENDER_HANDOFF: handoff.json\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "scope": "Blender render/export/fresh-import only; import the four files through MCP and inspect_blender_asset for managed acceptance"}, indent=2))
    return 0


if __name__ == "__main__":
    if "--" in sys.argv:
        mode, directory = sys.argv[sys.argv.index("--") + 1:]
        {"build": build, "inspect": inspect}[mode](Path(directory))
    else:
        raise SystemExit(main())
