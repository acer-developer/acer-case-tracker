# ACER Office · 3D Case Journey (prototype)

Open it through a small local web server (browsers block 3D model files opened straight from disk):

```
cd prototype/acer-office-3d
npx serve .          # or: python3 -m http.server 8000
```

Then open the printed address (e.g. http://localhost:3000) in Chrome. Needs internet for the three.js library (CDN).

- **Site switcher** (top): Network overview · ACER Office · ABC Infrastructure · On the road
- **Click** any person, room, car, robot or building for its detail card
- **Replay Journey**: the BD walks the full ABC Infrastructure journey; the camera follows

3D models in `assets/` are by Kenney (www.kenney.nl), CC0 public domain — see `assets/LICENSE-kenney.txt`.
