# Retrieval record

## Provisioned inputs

Read event.yaml; record/context.json; record/snapshots/2026-09-18.json; record/documents/documents.json, questions-presented.txt, and petition.txt. No case outcome, subsequent case history, other predictor output, or topic-label artifact was consulted.

## Committed general context

- Read metrics/statpack.md: modern discretionary-cert dispositions, originating circuit, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table.
- Read the corresponding aggregate fields in metrics/statpack.json. Computed the elevated reached pool across displayed Terms 2017–2025 as 521 / 3,085 = 0.16888168557536468. No case-level rows were retrieved.
- Read the prediction prompt, applicable instructions, prediction/flags/tooling schemas, and the repository's ID, path, and serialization helpers for output compliance.
- Ran `uv run fedcourts paths --court scotus --docket 9026000173 --event evt-petition-disposition --role predictor`. The first attempt encountered a read-only default cache; a retry with a temporary cache succeeded. This resolves paths, not corpus priors.
- No `fedcourts query` or `open-events` call was made; there are no ranged-corpus transfer lines to report.

## Web attempts

1. Search: `site.supremecourt.gov Rule 10 considerations governing review certiorari misapplication properly stated rule law`. The tool returned no usable output.
2. Opened the Supreme Court's filing-and-rules landing page twice. Both returned no usable output. No rule text, case information, or outcome information was obtained from these calls.

## CourtListener MCP

1. `search(type="o", citation="395 F.3d 1019", num_results=1, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`: returned Lands Council v. Powell, January 24, 2005, opinion 3029990.
2. `search_document(opinion_id=3029990, query="exceptions", snippet_size=1200)`: read the opinion's discussion at page 1030 of four limited exceptions, their narrow application, and its decision not to resolve the extra-record issue unnecessarily.
3. `search(type="o", citation="82 F.3d 1085", num_results=1, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`: returned James Madison Ltd. v. Ludwig, July 3, 1996, opinion 717539.
4. `search_document(opinion_id=717539, query="supplement", snippet_size=850)`: read its discussion of supplementation, including omitted adverse documents, explanatory background, and the required showing of bad faith.

These were historical legal-context lookups of authorities named in the petition, not searches for Jones, docket 26-173, docket 24-1166, or this petition's disposition. Only targeted passages, not the complete historical opinions, were read. Their overlap reduced the weight assigned to the petition's asserted split. No outcome-revealing material about the target case surfaced.
