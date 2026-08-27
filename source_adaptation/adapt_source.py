"""Noncommercial visual adaptation of the user-provided Judy Hopps scene.
Original meshes and rig retained hidden; rendered copy uses evaluated source geometry.
This is a look-development scene, not a validated animated mobile export.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--source', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
args=parser.parse_args()
SOURCE=args.source.resolve()
OUT=args.out.resolve();OUT.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.use_scripts_auto_execute=False
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
scene=bpy.context.scene
scene.use_nodes=False
originals=list(scene.objects)
for obj in originals:
 if obj.type=='MESH':
  for mod in obj.modifiers:
   if mod.type=='PARTICLE_SYSTEM':mod.show_viewport=False;mod.show_render=False
   if mod.type=='SUBSURF':mod.levels=2 if obj.name=='Head' else 1;mod.render_levels=mod.levels
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
col=bpy.data.collections.new('MARTIN_SOURCE_ADAPTATION');scene.collection.children.link(col)
source_names=['Head','Mouth','Eye.L','Eye.R','Hands','Feet','UniformMain','ArmourFeet','ArmourArm']
render_objects=[]
source_ear_faces={}
def deform(p):
 x,y,z=p
 blend=max(0,min(1,(z-.74)/.10));blend=blend*blend*(3-2*blend)
 body_width=1.25+.65*math.exp(-((z-.60)/.14)**2)
 xx=x*(body_width*(1-blend)+1.8*blend)
 if .81<z<.88:xx*=1+.10*math.exp(-((z-.85)/.035)**2)*math.exp(-(x/.065)**2)
 if y<-.08:xx*=1-.25*math.exp(-(x/.065)**4-((z-.885)/.027)**4)
 yy=y*(1.3-.05*blend)
 if y<0 and abs(x)<.11:yy-=.02*math.exp(-((z-.57)/.12)**2)
 zz=z*.65 if z<=.75 else .4875+(z-.75)*1.45
 return (xx,yy,zz)

def cat_ear(p):
 x,y,z=p;side=1 if x>0 else -1
 t=max(0,min(1,(z-.995)/.405))
 target=Vector((side*(.145+.060*t)+(x-side*.075)*2.2*(1-t)**.7,(y-.075)*.55+.02,.843+.165*t))
 blend=max(0,min(1,(z-.975)/.060))
 return Vector(deform(p)).lerp(target,blend)
for name in source_names:
 source=bpy.data.objects[name];ev=source.evaluated_get(dg)
 mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
 source_ear_faces[name]={f.index for f in mesh.polygons if mesh.materials[f.material_index].name=='BodySSS'}
 obj=bpy.data.objects.new('Martin_'+name,mesh);col.objects.link(obj)
 ear_ids={v for f in mesh.polygons if mesh.materials[f.material_index].name=='BodySSS' for v in f.vertices} if name=='Head' else set()
 nose_ids={v for f in mesh.polygons if mesh.materials[f.material_index].name=='Nose' for v in f.vertices} if name=='Head' else set()
 for vert in mesh.vertices:
  point=source.matrix_world@vert.co
  vert.co=cat_ear(point) if vert.index in ear_ids else deform(point)

 for face in mesh.polygons:face.use_smooth=True
 obj['source_object']=name;obj['adaptation_stage']='visual geometry; rig transfer pending'
 render_objects.append(obj)
for obj in originals:obj.hide_render=True;obj.hide_set(True)
# The original README and source rig remain in the file, hidden and unmodified.
for text in bpy.data.texts:text.use_module=False

def mat(name,color,rough=.65,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
fur=mat('Martin_gray_tabby',(.18,.17,.15),.85)
nodes=fur.node_tree.nodes;links=fur.node_tree.links;p=nodes.get('Principled BSDF')
attr=nodes.new('ShaderNodeVertexColor');attr.layer_name='MartinCoat'
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images['Fur_COL']
mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.15;mix.inputs[1].default_value=(1,1,1,1);links.new(tex.outputs['Color'],mix.inputs[2])
mul=nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
links.new(attr.outputs['Color'],mul.inputs[1]);links.new(mix.outputs[0],mul.inputs[2]);links.new(mul.outputs[0],p.inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=220;noise.inputs['Detail'].default_value=2
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.0005
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
cloth=mat('Martin_charcoal_fabric',(.018,.022,.027),.9)
p=cloth.node_tree.nodes.get('Principled BSDF');tex=cloth.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images['Fabric_BUMP']
bump=cloth.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.20;bump.inputs['Distance'].default_value=.0004
cloth.node_tree.links.new(tex.outputs['Color'],bump.inputs['Height']);cloth.node_tree.links.new(bump.outputs[0],p.inputs['Normal'])
rubber=mat('Martin_sneaker_trim',(.62,.62,.58),.8)
gold=mat('Martin_muted_gold',(.58,.33,.08),.3,.65)
nose=mat('Martin_rose_nose',(.22,.095,.067),.55)
eye=mat('Martin_eye_olive',(.34,.28,.055),.27)
eye.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.22
import numpy as np
n=512;gy,gx=np.mgrid[0:n,0:n];gx=(gx+.5)/n*2-1;gy=(gy+.5)/n*2-1
r=np.sqrt(gx*gx+gy*gy);a=np.arctan2(gy,gx);pupil=np.clip((r-.53)/.02,0,1)
rgba=np.ones((n,n,4),dtype=np.float32)
fiber=.86+.09*np.sin(a*113+r*18)+.05*np.sin(a*171-r*11)
for c,base in enumerate((.65,.54,.22)):rgba[:,:,c]=.018*(1-pupil)+base*pupil*fiber
im=bpy.data.images.new('Martin_Iris',width=n,height=n,alpha=False);im.pixels.foreach_set(rgba.ravel());im.pack()
tx=eye.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;eye.node_tree.links.new(tx.outputs['Color'],eye.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
black=mat('Martin_black',(.008,.009,.012),.65)
inner=mat('Martin_inner_ear',(.20,.105,.088),.9)
for obj in render_objects:
 at=obj.data.color_attributes.new(name='MartinCoat',type='FLOAT_COLOR',domain='POINT')
 for vert,c in zip(obj.data.vertices,at.data):
  x,y,z=vert.co
  # Grey tabby forehead and cheek strokes, with a light muzzle.
  def segment_dist(px,pz,a,b):
   dx,dz=b[0]-a[0],b[1]-a[1]
   t=max(0,min(1,((px-a[0])*dx+(pz-a[1])*dz)/(dx*dx+dz*dz)))
   return math.hypot(px-a[0]-t*dx,pz-a[1]-t*dz)
  lines=[((.013,.922),(.025,.848)),((.040,.918),(.057,.849)),((.058,.849),(.091,.884)),((.091,.884),(.127,.822)),((.135,.845),(.174,.811))]
  distance=min(segment_dist(abs(x),z,a,b) for a,b in lines)
  stripes=math.exp(-(distance/.006)**2)*max(0,min(1,(-y+.025)/.06))
  if abs(x)>.16 and z<.79:
   stripe_z=.735-.20*(abs(x)-.16)
   distance=min(abs(z-stripe_z),abs(z-stripe_z+.035),abs(z-stripe_z+.066))
   stripes=max(stripes,.65*math.exp(-(distance/.005)**2))
  light=math.exp(-(x/.125)**4-((z-.647)/.063)**4)*max(0,min(1,(-y-.07)/.055))
  value=.17-.060*stripes+.12*light
  c.color=(value,value*.97,value*.89,1)
 for i,m in enumerate(obj.data.materials):
  if m.name in ['Body','BodySSS','Hair','LooseHairs']:obj.data.materials[i]=fur
  elif m.name=='Nose':obj.data.materials[i]=nose
  elif m.name in ['Eyes','Iris','Pupil']:obj.data.materials[i]=eye
  elif m.name in ['UniformLight','UniformDark','Belt','FeetArmour','ArmArmour','VelcroStrap','Velcro']:obj.data.materials[i]=cloth
  elif m.name=='FeetArmourLight':obj.data.materials[i]=rubber
  elif m.name=='Metal':obj.data.materials[i]=black
 if obj.name.startswith('Martin_Eye.'):
  xs=[v.co.x for v in obj.data.vertices];zs=[v.co.z for v in obj.data.vertices]
  cx=(max(xs)+min(xs))/2;cz=(max(zs)+min(zs))/2;wx=(max(xs)-min(xs))/2;hz=(max(zs)-min(zs))/2
  for loop in obj.data.loops:
   co=obj.data.vertices[loop.vertex_index].co
   obj.data.uv_layers.active.data[loop.index].uv=(.5+(co.x-cx-(.018 if cx>0 else -.018))/(2*wx),.5+(co.z-cz)/(2*hz))
 if obj.name=='Martin_Head':
  obj.data.materials.append(inner);inner_index=len(obj.data.materials)-1
  for f in obj.data.polygons:
   if f.index in source_ear_faces['Head'] and f.normal.y<-.35:f.material_index=inner_index
 if obj.name=='Martin_Feet':
  for index in range(len(obj.data.materials)):obj.data.materials[index]=rubber
  smooth=obj.modifiers.new('Soften shoe toe contours','SMOOTH');smooth.factor=.65;smooth.iterations=8
 # Hide buck teeth inside the existing mouth; retain source cavity geometry.
 if obj.name=='Martin_Mouth':
  tooth_ids={v for f in obj.data.polygons if obj.data.materials[f.material_index].name=='Teeth' for v in f.vertices}
  for i in tooth_ids:obj.data.vertices[i].co.y+=.024

def finish(obj,material):
 obj.data.materials.append(material)
 for p in obj.data.polygons:p.use_smooth=True
 return obj

def tube(name,points,radius,material):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=radius;c.bevel_resolution=3;c.use_fill_caps=True
 sp=c.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type=p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);col.objects.link(o);c.materials.append(material);return o

def cylinder(name,loc,radius,depth,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc,rotation=(math.pi/2,0,0))
 o=bpy.context.object;o.name=name;bevel=o.modifiers.new('Rounded edges','BEVEL');bevel.width=.008;bevel.segments=3
 return finish(o,material)
# A hood rim and DJ accessories, placed on the adapted source torso.
tube('Hood_rim',[(-.12,-.015,.51),(-.11,.075,.55),(0,.12,.56),(.11,.075,.55),(.12,-.015,.51)],.032,cloth)
for s in (-1,1):
 cylinder('Headphone_cushion',(s*.16,-.078,.485),.065,.045,black)
 cylinder('Headphone_gold_ring',(s*.16,-.108,.485),.057,.013,gold)
 cylinder('Headphone_cup',(s*.16,-.120,.485),.049,.018,black)
 tube('Drawstring',[(s*.065,-.092,.51),(s*.071,-.112,.445),(s*.078,-.12,.395)],.004,black)
 tube('Whisker',[(s*.105,-.18,.626),(s*.21,-.18,.64),(s*.31,-.15,.65)],.0009,rubber)
 tube('Whisker',[(s*.105,-.178,.612),(s*.22,-.17,.609),(s*.33,-.13,.594)],.0009,rubber)
tube('Headphone_band',[(-.16,.015,.51),(0,.065,.56),(.16,.015,.51)],.010,black)
tube('Cat_tail',[(0,.12,.30),(.12,.18,.20),(.29,.17,.24),(.33,.13,.38),(.30,.10,.44)],.024,fur)
# Curves lack coat vertex colours; use a dedicated matching material.
tailmat=mat('Tail_gray',(.14,.135,.12),.85)
bpy.data.objects['Cat_tail'].data.materials[0]=tailmat
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=.024,location=(.30,.10,.44));finish(bpy.context.object,tailmat);bpy.context.object.name='Tail_tip'
for label,z,size in [('M',.425,.075),('MARTIN',.375,.025)]:
 bpy.ops.object.text_add(location=(0,-.109,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Logo_'+label;o.data.body=label;o.data.align_x='CENTER';o.data.size=size;o.data.extrude=.0005;o.data.materials.append(gold)
tube('Microphone_handle',[(-.244,-.044,.23),(-.244,-.062,.405)],.012,black)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(-.244,-.063,.426));o=bpy.context.object;o.name='Microphone_grille';o.scale=(.026,.026,.038);finish(o,black)
# Neutral studio: actual geometry, no compositor image substitution.
scene.world=bpy.data.worlds.new('Martin_studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.04,.045,.055,1)
scene.render.film_transparent=False
floor=mat('Martin_studio_floor',(.032,.040,.052),.83)
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.name='Martin_floor';bpy.context.object.data.materials.append(floor)
for name,loc,power,size,color in [('Catchlight',(-.45,-2.0,1.45),12,.12,(1,1,1)),('Key',(-1.8,-2.5,2.7),150,2,(1,.89,.78)),('Fill',(1.8,-1.3,1.8),75,2,(.75,.83,1)),('Rim',(1,2,2),180,1,(1,.75,.45))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='Martin_'+name;o.data.energy=power;o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,.55))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.65,-3,1.0));cam=bpy.context.object;cam.name='Martin_camera';cam.rotation_euler=(Vector((0,-.02,.52))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.30;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene['source']='User-provided Judy Hopps 2.0.blend; original source retained hidden'
scene['usage']='NONCOMMERCIAL FANART ADAPTATION. See original Readme. Not a freely licensed commercial cat.'
scene['status']='Visual adaptation only; deformed render meshes are not yet rigged or optimized for Android.'
scene.render.filepath=str(OUT/'martin-source-render.png')
notes=bpy.data.texts.new('MARTIN_ADAPTATION_README')
notes.write('Visual adaptation of the supplied Judy Hopps 2.0 model. Noncommercial fanart only; original Readme applies.\nVisible Martin meshes were made from evaluated source objects, then reshaped. The original rig and meshes are retained hidden. Visible meshes are not yet rigged. No Android or GLB performance claim.\n')
script=bpy.data.texts.new('Martin_adaptation_source.py');script.write(Path(__file__).read_text());script.use_module=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'martin-source-adaptation.blend'),compress=True)
bpy.ops.render.render(write_still=True)
print('SOURCE_ADAPTATION_RENDERED')
