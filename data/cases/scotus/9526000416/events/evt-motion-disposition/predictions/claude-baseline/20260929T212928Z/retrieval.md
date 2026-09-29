# Retrieval log

## Corpus tooling

1. `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 500`
   stderr: `ranged corpus reads: 40 GET(s), 10354688 byte(s)`
   500 rows (440 application dockets: 342 extension, 80 substantive, 18 unknown
   ask). Filtered locally to substantive rows and to rows with the Solicitor
   General as counsel or a federal-officer caption; the disposition, response,
   referral and amicus figures in `reasoning.md` come from this sweep.

Base rates: `metrics/statpack.md`, section "The interim docket (applications)".

## CourtListener MCP

- `search` type `d`, q `Kingdom v. Trump`, courts dcd/cadc/scotus: 0 results.
- `search` type `d`, court `dcd`, docket_number `1:25-cv-00691`: 1 result,
  KINGDOM v. TRUMP, docket 69717615, Judge Royce C. Lamberth, filed 2025-03-07.
- `call_endpoint` `docket-entries`, docket 69717615, newest first, 12 entries:
  latest is a September 28, 2026 order on non-party filings with a status report
  due October 5; notice of appeal 26-5310 transmitted August 31 to September 1.
  Nothing there bears on the application's disposition.

## Web

- WebSearch: `Trump v. Kingdom Supreme Court stay application Bureau of Prisons gender dysphoria September 2026`
- WebFetch: supremecourt.gov docket 26A416 (live entries as of Sept 29, 2026:
  submission to the Chief Justice; response requested, due 4 p.m. Oct 8, 2026)
- WebFetch: scotusblog.com case page for Trump v. Kingdom (same two entries)
- WebFetch: courthousenews.com, Sept 28, 2026 report on the application
- WebFetch: law360.com, Sept 28, 2026 headline (paywalled; no detail)
- WebFetch: supremecourt.gov docket 25A319, Trump v. Orr (submitted Sept 19,
  2025 to Justice Jackson; response requested Sept 22, due Oct 6; one amicus
  entry Oct 3; referred and granted Nov 6, 2025, Jackson, Sotomayor, Kagan
  dissenting)
- WebFetch: aclu.org case page for Kingdom v. Trump (class of about 2,000)

None of the above disclosed this application's disposition; it is pending.
