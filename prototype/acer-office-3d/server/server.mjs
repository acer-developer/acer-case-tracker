#!/usr/bin/env node
// Serves the 3D office and a live /api/cases endpoint that reads Zoho CRM on each request.
//   ZOHO_CLIENT_ID=… ZOHO_CLIENT_SECRET=… ZOHO_REFRESH_TOKEN=… ZOHO_DC=in node server/server.mjs  (PORT, default 8080)
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { dirname, extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { fetchCases } from './zoho.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.txt': 'text/plain' };

createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/api/cases') {
    try {
      const body = JSON.stringify(await fetchCases());
      res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }).end(body);
    } catch (e) {
      console.error(e.message);
      res.writeHead(502, { 'Content-Type': 'application/json' }).end(JSON.stringify({ error: 'Zoho CRM unavailable' }));
    }
    return;
  }
  let file = join(ROOT, normalize(decodeURIComponent(url.pathname)));
  if (file.endsWith(sep)) file += 'index.html';
  if (!file.startsWith(ROOT + sep) || file.startsWith(join(ROOT, 'server'))) return res.writeHead(404).end();
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': TYPES[extname(file)] || 'application/octet-stream' }).end(body);
  } catch { res.writeHead(404).end(); }
}).listen(process.env.PORT || 8080, () => console.log(`ACER office on http://localhost:${process.env.PORT || 8080}`));
