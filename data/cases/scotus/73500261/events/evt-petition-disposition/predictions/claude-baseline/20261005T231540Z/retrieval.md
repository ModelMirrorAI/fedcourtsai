# Retrieval log

## Corpus
- `uv run fedcourts query --court scotus --era 2020s --limit 12` → `ranged corpus reads: 6 GET(s), 1572864 byte(s)`. Returned recent OT2025 paid petitions resolved at the Sept. 28 conference; used only to confirm the shape of once-distributed petitions, no close analogue to a conditional cross-petition.

## Committed statpack
- `metrics/statpack.md`: modern discretionary-cert base rate; relist-count and CVSG cuts (paid scored segment); salience-band table; per-Term "Segment base rate by salience band (sal-v4)", from which the state band's bracketed reached rate was pooled over OT2017–OT2024.
- `metrics/statpack.json`: searched for a cert-order route baseline; found only the merits section's `cert_order_excluded` counts.

## CourtListener MCP
- `search` (type docket, court scotus, q "Nathan Alamo Heights") → 0 results.
- `search` (type docket, court scotus, q "Roake Brumley") → 0 results.
- `call_endpoint` dockets with a `case_name__icontains` filter, twice → endpoint validation error (filter not accepted); not retried.

## Web
- WebSearch: "Nathan v. Alamo Heights certiorari petition Supreme Court Ten Commandments Texas S.B. 10 2026" → ACLU/AU pages confirming the Texas plaintiffs' petition filed Aug. 2026.
- WebSearch: "Roake v. Brumley Supreme Court petition certiorari plaintiffs filed August 2026 …" → SCOTUSblog 25-1360 page, supremecourt.gov docket, application 26A15 PDF.
- WebSearch: "Nathan v. Alamo Heights Supreme Court docket 26- brief in opposition …" → docket No. 26-257; response extended to Oct. 28, 2026.
- WebSearch: "Stinson v. Arkansas Eighth Circuit Ten Commandments oral argument 2026" → Eighth Circuit argued Sept. 22, 2026 (Shepherd, Grasz, Stras).
- WebSearch: "Louisiana families Roake petition Supreme Court …" → no petition by the Roake plaintiffs found.
- WebFetch: scotusblog.com/cases/nathan-v-alamo-heights-independent-school-district/ → 26-257 timeline.
- WebFetch: scotusblog.com/cases/brumley-v-roake/ → 25-1360 timeline (matches the provisioned snapshot).
- WebFetch: supremecourt.gov docket 26-257 → proceedings, counsel, response due Oct. 28, 2026; one amicus brief (Sept. 28).
- WebFetch: supremecourt.gov application 26A15 PDF → unreadable (binary); identity established from the 26-257 docket instead (the Nathan plaintiffs' extension).
- WebFetch: supremecourt.gov docket 25A1239 → Roake plaintiffs' extension to petition, granted to June 20, 2026.

No search surfaced a disposition of this petition; none exists as of the snapshot.
