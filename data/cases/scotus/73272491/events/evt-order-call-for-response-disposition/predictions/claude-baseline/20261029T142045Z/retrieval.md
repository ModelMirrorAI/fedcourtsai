# Retrieval log

- WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1238.html`: docket entries. Still pending. Response deadline extended three times; BIO filed 2026-10-13; reply filed 2026-10-19; distributed 2026-10-28 for the 11/13/2026 conference.
- WebFetch of the same page to get the BIO and reply PDF links.
- WebFetch of the BIO PDF (`.../25-1238/429402/20261013171557146_25-1238%20Mizrahi%20Opp_final.pdf`): the fetcher could not render it. I extracted the text locally with pypdf from the saved binary. It is an 8-page merits-only opposition that lists 12 prior denials.
- `uv run fedcourts query --court scotus --docket-number 23-95` (Esformes v. United States): denied 2023-12-11, distribution_count 1.
  `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
- `uv run fedcourts query --court scotus --docket-number 16-900` (Stevenson v. United States): sparse row with no disposition recorded.
  `ranged corpus reads: 641 GET(s), 168034304 byte(s)`
- `uv run fedcourts query --help`
- Base rates: committed `metrics/statpack.md` (sal-v4 band table, relist, CVSG and amicus cuts).
- No CourtListener MCP calls.
