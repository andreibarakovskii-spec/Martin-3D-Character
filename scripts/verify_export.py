"""Reimport GLB and render the exported mesh in the same studio."""
import bpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'build'
bpy.ops.wm.open_mainfile(filepath=str(out/'martin-prototype.blend'))
for obj in list(bpy.data.objects):
    if obj.type=='ARMATURE' or (obj.type=='MESH' and obj.name!='Plane'):
        bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'martin-prototype.glb'))
rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
assert rigs
for rig in rigs:
    if rig.animation_data:
        rig.animation_data.action=None
        for track in rig.animation_data.nla_tracks:track.mute=True
    for bone in rig.pose.bones:bone.matrix_basis.identity()
bpy.context.scene.frame_set(1)
bpy.context.scene.render.filepath=str(out/'exported-glb-render.png')
bpy.ops.render.render(write_still=True)
print('GLB_REIMPORT_RENDER_COMPLETE')
