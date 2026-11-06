"""Air China fictional A380 livery art. Run inside GIMP 3 python-fu-eval.
All raster compositing, graphic placement, text, PNG and XCF exports use GIMP.
World projection: Y [-38,40], Z [-4,20.375], +X port and -X starboard.
"""
from pathlib import Path
import math,json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
out=root/'artwork/projection';out.mkdir(parents=True,exist_ok=True)
assets=root/'resources/airchina'
W,H=8192,2560
S=W/78.0
def log(s):
    with (out/'progress.txt').open('a',encoding='utf-8') as f:f.write(s+'\n')
def x(y,side):return (y+38)*S if side=='pos' else (40-y)*S
def z(height):return (20.375-height)*S
def new_layer(im,name,color=None):
    layer=Gimp.Layer.new(im,name,W,H,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
    im.insert_layer(layer,None,0)
    layer.fill(Gimp.FillType.TRANSPARENT)
    if color:
        Gimp.context_set_foreground(Gegl.Color.new(color));layer.edit_fill(Gimp.FillType.FOREGROUND)
    return layer
def rect(im,layer,xx,yy,ww,hh,color):
    Gimp.context_set_foreground(Gegl.Color.new(color))
    im.select_rectangle(Gimp.ChannelOps.REPLACE,xx,yy,ww,hh)
    layer.edit_fill(Gimp.FillType.FOREGROUND);Gimp.Selection.none(im)
def star(im,layer,cx,cy,radius,rotation=0):
    points=[]
    for n in range(10):
        a=rotation-math.pi/2+n*math.pi/5;r=radius if n%2==0 else radius*.381966
        points.extend([cx+math.cos(a)*r,cy+math.sin(a)*r])
    im.select_polygon(Gimp.ChannelOps.REPLACE,points)
    Gimp.context_set_foreground(Gegl.Color.new('#FFDE00'));layer.edit_fill(Gimp.FillType.FOREGROUND);Gimp.Selection.none(im)
def flag(im,side,y0,top,width):
    xx=min(x(y0,side),x(y0+width,side));yy=z(top);fw=width*S;fh=fw*2/3
    layer=new_layer(im,'PRC flag — hand constructed five stars')
    rect(im,layer,xx,yy,fw,fh,'#DE2910')
    # National flag 30x20 construction grid; all stars point toward the large star.
    cx,cy=xx+fw*5/30,yy+fh*5/20
    star(im,layer,cx,cy,fh*3/20)
    for gx,gy in [(10,2),(12,4),(12,7),(10,9)]:
        sx,sy=xx+fw*gx/30,yy+fh*gy/20
        star(im,layer,sx,sy,fh/20,math.atan2(cy-sy,cx-sx)+math.pi/2)
def svg_image(filename,width):return load_svg(assets/filename,width)
def paste_image(im,source,name,y0,top,width,side):
    sw=round(width*S);sh=round(source.get_height()*sw/source.get_width())
    cp=source.duplicate();cp.scale(sw,sh)
    if side=='neg' and name.startswith('Red phoenix'):
        cp.flip(Gimp.OrientationType.HORIZONTAL)
    layer=Gimp.Layer.new_from_visible(cp,im,name);im.insert_layer(layer,None,0)
    layer.set_offsets(round(min(x(y0,side),x(y0+width,side))),round(z(top)))
    cp.delete();return layer
phoenix=svg_image('airchina-phoenix-companieslogo.svg',2048)
wordmark=svg_image('airchina-wordmark-commons.svg',2048)
chinese=svg_image('airchina-full-lockup-companieslogo.svg',6048)
# Crop the authentic calligraphic Chinese title from the corporate vector artwork.
chinese.crop(4128,800,1920,960)
log('Vector brand assets loaded at high resolution')
for side in ['pos','neg']:
    im=Gimp.Image.new(W,H,Gimp.ImageBaseType.RGB);im.undo_disable()
    new_layer(im,'White fuselage base','#F5F5F2')
    stripe=new_layer(im,'Classic Air China blue window band and lower pinstripe')
    rect(im,stripe,0,z(2.50),W,(2.50-1.78)*S,'#153A73')
    rect(im,stripe,0,z(1.48),W,(1.48-1.31)*S,'#153A73')
    flag(im,side,-30.0,4.27,1.30)
    paste_image(im,wordmark,'AIR CHINA official italic wordmark',-27.75,4.20,4.90,side)
    paste_image(im,chinese,'中国国际航空公司 — authentic calligraphic title',-21.8,4.48,6.0,side)
    paste_image(im,phoenix,'Red phoenix vertical tail emblem',27.7,17.0,6.7,side)
    xx=min(x(16.0,side),x(20.7,side))
    new_text(im,'B-38AC',52,xx,z(3.75),'Arial Bold','#171C25')
    new_text(im,'AIRBUS A380-800',18,xx,z(3.10),'Arial Bold','#353A40')
    save_png(im,out/f'side_{side}_x.png')
    pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(out/f'AirChina_side_{side}_x.xcf')))
    im.delete();log(side+' side PNG and layered XCF saved')
phoenix.delete();wordmark.delete();chinese.delete()
(out/'projection.json').write_text(json.dumps({'width':W,'height':H,'Y_min':-38,'Y_max':40,'Z_min':-4,'Z_max':20.375,'pos_x':'port; U=(Y+38)/78','neg_x':'starboard; U=(40-Y)/78','registration':'B-38AC (fictional)','blue':'#153A73','base':'#F5F5F2'},indent=2),encoding='utf-8')
