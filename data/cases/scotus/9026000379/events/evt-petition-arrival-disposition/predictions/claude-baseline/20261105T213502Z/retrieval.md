# Retrieval log
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-379.html: live docket. Shows cert before judgment, the extension granted in part to Dec 8, and the Iowa et al. amicus brief on Oct 20. No disposition.
- WebSearch "Genalo v. D.C. Second Circuit ICE petition certiorari Solicitor General": Bloomberg Law and Fox News coverage of the stand-in vehicle after the *Genalo v. Black* pardon.
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/25-886.html: *Genalo v. Black*. Cert granted June 15, 2026; argument set Oct 13; dismissed under Rule 46.1 on Sep 11, 2026.
- WebFetch of the Fox News print article: the QP characterization and the circuit-split framing.
- `uv run fedcourts query --docket-number 25-886`: usage error (needs `--court`). No rows.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`. Recent granted priors, including several SG petitions. Used as general context only.
- Read `metrics/statpack.md`, the salience-band table (sal-v7, `federal` column).
