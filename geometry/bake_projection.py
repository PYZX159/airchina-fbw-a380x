"""Bake GIMP's two opaque side projections to the official A380X UV layout.

Run only after side_pos_x.png and side_neg_x.png have been finalized:
  blender -b --factory-startup --python geometry/bake_projection.py

No image Y flip is applied. The unflipped DDS->PNG/OBJ alignment was verified.
"""
import bpy, json, sys, time, argparse
import numpy as np
from pathlib import Path

ROOT=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parents[1]).resolve()
GEOM=ROOT/'geometry'
ART=ROOT/'artwork/projection'
OUT=ROOT/'artwork/baked'

parser=argparse.ArgumentParser()
parser.add_argument('--resolution',type=int,default=4096)
parser.add_argument('--materials',nargs='*',default=[f'A380X_FUSE{i}' for i in range(1,6)])
parser.add_argument('--no-preview',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT.mkdir(parents=True,exist_ok=True)
sources={'pos':ART/'side_pos_x.png','neg':ART/'side_neg_x.png'}
for path in sources.values():
    if not path.is_file():raise FileNotFoundError(f'Awaiting completed GIMP projection: {path}')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=1  # Emission has no stochastic lighting to converge.
scene.render.bake.margin=16
scene.render.bake.margin_type='EXTEND'
scene.render.bake.use_clear=True
scene.render.bake.use_selected_to_active=False
scene.render.bake.target='IMAGE_TEXTURES'
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.render.image_settings.color_depth='8'
src={k:bpy.data.images.load(str(p),check_existing=True) for k,p in sources.items()}
for image in src.values():
    if tuple(image.size)!=(8192,2560):raise ValueError(f'Projection must be 8192x2560: {image.filepath} {tuple(image.size)}')
    image.colorspace_settings.name='sRGB'

def math_node(nodes,links,operation,a=None,b=None):
    n=nodes.new('ShaderNodeMath');n.operation=operation
    for i,val in enumerate([a,b]):
        if val is None:continue
        if isinstance(val,(int,float)):n.inputs[i].default_value=val
        else:links.new(val,n.inputs[i])
    return n.outputs[0]

def srgb_linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4

def material(name,target):
    mat=bpy.data.materials.new(name+'_Projection_Bake');mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
    emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1
    output=nodes.new('ShaderNodeOutputMaterial');links.new(emission.outputs[0],output.inputs['Surface'])
    # FUSE5 consists of belly/wing-box parts. Keep it a uniform light grey.
    if name=='A380X_FUSE5':
        emission.inputs['Color'].default_value=tuple(srgb_linear(x) for x in (0.92,0.93,0.94))+(1,)
    else:
        position=nodes.new('ShaderNodeNewGeometry')
        sep=nodes.new('ShaderNodeSeparateXYZ');links.new(position.outputs['Position'],sep.inputs[0])
        # Port +X: nose at image left. Starboard -X: nose at image right.
        u=math_node(nodes,links,'DIVIDE',math_node(nodes,links,'ADD',sep.outputs['Y'],38),78)
        v=math_node(nodes,links,'DIVIDE',math_node(nodes,links,'ADD',sep.outputs['Z'],4),24.375)
        uneg=math_node(nodes,links,'SUBTRACT',1,u)
        colors={}
        for side,uvx in [('pos',u),('neg',uneg)]:
            coords=nodes.new('ShaderNodeCombineXYZ');links.new(uvx,coords.inputs['X']);links.new(v,coords.inputs['Y'])
            tex=nodes.new('ShaderNodeTexImage');tex.image=src[side];tex.interpolation='Linear';tex.extension='CLIP';tex.label=f'{side}: opaque RGB, alpha intentionally unused'
            links.new(coords.outputs[0],tex.inputs['Vector']);colors[side]=tex.outputs['Color']
        side_mask=math_node(nodes,links,'GREATER_THAN',sep.outputs['X'],0)
        side_mix=nodes.new('ShaderNodeMixRGB');side_mix.blend_type='MIX'
        links.new(side_mask,side_mix.inputs[0]);links.new(colors['neg'],side_mix.inputs[1]);links.new(colors['pos'],side_mix.inputs[2])
        # Outside the declared projection rectangle the aircraft remains white.
        inside=math_node(nodes,links,'MULTIPLY',math_node(nodes,links,'GREATER_THAN',u,0),math_node(nodes,links,'LESS_THAN',u,1))
        inside=math_node(nodes,links,'MULTIPLY',inside,math_node(nodes,links,'GREATER_THAN',v,0))
        inside=math_node(nodes,links,'MULTIPLY',inside,math_node(nodes,links,'LESS_THAN',v,1))
        region=nodes.new('ShaderNodeMixRGB');region.inputs[1].default_value=(1,1,1,1)
        links.new(inside,region.inputs[0]);links.new(side_mix.outputs[0],region.inputs[2]);links.new(region.outputs[0],emission.inputs['Color'])
    # Active unlinked image node is Cycles' bake destination, never an input.
    target_node=nodes.new('ShaderNodeTexImage');target_node.image=target;target_node.label='ACTIVE BAKE DESTINATION'
    for node in nodes:node.select=False
    target_node.select=True;nodes.active=target_node
    return mat

manifest={'resolution':args.resolution,'margin_px':16,'bake':'EMIT','device':'CPU','source_alpha':'ignored; opaque RGB only','mapping':{'Y':[-38,40],'Z':[-4,20.375],'port_pos_x':'U=(Y+38)/78','starboard_neg_x':'U=1-(Y+38)/78','V':'(Z+4)/24.375'},'FUSE5_sRGB':[.92,.93,.94],'outputs':[]}
for name in args.materials:
    start=time.time()
    data=np.load(GEOM/f'{name}_coordinates_uv.npz')
    xyz=data['xyz'];uv=data['uv'];offsets=data['face_offsets']
    # World-space mesh reconstructed from the original polygon-loop data.
    # Each polygon keeps its exact OBJ UVs; normals do not determine side.
    mesh=bpy.data.meshes.new(name+'_BakeMesh')
    faces=[list(range(int(a),int(b))) for a,b in zip(offsets[:-1],offsets[1:])]
    mesh.from_pydata(xyz.tolist(),[],faces);mesh.update()
    uv_layer=mesh.uv_layers.new(name='UVMap')
    uv_layer.data.foreach_set('uv',uv.reshape(-1))
    obj=bpy.data.objects.new(name+'_BakeObject',mesh);scene.collection.objects.link(obj)
    target=bpy.data.images.new(name+'_Projection',width=args.resolution,height=args.resolution,alpha=True,float_buffer=False)
    target.generated_color=(1,1,1,0);target.colorspace_settings.name='sRGB'
    mat=material(name,target);mesh.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.bake(type='EMIT')
    # Cycles fills unused texels with opaque black even on a generated RGBA
    # target. A second, white emission bake provides exact UV coverage/margin.
    # Use it as alpha rather than guessing coverage from black artwork pixels.
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    emission=next(n for n in nodes if n.type=='EMISSION')
    for link in list(emission.inputs['Color'].links):links.remove(link)
    emission.inputs['Color'].default_value=(1,1,1,1)
    mask=bpy.data.images.new(name+'_UV_Coverage',width=args.resolution,height=args.resolution,alpha=True,float_buffer=False)
    masknode=nodes.new('ShaderNodeTexImage');masknode.image=mask;nodes.active=masknode
    bpy.ops.object.bake(type='EMIT')
    colorpixels=np.empty(args.resolution*args.resolution*4,dtype=np.float32);target.pixels.foreach_get(colorpixels)
    maskpixels=np.empty_like(colorpixels);mask.pixels.foreach_get(maskpixels)
    colorpixels=colorpixels.reshape(-1,4);coverage=maskpixels.reshape(-1,4)[:,0]
    colorpixels[:,3]=coverage
    colorpixels[coverage<.0001,:3]=1
    target.pixels.foreach_set(colorpixels.reshape(-1));target.update()
    empty_texels=int(np.count_nonzero(coverage<.0001))
    path=OUT/f'{name}.png'
    target.filepath_raw=str(path);target.file_format='PNG';target.save()
    manifest['outputs'].append({'material':name,'path':str(path),'faces':len(faces),'transparent_unused_texels':empty_texels,'seconds':round(time.time()-start,3)})
    print('BAKED',name,str(path),flush=True)
    # Each FUSE is baked as one object, avoiding multiple-object image clears.
    bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
    bpy.data.images.remove(mask)
    data.close()
(OUT/'projection-bake-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

all_materials=[f'A380X_FUSE{i}' for i in range(1,6)]
if not args.no_preview and all((OUT/f'{name}.png').is_file() for name in all_materials):
    bpy.ops.wm.open_mainfile(filepath=str(GEOM/'A380X-neutral-preview.blend'))
    scene=bpy.context.scene
    for name in all_materials:
        mat=bpy.data.materials[name];nodes=mat.node_tree.nodes;links=mat.node_tree.links
        bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/f'{name}.png'))
        tex.image.colorspace_settings.name='sRGB'
        links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
    scene.cycles.samples=16
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A380X-projection-preview.blend'))
    for camera,filename in [('Camera_Port_Side','projection-port-side.png'),('Camera_Starboard_Side','projection-starboard-side.png'),('Camera_Three_Quarter','projection-three-quarter.png')]:
        scene.camera=bpy.data.objects[camera];scene.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True)
print('BAKE_COMPLETE',flush=True)
