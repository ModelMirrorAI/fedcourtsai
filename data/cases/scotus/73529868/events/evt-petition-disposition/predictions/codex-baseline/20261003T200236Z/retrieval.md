# Retrieval log

## Local inputs and reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, flags,
  and tooling schemas. Checked for applicable nested agent instructions.
- Read this event's `event.yaml`, `record/context.json`, and
  `record/snapshots/2026-10-03.json`. No filed-document directory was present.
- Read `metrics/statpack.md`: modern-cert disposition and originating-circuit
  sections, paid-segment relist and CVSG cuts, and sal-v4 prior-Term reached
  rates. Inspected only the top-level keys of `metrics/statpack.json`; did
  not read case-level measurement artifacts. Computed the federal pooled rate
  locally from the displayed prior-Term Markdown rows.
- Ran `uv run fedcourts paths --court scotus --docket 73529868 --event
  evt-petition-disposition --role predictor`. The first invocation failed
  because the default uv cache was read-only; retry with a temporary cache
  succeeded. No outcome file was opened.
- No `fedcourts query` or `open-events` lookup was used. There are no ranged
  corpus transfer lines to report.

## CourtListener MCP

1. `search(type="o", court="ca6", q='"Lopez-Campos"',
   filed_before="2026-06-22", num_results=5)`. Returned one May 11, 2026
   opinion, indexed as Juan Sanchez Alvarez v. MarkWayne Mullin, cluster
   10857213, opinion 11324612. The consolidated caption and appellate docket
   numbers match the provisioned lower-court record. The date filter confines
   this lookup to material predating the cert petition.
2. `read_document(opinion_id=11324612, chunk_index=0, chunk_size=14000)`:
   caption, posture, initial facts, and statutory framework. Tool output was
   partially truncated; no claim of reading the full opinion is made.
3. `search_document(opinion_id=11324612, query="Buenrostro",
   snippet_size=1200)`: majority and dissent's descriptions of the circuit
   conflict and statutory question.
4. `search_document(opinion_id=11324612, query="due process",
   snippet_size=350)`: locations of the constitutional discussion, including
   the distinction between statutory and constitutional arguments.
5. `read_document(opinion_id=11324612, chunk_index=10, chunk_size=8000)`:
   majority's conclusion and due-process discussion, and opening of the
   dissent, approximately opinion pages 23-26.

## Web and direct primary-document retrieval

- `web.run` attempted to open the September 25 respondents' letter linked
  in the snapshot twice and the official Sixth Circuit opinion PDF once.
  These calls returned no usable content. No web search was run and no
  search-result snippet was surfaced.
- A shell attempt to stream that same letter through `pdftotext` failed
  because that program is unavailable. A retry using Python's URL reader
  and installed `pypdf` read the one-page PDF in memory successfully. No
  downloaded file was written. The precise snapshot-linked source was
  `https://www.supremecourt.gov/DocketPDF/25/25-1415/425716/20260925165614696_2026.09.25%20Letter%20re%20DC.pdf`.
- The letter is dated September 25, 2026, in Putra No. 25-1415, Rhoney
  No. 26-104, and Buenrostro-Mendez No. 26-43. It reports a September 21
  certiorari-before-judgment petition in Genalo v. D.C. and asks the Court
  to allocate the statutory and constitutional issues among vehicles. It
  also reports another case's dismissal, Genalo v. G.M.; that is
  pre-snapshot companion context, not this petition's outcome. I did not
  follow the letter's additional references or retrieve later history.

No disposition of this cell's petition was retrieved, and no material under
`data/qp-topics/` or another predictor's output was read.
