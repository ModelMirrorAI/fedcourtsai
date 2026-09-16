# Retrieval log

## Provisioned inputs and local reference material

- Read the case-level September 16, 2026 snapshot, context, petition, questions presented, and document manifest, together with this event's definition. No outcome file or another predictor's output was read.
- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, tooling, and flags schemas to establish the artifact contract.
- Read the committed `metrics/statpack.md` modern-cert, circuit, paid relist, paid CVSG, and salience sections. A heading/Term search also surfaced other stage headings and aggregate rows; those did not supply the cert anchor.
- Inspected `metrics/statpack.json` structure and pooled the primary `sal-v4` baseline fields over displayed Terms 2017–2024: sum of `prefix_est_grant_rate * prefix_weighted_resolved` divided by sum of `prefix_weighted_resolved`, yielding 593 / 11,580 = 0.051208981. No individual case rows were retrieved.
- Ran `uv run fedcourts paths --court scotus --docket 73372297 --event evt-petition-disposition --role predictor`; the initial default-cache invocation failed with a read-only-cache error. Repeated successfully with a writable temporary uv cache. This command resolves paths only.
- No `fedcourts query`, `open-events`, live-corpus lookup, or CourtListener MCP lookup was performed. There are no ranged-corpus transfer lines to report.

## General legal context only

All requests were for general Court rules, not this case, its outcome, or subsequent history.

1. `web.run` search: `site.supremecourt.gov Rule 10 certiorari rarely granted erroneous factual findings misapplication properly stated rule law`. No visible response content was returned.
2. `web.run` open of `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`. No visible response content was returned; no inference from its contents was made.
3. Four `web.run` opens of `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`. These likewise returned no visible response content.
4. Fetched that official guidance page with `curl -fsSL --max-time 25`, extracting only PDF link targets. It identifies `2026RulesoftheCourt_WEB.pdf` among the current rules resources.
5. Attempted `curl -fsSL --max-time 25 https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf | pdftotext -layout - -`; this failed because `pdftotext` is not installed. No extracted text resulted.
6. Successfully fetched the same official 2026 rules PDF with `httpx` inside `uv run python`, read it in memory using `pypdf.PdfReader`, and printed the page containing Rule 10 and its continuation: PDF pages 9–10, printed pages 5–6. The output incidentally included adjacent Rules 9, 11, and the start of 12. Only Rule 10 informed the cert analysis. No downloaded file was written.

No outcome-revealing material was encountered.
