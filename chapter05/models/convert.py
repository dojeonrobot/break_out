# Blender 4.5 headless: FBX (Meshy textured) -> one decimated mesh with the base-colour image -> optional humanoid rig -> GLB (JPEG textures, no Draco)
# usage: blender -b --python convert.py -- <src.fbx> <out.glb> <mesh name> <rig|norig> [tri target]
import bpy, bmesh, sys, math
from mathutils import Vector
argv = sys.argv[sys.argv.index('--')+1:]
src, out, name, rigmode = argv[0], argv[1], argv[2], argv[3]
TRI = int(argv[4]) if len(argv) > 4 else 16000

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src)
# meshes only, transforms baked
for o in list(bpy.data.objects):
    if o.type != 'MESH': bpy.data.objects.remove(o, do_unlink=True)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
if len(meshes) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active; ob.name = name; ob.data.name = name

# the base-colour image: the one wired into Principled Base Color, else the first image
base = None
for m in ob.data.materials:
    if not m or not m.use_nodes: continue
    for l in m.node_tree.links:
        if l.to_node.type == 'BSDF_PRINCIPLED' and l.to_socket.name == 'Base Color' and l.from_node.type == 'TEX_IMAGE': base = l.from_node.image
if base is None:
    imgs = [i for i in bpy.data.images if i.size[0] > 0 and 'rough' not in i.name.lower() and 'metal' not in i.name.lower() and 'normal' not in i.name.lower()]
    base = imgs[0] if imgs else None
print('BASE IMAGE', base.name if base else None)

# clean + decimate
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.remove_doubles(threshold=0.0001); bpy.ops.object.mode_set(mode='OBJECT')
try: bpy.ops.mesh.customdata_custom_splitnormals_clear()
except Exception as e: print('no custom normals', e)
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
if tris > TRI:
    md = ob.modifiers.new('dec', 'DECIMATE'); md.ratio = TRI / tris; md.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier='dec')
for p in ob.data.polygons: p.use_smooth = True
# one UV layer, one material
while len(ob.data.uv_layers) > 1: ob.data.uv_layers.remove(ob.data.uv_layers[-1])
ob.data.materials.clear()
mat = bpy.data.materials.new(name + '_mat'); mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes.get('Principled BSDF')
if base is not None:
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = base; nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.9
ob.data.materials.append(mat)

# rig: a simple humanoid armature placed from the mesh's shape (z up), weights from distance to each bone segment
if rigmode == 'rig':
    vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    zs = [v.z for v in vs]; z0, z1 = min(zs), max(zs); H = z1 - z0
    xs = [v.x for v in vs]; W = max(xs) - min(xs)
    def band(a, b): return [v for v in vs if z0 + a*H <= v.z <= z0 + b*H]
    # crotch: the lowest band (from 0.26H up) whose cross-section reaches the centre line
    crotch = z0 + 0.45*H
    for k in range(26, 60):
        a = k/100; bb = band(a, a + 0.01)
        if any(abs(v.x) < 0.03*W and abs(v.y) < 0.2*W for v in bb): crotch = z0 + a*H; break
    legs = [v for v in vs if v.z < crotch]
    lx = sum(v.x for v in legs if v.x < 0)/max(1, len([v for v in legs if v.x < 0])); rx = sum(v.x for v in legs if v.x > 0)/max(1, len([v for v in legs if v.x > 0]))
    arm = band(0.33, 0.72); hl = min(arm, key=lambda v: v.x); hr = max(arm, key=lambda v: v.x)
    neck = z0 + 0.80*H; shoulder = z0 + 0.76*H; sx = 0.16*W
    J = {'hips':(Vector((0, 0, crotch)), Vector((0, 0, crotch + 0.16*H))), 'spine':(Vector((0, 0, crotch + 0.16*H)), Vector((0, 0, neck))), 'head':(Vector((0, 0, neck)), Vector((0, 0, z1))),
         'thigh.L':(Vector((lx, 0, crotch)), Vector((lx, 0, (crotch + z0)/2))), 'shin.L':(Vector((lx, 0, (crotch + z0)/2)), Vector((lx, 0, z0 + 0.03*H))),
         'thigh.R':(Vector((rx, 0, crotch)), Vector((rx, 0, (crotch + z0)/2))), 'shin.R':(Vector((rx, 0, (crotch + z0)/2)), Vector((rx, 0, z0 + 0.03*H))),
         'upperarm.L':(Vector((-sx, 0, shoulder)), (Vector((-sx, 0, shoulder)) + Vector((hl.x, hl.y, hl.z)))/2), 'forearm.L':((Vector((-sx, 0, shoulder)) + Vector((hl.x, hl.y, hl.z)))/2, Vector((hl.x, hl.y, hl.z))),
         'upperarm.R':(Vector((sx, 0, shoulder)), (Vector((sx, 0, shoulder)) + Vector((hr.x, hr.y, hr.z)))/2), 'forearm.R':((Vector((sx, 0, shoulder)) + Vector((hr.x, hr.y, hr.z)))/2, Vector((hr.x, hr.y, hr.z)))}
    PARENT = {'spine':'hips', 'head':'spine', 'thigh.L':'hips', 'thigh.R':'hips', 'shin.L':'thigh.L', 'shin.R':'thigh.R', 'upperarm.L':'spine', 'upperarm.R':'spine', 'forearm.L':'upperarm.L', 'forearm.R':'upperarm.R'}
    arm_data = bpy.data.armatures.new('rig'); rig = bpy.data.objects.new('rig', arm_data); bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
    eb = {}
    for n in ['hips', 'spine', 'head', 'thigh.L', 'shin.L', 'thigh.R', 'shin.R', 'upperarm.L', 'forearm.L', 'upperarm.R', 'forearm.R']:
        b = arm_data.edit_bones.new(n); b.head, b.tail = J[n]; eb[n] = b
    for n, pn in PARENT.items(): eb[n].parent = eb[pn]
    bpy.ops.object.mode_set(mode='OBJECT')
    # weights: gaussian of the distance to each bone segment (sigma 0.07H), the best two per vertex
    sig = 0.07*H
    def dseg(p, a, b):
        ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab)/max(1e-9, ab.dot(ab)))); return (p - (a + ab*t)).length
    groups = {n: ob.vertex_groups.new(name=n) for n in J}
    for i, v in enumerate(vs):
        ws = sorted(((math.exp(-(dseg(v, *J[n])/sig)**2), n) for n in J), reverse=True)[:2]
        tot = sum(w for w, _ in ws) or 1
        for w, n in ws: groups[n].add([i], w/tot, 'REPLACE')
    ob.parent = rig; md = ob.modifiers.new('arm', 'ARMATURE'); md.object = rig
    print('RIG crotch', round((crotch - z0)/H, 3), 'H', round(H, 3), 'hands', [round(hl.x, 2), round(hr.x, 2)])

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=82, export_draco_mesh_compression_enable=False, export_apply=True, export_skins=True, export_yup=True, export_animations=False, export_cameras=False, export_lights=False, use_selection=True)
print('DONE', out)
