# Retrieval log — scotus/9526000370, evt-order-response-requested-disposition, claude-baseline, 20260927T182226Z

Mode: forward (no `DECIDED_BEFORE`; `--decided-before` not passed). About 22 retrieval calls.

## Provisioned inputs read

- `data/cases/scotus/9526000370/record/context.json`
- `data/cases/scotus/9526000370/record/snapshots/2026-09-18.json`
- `data/cases/scotus/9526000370/record/documents/documents.json` and `application.txt` (argument sections and the Ninth Circuit order in the appendix)
- `data/cases/scotus/9526000370/events/evt-order-response-requested-disposition/event.yaml` (and the sibling `evt-brief-response-disposition/event.yaml` for orientation)
- `metrics/statpack.md`, "The interim docket (applications)" section
- `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`

## Corpus lookups (`fedcourts query`, corpus service backend)

| # | command | stderr transfer line |
| --- | --- | --- |
| 1 | `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 15` | `ranged corpus reads: 7 GET(s), 1703936 byte(s)` |
| 2 | `uv run fedcourts query --court scotus --include-applications --disposition denied --limit 15` | `ranged corpus reads: 0 GET(s), 0 byte(s)` |
| 3 | `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 60` | `ranged corpus reads: 2 GET(s), 524288 byte(s)` |
| 4 | `uv run fedcourts query --court scotus --include-applications --disposition denied --limit 80` | `ranged corpus reads: 7 GET(s), 1835008 byte(s)` |
| 5 | `uv run fedcourts query --court scotus --include-applications --limit 200` | `ranged corpus reads: 0 GET(s), 0 byte(s)` |
| 6 | `uv run fedcourts query --court scotus --include-applications --limit 3000` | failed: `invalid corpus service request ... limit Input should be less than or equal to 500`; no rows, no transfer line |
| 7 | `uv run fedcourts query --court scotus --include-applications --limit 900` | failed the same way |
| 8 | `uv run fedcourts query --court scotus --include-applications --limit 500` | `ranged corpus reads: 26 GET(s), 6815744 byte(s)` |
| 9 | `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 500` | `ranged corpus reads: 9 GET(s), 2359296 byte(s)` |
| 10 | `uv run fedcourts query --court scotus --include-applications --disposition denied --limit 500` | `ranged corpus reads: 0 GET(s), 0 byte(s)` |
| 11 | `uv run fedcourts query --court scotus --include-applications --disposition withdrawn --limit 200` | `ranged corpus reads: 715 GET(s), 187301888 byte(s)` |
| 12 | `uv run fedcourts query --court scotus --include-applications --disposition dismissed --limit 200` | `ranged corpus reads: 63 GET(s), 16515072 byte(s)` |

Rows from 8–12 were deduplicated by `case_id` (1,219 unique rows, 99 resolved substantive applications) and filtered client-side on `application_kind`, `disposition`, `response_requested`, `referred_to_court`, and `amicus_briefs` to build the conditioned table in `reasoning.md`. No `--full` hydration.

## CourtListener MCP lookups

1. `search` type=d, q="Jensen v. Thornell", court=[ca9, azd] — located D. Ariz. docket 2:12-cv-00601 (id 4133612).
2. `search` type=d, q="Jensen v. Thornell", court=ca9 — located CA9 dockets 26-5060 (id 73734346), 26-1746 (id 73291278), 25-4365.
3. `call_endpoint docket-entries` docket=4133612, newest first, 15 rows — confirmed the September 10 order lifting the stay of the appointment order effective October 19, 2026, and no later dispositive entry.
4. `call_endpoint docket-entries` docket=73734346 (CA9 26-5060), 25 rows — September 1 order denying stay (Thomas, Berzon; Forrest partial dissent), expedited schedule, opening brief filed September 15–16, legislative leaders' amicus.
5. `call_endpoint docket-entries` docket=73291278 (CA9 26-1746), 25 rows — same order mirrored; earlier stay of appellate proceedings pending the receivership decision.

## Web

1. `WebSearch` "Arizona prison healthcare receivership Supreme Court stay application Thornell Jensen Kagan" — news coverage of the September 16 filing (Arizona Capitol Times, AZ Mirror, KJZZ, tucson.com); no disposition reported.
2. `WebSearch` "\"26A370\" Thornell Jensen Supreme Court" — surfaced the supremecourt.gov docket page and the application PDF; no disposition reported.
3. `WebFetch` https://www.supremecourt.gov/docket/docketfiles/html/public/26A370.html — entries: Sep 16 application submitted to Justice Kagan; Sep 18 response requested, due Sep 25; Sep 25 response filed by respondents. No referral, amicus, or disposition entries.
4. `WebFetch` same page for hyperlinks — obtained the opposition PDF URL.
5. `WebFetch` https://www.supremecourt.gov/DocketPDF/26/26A370/425682/20260925153133136_20260925%20Respondents%20Stay%20Opp%20Jensen%20v%20Thornell.pdf — the fetcher could not read the PDF text; the saved binary was extracted locally with pypdf (48 pages) and the introduction, background, argument I (certworthiness), and argument III (equities) sections were read.

## Not consulted

Nothing under `data/qp-topics/`; no outcome file; no search for this application's disposition beyond its own docket page, which shows none.
