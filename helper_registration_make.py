from pathlib import Path
import json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf8'))
src=root/'artwork/orientation-check/REGISTRATION_original_no_flip.png'
final=root/'artwork/final';final.mkdir(exist_ok=True)
source=root/'artwork/source';source.mkdir(exist_ok=True)
package=root/'package/airchina-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_AirChina_Fictional/texture.AIRCHINA'
im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(src)))
im.undo_disable()
base=im.get_layers()[0]
backup=Gimp.Layer.new_from_drawable(base,im);im.insert_layer(backup,None,1);backup.set_name('Original FBW registration reference (hidden)');backup.set_visible(False)
base.set_name('Preserved original SELCAL RE-PS and labels')
old_alpha=str(base.get_pixel(130,150).get_rgba())
im.select_rectangle(Gimp.ChannelOps.REPLACE,96,118,390,110)
base.edit_clear()
Gimp.Selection.none(im)
rect=Gegl.Rectangle.new(96,118,390,110)
base.get_buffer().clear(rect)
base.update(96,118,390,110)
clear_alpha=str(base.get_pixel(130,150).get_rgba())
fonts={name:bool(Gimp.Font.get_by_name(name)) for name in ['Arial Bold','Arial','Arial Rounded MT Bold','Arial Narrow Bold']}
font=Gimp.Font.get_by_name('Arial Bold') or Gimp.Font.get_by_name('Arial')
if not font:raise RuntimeError('Arial font unavailable')
text=Gimp.TextLayer.new(im,'B-38AC',font,100,Gimp.Unit.pixel())
im.insert_layer(text,None,0);text.set_name('B-38AC | fictional aircraft registration');text.set_color(Gegl.Color.new('#FFFFFF'));text.set_offsets(112,117)
info={'font':font.get_name(),'fonts':fonts,'text_layer_dimensions':[text.get_width(),text.get_height()],'position':[112,117],'original_reg_clear_rectangle':[96,118,390,110],'clear_sample_before':old_alpha,'clear_sample_after':clear_alpha,'preserved':'SELCAL CODE and RE-PS; transparent background','flip_image':False,'layers':[(l.get_name(),l.get_visible()) for l in im.get_layers()]}
pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(source/'A380X_REGISTRATION_B38AC.xcf')))
im.remove_layer(backup)
save_png(im,final/'A380X_REGISTRATION_ALBEDO.PNG')
save_dds(im,package/'A380X_REGISTRATION_ALBEDO.PNG.DDS',compression='bc3',flip=False)
(final/'registration-edit.json').write_text(json.dumps(info,indent=2),encoding='utf8')
im.delete()
