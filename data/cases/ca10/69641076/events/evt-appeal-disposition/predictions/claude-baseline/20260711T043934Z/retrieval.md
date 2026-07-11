# Retrieval log — ca10/69641076 / evt-appeal-disposition / claude-baseline / 20260711T043934Z

## Provisioned inputs

- `data/cases/ca10/69641076/record/snapshots/2026-07-11.json` (baseline snapshot)
- `data/cases/ca10/69641076/events/evt-appeal-disposition/event.yaml`
- `data/cases/ca10/69641076/record/context.json` (mode: `forward`)
- No `record/documents/` were provisioned for this cell.

## Corpus base rates (committed statpack)

- Read `metrics/statpack.md` — overall and by-court disposition base rates.
  CA10 cut: 34 resolved (other 88.2%, denied 11.8%).

## Corpus priors (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court ca10 --corpus-backend ranged`
   — 20 rows, mostly `other`/prisoner/civil-rights dockets, no employment-trial
   analogue. Stderr: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
2. `uv run fedcourts query --court ca10 --topic "3442 Civil Rights: Jobs" --corpus-backend ranged`
   — 0 rows. Stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`

## CourtListener MCP

The configured CourtListener MCP server errored on every call
(`REDIS_URL is not set; cannot access session store`) — 2 failed `search`
attempts. Fell back to the CourtListener REST API directly (same data
source), using the provisioned API token.

## CourtListener REST API calls

All GETs against `https://www.courtlistener.com/api/rest/v4/`:

1. `search/?type=d&q="Federal Home Loan Bank" Zhang` — located the district
   case: ksd 5:19-cv-04073 (docket id 16077204), Title VII job-discrimination,
   filed 2019-08-19, terminated 2023-08-10, Judge Toby Crouse.
2. `docket-entries/?docket=16077204&order_by=recap_sequence_number&page_size=100`
   — first page (descriptions mostly blank).
3. `docket-entries/?docket=16077204&order_by=-recap_sequence_number&page_size=60`
   — tail of the docket: jury verdict 2023-08-10, new-trial motion denied
   2024-01-25, notice of appeal 2024-02-23, transcripts spring 2024.
   (Incidentally saw descriptions of two post-decision entries — "Letter re
   Writ of Certiorari", 2025-07-16 and 2025-10-06 — not opened; disclosed in
   `flags.json`.)
4. `docket-entries/?docket=16077204&...&entry_number__lte=159&entry_number__gte=80`
   — trial-phase entries (directed-verdict motion, instructions, verdict).
5. `docket-entries/?docket=16077204&...&entry_number__lte=132&entry_number__gte=60`
   — pretrial/in-limine phase.
6. `docket-entries/?docket=16077204&...&entry_number__lte=113`
   — earlier entries; found entry 100: summary judgment **denied** 2021-04-28
   (Judge Sam Crow) on defendant's motion (entry 90).
7. `parties/?docket=16077204` (3 variant calls) — no party/attorney data in
   RECAP for this docket.
8. `docket-entries/?docket=16077204&entry_number=162` — located the Rule 59
   denial order document (recap-document 384271162, available, 7 pages).
9. `recap-documents/384271162/?fields=plain_text` (2 reads) — full text of the
   2024-01-25 memorandum and order denying the new-trial motion (the primary
   source for the appellate-issue analysis in `reasoning.md`).
10. `docket-entries/?docket=69641076&date_filed__lt=2025-02-14` — pre-decision
    CA10 entries: **0 results** (CourtListener holds only the termination
    entry the snapshot already shows).

Deliberately **not** retrieved: the CA10 order and judgment, the linked
opinion cluster (`clusters/10333578`), the termination document (recap
document 430311956), the two post-decision district entries, and any search
for the appeal's outcome or coverage of it.

No web searches were used.
