const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
const NM = process.argv[2];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('pageerror', e => console.log('pageerror:', e.message));
  await p.route('https://cdn.jsdelivr.net/npm/three@0.169.0/**', r => r.fulfill({ path: path.join(NM, r.request().url().split('three@0.169.0/')[1]), contentType: 'application/javascript' }));
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await p.addInitScript({ path: process.argv[3] });
  await p.goto('http://localhost:8766/'); await p.waitForFunction(() => window.__ready, null, { timeout: 120000 });
  const b64 = await p.evaluate(async () => {
    const { GLTFExporter } = await import('three/addons/exporters/GLTFExporter.js');
    const scene = window.__scene;
    const keep = scene.children.filter(o => !o.isLight && !o.isCamera);
    const root = new (scene.constructor)(); // export a copy without lights/camera helpers
    for (const o of keep) root.add(o.clone(true));
    root.traverse(o => { if (o.isCSS2DObject) o.visible = false; });
    const buf = await new GLTFExporter().parseAsync(root, { binary: true, onlyVisible: true });
    let s = ''; const u = new Uint8Array(buf); for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000));
    return btoa(s);
  });
  fs.writeFileSync(process.argv[4], Buffer.from(b64, 'base64'));
  console.log('wrote', fs.statSync(process.argv[4]).size);
  await b.close();
})();
