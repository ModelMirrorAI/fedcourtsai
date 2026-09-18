# Retrieval log

## Corpus (fedcourts query, service backend)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` — `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Shape check on recent granted rows.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 1` — `ranged corpus reads: 0 GET(s), 0 byte(s)`. Field inventory of a prior row.
- `uv run fedcourts query --court scotus --era 2020s --limit 400` — `ranged corpus reads: 19 GET(s), 4980736 byte(s)`. Filtered locally to rows with a `cvsg_date`: 6 rows (4 denied, 2 granted); too thin to condition on, used for shape only.

## Statpack

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (pooled `high` bracketed `reached` over OT2017–OT2024: 35.0%, n=898).

## CourtListener MCP

- `get_endpoint_item dockets 73279035` — docket metadata (no `date_terminated`; modified 2026-09-16).
- `call_endpoint docket-entries docket=73279035` — returned 0 entries (SCOTUS dockets carry no RECAP entries).

## Web

- WebSearch: "Aldridge v. Regions Bank 25-590 Solicitor General brief surcharge ERISA" — surfaced the SCOTUSblog case page and the fact that the SG filed on 2026-08-31.
- WebSearch: "Aramark Aetna Fifth Circuit surcharge 502(a)(3) certiorari petition Supreme Court 2026" — background on Aramark v. Aetna (5th Cir.) and Labor Department amicus participation.
- WebFetch: https://www.supremecourt.gov/docket/docketfiles/html/public/25-590.html — current docket: SG brief filed 2026-08-31; distributed 2026-09-16 for the 2026-10-09 conference; petitioners' supplemental reply filed 2026-09-16; no disposition.
- WebFetch: https://www.scotusblog.com/cases/aldridge-v-regions-bank/ — case page, same docket state.
- WebFetch: https://www.supremecourt.gov/DocketPDF/25/25-590/422539/20260831142837907_25-590_Aldridge_Final.pdf — the SG's amicus brief (text extracted locally with pypdf): recommends denial; Sixth Circuit erred on QP1 but poor vehicle (top-hat plan, disputed fiduciary status); preemption holding correct; Aramark vacated for en banc rehearing.
