# Retrieval log

- `uv run fedcourts query --help` (read the interface; no transfer line).
- `uv run fedcourts query --court scotus --docket-number 25-944` → `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned the Robinhood Markets v. Sodha row (case scotus/73280982) with counsel and the United States as amicus.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 3` → usage error (unknown era `modern`); re-issued as below.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 3` → `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Three recent GVRs (25-1269, 25-1367, 25-7569), used only as a sanity check of the GVR route.
- `metrics/statpack.md`: the sal-v4 segment base rate by salience band (read locally).
- WebFetch: supremecourt.gov docket for 25-944 (Robinhood). It shows the CVSG on 6/1/2026, the US brief on 10/7/2026, supplemental briefs, and distribution for the 11/6/2026 conference.
- WebFetch: supremecourt.gov docket for 25-1376 (this case). Entries after my snapshot: response extension, BIO filed 9/21/2026, reply filed 10/6/2026, distributed for the 11/6/2026 conference. No disposition.
- WebSearch: "Robinhood v. Sodha 25-944 Solicitor General brief recommends". It returned docket and news links, without the recommendation.
- WebFetch: 25-944 docket page again, to get the PDF URLs of the US brief and the supplemental briefs.
- WebFetch: the US amicus brief PDF (the summarizer could not read it; the binary was saved). I extracted its text locally with pypdf: the US recommends granting QP 1 (reformulated) and denying QP 2.
