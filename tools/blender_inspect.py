"""Fixed Blender worker. Never execute submitted builders or embedded Python."""
import json
from pathlib import Path
import sys

import bpy

source, output = map(Path, sys.argv[sys.argv.index("--") + 1:])
if source.suffix == ".blend":
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
meshes = [{"name": obj.name, "vertices": len(obj.data.vertices)}
          for obj in bpy.data.objects if obj.type == "MESH"]
if not meshes or not any(item["vertices"] for item in meshes):
    raise ValueError("Model contains no mesh geometry")
output.write_text(json.dumps({"blender_version": bpy.app.version_string, "meshes": meshes}), encoding="utf-8")
