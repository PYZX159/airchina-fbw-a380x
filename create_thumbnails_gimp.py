from pathlib import Path
import struct,json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
source=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(root/'preview/airchina-three-quarter.png')))
side=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(root/'preview/airchina-port.png')))
tex=root/'package/airchina-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_AirChina_Fictional/texture.AIRCHINA'
native=root/'project/PackageSources/SimObjects/airplanes/FlyByWire_A380X/liveries/eason/AirChina_Fictional_B38AC/thumbnail'
def scaled(im,w,h):
    cp=im.duplicate(); ow,oh=cp.get_width(),cp.get_height()
    if ow/oh>w/h:
        nw=round(oh*w/h);cp.crop(nw,oh,(ow-nw)//2,0)
    elif ow/oh<w/h:
        nh=round(ow*h/w);cp.crop(ow,nh,0,(oh-nh)//2)
    cp.scale(w,h);return cp
for name,sz in [('thumbnail.jpg',(1024,512)),('thumbnail_small.jpg',(400,200))]:
    im=scaled(source,*sz)
    pdb_run('file-jpeg-export',image=im,file=Gio.File.new_for_path(str(tex/name)),quality=.94)
    im.delete()
for path in native.glob('*.png'):
    w,h=struct.unpack('>II',path.read_bytes()[16:24])
    im=scaled(side if 'side' in path.name else source,w,h)
    save_png(im,path);im.delete()
source.delete();side.delete()
