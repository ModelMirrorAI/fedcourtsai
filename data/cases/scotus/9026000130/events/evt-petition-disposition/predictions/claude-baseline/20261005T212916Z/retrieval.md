# Retrieval log

Mode: `forward` (pending petition). No search for this case's own disposition was made.

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   - `ranged corpus reads: 16 GET(s), 4063232 byte(s)`
   - Returned eight recent SCOTUS grants, mostly federal-party petitions and
     substantive emergency applications; none a close analog to a private CERCLA
     petition. Used only to confirm the corpus had nothing closer to offer.
2. `uv run fedcourts query --court scotus --citation "552 U.S. 1095" --citation "587 U.S. 1051"`
   (the two earlier Teck denials in this litigation)
   - `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Empty result with the corpus's own `note:` that only about 200 scotus rows carry
     any reporter citation, so this is a coverage gap rather than a missing case.

## Committed base rates

- `metrics/statpack.md`: modern discretionary-cert disposition table; cuts by
  originating circuit, relist count, CVSG status, capital marking, and salience band;
  the per-Term cert table; and the "Segment base rate by salience band (sal-v4)" table,
  from which the `high` band's bracketed `reached` figures for OT2017 through OT2025
  were pooled (about 35.5%, n=966).

## CourtListener MCP lookups

1. `search` (type `o`, court `ca9`, filed after 2025-01-01, query on the case caption
   and "natural resource damages cultural") — one result: Confederated Tribes of the
   Colville Reservation v. Teck Cominco Metals Ltd, No. 24-5565, filed 2025-09-03,
   published, cluster 10665433, opinion 11132020.
2. `read_document` (opinion 11132020, chunk 0 of 12 at 3,500 characters) — the caption
   page and staff summary: panel of Gould and Paez, Circuit Judges, and McShane, Chief
   District Judge (D. Or.) by designation; opinion by Judge Gould; argued April 17,
   2025. Not read further.

## Web searches

None.
