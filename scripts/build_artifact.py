#!/usr/bin/env python3
"""Bundle prototype/acer-office-3d into a claude.ai Artifact folder (live Zoho data via the viewer's connector).

Artifacts don't serve .glb, so the 3D models ship as base64 inside js/glb-bundle.js and load through blob URLs.
Usage: python3 scripts/build_artifact.py OUT_DIR
"""
import base64, json, re, shutil, sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / 'prototype' / 'acer-office-3d'
out = Path(sys.argv[1]); shutil.rmtree(out, ignore_errors=True); (out / 'js').mkdir(parents=True)

page = (SRC / 'index.html').read_text()
for tag in ['<!doctype html>\n', '<html lang="en">\n', '<head>\n', '<meta charset="utf-8" />\n',
            '<meta name="viewport" content="width=device-width, initial-scale=1" />\n', '</head>\n', '<body>\n', '</body>\n', '</html>']:
    assert tag in page, tag
    page = page.replace(tag, '', 1)
page = page.replace('<title>ACER Case Journey</title>', '<title>ACER Office</title>')

used = re.findall(r"'((?:furniture|cars|city|characters)/[\w-]+)'", page[page.index('const ASSET_LIST'):page.index('const ASSETS = {}')])
bundle = {f'assets/{u}.glb': base64.b64encode((SRC / 'assets' / f'{u}.glb').read_bytes()).decode() for u in used}
(out / 'js' / 'glb-bundle.js').write_text('export default ' + json.dumps(bundle) + ';\n')

loader = "const gltfLoader = new GLTFLoader();"
assert loader in page
page = page.replace(loader, """const GLB = (await import('./js/glb-bundle.js')).default, glbUrls = {};
const glbManager = new THREE.LoadingManager();
glbManager.setURLModifier((u) => {
  const k = u.replace(/^.*?(assets\\/)/, '$1');
  if (!GLB[k]) return u;
  return glbUrls[k] ||= URL.createObjectURL(new Blob([Uint8Array.from(atob(GLB[k]), (ch) => ch.charCodeAt(0))], { type: 'model/gltf-binary' }));
});
const gltfLoader = new GLTFLoader(glbManager);""")
(out / 'acer-office.html').write_text(page)

for f in ['js/stages.js', 'js/zoho-cases.js', 'js/zoho-login.js']: shutil.copy(SRC / f, out / f)
for png in (SRC / 'assets').rglob('*.png'):
    d = out / png.relative_to(SRC); d.parent.mkdir(parents=True, exist_ok=True); shutil.copy(png, d)
files = sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p.name != 'acer-office.html')
print(json.dumps({f: f for f in files}))
