# Retrieval log

Forward-mode cell; retrieval unrestricted. Beyond the provisioned snapshot,
event, and context:

## Corpus

- `uv run fedcourts query --court scotus --include-applications --era 2020s --disposition granted --limit 6`
  — stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Used for recent
  granted-application shapes; the useful comparator was 26A203 (NPS v. National
  Trust, granted 2026-08-31, response requested, referred, 7 amici).
- (An earlier `fedcourts query --text ...` invocation was rejected — no such
  option — and read nothing.)

## Committed statpack

- `metrics/statpack.md`, "The interim docket (applications)" section — pooled
  strictly-prior substantive grant rate for a Term-2026 application:
  (17+14)/(226+70) = 31/296 ≈ 10.5%, clearing the 50-resolved floor.

## Web

- WebSearch: `NRCC Supreme Court emergency stay application 26A274 Brown FCC`
  — surfaced SCOTUSblog and insideradio coverage plus the supremecourt.gov
  filing PDFs. No disposition of 26A274 itself appeared (the "Court Rejects
  Stay" headline is the Fourth Circuit's own stay denial).
- WebFetch: SCOTUSblog, "Republican groups file emergency application to court
  on broadcasting rates for political ads" (2026-08) — case background, CA4
  panel line-up (King majority, Wilkinson jurisdictional dissent), timeline,
  and the administration brief's supportive position.
- WebFetch: the government response PDF on supremecourt.gov
  (`26A274GovtResponse.pdf`) — **failed with HTTP 403**; its position is taken
  from the SCOTUSblog reporting instead.

## CourtListener MCP

- Not used; the snapshot and the web coverage answered what the corpus did not.
