# Retrieval log — scotus/73277388 evt-petition-disposition (claude-baseline, 20260713T234230Z)

Mode: `forward` (pending case; retrieval unrestricted). All calls below were
about base rates, priors, and the companion petition — never this case's own
outcome (which does not exist yet).

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "563 U.S. 333" --citation "581 U.S. 246" --citation "9 U.S.C. § 2" --limit 8`
  — sought resolved FAA-preemption cert priors; **0 rows returned**.
  `ranged corpus reads: 409 GET(s), 107151360 byte(s)`
- `uv run fedcourts query --court scotus --citation "9 U.S.C." --limit 8`
  — broader FAA-citation retry; **0 rows returned**.
  `ranged corpus reads: 409 GET(s), 107151360 byte(s)`
- Read the committed `metrics/statpack.md` for base rates (modern
  discretionary-cert disposition split, originating-circuit, relist, CVSG,
  and per-Term cuts).

## CourtListener MCP

- `search` (dockets, scotus, q=`"Johnson" "Continental Finance"`) — locate the
  companion petition No. 25-34; 0 hits via search index.
- `search` (dockets, q=`"Continental Finance"`, docket_number=25-34) — 0 hits.
- `call_endpoint` `dockets` (court=scotus, docket_number=25-34) — found
  docket 73272764, *Continental Finance Company, LLC v. Tiffany Johnson*,
  filed 2025-07-10, `date_terminated`/`date_cert_granted`/`date_cert_denied`
  all null (record last modified 2026-05-07): companion still pending.
- `call_endpoint` `docket-entries` (docket=73272764) — 0 entries (CourtListener
  carries no entry-level data for this SCOTUS docket).
- `call_endpoint` `dockets` (id=73272764, full record) — confirmed CA4 origin
  (Nos. 23-2047/23-2049, judgment 2025-03-11, rehearing denied 2025-04-08) and
  pending status.

## Web (engine-surfaced)

- WebSearch: `Continental Finance v. Johnson 25-34 Supreme Court cert petition arbitration Maryland consideration`
  — background on the companion case (4th Cir. Nos. 23-2047/23-2049; petition
  filed July 2025).
- WebSearch: `"25-34" Continental Finance Johnson certiorari granted denied conference 2026`
  — no grant/denial of 25-34 found in 2026 order lists surfaced; also surfaced
  ABA Banking Journal item that the Court declined the related Conti
  NBA-preemption petition in May 2026.
- WebSearch: `Continental Finance Johnson Supreme Court CVSG solicitor general arbitration FAA Maryland Cheek relist`
  — could not confirm or rule out a CVSG in 25-34.
- WebSearch: `"25-311" OR "Genesis Financial" Supreme Court cert petition arbitration Ford Spring Oaks`
  — surfaced ABA and U.S. Chamber advocacy pages tracking this case.
- WebFetch: `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-34.html`
  — **failed (HTTP 403)**; supremecourt.gov blocks the fetcher. Did not use
  the REST fallback (no MCP failure occurred; this is outside CourtListener).
- WebFetch: `https://www.aba.com/advocacy/policy-analysis/genesis-financial-solutions-inc-v-ford`
  — ABA amicus page; no petition-status information beyond the amicus filing.

No other retrieval. Roughly 13 calls total, inside the ~25-call budget.
