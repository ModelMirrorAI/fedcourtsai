# Retrieval log

## Committed base rates

- `metrics/statpack.md` — "The interim docket (applications)" section: pooled
  the strictly-prior Terms (OT2025: 178 resolved / 16 granted; OT2024: 47
  resolved / 14 granted) for the 13.3% scored baseline.

## Corpus lookups (`fedcourts query`)

- `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 8`
  — stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Returned one
  substantive application prior (26A171, denied) and seven time-extension
  applications; not useful as analogues, so the statpack pool carried the
  anchoring.
- (A first invocation with an unsupported `--text` flag errored before reading
  the corpus; no transfer line.)

## Web searches (engine-surfaced)

- `Supreme Court application 26A139 Alabama v. California stay Justice Jackson`
  — identified the application as the twelve intervenor states' request to
  stay the D. Mass. injunction against the President's mail-in voting
  executive order pending First Circuit appeal, alongside the consolidated
  opposition (filed Aug 3) and applicants' reply (Aug 4). Sources:
  supremecourt.gov docket PDFs for 26A139; scotusblog.com interim docket.
- `California v. Trump mail-in voting executive order injunction District of
  Massachusetts First Circuit stay 26A124` — background on the underlying
  litigation: the executive order's USPS/DHS citizenship-list regime, Judge
  Talwani's nationwide preliminary injunction on constitutional grounds, the
  First Circuit's language declining relief, the Solicitor General's parallel
  application 26A124 (filed July 27), and the 23-state respondent coalition.
  Sources: scotusblog.com, constitutioncenter.org, votebeat.org,
  electionlawblog.org, cnbc.com. One result (votebeat.org, dated 2026-08-12,
  post-cutoff) headlined another injunction in parallel mail-voting
  litigation; it was not opened and no post-cutoff outcome material about
  this application was retrieved.

## CourtListener MCP

- None.
