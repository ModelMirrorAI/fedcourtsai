# Retrieval log

Beyond the provisioned snapshot, context, and event definition:

## Committed base rates

- `metrics/statpack.md`, "The interim docket (applications)" section — pooled
  the strictly-prior resolved substantive slice (Terms 2025 + 2024: 227
  resolved, 30 granted → 13.2%) as the scored baseline.

## Corpus

- `uv run fedcourts query --court scotus --include-applications --limit 40`
  — stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`. Returned recent
  Term-2026 application-docket rows (26A2xx), mostly time-extension
  applications whose routine grants are not informative for a substantive
  injunction ask; used only to confirm the docket neighborhood, not as an
  anchor.

## CourtListener MCP

1. `search` (type=d, q="Cassandra Perkins", courts ca11+gand) — found the
   applicant's two pro se N.D. Ga. ADA employment suits: Perkins v. United
   Health Group Optum (1:24-cv-01551) and Perkins v. Ascension Health
   (1:24-cv-05425), both before Judge Leigh Martin May.
2. `search` (type=d, docket_number=25-12952, court=ca11) — no RECAP docket for
   the Eleventh Circuit case the snapshot names; could not read the order
   below.
3. `call_endpoint` docket-entries for docket 69413754 (Ascension Health) —
   RECAP holds only the 2024-11-25 IFP application entries.
4. `call_endpoint` docket-entries for docket 68434583 (United Health Group
   Optum) — RECAP holds only the 2024-04-11 IFP application entries.

No web searches. This case's own disposition was not sought and did not
surface.
