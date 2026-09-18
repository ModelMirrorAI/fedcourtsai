# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 12`
  stderr: `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
  Result: 12 rows, mostly 2026 emergency applications and OT2025 granted petitions with 2 to 22 distributions; no captions returned, and the structured filters cannot target mandamus or military-commission subject matter, so this served only as a sanity check on the shape of recent grants.
- Read the committed `metrics/statpack.md`: modern discretionary-cert disposition, originating-circuit, relist, CVSG, capital-case, and salience-band cuts, and the per-Term *Segment base rate by salience band (sal-v4)* table (pooled OT2017 to OT2025 `baseline` bracketed `reached` rate, about 5.0%).

## CourtListener MCP

- `search` (type docket, court scotus, docket_number 25-1335): 0 results.
- `search` (type docket, court scotus, q on party names, filed after 2025-06-01): 0 results.
- `call_endpoint dockets` (court scotus, docket_number 25-1335): found docket 73500235, *Walid bin 'Atash v. United States*, filed 2026-06-01, not terminated.
- `call_endpoint docket-entries` (docket 73500235): 0 entries indexed.

## Web

- WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1335.html`: bin 'Atash petition filed May 21, 2026; BIO filed Aug 26, 2026; distributed Sep 9 for the Sep 28, 2026 conference; reply filed Sep 9.
- WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/26-13.html`: confirmed no entries after Sep 9, 2026; the petition is pending.
- WebSearch: `"Khalid Shaikh Mohammad" certiorari petition Supreme Court 26-13 mandamus plea agreements Will v. United States`.
- WebSearch: `Vladeck amicus KSM cert petition mandamus 9/11 plea deal Supreme Court September 2026 conference`.
- WebFetch `https://www.courthousenews.com/nearly-25-years-after-the-attacks-supreme-court-asked-to-bring-closure-to-9-11-case/`: summary of the petition, BIO, and three amicus briefs; notes a military judge's suppression of the 2007 confessions and a trial date in June 2028.
- WebFetch of the reply brief PDF (`.../26-13%20Petitioner%20Reply%20Brief.pdf`); text extracted locally with pdftotext. Read the introduction and Part I (preservation, the reading of *Will*, the circuit-split rebuttal).

None of these surfaced the petition's disposition, which does not yet exist.
