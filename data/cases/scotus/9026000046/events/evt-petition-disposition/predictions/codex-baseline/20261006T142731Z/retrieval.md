# Retrieval log

## Local statistical context

- Read metrics/statpack.md: modern discretionary-cert dispositions, originating
  circuit, paid relist and CVSG cuts, and the sal-v4 per-Term band table.
- Read metrics/statpack.json's Term and segment fields to pool the baseline
  reached rate across the displayed prior Terms 2017-2025: 638 / 12,720.
- Inspected the pack file's latest commit timestamp with git log:
  2026-09-28T12:02:50Z. This identifies the committed artifact's vintage,
  not a newly measured corpus-wide pull timestamp.
- No fedcourts query or open-events lookup was made. Consequently there are
  no ranged corpus reads transfer lines to report.

## External general-precedent attempts

1. web.run search query: site:supremecourt.gov opinions Caetano Massachusetts
   577 U.S. 411 2016. No usable result content returned.
2. web.run search query: site:supremecourt.gov "Wolford" "2026" "opinion".
   No usable result content returned.
3. web.run open of the official Caetano opinion PDF at
   https://www.supremecourt.gov/opinions/15pdf/14-10078_aplc.pdf.
   No usable document content returned.
4. CourtListener MCP search: type=o, citation="577 U.S. 411", num_results=2.
   Returned HTTP 429, daily limit 1400, with an indicated wait of 2337 seconds.
   No opinion or case-result content was obtained. No REST fallback was used.

No target-case outcome or subsequent-history search was performed. No external
substantive content informed the forecast. The legal descriptions are grounded
in the provisioned petition and appended lower-court decisions, with their
advocacy and verification limitations stated in reasoning.md.
