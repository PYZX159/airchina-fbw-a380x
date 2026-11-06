"""Finalize texture sheets, editable XCFs and mipmapped DDS entirely in GIMP."""
from pathlib import Path
import csv,json,time
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
out=root/'artwork/final';out.mkdir(parents=True,exist_ok=True)
src=root/'artwork/xcf';src.mkdir(parents=True,exist_ok=True)
tex=root/'package/airchina-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_AirChina_Fictional/texture.AIRCHINA'
jobs=[(f'FUSE_{n}',f'A380X_FUSE{n}_ALBEDO',f'A380X_FUSE{n}.png',4096) for n in range(1,6)]
jobs += [('ENG_LH','A380_EXTERIOR_ENG_LH_ALBEDO',None,4096),('ENG_RH','A380_EXTERIOR_ENG_RH_ALBEDO',None,4096),('WINGFENCE','A380X_EXTERIOR_WINGFENCE_ALBEDO',None,1024)]
if 'ONLY' in globals(): jobs=[j for j in jobs if j[0] in ONLY]
report=[]
for group,name,baked,size in jobs:
    base=root/'artwork/template'/f'{group}_base.png'
    detail=root/'artwork/template'/f'{group}_detail.png'
    if not base.exists() or not detail.exists():raise FileNotFoundError(str(base)+' / '+str(detail))
    im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(base)));im.undo_disable()
    im.get_layers()[0].set_name('Official airframe base and panel details')
    if baked:
        layer=Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(root/'artwork/baked'/baked)))
        im.insert_layer(layer,None,0);layer.set_name('Air China artwork — UV projected from GIMP side masters')
        overlay=Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(detail)))
        im.insert_layer(overlay,None,0);overlay.set_name('Official markings and weathering — transparent normal overlay')
    if im.get_width()!=size:im.scale(size,size)
    xcf=src/(name+'.xcf');png=out/(name+'.PNG');dds=tex/(name+'.PNG.DDS')
    pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(xcf)))
    save_png(im,png)
    save_dds(im,dds,compression='bc7',flip=False)
    mark_bc7_srgb(dds)
    im.delete()
    report.append({'texture':name,'size':size,'dds':str(dds),'bytes':dds.stat().st_size,'format':'BC7 sRGB / DXGI 99','flip':False})
    (out/(group+'_done.json')).write_text(json.dumps(report[-1],indent=2),encoding='utf-8')
    print('EXPORTED',name,flush=True)
(out/'texture-export-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
