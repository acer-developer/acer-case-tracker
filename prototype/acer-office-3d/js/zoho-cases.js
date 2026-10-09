// Zoho CRM → ACER case list. Shared by the browser (Zoho connector) and server/zoho.mjs (OAuth).
// Pass a `coql(query)` function that returns `{ data: [...], info: { more_records } }` for one page.
//
// Chain: Accounts ← Deals.Account_Name ← Mandates.Deal_rec ← Entity.Mandate ← RC_Review.Entity
//        Entity ↔ Surveillances.Entity_rec · Invoice (CustomModule5001).Account_Name → Accounts

const person = (p) => (f) => [f[`${p}.first_name`], f[`${p}.last_name`]].filter(Boolean).join(' ') || null;

export const QUERIES = {
  Deals: ['Deal_Name', 'Account_Name', 'Account_Name.Account_Name', 'Stage', 'Owner.first_name', 'Owner.last_name', 'BD_User.first_name', 'BD_User.last_name', 'Type', 'Issue_Size_in_Cr', 'Modified_Time'],
  Mandates: ['Company', 'Mandate_Stage', 'Deal_rec', 'Compliance_user.first_name', 'Compliance_user.last_name', 'Instrument_Name', 'Issue_Size', 'Modified_Time'],
  Entity: ['Status', 'Entity_Type', 'Lead_Analyst.first_name', 'Lead_Analyst.last_name', 'Mandate', 'Instrument_Name', 'Issue_Size', 'ACER_Final_Rating', 'Short_term_Rating', 'Long_term_Rating_Outlook_Watch', 'IPO_Rating', 'Modified_Time'],
  RC_Review: ['Entity', 'RC_Review_Phase', 'Meeting_Date_Time', 'RC_Category', 'Committee_Final_Rating', 'Committee_final_Short_term_Rating', 'Committee_final_Long_term_Outlook_Watch', 'Commitee_Final_IPO_Rating', 'Modified_Time'],
  Surveillances: ['Status', 'Entity_rec', 'Modified_Time'],
  CustomModule5001: ['Account_Name', 'Potential_Name', 'Status', 'Grand_Total', 'Balance', 'Due_Date', 'Invoice_Date'],
};

// Zoho's INVALID_QUERY names the offending column in details.column_name — in the payload, an Error message, or err.result
const badColumn = (x) => {
  const s = typeof x === 'string' ? x : JSON.stringify(x ?? '');
  return /INVALID_QUERY/.test(s) ? s.match(/column_name\\?"?\s*[:=]\s*\\?"?([\w.$]+)/)?.[1] || null : null;
};

async function all(coql, module) {
  const cols = [...QUERIES[module]], rows = [];
  for (let offset = 0; offset < 20000;) {
    let page, bad;
    try {
      page = await coql(`select ${cols.join(', ')} from ${module} where id is not null limit ${offset}, 2000`);
      if (!page?.data) bad = badColumn(page);
    } catch (err) {
      bad = badColumn(err?.message) || badColumn(err?.result);
      if (!bad) throw err;
    }
    if (bad) {
      // a renamed/removed field: drop it and retry this page rather than losing the whole module
      const i = cols.indexOf(bad);
      if (i < 0 || cols.length === 1) throw new Error(`Zoho rejected ${module}.${bad}`);
      console.warn(`Zoho ${module}: dropping unknown field ${bad}`);
      cols.splice(i, 1);
      continue;
    }
    rows.push(...(page?.data || []));
    if (!page?.info?.more_records) break;
    offset += 2000;
  }
  return rows;
}

const acer = (r) => (r && !/^ACER\b/i.test(r) && !/^(Approved|Deferred|Satisfactory)$/i.test(r) ? `ACER ${r}` : r || null);
const id = (v) => (v && typeof v === 'object' ? v.id : v) || null;
const newest = (a, b, k) => (!a ? b : String(b[k] || '') > String(a[k] || '') ? b : a);

/** Reads Zoho now and returns { source, generated, cases }. */
export async function loadCases(coql) {
  const [deals, mandates, entities, rcs, survs, invoices] = await Promise.all(Object.keys(QUERIES).map((m) => all(coql, m)));

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
      ? { longTerm: acer(rc.Committee_Final_Rating), shortTerm: acer(rc.Committee_final_Short_term_Rating), ipo: rc.Commitee_Final_IPO_Rating, outlook: rc.Committee_final_Long_term_Outlook_Watch }
      : e && { longTerm: acer(e.ACER_Final_Rating), shortTerm: acer(e.Short_term_Rating), ipo: e.IPO_Rating, outlook: e.Long_term_Rating_Outlook_Watch };
    const amount = d.Issue_Size_in_Cr ? `₹${d.Issue_Size_in_Cr} Cr` : (m?.Issue_Size || e?.Issue_Size || '');
    const c = {
      id: d.id,
      company: d['Account_Name.Account_Name'] || d.Account_Name?.name || m?.Company || d.Deal_Name,
      caseType: d.Type || e?.Entity_Type || 'Rating Process',
      instrument: [e?.Instrument_Name || m?.Instrument_Name, amount].filter(Boolean).join(' · '),
      deal: { stage: d.Stage, owner: person('BD_User')(d) || person('Owner')(d) },
      entity: e ? { status: e.Status, leadAnalyst: person('Lead_Analyst')(e) } : null,
      rc: rc ? { phase: rc.RC_Review_Phase, meetingDate: rc.Meeting_Date_Time } : null,
      rating: rating || null,
      invoice: inv ? { total: Number(inv.Grand_Total) || 0, balance: Number(inv.Balance) || 0, dueDate: inv.Due_Date, status: inv.Status } : null,
      // surveillance status lives only in the Surveillances module
      surveillance: s ? { status: s.Status, rcPhase: rcs.find((r) => id(r.Entity) === e.id && r.Modified_Time > s.Modified_Time)?.RC_Review_Phase || null } : null,
      publishedDate: voted ? rc.Meeting_Date_Time : null,
    };
    if (m) c.mandate = { stage: m.Mandate_Stage, compliance: person('Compliance_user')(m) };
    return c;
  });
  return { source: 'zoho', generated: new Date().toISOString(), cases };
}
