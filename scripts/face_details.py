"""Original Martin geometry. No third-party mesh, texture or rig data is used."""
import math
import bpy


def eyelids(finish, material):
    """An annular surface around each eye; morphs slide over the eyeball."""
    verts, faces, closed, sides = [], [], [], []
    segments, rows = 48, 5
    for side in (-1, 1):
        offset = len(verts)
        for row in range(rows):
            r = row / (rows - 1)
            for i in range(segments):
                theta = 2 * math.pi * i / segments
                u, v = math.cos(theta), math.sin(theta)
                x = side * .177 + u * (.101 + .047 * r)
                dz = v * (.078 + .070 * r)
                z = 1.805 + dz
                # Outer boundary is buried in the face, inner edge follows eye.
                outer_y = -.02 - .33 * math.sqrt(max(.02, 1 - (x/.46)**2 - ((z-1.77)/.345)**2)) + .006
                def eye_y(zlocal):
                    return -.265 - .095 * math.sqrt(max(.015, 1 - ((x-side*.177)/.112)**2 - (zlocal/.116)**2)) - .005
                y = eye_y(dz) * (1-r) + outer_y * r
                verts.append((x, y, z))
                closed_dz = dz * r
                closed.append((x, eye_y(closed_dz)*(1-r) + outer_y*r, 1.805+closed_dz))
                sides.append(side)
        for row in range(rows-1):
            for i in range(segments):
                a=offset+row*segments+i; b=offset+row*segments+(i+1)%segments
                faces.append((a+segments,b+segments,b,a))
    mesh=bpy.data.meshes.new('Eyelid_quad_loops')
    mesh.from_pydata(verts, [], faces); mesh.update()
    obj=bpy.data.objects.new('Eyelids',mesh); bpy.context.collection.objects.link(obj)
    finish(obj,material,'head')
    obj.shape_key_add(name='Basis')
    for side,label in [(-1,'R'),(1,'L')]:
        key=obj.shape_key_add(name='Blink.'+label)
        for i,co in enumerate(closed):
            if sides[i]==side:key.data[i].co=co
    # Independent glTF morph clip; no drivers or runtime Blender dependency.
    keys=mesh.shape_keys
    for frame,value in [(1,0),(43,0),(46,1),(49,0),(120,0)]:
        for key in list(keys.key_blocks)[1:]:
            key.value=value; key.keyframe_insert('value',frame=frame)
    keys.animation_data.action.name='Blink'
    action=keys.animation_data.action
    track=keys.animation_data.nla_tracks.new();track.name='Blink'
    track.strips.new('Blink',1,action);track.mute=True
    keys.animation_data.action=None
    return obj


def cloth_normal(materials, out):
    """Small, shared tangent-space woven normal map; standard glTF material."""
    import numpy as np
    n=256
    y,x=np.mgrid[0:n,0:n]
    h=.12*np.sin(x*2*math.pi/8)*np.cos(y*2*math.pi/16)+.12*np.sin(y*2*math.pi/8)*np.cos(x*2*math.pi/16)
    dy,dx=np.gradient(h)
    normal=np.stack((-dx*2,-dy*2,np.ones_like(h)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    rgba=np.ones((n,n,4),dtype=np.float32);rgba[:,:,:3]=normal*.5+.5
    image=bpy.data.images.new('Martin_fabric_normal_256',width=n,height=n,alpha=False)
    image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(rgba.ravel())
    image.filepath_raw=str(out/'martin-fabric-normal.png');image.file_format='PNG';image.save();image.pack()
    for mat in materials:
        nodes,links=mat.node_tree.nodes,mat.node_tree.links
        tex=nodes.new('ShaderNodeTexImage');tex.image=image
        normal_node=nodes.new('ShaderNodeNormalMap');normal_node.inputs['Strength'].default_value=.5
        links.new(tex.outputs['Color'],normal_node.inputs['Color'])
        links.new(normal_node.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])


def smile_morph(obj):
    obj.shape_key_add(name='Basis')
    key=obj.shape_key_add(name='Smile')
    # Local-to-world selection avoids touching paws and tail in the coat atlas mesh.
    inverse=obj.matrix_world.inverted()
    for vert,point in zip(obj.data.vertices,key.data):
        co=obj.matrix_world@vert.co
        if co.y < -.25 and 1.50 < co.z < 1.73:
            weight=math.exp(-((abs(co.x)-.14)/.105)**2-((co.z-1.60)/.10)**2)
            co.z+=.026*weight; co.x+=math.copysign(.009*weight,co.x)
            point.co=inverse@co
