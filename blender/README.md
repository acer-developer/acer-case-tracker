# ACER office in Blender

`acer-office.blend` is the same office as the website: rooms, walls, name plates, furniture, people, robot, the road and the client office. Open it in Blender 4.2 or newer.

The Outliner has one collection per area. Use them to hide or move a whole area at once:

- **ACER office (inside)**: rooms, furniture, staff and the robot
- **ACER building (roof & glass)**: hidden by default so you can see inside. Click the eye icon to show it.
- **Client office**, and **City, road & client site**
- **Markers**: the robot's three stops and the client office. Moving these moves where the website sends the robot.

The units are metres. The website's (x, y, z) is Blender's (x, −z, y).

Rebuilding from the website:

```
node export_scene.js <path-to-three-package> <init-script.js> scene.glb   # page served on :8766
python build_blend.py scene.glb acer-office.blend blend_preview.png      # pip install bpy
```
