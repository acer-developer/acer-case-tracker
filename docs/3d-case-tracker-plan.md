# ACER 3D Case Floor — concept plan

Inspired by the "WareTrack" 3D warehouse demo (React + React Three Fiber, every object clickable, 3D as a view layer over an ordinary data model). We map the same idea onto ACER's rating-mandate lifecycle.

## Metaphor

| Warehouse demo | ACER case floor |
|---|---|
| Warehouse site | Office (Mumbai HQ, New Delhi, Kolkata) |
| Zones / docks | Lifecycle stages: Intake → Info Gathering → Analysis → Mgmt Meeting → Rating Committee → Letter & Acceptance → Published / Surveillance |
| Pallets / stock | Cases (one crate per mandate), coloured by SLA: green on track, amber at risk, red overdue vs SEBI TAT |
| Trucks / forklifts | Cases in transit between stages (conveyor) |
| Workers | Analysts; second view shows per-analyst desks with workload |
| KPI bar | Active mandates, overdue, at risk, avg TAT, committee slots this week, published MTD |

## Mockups

- `mockups/00-case-floor-game.svg` — animated game-style main view (open in a browser to see motion)
- `mockups/01-case-floor-overview.svg` — main floor with HUD, filters, selected-case panel, live event ticker
- `mockups/02-team-workload.svg` — analyst desks, floor tint = load, rebalance suggestions
- `mockups/03-architecture.svg` — data flow

## Architecture

Zoho CRM/Creator stays the source of truth. A thin Case API normalises mandates, runs the SLA engine, and pushes changes over WebSocket (Zoho webhooks + periodic COQL delta sync). The React client holds one store feeding both a plain 2D table and the R3F 3D scene. Write-backs (reassign, nudge) go through the API to Zoho.

## Phases

1. **Data model + 2D (2 wks)** — map Zoho fields to a Case model, SLA rules, table/kanban view. Validates data quality before any 3D.
2. **3D floor MVP (2–3 wks)** — R3F scene, stage buildings, instanced crates, click → detail panel, office switcher.
3. **Live + actions (2 wks)** — webhooks/WebSocket, event ticker, reassign/nudge write-backs, SSO + roles.
4. **Polish (1–2 wks)** — team workload view, wall-display mode, 2D fallback for low-power devices, audit log.

## Risks

- Stale or incomplete Zoho data makes the scene misleading — phase 1 must fix data hygiene first.
- 3D must stay a layer: every action must also be possible from the 2D view.
- Confidentiality: client names on wall displays need a masked mode.
