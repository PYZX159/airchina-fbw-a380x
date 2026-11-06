import bpy, json, math, gzip, csv, time
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT = Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parents[1]).resolve()
OUT = ROOT / 'geometry'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=str(ROOT/'resources/paintkit/A380X_PAINTKIT.obj'), forward_axis='NEGATIVE_Z', up_axis='Y')
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']

def bounds(points):
    a = np.asarray(points)
    return {'min':a.min(axis=0).round(6).tolist(), 'max':a.max(axis=0).round(6).tolist(), 'size':np.ptp(a,axis=0).round(6).tolist()}

report={'import':{'file':'A380X_PAINTKIT.obj','Blender':bpy.app.version_string,'forward_axis':'NEGATIVE_Z','up_axis':'Y'}, 'objects':[], 'materials':{}, 'fuse':{}}
allpts=[]
fuse_data={f'A380X_FUSE{i}':{'xyz':[], 'uv':[], 'normals':[], 'face_offsets':[0], 'objects':set()} for i in range(1,6)}
for obj in meshes:
    mesh=obj.data
    xyz=np.asarray([tuple(obj.matrix_world@v.co) for v in mesh.vertices], dtype=np.float32)
    allpts.append(xyz)
    mats=[slot.material.name if slot.material else '' for slot in obj.material_slots]
    report['objects'].append({'name':obj.name,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'bounds':bounds(xyz),'materials':mats,'uv_layers':[x.name for x in mesh.uv_layers]})
    uvs=mesh.uv_layers.active
    for poly in mesh.polygons:
        matname=mats[poly.material_index] if poly.material_index<len(mats) else ''
        entry=report['materials'].setdefault(matname,{'faces':0,'objects':set()})
        entry['faces']+=1
        entry['objects'].add(obj.name)
        if matname not in fuse_data: continue
        d=fuse_data[matname]
        d['objects'].add(obj.name)
        for loopidx in poly.loop_indices:
            vidx=mesh.loops[loopidx].vertex_index
            d['xyz'].append(xyz[vidx])
            d['uv'].append(tuple(uvs.data[loopidx].uv) if uvs else (float('nan'),float('nan')))
            d['normals'].append(tuple(obj.matrix_world.to_3x3()@poly.normal))
        d['face_offsets'].append(len(d['xyz']))
report['bounds']=bounds(np.concatenate(allpts))
for matname,entry in report['materials'].items(): entry['objects']=sorted(entry['objects'])
for matname,d in fuse_data.items():
    xyz=np.asarray(d['xyz'],dtype=np.float32)
    uv=np.asarray(d['uv'],dtype=np.float32)
    offsets=np.asarray(d['face_offsets'],dtype=np.int32)
    normals=np.asarray(d['normals'],dtype=np.float32)
    np.savez_compressed(OUT/f'{matname}_coordinates_uv.npz', xyz=xyz, uv=uv, normals=normals, face_offsets=offsets)
    report['fuse'][matname]={'faces':len(offsets)-1,'loops':len(xyz),'objects':sorted(d['objects']), 'bounds':bounds(xyz),'uv_bounds':bounds(uv), 'uv_outside_0_1_loops':int(np.any((uv<0)|(uv>1),axis=1).sum()),'npz':f'{matname}_coordinates_uv.npz'}
    # Lightweight, vector UV wireframe: SVG Y flipped only for top-left display.
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="2048" viewBox="0 0 2048 2048">','<rect width="2048" height="2048" fill="white"/>','<g fill="none" stroke="#356393" stroke-opacity="0.55" stroke-width="0.35">']
    for i in range(len(offsets)-1):
        p=uv[offsets[i]:offsets[i+1]]
        coord=' '.join(f'{x*2048:.2f},{(1-y)*2048:.2f}' for x,y in p)
        lines.append(f'<polygon points="{coord}"/>')
    lines.extend(['</g>','</svg>'])
    (OUT/f'{matname}_uv.svg').write_text('\n'.join(lines),encoding='utf-8')

(OUT/'geometry-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('GEOMETRY_REPORT',json.dumps({'bounds':report['bounds'],'fuse':report['fuse']},ensure_ascii=False),flush=True)

# Clean, neutral material preview. No livery artwork is created here.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    nodes.clear()
    bsdf=nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value=(0.82,0.84,0.87,1)
    bsdf.inputs['Roughness'].default_value=.42
    bsdf.inputs['Metallic'].default_value=.08
    output=nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'],output.inputs['Surface'])
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=16
scene.cycles.use_denoising=True
scene.render.resolution_x=2000
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('Neutral Studio')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.20,0.24,0.30,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
scene.view_settings.view_transform='AgX'

def area(name,location,power,size,target):
    light=bpy.data.lights.new(name,'AREA'); light.energy=power; light.shape='DISK'; light.size=size
    obj=bpy.data.objects.new(name,light); scene.collection.objects.link(obj); obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

b=report['bounds']; center=Vector([(a+c)/2 for a,c in zip(b['min'],b['max'])])
area('Key',(-25,-20,55),140000,45,center)
area('Fill',(35,25,35),100000,45,center)
area('Rim',(-10,50,45),80000,30,center)

def camera(name,location,target,scale):
    data=bpy.data.cameras.new(name); data.type='ORTHO'; data.ortho_scale=scale
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

side=camera('Camera_Port_Side',(130,center.y,center.z),center,86)
other=camera('Camera_Starboard_Side',(-130,center.y,center.z),center,86)
three=camera('Camera_Three_Quarter',(-95,-85,45),center,100)
scene.camera=side
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A380X-neutral-preview.blend'))
for cam,name in [(side,'neutral-port-side'),(other,'neutral-starboard-side'),(three,'neutral-three-quarter')]:
    scene.camera=cam
    scene.render.filepath=str(OUT/f'{name}.png')
    bpy.ops.render.render(write_still=True)
print('PREVIEWS_COMPLETE',flush=True)
