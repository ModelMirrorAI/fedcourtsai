# Retrieval log — scotus/73274796 evt-petition-disposition (claude-baseline, 20260717T180352Z)

Mode: `forward` (retrieval unrestricted; all context below predates any disposition —
the petition is confirmed still pending).

## Provisioned inputs read

- `record/snapshots/2026-07-17.json` (baseline docket snapshot, SCOTUS No. 25-113)
- `record/documents/questions-presented.txt`, `petition.txt` (217 pp., truncated),
  `brief-in-opposition.txt` (32 pp.); `documents.json`
- `events/evt-petition-disposition/event.yaml`, `record/context.json`
- Committed base rates: `metrics/statpack.md` (modern discretionary-cert
  disposition, CVSG cut, relist cut, originating-circuit cut, per-Term table).
  Note: the statpack.md in this checkout carries no "Segment base rate by
  salience band" table, so no band anchor was available.

## Corpus lookups (fedcourts CLI)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s`
   - stderr: `ranged corpus reads: 145 GET(s), 37879808 byte(s)`
   - Used for recent granted-petition priors; surfaced *Hoffmann v. WBI Energy*
     (25-159), a CVSG'd petition distributed for the same 6/25/2026 conference
     and granted 6/29/2026 — the contrast case for Renteria's post-conference
     silence.
   - (The command was re-run once with identical arguments solely to recapture
     the stderr transfer line; the warm second run's line is the one recorded
     above.)

## Web lookups (engine web tools)

2. WebSearch: `Renteria v. New Mexico Office of Superintendent of Insurance
   solicitor general brief 25-113 health care sharing ministry`
   - Result: DOJ OSG brief listing shows the SG's CVSG response (filed May 26,
     2026, updated June 9, 2026) recommends **holding the petition pending
     St. Mary Catholic Parish v. Roy, No. 25-581** (overlapping QP1), then
     disposing of it as appropriate.
3. WebFetch: `https://www.justice.gov/osg/brief/renteria-v-new-mexico-office-superintendent-insurance`
   - HTTP 403 (blocked); recommendation taken from the search-result summary of
     the same page instead.
4. WebSearch: `"St. Mary Catholic Parish" v. Roy Supreme Court 25-581 cert granted`
   - Result: cert **granted April 20, 2026**; Tenth Circuit free-exercise case on
     *Smith* general applicability (Colorado universal-preschool
     nondiscrimination condition); OT2026 argument.
5. WebFetch: `https://www.supremecourt.gov/docket/docketfiles/html/public/25-113.html`
   - HTTP 403 (supremecourt.gov blocks the fetcher).
6. WebFetch: `https://certpool.com/dockets/25-113`
   - Confirms the petition is **still pending** as of today: latest entry is the
     June 9, 2026 supplemental brief / 6/25/2026 conference distribution; no
     order after the 6/25 conference.

## CourtListener MCP

Not used — the supremecourt.gov snapshot was fresh (created 7/16/2026) and the
docket-status check was satisfied via the web lookups above.

Total retrieval calls: 1 corpus query (+1 stderr recapture) and 5 web
lookups, within the ~25-call budget.
