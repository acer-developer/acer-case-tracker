"""Build blender/acer-office.blend from a GLB export of the web scene.

Run:  python build_blend.py SCENE.glb OUT.blend [PREVIEW.png]   (needs the `bpy` package, Blender 5.x)
Three.js is Y-up, Blender is Z-up; the glTF importer converts, so web (x, y, z) = Blender (x, -z, y).
"""
import sys, math
import bpy
from mathutils import Vector

glb, out = sys.argv[1], sys.argv[2]
preview = sys.argv[3] if len(sys.argv) > 3 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)

# ---- one collection per top-level part of the scene, so each area can be hidden or moved as a unit
def top(o):
    while o.parent: o = o.parent
    return o
GROUPS = {'ACER office': 'ACER office (inside)', 'ACER building shell': 'ACER building (roof & glass)', 'Client office': 'Client office'}
roots = sorted({top(o) for o in bpy.context.scene.objects}, key=lambda o: o.name)
for r in roots:
    name = GROUPS.get(r.name.split('.')[0], 'City, road & client site')
    col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    stack = [r]
    while stack:
        o = stack.pop(); stack.extend(o.children)
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)

# roof hidden by default so the rooms are visible (click the eye in the Outliner to show it)
lc = bpy.context.view_layer.layer_collection.children.get('ACER building (roof & glass)')
if lc: lc.hide_viewport = True
shell = bpy.data.collections.get('ACER building (roof & glass)')
if shell: shell.hide_render = True

# ---- markers the website uses for movement (web x,z → Blender x,-z)
mk = bpy.data.collections.new('Markers (robot stops, client)'); bpy.context.scene.collection.children.link(mk)
FY = .22
MARKERS = {
    'Robot stop · Compliance': (3.6, -14.2), 'Robot stop · Rating Team': (19.6, -14.2), 'Robot stop · Committee': (28.7, -14.2),
    'Client office': (-46, -2),
}
for name, (x, z) in MARKERS.items():
    e = bpy.data.objects.new(name, None); e.empty_display_type = 'CONE'; e.empty_display_size = .8
    e.location = (x, -z, FY); e.rotation_euler = (math.pi, 0, 0); mk.objects.link(e)

# ---- light + camera matching the website's "ACER office" view
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sun.data.energy = 3.2
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35)); bpy.context.scene.collection.objects.link(sun)
cam = bpy.data.objects.new('Camera · ACER office', bpy.data.cameras.new('Camera')); cam.data.lens = 35
bpy.context.scene.collection.objects.link(cam)
eye, look = Vector((2, -38, 42)), Vector((17, 9, 0))
cam.location = eye; cam.rotation_euler = (look - eye).to_track_quat('-Z', 'Y').to_euler()
sc = bpy.context.scene; sc.camera = cam
world = bpy.data.worlds.new('Sky'); world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.80, .87, .95, 1); world.node_tree.nodes['Background'].inputs[1].default_value = .9
sc.world = world
sc.unit_settings.system = 'METRIC'

bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print('saved', out)

if preview:
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.render.filepath = preview
    bpy.ops.render.render(write_still=True)
    print('preview', preview)
