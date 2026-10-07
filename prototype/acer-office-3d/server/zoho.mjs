// Live Zoho CRM reader for the ACER office. Nothing is stored: every call reads Zoho via the API.
// Server-side only: credentials come from env vars and never reach the browser.
//
//   ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN   (Zoho API console → Self Client)
//   ZOHO_DC = in | com | eu | com.au | jp                    (default: in)
//
// Chain: Accounts ← Deals.Account_Name ← Mandates.Deal_rec ← Entity.Mandate ← RC_Review.Entity
//        Entity ↔ Surveillances.Entity_rec · Invoice (CustomModule5001).Account_Name → Accounts
const DC = process.env.ZOHO_DC || 'in';
const ACCOUNTS = `https://accounts.zoho.${DC}`, API = `https://www.zohoapis.${DC}/crm/v6`;

let token = null, tokenExp = 0;
async function accessToken() {
  if (token && Date.now() < tokenExp) return token;
  for (const k of ['ZOHO_CLIENT_ID', 'ZOHO_CLIENT_SECRET', 'ZOHO_REFRESH_TOKEN']) if (!process.env[k]) throw new Error(`Missing ${k}`);
  const body = new URLSearchParams({ grant_type: 'refresh_token', client_id: process.env.ZOHO_CLIENT_ID, client_secret: process.env.ZOHO_CLIENT_SECRET, refresh_token: process.env.ZOHO_REFRESH_TOKEN });
  const r = await fetch(`${ACCOUNTS}/oauth/v2/token`, { method: 'POST', body });
  const j = await r.json();
  if (!j.access_token) throw new Error(`Zoho token error: ${JSON.stringify(j)}`);
  token = j.access_token; tokenExp = Date.now() + (j.expires_in - 120) * 1000;
  return token;
}

async function zoho(path, init = {}) {
  const r = await fetch(API + path, { ...init, headers: { Authorization: `Zoho-oauthtoken ${await accessToken()}`, 'Content-Type': 'application/json', ...init.headers } });
  if (r.status === 204) return { data: [] };
  const j = await r.json();
  if (!r.ok) throw new Error(`${path}: ${r.status} ${JSON.stringify(j)}`);
  return j;
}

/** COQL with paging (2000 per page). */
async function coql(fields, module, where = 'id is not null') {
  const rows = [];
  for (let offset = 0; ; offset += 2000) {
    const j = await zoho('/coql', { method: 'POST', body: JSON.stringify({ select_query: `select ${fields.join(', ')} from ${module} where ${where} limit ${offset}, 2000` }) });
    rows.push(...(j.data || []));
    if (!j.info?.more_records) return rows;
  }
}

const id = (v) => (v && typeof v === 'object' ? v.id : v) || null;
const newest = (a, b, k) => (!a ? b : String(b[k] || '') > String(a[k] || '') ? b : a);

async function users() {
  const map = {};
  for (let page = 1; ; page++) {
    const j = await zoho(`/users?type=AllUsers&per_page=200&page=${page}`);
    for (const u of j.users || []) map[u.id] = u.full_name;
    if (!j.info?.more_records) return map;
  }
}

/** Reads Zoho now and returns { source, generated, cases }. */
export async function fetchCases() {
  const [U, deals, mandates, entities, rcs, survs, invoices] = await Promise.all([
    users(),
    coql(['Deal_Name', 'Account_Name', 'Account_Name.Account_Name', 'Stage', 'Owner', 'BD_User', 'Type', 'Instrument_Category', 'Issue_Size_in_Cr', 'Modified_Time'], 'Deals'),
    coql(['Name', 'Company', 'Mandate_Stage', 'Mandate_Type', 'Deal_rec', 'Compliance_user', 'Instrument_Name', 'Issue_Size', 'Approved_Date', 'Modified_Time'], 'Mandates'),
    coql(['Name', 'Status', 'Entity_Type', 'Lead_Analyst', 'Mandate', 'Instrument_Name', 'Issue_Size', 'ACER_Final_Rating', 'Short_term_Rating', 'Long_term_Rating_Outlook_Watch', 'IPO_Rating', 'Modified_Time'], 'Entity'),
    coql(['Name', 'Entity', 'RC_Review_Phase', 'Meeting_Date_Time', 'RC_Category', 'Committee_Final_Rating', 'Committee_final_Short_term_Rating', 'Committee_final_Long_term_Outlook_Watch', 'Commitee_Final_IPO_Rating', 'Modified_Time'], 'RC_Review'),
    coql(['Name', 'Status', 'Entity_rec', 'Lead_Analyst', 'Modified_Time'], 'Surveillances'),
    coql(['Name', 'Account_Name', 'Potential_Name', 'Status', 'Grand_Total', 'Balance', 'Due_Date', 'Invoice_Date'], 'CustomModule5001'),
  ]);
  const who = (v) => U[id(v)] || null;

  // index children by parent id, keeping the most recently modified record
  const mandateByDeal = {}, entityByMandate = {}, rcByEntity = {}, survByEntity = {}, invByDeal = {}, invByAccount = {};
  for (const m of mandates) { const k = id(m.Deal_rec); if (k) mandateByDeal[k] = newest(mandateByDeal[k], m, 'Modified_Time'); }
  for (const e of entities) { const k = id(e.Mandate); if (k) entityByMandate[k] = newest(entityByMandate[k], e, 'Modified_Time'); }
  for (const r of rcs) { const k = id(r.Entity); if (k && !/appeal/i.test(r.RC_Category || '')) rcByEntity[k] = newest(rcByEntity[k], r, 'Modified_Time'); }
  for (const s of survs) { const k = id(s.Entity_rec); if (k) survByEntity[k] = newest(survByEntity[k], s, 'Modified_Time'); }
  for (const v of invoices) {
    if (/void/i.test(v.Status || '')) continue;
    const d = id(v.Potential_Name), a = id(v.Account_Name);
    if (d) invByDeal[d] = newest(invByDeal[d], v, 'Invoice_Date');
    if (a) invByAccount[a] = newest(invByAccount[a], v, 'Invoice_Date');
  }

  const cases = deals.map((d) => {
    const m = mandateByDeal[d.id], e = m && entityByMandate[m.id], rc = e && rcByEntity[e.id], s = e && survByEntity[e.id];
    const inv = invByDeal[d.id] || invByAccount[id(d.Account_Name)];
    const voted = rc && /Voting Done|RC Completed/.test(rc.RC_Review_Phase || '');
    const rating = voted
      ? { longTerm: rc.Committee_Final_Rating, shortTerm: rc.Committee_final_Short_term_Rating, ipo: rc.Commitee_Final_IPO_Rating, outlook: rc.Committee_final_Long_term_Outlook_Watch }
      : e && { longTerm: e.ACER_Final_Rating, shortTerm: e.Short_term_Rating, ipo: e.IPO_Rating, outlook: e.Long_term_Rating_Outlook_Watch };
    const amount = d.Issue_Size_in_Cr ? `₹${d.Issue_Size_in_Cr} Cr` : (m?.Issue_Size || e?.Issue_Size || '');
    return {
      id: d.id,
      company: d['Account_Name.Account_Name'] || m?.Company || d.Deal_Name,
      caseType: d.Type || e?.Entity_Type || 'Rating Process',
      instrument: [e?.Instrument_Name || m?.Instrument_Name || d.Instrument_Category, amount].filter(Boolean).join(' · '),
      deal: { stage: d.Stage, owner: who(d.BD_User) || who(d.Owner) },
      mandate: m ? { stage: m.Mandate_Stage, compliance: who(m.Compliance_user) } : null,
      entity: e ? { status: e.Status, leadAnalyst: who(e.Lead_Analyst) } : null,
      rc: rc ? { phase: rc.RC_Review_Phase, meetingDate: rc.Meeting_Date_Time } : null,
      rating: rating || null,
      invoice: inv ? { total: Number(inv.Grand_Total) || 0, balance: Number(inv.Balance) || 0, dueDate: inv.Due_Date, status: inv.Status } : null,
      // surveillance status lives only in the Surveillances module
      surveillance: s ? { status: s.Status, rcPhase: rcs.find((r) => id(r.Entity) === e.id && r.Modified_Time > s.Modified_Time)?.RC_Review_Phase || null } : null,
      publishedDate: voted ? rc.Meeting_Date_Time : null,
    };
  });

  for (const c of cases) if (c.mandate === null) delete c.mandate;
  return { source: 'zoho', generated: new Date().toISOString(), cases };
}
