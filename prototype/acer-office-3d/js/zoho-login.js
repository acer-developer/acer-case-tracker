// "Sign in with Zoho" for the static site (GitHub Pages). Zoho client-based app, implicit grant:
// the viewer logs in with their own Zoho account, the short-lived token stays in this browser tab,
// and the page calls Zoho CRM directly. No secret lives in the repo — the client ID is public by design.
//
// Setup (once): api-console.zoho.in → Add Client → "Client-based Applications"
//   JavaScript domain: https://acer-developer.github.io
//   Redirect URI:      https://acer-developer.github.io/acer-case-tracker/prototype/acer-office-3d/
// then put the Client ID below.
export const ZOHO = {
  clientId: '',                         // ← paste the Client ID from the Zoho API console
  accounts: 'https://accounts.zoho.in', // ACER's Zoho data centre
  scope: 'ZohoCRM.coql.READ,ZohoCRM.modules.READ',
};

const KEY = 'acer.zoho.token';
const store = {
  get() { try { const t = JSON.parse(sessionStorage.getItem(KEY)); return t && t.exp > Date.now() ? t : null; } catch { return null; } },
  set(t) { try { sessionStorage.setItem(KEY, JSON.stringify(t)); } catch {} },
  clear() { try { sessionStorage.removeItem(KEY); } catch {} },
};

/** Pick up a token Zoho just sent back in the URL hash. */
function takeRedirect() {
  if (!location.hash.includes('access_token=')) return;
  const p = new URLSearchParams(location.hash.slice(1));
  store.set({ token: p.get('access_token'), api: p.get('api_domain') || 'https://www.zohoapis.in', exp: Date.now() + (Number(p.get('expires_in')) || 3600) * 1000 - 60000 });
  history.replaceState(null, '', location.pathname + location.search);
}
takeRedirect();

export const zohoConfigured = () => !!ZOHO.clientId;
export const zohoSignedIn = () => !!store.get();

export function zohoSignIn() {
  const u = new URL(`${ZOHO.accounts}/oauth/v2/auth`);
  u.search = new URLSearchParams({ response_type: 'token', client_id: ZOHO.clientId, scope: ZOHO.scope, redirect_uri: location.origin + location.pathname, prompt: 'consent' });
  location.assign(u);
}

/** COQL as the signed-in viewer. Throws {code:'needs_login'} when there is no valid token. */
export async function zohoCoql(select_query) {
  const t = store.get();
  if (!t) throw { code: 'needs_login' };
  const r = await fetch(`${t.api}/crm/v6/coql`, { method: 'POST', headers: { Authorization: `Zoho-oauthtoken ${t.token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ select_query }) });
  if (r.status === 401) { store.clear(); throw { code: 'needs_login' }; }
  if (r.status === 204) return { data: [] };
  if (!r.ok) throw { code: 'zoho_unavailable', message: await r.text() };
  return r.json();
}
