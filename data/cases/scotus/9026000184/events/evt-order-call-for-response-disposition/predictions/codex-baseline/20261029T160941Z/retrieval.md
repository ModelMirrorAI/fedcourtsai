# Retrieval record

## Provisioned and stable local material

Read AGENTS.md, .github/prompts/predict.md, the prediction/tooling/flags schemas, this event's event.yaml, record/context.json, record/snapshots/2026-09-25.json, record/documents/documents.json, questions-presented.txt, and relevant portions of petition.txt and appendix.txt. No other cell's prediction or evaluation, own outcome, or data/qp-topics artifact was read. Read .claude/agents/stats-reviewer.md for the statistical review checklist.

Beyond provisioned case inputs, read the committed metrics/statpack.md modern-cert, circuit, paid relist/CVSG/amicus, and sal-v4 Term-band tables, with matching metrics/statpack.json terms/segments fields. Local jq arithmetic pooled the prior-Term baseline reached estimates to 660 / 12,913 = 0.0511112832. This is committed-pack context, not a fresh corpus count. A read-only statistical subagent independently reproduced the arithmetic and found no blockers in that bounded review, without case-outcome retrieval or reading any prediction output. It correctly noted that context.response_requested is null; the affirmative evidence of the call is the snapshot's September 24 entry and this cert event, not that interim-oriented context field.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000184 --event evt-order-call-for-response-disposition --role predictor` failed before execution because uv's default cache directory was read-only. Repeated successfully with `UV_CACHE_DIR=/tmp/uv-cache`; the listing identified the event path and withheld the evaluator-only outcome path. No outcome was opened.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded; consulted the structured court, disposition, era, decided-before, and limit options. This is help, not a corpus read.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3` succeeded. The service returned U.S. DOGE Service v. United States District Court for the District of Columbia (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche, Attorney General v. Izuchukwu Ozurumba (25-1343), all grant-labeled prior docket-Term examples. These were not close substantive analogues and supplied no numerical conditional estimate. No full opinion bodies were requested. The cutoff masks by derived docket year, not by an exact date, so returned grant dates in October 2026 do not make this an exact-date historical sample. The cell is forward; no replay-boundary claim is made.

   Reported stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`.

## Web and CourtListener calls

4. One web search call contained two queries: `Junger v Daley 209 F.3d 481 2000 source code expressive means First Amendment` and `Christianson Colt 486 U.S. 800 1988 transfer plausible law of case`. Results included public discussions of code-as-speech, general transfer-law material, and this case's August 10 petition at supremecourt.gov, already staged locally. I did not open the search-result discussions, other cases' dockets, or that petition online. No result I used asserted this petition's own disposition. The only separately opened source from this research was the official Christianson opinion below.
5. CourtListener MCP `search(type="o", citation="209 F.3d 481", num_results=1)` failed with HTTP 429, daily rate limit, with a suggested wait of 5,410 seconds. No result or opinion text was returned. I did not retry, wait for the daily window, seek credentials, or fall back to direct CourtListener REST.
6. Web open of the official U.S. Reports opinion: `https://www.govinfo.gov/content/pkg/USREPORTS-486/pdf/USREPORTS-486-800.pdf`. Returned the 23-page opinion, Christianson v. Colt Industries Operating Corp., 486 U.S. 800 (1988). Used as general law-of-the-case and transfer background, particularly pages 816–819, not as a precedent deciding this petition or establishing its current status.

No search for this petition's disposition or subsequent history, and no live Supreme Court docket refresh, was attempted. General-source search snippets were not used to infer an unseen opposition brief or a later proceeding.

## Artifact checks

`UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data` passed after artifact creation: `OK: 29704 artifact(s) valid, 71066 reference(s) consistent`. Validation was a schema/reference check, not a retrieval of another cell's forecast or this case's outcome. A path-scoped git status confirmed the output directory is untracked; no commit, push, or PR operation was performed.
