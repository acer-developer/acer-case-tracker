// ACER workflow rules — the single place that turns Zoho CRM statuses into dashboard stages.
// Zoho CRM stays the source of truth; this file only interprets the records.

export const ED_STAGES = ['Pitching', 'Pricing', 'Mandate', 'Rating WIP', 'Published'];
export const CRO_STAGES = ['Team Allocation', 'Data Collection', 'Analysis', 'Committee', 'Published', 'Surveillance'];

const DEAL_STAGE = {
  'Initiated': 'Pitching',
  'Proposal Sent': 'Pricing', 'Negotiation': 'Pricing', 'Price Approval': 'Pricing',
  'Sent to CCO': 'Mandate', 'Accounts Review': 'Mandate',
};
const MANDATE_STAGE = { 'Drafted': 'Mandate', 'Sent for Re-Work': 'Mandate', 'CCO Approved': 'Mandate' };
const ENTITY_CRO = {
  'LA Selected': 'Team Allocation',
  'WD Create': 'Data Collection', 'Send to Client': 'Data Collection', 'Resent to Client': 'Data Collection',
  'COI Verified': 'Analysis', 'Rating Note Create': 'Analysis', 'LA Approval': 'Analysis',
};
const ENTITY_PUBLISHED = new Set(['CRO Approved', 'Rating Record Created', 'Crt. Surveillance', 'Surveillance Created']);
const RC_COMMITTEE = new Set(['RC Selection', 'Meeting Scheduled', 'RC Agenda', 'RC Meeting Done', 'Voting Process Initiate']);
const SURV_CRO = {
  'Rating Initiate': 'Team Allocation', 'New': 'Team Allocation',
  'WD Create': 'Data Collection', 'Send to Client': 'Data Collection', 'Resent to Client': 'Data Collection',
  'COI Verified': 'Analysis', 'Rating Note Create': 'Analysis', 'LA Approval': 'Analysis',
};

/** Paid amount from a Zoho Books invoice: total − balance. */
export function payment(inv) {
  if (!inv) return { status: 'No invoice', paid: 0 };
  const paid = (inv.total || 0) - (inv.balance || 0);
  let status = paid <= 0 ? 'Unpaid' : inv.balance > 0 ? 'Partially Paid' : 'Paid';
  if (inv.balance > 0 && inv.dueDate && new Date(inv.dueDate) < new Date()) status = 'Overdue';
  return { status, paid };
}

/** Where a case is, in both views. Returns null for hidden cases (deal lost, mandate dropped). */
export function classify(c) {
  const deal = c.deal || {}, mandate = c.mandate, entity = c.entity, rc = c.rc, surv = c.surveillance;
  if (deal.stage === 'Lost') return null;
  if (mandate && mandate.stage === 'Dropped' && !entity) return null;
  let ed = null, cro = null, status = '', withWhom = '', ratingVisible = false, step = 0;

  if (!mandate && !entity) {
    ed = DEAL_STAGE[deal.stage] || (deal.stage === 'All Done' ? 'Mandate' : 'Pitching');
    status = deal.stage || 'Initiated';
    withWhom = ed === 'Mandate' ? 'Compliance user' : 'Deal owner';
    step = ed === 'Pitching' ? 0 : ed === 'Pricing' ? 2 : 3;
  } else if (mandate && !entity) {
    ed = MANDATE_STAGE[mandate.stage] || 'Mandate'; status = mandate.stage; withWhom = 'Compliance user'; step = 3;
  } else {
    const es = entity.status;
    if (ENTITY_PUBLISHED.has(es)) { ed = 'Published'; cro = 'Published'; status = es; withWhom = 'CRO'; step = 7; ratingVisible = true; }
    else if (rc && (RC_COMMITTEE.has(rc.phase) || rc.phase === 'Voting Done' || rc.phase === 'RC Completed')) {
      ed = rc.phase === 'RC Completed' ? 'Published' : 'Rating WIP';
      cro = rc.phase === 'RC Completed' ? 'Published' : 'Committee';
      status = rc.phase; withWhom = rc.phase === 'Voting Done' ? 'CRO' : 'Committee';
      ratingVisible = rc.phase === 'Voting Done' || rc.phase === 'RC Completed';
      step = cro === 'Published' ? 7 : 6;
    } else if (ENTITY_CRO[es]) {
      ed = 'Rating WIP'; cro = ENTITY_CRO[es]; status = es;
      withWhom = es === 'Send to Client' || es === 'Resent to Client' ? 'Client' : 'Lead analyst';
      step = es === 'LA Selected' ? 4 : 5;
    } else { ed = 'Rating WIP'; cro = 'Analysis'; status = es || 'Unknown'; withWhom = 'Lead analyst'; step = 5; }
  }
  // Surveillance (CRO only) comes from the Surveillance module — its own status and its own RC review.
  let survStage = null;
  if (surv) {
    const ss = surv.status, sp = surv.rcPhase;
    if (ss === 'CRO Approved') survStage = 'Surveillance completed';
    else if (sp === 'Voting Done') survStage = 'Committee (with CRO)';
    else if (sp) survStage = 'Committee';
    else survStage = SURV_CRO[ss] || 'Team Allocation';
  }
  return { ed, cro: cro || (ed === 'Rating WIP' ? 'Analysis' : null), status, withWhom, step, ratingVisible, survStage, pay: payment(c.invoice) };
}

/** Fixed-rule alerts (no AI). */
export function alerts(c) {
  const out = [], deal = c.deal || {}, pay = payment(c.invoice);
  if (pay.status === 'Paid' && deal.stage === 'Initiated') out.push({ view: 'ED', text: 'Paid but deal still Initiated', open: 'Deal' });
  if (deal.stage === 'Lost' && c.invoice) out.push({ view: 'ED', text: 'Deal lost but invoiced', open: 'Deal' });
  if (c.rc && c.rc.phase === 'Voting Done' && !(c.entity && ENTITY_PUBLISHED.has(c.entity.status))) out.push({ view: 'CRO', text: 'RC voted, not closed', open: 'RC Review' });
  const k = classify(c);
  if (k && k.ed === 'Published' && !c.publishedDate && !(c.rc && c.rc.meetingDate)) out.push({ view: 'CRO', text: 'Published date missing', open: 'RC Review / Entity' });
  if (c.entity && c.entity.status && !ENTITY_CRO[c.entity.status] && !ENTITY_PUBLISHED.has(c.entity.status)) out.push({ view: 'CRO', text: `Unknown status "${c.entity.status}"`, open: 'Entity' });
  return out;
}

export function ratingText(c) {
  const r = c.rating || {};
  return [r.longTerm, r.shortTerm, r.ipo].filter(Boolean).join(' / ') + (r.outlook ? ` | ${r.outlook}` : '');
}
