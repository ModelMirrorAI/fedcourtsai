# Retrieval log

## Corpus (`fedcourts`)

1. `uv run fedcourts corpus-info` — errored: the cell's service backend has no
   client-side connection for this command. No corpus read occurred.
2. `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 8`
   — stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Returned eight
   recent granted applications, all `application_kind: "extension"` (routine
   time-extension grants) — not informative priors for a substantive stay
   application; none used.

## CourtListener MCP

1. `search` (type `d`, court `cadc`, docket_number `26-5123`) — located the
   court of appeals docket: *National Trust for Historic Preservation v. NPS*,
   CADC No. 26-5123, docket id 73204895, filed 2026-04-16.
2. `call_endpoint` (`docket-entries`, docket 73204895, newest first, 15
   entries) — read the recent entries: the 2026-08-07 per curiam judgment
   affirming the district court's modified preliminary injunction (Millett,
   Garcia; Rao dissenting), the vacatur of the April 17 administrative stay,
   the 14-day self-stay for Supreme Court review, the mandate directed to
   issue 2026-08-21, and the merits-briefing/argument history.

No web searches. I did not retrieve this application's own disposition or any
post-cutoff state of the Supreme Court docket.

## Local pipeline-source reads (not case retrieval)

Read `src/fedcourtsai/pipeline/interim_signals.py` and
`src/fedcourtsai/pipeline/claims.py` to understand how the escalation signals
and increment claims are parsed and resolved — this informed the
`amicus-increment` and `referral-increment` probabilities and the data-quality
flag.
