# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 9526000370 --event evt-motion-disposition --role predictor` — path resolution only.
- `uv run fedcourts query --court scotus --include-applications --disposition granted --era 2020s --limit 12` — `ranged corpus reads: 7 GET(s), 1703936 byte(s)`. Returned mostly time-extension grants plus two substantive grants (26A308 DHS v. League of Women Voters; 26A388 People Not Politicians v. Onder), both with response requested and referral.
- `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 15` — `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache).
- `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 60` (filtered locally to `application_kind == substantive`) — `ranged corpus reads: 0 GET(s), 0 byte(s)`. Fourteen substantive September-2026 applications: 2 granted (both response-requested + referred), 1 withdrawn, 11 denied (one denied with response requested and 4 amici: 26A325 M.W. v. Superior Court of California).
- `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 1` — field-name check only, no transfer line captured.
- Base rates: committed `metrics/statpack.md`, section "The interim docket (applications)". Pooled Terms 2024–2025: 31 granted / 296 resolved = 10.5%.

## CourtListener MCP

- `get_endpoint_item dockets 9526000370` — HTTP 404 (the live-channel SCOTUS docket id is not a CourtListener docket id).
- `call_endpoint docket-entries docket=9526000370` — HTTP 400 for the same reason.
- `search type=d court=scotus q="receiver prison stay application" filed_after=2020-01-01` — 0 results.
- `search type=o court=scotus q="Prison Litigation Reform Act" stay "pending appeal" state prison injunction filed_after=2018-01-01` — 0 results.
- `search type=r court=ca9 q="Jensen Thornell receiver" filed_after=2026-01-01` — 2 dockets (CA9 26-5060, id 73734346; CA9 26-1746, id 73291278).
- `call_endpoint docket-entries docket=73734346` — 20 entries: stay motion (Aug 12), amicus brief by Arizona House Speaker and Senate President (Aug 19, filed Sept 1), response (Aug 24), reply (Aug 28), order denying stay with Judge Forrest's partial dissent (Sept 1), opening brief (Sept 15/16).

## Web

- WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/26a370.html` (twice: entries, then PDF links). Three entries as of 2026-09-27: application submitted to Justice Kagan (Sept 16); response requested by Justice Kagan, due Sept 25 (Sept 18); response filed by respondents (Sept 25). No amicus, no referral entry, no disposition.
- WebFetch of the respondents' opposition PDF (`.../26A370/425682/20260925153133136_20260925 Respondents Stay Opp Jensen v Thornell.pdf`); the fetch tool could not read the binary, so I extracted its text locally with pypdf (48 pages) and read the introduction, argument, and conclusion.
- WebSearch `Thornell v. Jensen Supreme Court stay application Arizona prison receivership 26A370` — background links only (ACLU, Prison Law Office, Clearinghouse, Courthouse News); nothing on the application's disposition surfaced.

All retrieval was forward-mode; the case is undecided as of retrieval. Post-baseline material used: the two docket entries of Sept 18 and Sept 25 and the opposition brief, disclosed in `flags.json`.
