# Retrieval log

Corpus (`fedcourts`):
- `uv run fedcourts query --help`
- `uv run fedcourts query --court scotus --docket-number 26-630`: this docket's own row (open, 0 distributions). `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
- `uv run fedcourts query --court scotus --docket-number 26-104`: *Rhoney v. Barbosa da Cunha*, granted 2026-10-01, from CA2. `ranged corpus reads: 1 GET(s), 262144 byte(s)`
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s`: GVR priors, skimmed captions only. I truncated this command's output to its last rows, so its `ranged corpus reads` line was not captured.
- `metrics/statpack.md`: salience band table (federal column).

Web:
- WebSearch "Supreme Court certiorari granted mandatory detention 1225(b)(2)(A) bond hearings entered without inspection Yajure Hurtado circuit split": surfaced reports of the Oct 1, 2026 grant in No. 26-104 and summaries of the circuit split (CLINIC, CRS LSB11438, Bloomberg Government, Clearinghouse). Titles and snippets only; no pages opened.
- WebSearch "Guerrero Orellana First Circuit August 2026 class bond hearings decision government petition Supreme Court": district-court history of the class action (ACLU pages, Clearinghouse); nothing on the First Circuit ruling or this petition.
- WebFetch of the Court's docket page for No. 26-104 (supremecourt.gov): confirmed the grant and the merits briefing schedule.

CourtListener MCP: not used.

Nothing surfaced claiming a disposition of No. 26-630, and no third-party forecast of it.
