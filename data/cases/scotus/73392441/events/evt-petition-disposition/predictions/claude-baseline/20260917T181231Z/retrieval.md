# Retrieval log

Mode: `forward` (no `DECIDED_BEFORE` clock). Five CourtListener MCP calls and one corpus query, under the advisory budget.

## Corpus (`fedcourts`, via the cell's corpus service)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
  Returned 20 recent granted rows, mostly substantive emergency applications and high-profile petitions; used as a shape check only, no prior was read with `--full`.

## Committed base rates

- `metrics/statpack.md`: *Modern discretionary-cert petitions by disposition*; *Modern cert petitions by originating circuit*; *Cert petitions by relist count (paid scored segment)*; *by CVSG status*; *by salience band*; *Petitions by originating court (incl. state courts)*; *SCOTUS cert petitions by Term*; *Segment base rate by salience band (sal-v4)* — pooled the `baseline` bracketed `reached` figure over OT2017–OT2024.

## CourtListener MCP

1. `search` type=d court=scotus docket_number=25-1310 → 0 results.
2. `search` type=d court=scotus q=Stafne (counsel-history check) → 0 results.
3. `call_endpoint` docket-entries docket=73392441 → 0 results (no entries mirrored for this supremecourt.gov docket).
4. `call_endpoint` dockets court=scotus docket_number=25-1310 → 1 result: id 73392441, filed 2026-05-26, `date_terminated: null`, `date_modified` 2026-07-08. Confirms the docket is pending and matches the snapshot.

No web searches. No material about this case's disposition was encountered.
