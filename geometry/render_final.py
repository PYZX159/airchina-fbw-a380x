"""Render the GIMP-composited final textures on the original OBJ geometry.

Default inputs: artwork/final/A380X_FUSE1_ALBEDO.PNG through FUSE5.
Example: blender.exe -b --factory-startup --python geometry/render_final.py
Options after --: --texture-dir PATH --output-dir PATH --samples 48
--tail-check uses the temporary baked PNGs and renders only close tail views.
"""
import bpy, sys, argparse, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parents[1]).resolve()
parser=argparse.ArgumentParser()
parser.add_argument('--texture-dir',default=str(ROOT/'artwork/final'))
parser.add_argument('--output-dir',default=str(ROOT/'preview'))
parser.add_argument('--samples',type=int,default=48)
parser.add_argument('--tail-check',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
texdir=Path(args.texture_dir);outdir=Path(args.output_dir);outdir.mkdir(parents=True,exist_ok=True)
paths={f'A380X_FUSE{i}':texdir/f'A380X_FUSE{i}_ALBEDO.PNG' for i in range(1,6)}
for optional_material,filename in [('A380_EXTERIOR_ENG_LH','A380_EXTERIOR_ENG_LH_ALBEDO.PNG'),('A380_EXTERIOR_ENG_RH','A380_EXTERIOR_ENG_RH_ALBEDO.PNG'),('A380_EXTERIOR_WINGFENCE','A380X_EXTERIOR_WINGFENCE_ALBEDO.PNG')]:
    optional_path=texdir/filename
    if optional_path.is_file():paths[optional_material]=optional_path
if args.tail_check:
    paths={'A380X_FUSE4':ROOT/'artwork/baked/A380X_FUSE4.png'}
for path in paths.values():
    if not path.is_file():raise FileNotFoundError(f'Final GIMP texture not ready: {path}')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'geometry/A380X-neutral-preview.blend'))
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True
scene.view_settings.view_transform='Standard'
scene.view_settings.look='None'
scene.view_settings.exposure=0
scene.view_settings.gamma=1
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
scene.render.resolution_x=2400;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
# Neutral white illumination, one quarter of the initial AgX studio energy.
for obj in scene.objects:
    if obj.type=='LIGHT':obj.data.energy/=4;obj.data.color=(1,1,1)
background=scene.world.node_tree.nodes['Background']
background.inputs['Color'].default_value=(.32,.32,.32,1)
background.inputs['Strength'].default_value=.55
for mat in bpy.data.materials:
    if not mat.node_tree:continue
    for node in mat.node_tree.nodes:
        if node.type=='BSDF_PRINCIPLED':
            node.inputs['Metallic'].default_value=0
            node.inputs['Roughness'].default_value=.56
            node.inputs['Specular IOR Level'].default_value=.15
            node.inputs['Coat Weight'].default_value=0
for name,path in paths.items():
    mat=bpy.data.materials[name];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=True)
    tex.image.colorspace_settings.name='sRGB';tex.interpolation='Linear'
    links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
    # Alpha is intentionally not connected to the aircraft shader. UV-space
    # background transparency is packaging data, not aircraft transparency.
if args.tail_check:
    scene.render.resolution_x=1200;scene.render.resolution_y=1200
    for camname,side in [('Camera_Port_Side','port'),('Camera_Starboard_Side','starboard')]:
        cam=bpy.data.objects[camname];cam.location=(130 if side=='port' else -130,28.5,11.5)
        cam.rotation_euler=(Vector((0,28.5,11.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=23
        scene.camera=cam;scene.render.filepath=str(outdir/f'tail-{side}-standard.png');bpy.ops.render.render(write_still=True)
else:
    registration_path=texdir/'A380X_REGISTRATION_ALBEDO.PNG'
    if registration_path.is_file():
        registration_image=bpy.data.images.load(str(registration_path),check_existing=True)
        registration_image.colorspace_settings.name='sRGB';registration_image.use_fake_user=True
    # Open the delivered blend on a useful complete-aircraft view.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_location=Vector((0,1.3,8.5))
                area.spaces.active.region_3d.view_distance=105
                area.spaces.active.region_3d.view_rotation=bpy.data.objects['Camera_Three_Quarter'].rotation_euler.to_quaternion()
                area.spaces.active.region_3d.view_perspective='ORTHO'
                area.spaces.active.shading.type='MATERIAL'
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(outdir/'airchina-a380x-preview.blend'))
    for camname,name in [('Camera_Port_Side','airchina-port.png'),('Camera_Starboard_Side','airchina-starboard.png'),('Camera_Three_Quarter','airchina-three-quarter.png')]:
        scene.camera=bpy.data.objects[camname];scene.render.filepath=str(outdir/name);bpy.ops.render.render(write_still=True)
    metadata={'inputs':{k:str(v) for k,v in paths.items()},'color_space':'sRGB images -> Principled Base Color, no manual gamma/linear conversion','display':'Standard, None look, 0 exposure, gamma 1','lights':'1/4 original energy, neutral white','samples':args.samples,'preview_only':'Original paintkit geometry, not an in-simulator capture'}
    (outdir/'render-manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
print('FINAL_RENDER_COMPLETE',flush=True)
