# Retrieval log — scotus/73281063 evt-petition-disposition (claude-baseline, 20260717T072907Z)

Mode: `forward` (record/context.json). Beyond the provisioned snapshot and
documents, this cell consulted:

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert base rates (grant ~2.5–3.3%
  per recent Term), relist-count cuts (1 relist → 7.6% grant, 2 → 33.6%),
  originating-circuit (ca9) cut, per-Term table.

## Corpus (`fedcourts query`, ranged reads against the remote blob)

1. `uv run fedcourts query --court scotus --era 2020s --citation "570 U.S. 1"
   --citation "555 U.S. 488" --citation "594 U.S. 647"` — no rows returned.
   stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s` (default limit 20) —
   recent resolved SCOTUS priors; confirmed a 6/29/2026 conference with 6/30
   orders (grants/denials) that did not touch this docket.
   stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 200`
   then `--limit 1000`, grepping for the companion docket numbers — surfaced
   the corpus row for **25-1017 (RNC v. Mi Familia Vota): disposition
   `granted`, `date_cert_granted: 2026-06-29`, distributed 6/25, last live
   polled 2026-07-17**. 25-1019 and 25-1022 did not appear among returned
   rows. stderr for these two invocations was redirected/not captured; each
   `query` run reads the same remote blob (the captured runs each reported
   `ranged corpus reads: 420 GET(s), 110100480 byte(s)`).

## CourtListener MCP

4. `search` (type=d, court=scotus, docket_number=25-1017) — 0 results.
5. `search` (type=r, q="Republican National Committee" "Mi Familia Vota") — 0
   results (SCOTUS dockets are thin in the RECAP index).
6. `call_endpoint` dockets (court=scotus, docket_number=25-1017) — docket id
   73281056, RNC v. Mi Familia Vota, date_terminated null.
7. `call_endpoint` docket-entries (docket=73281056) — 0 entries.
8. `call_endpoint` dockets (court=scotus, docket_number=25-1019) — docket id
   73281059, Petersen v. Mi Familia Vota, date_terminated null.

## Web

9. WebSearch: "Supreme Court grants Republican National Committee v. Mi
   Familia Vota 25-1017 cert June 2026 Petersen 25-1019 Arizona 25-1022" —
   surfaced ballot-access.org (June 29, 2026) and SCOTUSblog case pages. The
   engine-generated summary claimed all three petitions were granted; this
   conflicted with the provisioned snapshot and was verified (next item)
   rather than relied on.
10. WebFetch of
    https://ballot-access.org/2026/06/29/u-s-supreme-court-agrees-to-hear-case-on-whether-states-can-require-voter-registration-applicants-to-attach-documents-proving-citizenship/
    — confirms the June 29, 2026 grant covers **25-1017 only**; the article
    says nothing about 25-1019 or 25-1022.

All retrieval about companion dockets 25-1017/25-1019 (pre-decision public
information about different petitions). This petition's own disposition was
not sought and does not exist; the snapshot (fetched 2026-07-16) shows it
pending after the 6/25/2026 conference.
