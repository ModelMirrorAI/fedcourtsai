# Retrieval log

Beyond the provisioned inputs (snapshot, event, context) and the committed
`metrics/statpack.md`:

1. **Corpus query (service-availability probe, result unused):**
   `uv run fedcourts query --court scotus --era modern --limit 5`
   stderr: `ranged corpus reads: 747 GET(s), 195821568 byte(s)`
   Run to confirm the cell's corpus service was reachable; the broad result
   set did not bear on this application and no further corpus queries were
   made (interim applications are not a population `query` surfaces well —
   the statpack's interim section was the anchor instead).

2. **CourtListener MCP — `search` (dockets):** `type=d`, `q="Gilmore Walmart"`,
   `court=ca5`. Found CA5 No. 26-30022, *Gilmore v. Walmart*, filed
   2026-01-20, nature of suit 3440 (Other Civil Rights), docket id 73507998.

3. **CourtListener MCP — `call_endpoint` (docket-entries):**
   `docket=73507998`, 46 entries. Source of the lower-court posture cited in
   `reasoning.md`: appeal dismissed on Walmart's motion 2026-02-26; rehearing
   en banc denied without poll 2026-03-31; successive motions to stay the
   mandate denied 2026-05-07 / 05-20 / 05-22; mandate issued 2026-05-29;
   originating district case W.D. La. 5:20-cv-1589.

Deliberately **not** retrieved: the Supreme Court docket's current state for
26A163, any search on the application's disposition, and anything under
`data/qp-topics/`. No web searches. Nothing outcome-revealing about this
application surfaced.
