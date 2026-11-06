"""Re-export the nine final editable UV XCFs without paintkit or Blender geometry.

Run with Run-Gimp.ps1. This reads the XCFs and writes PNG/DDS derivatives only.
EXPORT_OUTPUT_ROOT can select a separate output root when invoked programmatically.
"""
from pathlib import Path

root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
output=Path(globals().get('EXPORT_OUTPUT_ROOT') or root).resolve()
jobs=[(f'A380X_FUSE{i}_ALBEDO',f'A380X_FUSE{i}_ALBEDO',4096) for i in range(1,6)]
jobs += [(f'A380_EXTERIOR_ENG_{side}_ALBEDO',f'A380_EXTERIOR_ENG_{side}_ALBEDO',4096) for side in ['LH','RH']]
jobs += [('A380X_EXTERIOR_WINGFENCE_ALBEDO','A380X_EXTERIOR_WINGFENCE_ALBEDO',1024),
         ('A380X_REGISTRATION_B38AC','A380X_REGISTRATION_ALBEDO',1024)]
missing=[str(root/'artwork/xcf'/(source_name+'.xcf')) for source_name,_,_ in jobs
         if not (root/'artwork/xcf'/(source_name+'.xcf')).is_file()]
if missing:
    raise FileNotFoundError('Extract AirChina-FBW-A380X-GIMP-Sources-v0.1.1.zip from the release '
                            'into the project root before exporting. Missing XCFs:\n'+'\n'.join(missing))
final=output/'artwork/final';final.mkdir(parents=True,exist_ok=True)
tex=output/'package/airchina-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_AirChina_Fictional/texture.AIRCHINA'
tex.mkdir(parents=True,exist_ok=True)
for source_name,name,size in jobs:
    source=root/'artwork/xcf'/(source_name+'.xcf')
    im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(source)))
    try:
        im.undo_disable()
        if (im.get_width(),im.get_height())!=(size,size):
            raise ValueError(f'Unexpected XCF canvas dimensions: {source}')
        save_png(im,final/(name+'.PNG'))
        dds=tex/(name+'.PNG.DDS')
        registration=name=='A380X_REGISTRATION_ALBEDO'
        save_dds(im,dds,'bc3' if registration else 'bc7',False)
        if not registration:mark_bc7_srgb(dds)
        print('XCF_EXPORTED',name,flush=True)
    finally:
        im.delete()
print('NINE_XCF_EXPORT_COMPLETE',flush=True)
