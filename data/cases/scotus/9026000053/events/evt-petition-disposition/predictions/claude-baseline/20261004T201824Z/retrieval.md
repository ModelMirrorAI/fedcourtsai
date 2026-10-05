# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 9026000053 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 8` → `ranged corpus reads: 42 GET(s), 11010048 byte(s)`. Returned recent GVR rows (the Monsanto glyphosate holds GVR'd 2026-06-30, several criminal holds), confirming the hold-then-GVR shape and that the corpus labels such dispositions `gvr`.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6` → `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache).
- `uv run fedcourts open-events --court scotus --docket 9025001383` → no output; the corpus does not track Town of Vinton (25-1383). Also checked that no `data/cases/scotus/9025001383` directory exists.
- `metrics/statpack.md`: modern cert by disposition, by originating circuit, relist-count cut, CVSG cut, salience-band cut, per-Term table, and the `sal-v4` segment base rate by salience band.

## CourtListener MCP

- `search` (type `d`, court `scotus`, q `"Town of Vinton" Indian Harbor`) → 0 results.
- `call_endpoint` `dockets` (court `scotus`, docket_number `25-1383`) → docket id 73500284, "Indian Harbor Insurance Company v. Town of Vinton, Louisiana", filed 2026-06-15, not terminated.
- `call_endpoint` `docket-entries` (docket 73500284) → 0 entries (RECAP holds no entries for this SCOTUS docket).

## Web

- supremecourt.gov docket page for 25-1383 (fetched twice, second with a cache-busting parameter): 16 entries, last dated Sep 9 2026 (petitioners' reply); response requested Jul 27 2026 after a Jul 2 waiver; distributed Jul 8 for 9/28/2026; amicus briefs Jul 10 and Jul 15; BIO Aug 26. No redistribution, no disposition.
- supremecourt.gov docket page for 26-53 (this case; fetched twice): 11 entries, last dated Aug 27 2026 ("Rescheduled"). No redistribution, no disposition. Matches the provisioned snapshot.
- One web search for commentary on 25-1383: surfaced the extension applications, the Fifth Circuit's Vinton opinion (noting the panel also held the Convention did not directly apply for want of a foreign party), and general GE Energy commentary. No outcome material.
