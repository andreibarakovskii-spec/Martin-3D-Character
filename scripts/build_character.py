"""Reproducible, dependency-free Blender prototype. Not a final likeness."""
import bpy
import math
import random
import bisect
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parents[1] / 'build'
OUT.mkdir(exist_ok=True)
random.seed(27)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
parts = []


def material(name, color, roughness=.65, metallic=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    return m


fur = material('Coat_vertex_color', (.08, .075, .065))
v = fur.node_tree.nodes.new('ShaderNodeVertexColor')
v.layer_name = 'Coat'
fur.node_tree.links.new(v.outputs['Color'], fur.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
black = material('Hoodie_charcoal', (.018, .02, .023), .92)
rubber = material('Warm_white_rubber', (.7, .68, .61), .8)
shoe = material('Shoe_canvas', (.012, .014, .018), .85)
gold = material('Muted_gold', (.55, .33, .09), .31, .75)
eye = material('Eyes_dark_gloss', (.006, .008, .006), .12)
iris = material('Iris_olive_gold', (.4, .37, .1), .25)
nosemat = material('Nose_rose_brown', (.24, .10, .075), .5)
inner = material('Inner_ear', (.22, .145, .12), .9)
whisker = material('Whiskers', (.55, .53, .47), .65)


def finish(obj, mat, bone):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    parts.append((obj, bone))
    return obj


def sphere(name, location, scale, mat, bone='spine', segments=40, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, mat, bone)


def tube(name, points, radius, mat, bone='spine'):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 6
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    curve.use_fill_caps = True
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for p, co in zip(spline.bezier_points, points):
        p.co = co
        p.handle_left_type = p.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    return finish(bpy.context.object, mat, bone)


def coat(obj, light=False):
    # Exportable vertex color: same material in Blender and GLB, no hidden shader dependency.
    attr = obj.data.color_attributes.new(name='Coat', type='FLOAT_COLOR', domain='POINT')
    for i, vert in enumerate(obj.data.vertices):
        x,y,z = obj.matrix_world @ vert.co
        stripe = max(0, math.cos(z*24 + 2*math.sin(x*10) + y*7))**8
        if z > 1.6:
            stripe = max(0, math.cos(x*31 + 2*math.sin(z*9) + y*6))**10
        muzzle_mask = max(0.0, 1.0-abs(x)/.24)*max(0.0,1.0-abs(z-1.59)/.13) if y < -.30 else 0
        base = .16 if light else .075+.085*muzzle_mask
        tone = base - (.025 if light else .046)*stripe + random.uniform(-.004,.004)
        attr.data[i].color = (tone, tone*.90, tone*.78, 1)


# Front is -Y, Z is up. Height approximately 2.2 m in authoring coordinates.
body = sphere('Hoodie_body', (0,0,.98), (.39,.255,.46), black)
sphere('Hoodie_hem', (0,-.002,.62), (.39,.255,.085), black)
# The collar and fabric volumes are explicit mesh, not a backdrop.
sphere('Hood_fold_back', (0,.16,1.39), (.34,.16,.18), black)
mesh=bpy.data.meshes.new('Pocket_panel')
mesh.from_pydata([(-.25,-.233,.75),(.25,-.233,.75),(.25,-.26,.88),(.14,-.269,.97),(-.14,-.269,.97),(-.25,-.26,.88)],[],[(0,1,2,3,4,5)])
obj=bpy.data.objects.new('Pocket',mesh);bpy.context.collection.objects.link(obj)
finish(obj,black,'spine')
mod=obj.modifiers.new('Fabric_thickness','SOLIDIFY');mod.thickness=.012
bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
tube('Pocket_stitch',[(-.245,-.25,.755),(0,-.266,.752),(.245,-.25,.755)],.003,shoe)

for s in [-1,1]:
    side = 'L' if s > 0 else 'R'
    leg = sphere('Leg_'+side, (s*.19,0,.40), (.155,.155,.32), fur, 'leg.'+side)
    coat(leg)
    sphere('Sole_'+side, (s*.19,-.09,.07),(.18,.255,.065), rubber, 'leg.'+side)
    sphere('Shoe_'+side, (s*.19,-.085,.145), (.17,.24,.105), shoe, 'leg.'+side)
    sphere('Toe_cap_'+side, (s*.19,-.263,.14), (.16,.085,.073), rubber, 'leg.'+side)
    for j in range(4):
        yy = -.20+j*.043
        tube('Lace_'+side+str(j), [(s*.19-.065,yy,.22),(s*.19,yy-.015,.238),(s*.19+.065,yy,.22)], .008, rubber, 'leg.'+side)
    arm = sphere('Sleeve_'+side, (s*.405,0,1.055), (.145,.19,.32), black, 'arm.'+side)
    arm.rotation_euler.y = s*.20
    sphere('Cuff_'+side, (s*.46,-.04,.805), (.135,.16,.075), black, 'arm.'+side)
    paw = sphere('Paw_'+side, (s*.46,-.05,.715), (.12,.135,.13), fur, 'arm.'+side)
    coat(paw)
    for j in range(3):
        toe = sphere('Paw_digit_'+side+str(j), (s*.46+(j-1)*.05,-.151,.695), (.035,.036,.055), fur, 'arm.'+side, 20,12)
        coat(toe)
    tube('Drawstring_'+side, [(s*.10,-.235,1.43),(s*.105,-.29,1.25),(s*.12,-.30,1.16)], .012, black)

head = sphere('Head', (0,-.02,1.77), (.46,.33,.345), fur, 'head', 64,40)
coat(head)
for s in [-1,1]:
    cheek = sphere('Cheek', (s*.215,-.195,1.64), (.22,.15,.15), fur,'head')
    coat(cheek)
    muzzle = sphere('Muzzle', (s*.095,-.326,1.60), (.13,.08,.075),fur,'head')
    coat(muzzle,True)
    # Rounded triangular ear with thickness, subdivided before export.
    verts=[(s*.19,-.05,1.99),(s*.40,-.02,1.98),(s*.35,-.015,2.28),(s*.19,.075,1.99),(s*.40,.08,1.98),(s*.35,.06,2.28)]
    mesh=bpy.data.meshes.new('Ear_mesh')
    mesh.from_pydata(verts,[],[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)])
    obj=bpy.data.objects.new('Ear',mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Soft_ear','BEVEL'); mod.width=.045; mod.segments=3
    bpy.ops.object.modifier_apply(modifier=mod.name)
    finish(obj,fur,'head'); coat(obj)
    patch=sphere('Ear_inner',(s*.315,-.047,2.10),(.046,.012,.085),inner,'head')
    patch.rotation_euler.y=s*.23
    sphere('Eye_globe',(s*.177,-.302,1.805),(.111,.105,.114),eye,'head')
    sphere('Eye_iris',(s*.177,-.402,1.805),(.086,.018,.088),iris,'head')
    sphere('Pupil',(s*.177,-.419,1.809),(.063,.013,.068),eye,'head')
    # Highlights come from actual scene lights, not white painted spots.
    for j in range(4):
        tube('Whisker',[(s*.13,-.391,1.60+j*.018),(s*.32,-.41,1.60+j*.035),(s*(.52+j*.022),-.37,1.57+j*.053)],.0023,whisker,'head')
sphere('Nose',(0,-.423,1.656),(.059,.035,.035),nosemat,'head')
tube('Philtrum',[(0,-.421,1.63),(0,-.422,1.586)],.006,nosemat,'head')
chin=sphere('Jaw',(0,-.305,1.51),(.13,.07,.055),fur,'jaw');coat(chin,True)
tube('Smile',[(-.098,-.381,1.558),(0,-.402,1.54),(.098,-.381,1.558)],.006,nosemat,'jaw')

tail=tube('Tail',[(0,.20,.63),(.19,.36,.45),(.45,.34,.48),(.62,.25,.70),(.62,.15,.86)],.068,fur,'tail')
coat(tail)
tip=sphere('Tail_tip',(.62,.15,.86),(.068,.068,.068),fur,'tail',24,16);coat(tip)
# Headphones around collar, each cup is modeled with separate padded and metal parts.
for s in [-1,1]:
    sphere('Headphone_pad',(s*.28,-.18,1.40),(.096,.083,.145),shoe)
    sphere('Headphone_gold',(s*.31,-.23,1.40),(.082,.037,.12),gold)
    sphere('Headphone_shell',(s*.31,-.26,1.40),(.067,.022,.103),shoe)
tube('Headphone_band',[(-.28,.025,1.43),(0,.14,1.54),(.28,.025,1.43)],.025,shoe)
# Logo and lettering are real geometry facing front.
def text_mesh(text,location,size):
    bpy.ops.object.text_add(location=location,rotation=(math.pi/2,0,0))
    obj=bpy.context.object;obj.name='Logo_'+text
    obj.data.body=text;obj.data.align_x='CENTER';obj.data.size=size;obj.data.extrude=.001
    bpy.ops.object.convert(target='MESH');finish(bpy.context.object,gold,'spine')
text_mesh('M',(0,-.265,1.14),.18)
text_mesh('MARTIN',(0,-.277,.99),.072)
# Mic can be moved independently with right arm.
tube('Microphone_handle',[(-.46,-.22,.71),(-.46,-.22,1.03)],.029,shoe,'arm.R')
sphere('Microphone_grille',(-.46,-.22,1.07),(.064,.064,.087),shoe,'arm.R')

# Continuous facial surface: weld overlapping masses, smooth, and cut eye sockets.
facial=[o for o,b in parts if o.name=='Head' or o.name.startswith(('Cheek','Muzzle'))]
parts[:]=[(o,b) for o,b in parts if o not in facial]
bpy.ops.object.select_all(action='DESELECT')
for o in facial:o.select_set(True)
bpy.context.view_layer.objects.active=head
bpy.ops.object.join()
remesh=head.modifiers.new('Unified_face','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.009
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth=head.modifiers.new('Sculpt_transitions','SMOOTH');smooth.factor=1.1;smooth.iterations=6
bpy.ops.object.modifier_apply(modifier=smooth.name)
for side in [-1,1]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=(side*.177,-.302,1.805))
    cutter=bpy.context.object;cutter.scale=(.118,.114,.123)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=head
    mod=head.modifiers.new('Recessed_eye','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
for attr in list(head.data.color_attributes):head.data.color_attributes.remove(attr)
finish(head,fur,'head');coat(head)
bpy.context.view_layer.update()

# Surface-area distributed tapered strands: same geometry in source and exported GLB.
# Density is capped for mobile iteration; not a final fur-card groom.
for source,bone in list(parts):
    if not source.data.materials or source.data.materials[0]!=fur:continue
    source.data.calc_loop_triangles()
    tris=list(source.data.loop_triangles);cdf=[];total=0
    for tri in tris:
        total+=tri.area;cdf.append(total)
    if total==0:continue
    count=min(18000,max(150,int(total*13500)))
    verts=[];faces=[];colors=[]
    for unused in range(count):
        tri=tris[min(len(tris)-1,bisect.bisect_left(cdf,random.random()*total))]
        ids=tri.vertices;u=math.sqrt(random.random());v=random.random();weights=(1-u,u*(1-v),u*v)
        local=sum((source.data.vertices[i].co*w for i,w in zip(ids,weights)),Vector())
        p=source.matrix_world@local
        n=sum((source.data.vertices[i].normal*w for i,w in zip(ids,weights)),Vector())
        n=(source.matrix_world.to_3x3()@n).normalized()
        tangent=n.cross(Vector((0,0,1)))
        if tangent.length<.01:tangent=n.cross(Vector((0,1,0)))
        tangent.normalize()
        flow=Vector((p.x*.2,0,-1));flow-=n*flow.dot(n)
        if flow.length:flow.normalize()
        length=random.uniform(.009,.019);width=random.uniform(.00045,.0008)
        mid=p+n*(length*.48)+flow*(length*.20)
        tip=p+n*(length*.78)+flow*(length*.65)
        k=len(verts)
        verts.extend([p-tangent*width,p+tangent*width,mid-tangent*width*.55,mid+tangent*width*.55,tip])
        faces.extend([(k,k+1,k+2),(k+1,k+3,k+2),(k+2,k+3,k+4)])
        col=tuple(sum(source.data.color_attributes['Coat'].data[i].color[c]*w for i,w in zip(ids,weights)) for c in range(4))
        colors.extend([col]*5)
    mesh=bpy.data.meshes.new(source.name+'_fur');mesh.from_pydata(verts,[],faces)
    obj=bpy.data.objects.new(source.name+'_fur',mesh);bpy.context.collection.objects.link(obj)
    finish(obj,fur,bone)
    attr=mesh.color_attributes.new(name='Coat',type='FLOAT_COLOR',domain='POINT')
    for d,col in zip(attr.data,colors):d.color=col

# Armature with deliberately simple rigid prototype skin weights.
bpy.ops.object.select_all(action='DESELECT')
arm_data=bpy.data.armatures.new('Martin_skeleton')
rig=bpy.data.objects.new('Martin_rig',arm_data);bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=arm_data.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=arm_data.edit_bones[parent]
bone('root',(0,0,0),(0,0,.2))
bone('spine',(0,0,.65),(0,0,1.4),'root')
bone('head',(0,0,1.43),(0,0,1.99),'spine')
bone('jaw',(0,-.26,1.54),(0,-.39,1.54),'head')
bone('tail',(0,.20,.63),(.4,.3,.5),'root')
for s,side in [(1,'L'),(-1,'R')]:
    bone('arm.'+side,(s*.33,0,1.34),(s*.46,0,.73),'spine')
    bone('leg.'+side,(s*.19,0,.65),(s*.19,0,.10),'root')
bpy.ops.object.mode_set(mode='OBJECT')
for obj,bname in parts:
    group=obj.vertex_groups.new(name=bname);group.add(list(range(len(obj.data.vertices))),1,'REPLACE')
    mod=obj.modifiers.new('Skin','ARMATURE');mod.object=rig
    obj.parent=rig
rig.animation_data_create()
for name,end in [('Idle',120),('Talk',60),('Wave',90),('DJ',120)]:
    action=bpy.data.actions.new(name);rig.animation_data.action=action
    for frame in range(1,end+1,3):
        phase=2*math.pi*(frame-1)/(end-1)
        for p in rig.pose.bones:
            p.rotation_mode='XYZ';p.rotation_euler=(0,0,0);p.location=(0,0,0)
        rig.pose.bones['head'].rotation_euler.y=.025*math.sin(phase)
        rig.pose.bones['tail'].rotation_euler.y=.13*math.sin(phase)
        if name=='Talk':rig.pose.bones['jaw'].rotation_euler.x=.20*(.5-.5*math.cos(phase*4))
        if name=='Wave':rig.pose.bones['arm.L'].rotation_euler.y=-1.65*math.sin(phase/2);rig.pose.bones['arm.L'].rotation_euler.x=.15*math.sin(phase*3)
        if name=='DJ':
            rig.pose.bones['head'].rotation_euler.x=.08*math.sin(phase*2)
            rig.pose.bones['arm.L'].rotation_euler.x=.3+.16*math.sin(phase*2)
        for p in rig.pose.bones:p.keyframe_insert('rotation_euler',frame=frame)
    # Exact closing pose avoids a jump at clip boundary.
    for p in rig.pose.bones:
        p.rotation_euler=(0,0,0)
        if name=='DJ' and p.name=='arm.L':p.rotation_euler.x=.3
        p.keyframe_insert('rotation_euler',frame=end)
    track=rig.animation_data.nla_tracks.new();track.name=name
    track.strips.new(name,1,action)
    track.mute=True
rig.animation_data.action=None
for p in rig.pose.bones:p.rotation_euler=(0,0,0)
scene=bpy.context.scene;scene.render.fps=30;scene.frame_start=1;scene.frame_end=120;scene.frame_set(1)
rig['status']='PROTOTYPE: not 1:1; rigid skin; no phoneme morphs; Android untested'
# Export only character, excluding studio. Unmute NLA so exporter sees all tracks.
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for obj,_ in parts:obj.select_set(True)
for t in rig.animation_data.nla_tracks:t.mute=False
bpy.ops.export_scene.gltf(filepath=str(OUT/'martin-prototype.glb'),export_format='GLB',use_selection=True,export_animations=True,export_nla_strips=True,export_extras=True)
for t in rig.animation_data.nla_tracks:t.mute=True
for p in rig.pose.bones:p.rotation_euler=(0,0,0)
scene.frame_set(1)
# Studio rendering is explicitly of generated geometry.
floor=material('Studio_floor',(.035,.042,.05),.85)
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(floor)
def area(name,loc,power,color,size):
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-3,-4,5),450,(1,.86,.70),3)
area('Fill',(3,-2,3),240,(.65,.78,1),2.5)
area('Rim',(1,3,4),550,(1,.70,.36),2)
bpy.ops.object.camera_add(location=(3,-7,2.9))
cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.85;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=False
scene.render.resolution_x=800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18)
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'source-render.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'martin-prototype.blend'))
bpy.ops.render.render(write_still=True)
print('MARTIN_BUILD_COMPLETE')
