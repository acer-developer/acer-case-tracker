// Live Zoho CRM reader for server/server.mjs. Nothing is stored: every call reads Zoho via the API.
// Server-side only: credentials come from env vars and never reach the browser.
//
//   ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN   (Zoho API console → Self Client)
//   ZOHO_DC = in | com | eu | com.au | jp                    (default: in)
import { loadCases } from '../js/zoho-cases.js';

const DC = process.env.ZOHO_DC || 'in';
const ACCOUNTS = `https://accounts.zoho.${DC}`, API = `https://www.zohoapis.${DC}/crm/v6`;

let token = null, tokenExp = 0;
async function accessToken() {
  if (token && Date.now() < tokenExp) return token;
  for (const k of ['ZOHO_CLIENT_ID', 'ZOHO_CLIENT_SECRET', 'ZOHO_REFRESH_TOKEN']) if (!process.env[k]) throw new Error(`Missing ${k}`);
  const body = new URLSearchParams({ grant_type: 'refresh_token', client_id: process.env.ZOHO_CLIENT_ID, client_secret: process.env.ZOHO_CLIENT_SECRET, refresh_token: process.env.ZOHO_REFRESH_TOKEN });
  const j = await (await fetch(`${ACCOUNTS}/oauth/v2/token`, { method: 'POST', body })).json();
  if (!j.access_token) throw new Error(`Zoho token error: ${JSON.stringify(j)}`);
  token = j.access_token; tokenExp = Date.now() + (j.expires_in - 120) * 1000;
  return token;
}

async function coql(select_query) {
  const r = await fetch(`${API}/coql`, { method: 'POST', headers: { Authorization: `Zoho-oauthtoken ${await accessToken()}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ select_query }) });
  if (r.status === 204) return { data: [] };
  const j = await r.json();
  if (!r.ok) throw new Error(`COQL ${r.status}: ${JSON.stringify(j)}`);
  return j;
}

export const fetchCases = () => loadCases(coql);
