"""Execute/import inside GIMP python-fu-eval; not a standalone Python module."""
from pathlib import Path
import struct

def pdb_run(name, **properties):
    proc=Gimp.get_pdb().lookup_procedure(name)
    cfg=proc.create_config()
    cfg.set_property('run-mode',Gimp.RunMode.NONINTERACTIVE)
    for name,value in properties.items(): cfg.set_property(name.replace('_','-'),value)
    result=proc.run(cfg)
    status=result.index(0)
    if status != Gimp.PDBStatusType.SUCCESS:
        raise RuntimeError(f'PDB failed: {proc.get_name()} : {status}')
    return result

def load_svg(filename, width, height=0):
    return pdb_run('file-svg-load',file=Gio.File.new_for_path(str(filename)),width=width,height=height,
                   keep_ratio=True,prefer_native_dimensions=False).index(1)

def save_png(image,filename):
    return pdb_run('file-png-export',image=image,file=Gio.File.new_for_path(str(filename)),
                   compression=6,format='rgba8',save_transparent=True,include_color_profile=True,
                   include_thumbnail=False)

def save_dds(image,filename,compression='bc7',flip=False):
    # 'bc3, ' is the actual nickname in the locally installed GIMP 3.2.8.
    # Choose BC7 for main albedo, BC3 for legacy registration if desired.
    if compression=='bc3': compression='bc3, '
    return pdb_run('file-dds-export',image=image,file=Gio.File.new_for_path(str(filename)),
                   compression_format=compression,save_type='canvas',flip_image=flip,
                   mipmaps='generate',mipmap_filter='mitchell',gamma_correct=True,srgb=True,
                   gamma=2.2,perceptual_metric=True)

def mark_bc7_srgb(filename):
    """Set DXGI BC7_UNORM_SRGB metadata for an already-sRGB encoded albedo.
    GIMP 3.2.8 exports BC7_UNORM (98); its 'srgb' option only controls mip filtering.
    This patches the format header to 99, matching the installed aircraft albedos.
    It does not alter, recompress, or convert any pixel data. Caller must ensure
    the image is sRGB albedo rather than a linear data/normal/metalness map.
    """
    path=Path(filename)
    with path.open('r+b') as file:
        header=file.read(148)
        if header[:4]!=b'DDS ' or header[84:88]!=b'DX10':
            raise ValueError('Expected DX10 DDS: '+str(path))
        code=struct.unpack_from('<I',header,128)[0]
        if code not in (98,99): raise ValueError('Expected BC7 DDS, found DXGI '+str(code))
        if code==98:
            file.seek(128); file.write(struct.pack('<I',99))
    return {'file':str(path),'old_dxgi':code,'new_dxgi':99,'pixels_changed':False}

def composite_group(image,group,width=4096,height=4096):
    """Copy a PSD group to a new canvas; preserve group hierarchy and hidden children.
    Excludes all sibling groups. Caller should hide UV guide subgroup in copied group.
    Image should have same full-canvas dimension as group's original source PSD.
    """
    im=Gimp.Image.new(image.get_width(),image.get_height(),Gimp.ImageBaseType.RGB)
    layer=Gimp.Layer.new_from_drawable(group,im)
    im.insert_layer(layer,None,0)
    layer.set_visible(True)
    def hide_uv(l):
        if 'UV LAYOUT' in l.get_name().upper() or l.get_name().upper().endswith(' UV'):
            l.set_visible(False)
        if l.is_group():
            for child in l.get_children(): hide_uv(child)
    hide_uv(layer)
    im.scale(width,height)
    return im

def new_text(image,text,size,x,y,fontname='Arial',color='#111111'):
    font=Gimp.Font.get_by_name(fontname)
    if font is None: raise ValueError('Font is unavailable: '+fontname)
    layer=Gimp.TextLayer.new(image,text,font,size,Gimp.Unit.pixel())
    image.insert_layer(layer,None,0)
    layer.set_color(Gegl.Color.new(color))
    layer.set_offsets(int(x),int(y))
    return layer

if globals().get('HELPER_SELF_TEST',False):
    project_root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
    test_root=project_root/'helper-test'
    test_root.mkdir(exist_ok=True)
    im=Gimp.Image.new(16,16,Gimp.ImageBaseType.RGB)
    layer=Gimp.Layer.new(im,'Test',16,16,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
    im.insert_layer(layer,None,0)
    Gimp.context_set_background(Gegl.Color.new('#e92f20'))
    layer.fill(Gimp.FillType.BACKGROUND)
    save_png(im,test_root/'red.png')
    save_dds(im,test_root/'red-bc7.dds')
    save_dds(im,test_root/'red-bc3.dds','bc3')
    svg=load_svg(project_root/'resources/airchina/airchina-phoenix-companieslogo.svg',256)
    save_png(svg,test_root/'phoenix-256.png')
    (test_root/'success.txt').write_text('DDS BC7/BC3, PNG and SVG load succeeded',encoding='utf8')
