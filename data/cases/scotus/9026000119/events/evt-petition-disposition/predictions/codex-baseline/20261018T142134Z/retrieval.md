# Retrieval record

## Provisioned material

Read the event definition; `record/context.json`; `record/snapshots/2026-10-18.json`; `record/documents/documents.json`; `questions-presented.txt`; the petition body and selected appendix orders in `petition.txt`. The appendices are pre-decision lower-court material, not this event's Supreme Court outcome. No other predictor output, evaluation, outcome file, or topic-label artifact was read.

## Committed historical context

Read relevant sections of `metrics/statpack.md` and the matching Term/segment fields of `metrics/statpack.json`. Computed the state/sal-v4 reached pool across all rendered prior Terms, 2017–2025, using weighted risk-set denominators: 99/421. Consulted the prompt and schemas for output requirements, the path and serialization helpers for artifact handling, and the statistics-review checklist. A read-only reviewer was asked to verify only the committed base-rate population and arithmetic.

No `fedcourts query` or `open-events` lookup was made; there is no ranged-corpus transfer line to report. `fedcourts paths --court scotus --docket 9026000119 --event evt-petition-disposition --role predictor` resolved paths without reading an outcome. Its initial invocation encountered an unwritable default cache; it succeeded using a temporary writable cache and the existing environment.

## External retrieval

1. Web search: `site.supremecourt.gov Rules Rule 10 certiorari compelling reasons state court federal question`. No usable result content returned; not relied upon.
2. Web open attempt for the official Supreme Court `2023RulesoftheCourt.pdf` under its filing-and-rules directory. No usable content returned; not relied upon.
3. CourtListener `search`, type `o`, citation `353 F.3d 870`, limit 3. Returned *United States v. Bolden*, Tenth Circuit, December 24, 2003, opinion/cluster 164183.
4. CourtListener `search_document`, opinion 164183, literal query `separation`, context 900 characters. Returned passages concerning separation of powers, factual justification for disqualification, and recognized conflicts. Used to assess the scope of the petition's cited analogy, not to retrieve this petition's history.

No search used this case's caption, docket number, disposition, or subsequent history. No outcome-revealing material was encountered.
