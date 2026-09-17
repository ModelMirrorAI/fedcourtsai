# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts query --court scotus --era 2020s --limit 12` — 12 recent resolved SCOTUS cert
  priors (September 2026 denials, dismissals, three grants), used only as a sanity check on the live
  slice's shape; none topically related. stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`.
- Base rates from the committed `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "by originating circuit" (ca7), "by relist count (paid scored segment)", "by CVSG
  status", "Segment base rate by salience band (sal-v4)" pooled over OT2017–OT2024.

## CourtListener MCP

- `search` type=d court=scotus docket_number=25-1158 → 0 results; same for 25-1163 → 0 results.
- `search` type=o court=ca7 case_name="O'Donnell v. City of Chicago" filed_after 2025-12-01 →
  cluster 10762963, opinion 11229548 (No. 24-2946, decided 2025-12-22, Kirsch, J.).
- `read_document` opinion_id=11229548 — the full Seventh Circuit opinion (≈16k chars).
- `search` type=d court=scotus q=`Hadley "South Bend"` → 0; q=`Pena "Los Angeles"` → 0.
- `call_endpoint` dockets court=scotus docket_number=25-1158 → docket 73281642, *Amy Hadley v. City
  of South Bend*, filed 2026-04-08, not terminated; docket_number=25-1163 → docket 73281647, *Carlos
  Pena v. City of Los Angeles*, filed 2026-04-09, not terminated.
- `call_endpoint` docket-entries docket=73281642 and docket=73281647 → 0 entries each (CourtListener
  carries no entries for these SCOTUS dockets).
- `get_endpoint_item` dockets 73281642 (one call errored on an invalid field name and was retried) and
  73281647 → no cert-granted / cert-denied dates, no last-filing date.

## Web

- WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1158.html` — Hadley docket:
  petition filed 2026-04-06, five amicus briefs (May 7–8), BIO 2026-06-08, reply 2026-06-22,
  DISTRIBUTED for Conference of 9/28/2026 on 2026-06-24. No response request, no CVSG, no relist.
- WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1163.html` — Pena docket:
  petition filed 2026-04-06, five amicus briefs (May 8–11), BIO 2026-06-10, reply 2026-06-23,
  DISTRIBUTED for Conference of 9/28/2026 on 2026-06-24.
- WebSearch "Pung v. Isabella County Supreme Court June 23 2026 opinion holding" — confirmed the BIO's
  citation: a unanimous tax-sale just-compensation holding (sale price, not hypothetical fair market
  value, is the baseline). Not about this case.

Nothing retrieved concerned this petition's own disposition; the September 28, 2026 conference
postdates this run.
