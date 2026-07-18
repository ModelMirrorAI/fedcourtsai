# Retrieval log — scotus/73391039 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Mode: `forward` (pending petition; retrieval unrestricted). Nothing surfaced
suggested this case's disposition exists — the snapshot shows distribution for
a conference (September 28, 2026) that post-dates this run.

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 5`
  - stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
  - Generic recent-era priors (no free-text filter exists); confirmed the
    shape of recent grant-side dockets (multiple distributions, counseled
    petitions) versus this cell. Not directly load-bearing.
- Committed `metrics/statpack.md` (modern discretionary-cert base rates:
  disposition, originating circuit, relist count, CVSG, per-Term table) and
  `metrics/statpack.json` (Term 2025 per-fee-class grant rates: paid ~5.4%,
  IFP ~1.1%). These are the base-rate anchors used in `reasoning.md`.

## CourtListener MCP lookups

1. `search` (type=o, court=ca11, q="Foley v. Orange County", filed_after
   2024-01-01) — 0 results (opinion not in the opinions index).
2. `search` (type=o, court=ca11, docket_number=24-14143) — 0 results.
3. `search` (type=d, court=ca11, docket_number=24-14143) — found the
   Eleventh Circuit docket: *David Foley, Jr. v. Orange County*, docket id
   71794325.
4. `get_endpoint_item` (dockets/71794325) — appeal from the U.S. District
   Court for the Middle District of Florida; no nature-of-suit metadata.
5. `search` (type=r, court=flmd, q=Foley "Orange County") — identified the
   underlying district litigation: 6:22-cv-00456 *Foley v. Orange County*
   (42 U.S.C. § 1983, filed 2022) and the earlier 6:12-cv-00269 (2012,
   constitutional challenge to a state/county enactment), plus a new
   6:26-cv-00337 filed February 2026 — a repeat-litigant pattern.
6. `search` (type=r, court=flmd, party_name=Foley, filed_after 2023-01-01) —
   no other relevant district case; corroborates 6:22-cv-00456 as the source
   of appeal 24-14143.
7. `call_endpoint` (docket-entries, docket=71794325) — one entry: "Opinion
   Issued" October 29, 2025 (document not available; no text).
8. `call_endpoint` (docket-entries, docket=63132990, newest first) — 291
   entries, active into 2026; September 4, 2025 "JUDGMENT on attorney fees"
   entry.

## Web searches

None.
