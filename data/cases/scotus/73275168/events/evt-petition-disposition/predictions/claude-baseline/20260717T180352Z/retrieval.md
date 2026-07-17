# Retrieval log — scotus/73275168 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Mode: `forward` (unrestricted retrieval per the leakage doctrine; no query sought
this case's own disposition — the docket shows it pending as of the 2026-07-17
snapshot).

## Committed base rates

- `metrics/statpack.md` and `metrics/statpack.json` — modern discretionary-cert base
  rates, relist-count buckets, CVSG cut, originating-circuit cut, per-Term
  per-fee-class grant rates. Note: the "Segment base rate by salience band" section
  referenced in the predict prompt is not present in the committed statpack.

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   — stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`. Used to confirm the
   corpus's live-slice recency (grants dated through 2026-06-30) and inspect
   granted-case field shape (distribution counts, salience scores).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3`
   — stderr: `ranged corpus reads: 145 GET(s), 37879808 byte(s)`. Full-field
   inspection of the same rows.

## CourtListener MCP lookups

None (the provisioned snapshot and documents plus web retrieval sufficed).

## Web searches / fetches

1. WebSearch: `Supreme Court cert granted Sentencing Guidelines commentary deference
   Kisor Stinson 2026` — surfaced the April 20, 2026 cert grant in Beaird v. United
   States, No. 25-5343 (QP: whether Stinson still correctly states the deference rule
   for Guidelines commentary), and the later appointment of an amicus to defend
   Stinson.
2. WebFetch: https://sentencinglawandpolicy.wordpress.com/2026/04/20/supreme-court-grants-cert-on-long-simmering-issue-of-whether-guideline-commentary-should-still-garner-deference-from-courts/
   — confirmed the Beaird QP and grant date.
3. WebSearch: `"Poore" "25-227" Supreme Court relist Beaird held` — SCOTUSblog Relist
   Watch coverage tracking Poore as a serial relist with Beaird riding tandem.
4. WebFetch: https://www.scotusblog.com/2026/04/seven-relists-walk-into-a-bar/ —
   confirmed Beaird was granted after five relists, Poore relisted nine times, and
   Relist Watch's expectation that Poore "presumably awaits life as a hold."

## Provisioned inputs

- `record/snapshots/2026-07-17.json` (baseline docket snapshot)
- `record/documents/questions-presented.txt`, `petition.txt` (76 pp.),
  `brief-in-opposition.txt` (27 pp.), per `documents.json` (no truncation, no
  empty-text documents)
- `events/evt-petition-disposition/event.yaml`, `record/context.json`
