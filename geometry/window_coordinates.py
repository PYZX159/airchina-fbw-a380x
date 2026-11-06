import bpy, bmesh, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parents[1]).resolve()
OUT=ROOT/'geometry'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'A380X-neutral-preview.blend'))
# Correct camera labels: exact door names establish +X as port.
camneg=bpy.data.objects.get('Camera_Port_Side')
campos=bpy.data.objects.get('Camera_Starboard_Side')
camneg.name='Camera_Starboard_Side_corrected'
campos.name='Camera_Port_Side'
camneg.name='Camera_Starboard_Side'
bpy.context.scene.camera=campos
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A380X-neutral-preview.blend'))
results=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH' or not obj.name.startswith('MAIN_FUSELAGE'):continue
    bm=bmesh.new();bm.from_mesh(obj.data)
    adjacency={}
    for edge in bm.edges:
        if len(edge.link_faces)!=1:continue
        a,b=edge.verts
        adjacency.setdefault(a,set()).add(b);adjacency.setdefault(b,set()).add(a)
    seen=set()
    for v in adjacency:
        if v in seen:continue
        stack=[v]; group=[];seen.add(v)
        while stack:
            cur=stack.pop();group.append(cur)
            for n in adjacency[cur]:
                if n not in seen:seen.add(n);stack.append(n)
        co=[obj.matrix_world@p.co for p in group]
        lo=[min(p[i] for p in co) for i in range(3)];hi=[max(p[i] for p in co) for i in range(3)]
        dy=hi[1]-lo[1];dz=hi[2]-lo[2]
        if .15<dy<.9 and .15<dz<.9 and abs((lo[0]+hi[0])/2)>1.5 and 1<lo[2]<6:
            results.append({'object':obj.name,'vertices':len(co),'min':lo,'max':hi,'center':[(a+b)/2 for a,b in zip(lo,hi)]})
    bm.free()
results.sort(key=lambda x:(round(x['center'][2]),x['center'][1]))
(OUT/'window-boundaries.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('WINDOW_BOUNDARIES',len(results))
for r in results:
    print(json.dumps(r))
