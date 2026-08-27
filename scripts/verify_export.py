"""Reimport GLB and render the exported mesh in the same studio."""
import bpy
from pathlib import Path
from mathutils import Vector
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
keyed=[o for o in bpy.data.objects if o.type=='MESH' and o.data.shape_keys]
for obj in keyed:
    keys=obj.data.shape_keys
    if keys.animation_data:
        keys.animation_data.action=None
        for track in keys.animation_data.nla_tracks:track.mute=True
    for key in list(keys.key_blocks)[1:]:key.value=0
bpy.context.scene.frame_set(1)
bpy.context.scene.render.filepath=str(out/'exported-glb-render.png')
bpy.ops.render.render(write_still=True)
scene=bpy.context.scene
scene.camera.location=(.85,-6,2.05)
scene.camera.rotation_euler=(Vector((0,-.08,1.80))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale=1.30
scene.render.resolution_x=700;scene.render.resolution_y=700;scene.cycles.samples=48
scene.render.filepath=str(out/'face-neutral.png');bpy.ops.render.render(write_still=True)
seen=set()
for obj in keyed:
    for key in list(obj.data.shape_keys.key_blocks)[1:]:
        if key.name in ('Blink.L','Blink.R','Smile'):
            key.value=1;seen.add(key.name)
assert seen=={'Blink.L','Blink.R','Smile'}, seen
bpy.context.view_layer.update()
scene.render.filepath=str(out/'face-blink-smile.png');bpy.ops.render.render(write_still=True)
print('GLB_REIMPORT_RENDER_COMPLETE')
