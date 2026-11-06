import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parents[1]).resolve()
OUT=ROOT/'geometry'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'A380X-neutral-preview.blend'))
mat=bpy.data.materials['A380X_FUSE1']
nodes=mat.node_tree.nodes; links=mat.node_tree.links
bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'artwork/orientation-check/FUSE1_original_dds_no_flip_4096.png'))
links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
uv=nodes.new('ShaderNodeTexCoord');separate=nodes.new('ShaderNodeSeparateXYZ');combine=nodes.new('ShaderNodeCombineXYZ');flip=nodes.new('ShaderNodeMath');flip.operation='SUBTRACT';flip.inputs[0].default_value=1
links.new(uv.outputs['UV'],separate.inputs[0]);links.new(separate.outputs['X'],combine.inputs['X']);links.new(separate.outputs['Y'],flip.inputs[1]);links.new(flip.outputs[0],combine.inputs['Y'])
scene=bpy.context.scene;cam=bpy.data.objects['Camera_Port_Side'];cam.location=(100,-25,3);cam.rotation_euler=(Vector((0,-25,3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=26;scene.camera=cam
scene.render.resolution_x=2000;scene.render.resolution_y=1000;scene.cycles.samples=12
scene.render.filepath=str(OUT/'dds-no-flip-on-obj.png');bpy.ops.render.render(write_still=True)
links.new(combine.outputs[0],tex.inputs['Vector'])
scene.render.filepath=str(OUT/'dds-flip-y-on-obj.png');bpy.ops.render.render(write_still=True)
