# Retrieval log

- `uv run fedcourts query --help`: usage text.
- `uv run fedcourts query --court scotus --docket-number 26-159`: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Protopapas v. Whittaker Clark & Daniels (CA3); open, 0 distributions.
- `uv run fedcourts query --court scotus --docket-number 26-263`: `ranged corpus reads: 0 GET(s), 0 byte(s)`. Official Committee of Talc Claimants v. Whittaker (CA3); open, 0 distributions.
- `uv run fedcourts query --court scotus --docket-number 26-350`: `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Altrad v. Cape, the Vide companion.
- The same two docket-number queries for 26-159 and 26-263, re-run to print fields (stderr discarded; the read lines were not captured).
- WebFetch of the supremecourt.gov docket for 26-159: petition filed Jul 24, BIO Aug 25, reply Sep 4; no distribution shown.
- Read `metrics/statpack.md` (band table, relist, CVSG and amicus cuts).
