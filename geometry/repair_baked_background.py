"""Repair the first bake's opaque black outside-UV texels, without rebaking RGB."""
import bpy, numpy as np, json
from pathlib import Path
ROOT=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parents[1]).resolve()
OUT=ROOT/'artwork/baked'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
scene.render.bake.margin=16;scene.render.bake.margin_type='EXTEND';scene.render.bake.use_clear=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
summary=[]
for i in [1,2,3,5]:
    name=f'A380X_FUSE{i}';data=np.load(ROOT/'geometry'/f'{name}_coordinates_uv.npz')
    mesh=bpy.data.meshes.new(name);ofs=data['face_offsets']
    mesh.from_pydata(data['xyz'].tolist(),[],[list(range(int(a),int(b))) for a,b in zip(ofs[:-1],ofs[1:])]);mesh.update()
    uv=mesh.uv_layers.new();uv.data.foreach_set('uv',data['uv'].reshape(-1))
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
    emit=nodes.new('ShaderNodeEmission');emit.inputs['Color'].default_value=(1,1,1,1)
    out=nodes.new('ShaderNodeOutputMaterial');links.new(emit.outputs[0],out.inputs['Surface'])
    mask=bpy.data.images.new(name+'_UV_Coverage',width=4096,height=4096,alpha=True)
    tex=nodes.new('ShaderNodeTexImage');tex.image=mask;nodes.active=tex;mesh.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.bake(type='EMIT')
    target=bpy.data.images.load(str(OUT/f'{name}.png'));target.colorspace_settings.name='sRGB'
    colors=np.empty(4096*4096*4,dtype=np.float32);target.pixels.foreach_get(colors)
    coverage=np.empty_like(colors);mask.pixels.foreach_get(coverage);coverage=coverage.reshape(-1,4)[:,0]
    colors=colors.reshape(-1,4);colors[:,3]=coverage;colors[coverage<.0001,:3]=1
    target.pixels.foreach_set(colors.reshape(-1));target.update();target.file_format='PNG';target.filepath_raw=str(OUT/f'{name}.png');target.save()
    summary.append({'material':name,'transparent_unused_texels':int(np.count_nonzero(coverage<.0001))})
    print('REPAIRED',name,summary[-1]['transparent_unused_texels'],flush=True)
    bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh);bpy.data.images.remove(mask);bpy.data.images.remove(target);data.close()
(OUT/'background-repair.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
