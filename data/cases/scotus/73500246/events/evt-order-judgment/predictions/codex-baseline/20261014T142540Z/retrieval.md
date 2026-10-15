# Retrieval record

## Provisioned baseline

Read `event.yaml`, `record/context.json`, and `record/snapshots/2026-10-13.json` for this cell. No filed documents or documents manifest were provisioned. No other prediction, evaluation, outcome file, or labeling artifact was read.

## Committed base-rate context

Read the merits section of `metrics/statpack.md` and `merits` in `metrics/statpack.json`. Used `jq` to select grant Terms 2016 through 2025 and sum granted, parsed, disturbed, and excluded counts. Consulted `git log -1 --format='%h %cI %s' -- metrics/statpack.md` for the committed artifact's vintage. No `fedcourts query` or `open-events` call was made, so no ranged-corpus transfer line exists.

## Web attempts

The following `web.run` calls returned no usable content:

- Open `https://www.supremecourt.gov/qp/25-01343qp.pdf`.
- Search `site.justice.gov "Ozurumba" "petition"` and `site.ca4.uscourts.gov "24-2070"` in one call.
- Open `https://www.ca4.uscourts.gov/opinions/242070.P.pdf`.

No search snippets or decision coverage were surfaced by these calls.

## Official question presented

Retrieved `https://www.supremecourt.gov/qp/25-01343qp.pdf` using `curl -fsSL --max-time 30`. The initial pipe to `pdftotext` failed because that executable was absent. Repeated the same request and extracted the one-page PDF in memory using the installed `pypdf.PdfReader` through `uv run python`; no downloaded file was written. Read the full question-presented sheet, which states the October 13, 2026 cert grant and the material-support nexus question. It contains no Supreme Court merits disposition.

## CourtListener MCP

- `search(type="o", q='docketNumber:"24-2070"', court="ca4", filed_before="2026-10-14", num_results=3)`: one result, *Izuchukwu Ozurumba v. Pamela Bondi*, September 2, 2025; cluster 10665527, opinion 11132114. This is the decision below, not the target Supreme Court judgment.
- `read_document(opinion_id=11132114, chunk_index=[0,1,2], chunk_size=16000)`: returned the pre-grant appellate opinion; displayed output was truncated.
- `search_document(opinion_id=11132114, query="including", snippet_size=950)`: located statutory language and relevant passages; displayed output was truncated.
- `read_document(opinion_id=11132114, chunk_index=3, chunk_size=8000)`: read majority discussion on slip pages 12–14.
- `read_document(opinion_id=11132114, chunk_index=4, chunk_size=8000)`: read majority discussion on slip pages 14–17.
- `read_document(opinion_id=11132114, chunk_index=8, chunk_size=8000)`: read dissent discussion on slip pages 25–28.

The lower opinion is cited as *Ozurumba v. Bondi*, 153 F.4th 396 (4th Cir. 2025), with slip-page locators in the rationale. Its discussion of *Holder v. Humanitarian Law Project* was considered as the lower judges' competing readings; that precedent was not separately retrieved. No Supreme Court merits opinion, later disposition, or subsequent-history search was requested.
