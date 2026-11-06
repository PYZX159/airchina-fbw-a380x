from pathlib import Path
import json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
out=root/'artwork'/'template';out.mkdir(parents=True,exist_ok=True)
def export(im,path):
    p=Gimp.get_pdb().lookup_procedure('file-png-export'); c=p.create_config()
    for k,v in {'run-mode':Gimp.RunMode.NONINTERACTIVE,'image':im,'file':Gio.File.new_for_path(str(path)),'compression':3,'include-color-profile':False}.items():c.set_property(k,v)
    r=p.run(c)
    if r.index(0)!=Gimp.PDBStatusType.SUCCESS:raise RuntimeError(str(r.index(0)))
im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(root/'resources/paintkit/A380X_PAINTKIT_V0.3.psd')))
im.undo_disable()
im.scale(4096,4096)
groups=im.get_layers()
for group in groups:group.set_visible(False)
for group in groups:
    name=group.get_name().replace(' ','_')
    group.set_visible(True)
    for sub in group.get_children():
        if 'UV LAYOUT' in sub.get_name():sub.set_visible(False)
    export(im,out/(name+'_base.png'))
    for sub in group.get_children():
        if 'BASE COLOR' in sub.get_name():sub.set_visible(False)
    export(im,out/(name+'_detail.png'))
    group.set_visible(False)
    with (out/'progress.txt').open('a',encoding='utf-8') as f:f.write(name+'\n')
im.delete()
