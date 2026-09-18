# Retrieval log

Forward-mode cell; all retrieval below is permitted, and the post-snapshot docket check is
the ordinary forward shape rather than a breach.

## Corpus tooling

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned 2020s granted rows (several substantive applications plus cert grants); not
  informative for this petition and not used in the number.
- Base rates: committed `metrics/statpack.md` sections "Cert petitions by CVSG status (paid
  scored segment)", "Cert petitions by relist count (paid scored segment)", "Cert petitions
  by salience band", and "Segment base rate by salience band (sal-v4)".

## CourtListener MCP

- `call_endpoint` docket-entries, `docket=73279966`, ordered by date descending: returned
  `count: 0` (no entries held for this SCOTUS docket).

## Web

- WebSearch: `"25-828" GEO Group Nwauzor Solicitor General brief invitation Supreme Court`
  (surfaced the Supreme Court docket page, the SCOTUSblog case page, and the related
  petition in GEO Group v. Ferguson, No. 26-71).
- WebFetch: https://www.supremecourt.gov/docket/docketfiles/html/public/25-828.html
  (docket entries; shows "Sep 15 2026 Brief amicus curiae of United States filed").
- WebFetch: https://www.scotusblog.com/cases/geo-group-inc-v-nwauzor/ (timeline; no
  disposition listed).
- WebFetch/curl: https://www.supremecourt.gov/DocketPDF/26/26-71/416212/20260710143512335_26-%20Petition.pdf
  (identified the related petition GEO Group v. Ferguson, No. 26-71, filed July 10, 2026;
  read cover and QP only).
- curl: https://www.supremecourt.gov/DocketPDF/25/25-828/424228/20260915105245693_25-828cvsg_GEO_Nwauzor_final.pdf
  (Brief for the United States as amicus curiae, September 2026; read introduction,
  Part B "The Decision Below Warrants Review", and conclusion: recommends grant).
