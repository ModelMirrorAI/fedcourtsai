# Retrieval log (claude-baseline, 20260901T014205Z)

Beyond the provisioned inputs (event.yaml, record/context.json, the 2026-08-31
snapshot) and the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --include-applications "emergency application injunction pending appeal election ballot state canvassers"` —
  rejected (the command takes no free-text argument); no corpus read.
- `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 8` —
  stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Returned 8 recent
  application rows (mostly extensions; one substantive granted NPS application,
  26A203, and one substantive denied pro se application, 26A256) — used only as
  shape context for the application docket, none as a close prior.

## Web retrieval (forward cell — unrestricted)

- WebFetch of the application PDF
  (`supremecourt.gov/DocketPDF/26/26A275/422446/..._ACVM Emergency App for an Injunction Pending Appeal.pdf`) —
  **HTTP 403, not retrieved**; the application's own text did not inform this
  prediction.
- WebSearch: `Americans for Citizen Voting Michigan Board of State Canvassers Michigan Supreme Court ballot initiative 2026` —
  surfaced Votebeat, Bridge Michigan, Michigan Advance, Detroit News,
  ClickOnDetroit, Michigan Public/WKAR, WILX, and Election Law Blog coverage of
  the 2-2 board deadlock (Aug 24), the signature counts (709,841 collected vs
  446,198 required; the 1,000-signature sample), and the Michigan Supreme Court
  filing.
- WebFetch of the Election Law Blog post on the application — **HTTP 403, not
  retrieved**.
- WebSearch: `"Americans for Citizen Voting" Supreme Court emergency application injunction Kavanaugh Michigan ballot federal claim` —
  surfaced Ballot Access News (Aug 31) and the same coverage set; gave the
  operative deadlines (relief requested by Sept 3, 2026; ballot settled no
  later than Sept 4, 2026) and the rejected-affidavits argument.

No CourtListener MCP lookups were made. None of the retrieved material
contains a disposition of this application (none exists yet).
