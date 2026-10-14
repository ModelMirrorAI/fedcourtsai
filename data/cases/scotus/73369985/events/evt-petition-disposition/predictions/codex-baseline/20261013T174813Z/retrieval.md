# Retrieval log

## Provisioned materials

Read the event definition, `record/context.json`, `record/snapshots/2026-10-13.json`, and `record/documents/documents.json`. Read the questions presented and selected substantive sections of the petition, brief in opposition, cert reply, and appendix. The appendix is truncated; no videos were retrieved or viewed. These are provisioned inputs, not live case retrieval.

## Committed statistical context

Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table. Read the JSON keys and the 2024 segment structure in `metrics/statpack.json`, then pooled only the `high` reached estimates for 2017–2024 using jq. Result: 314 estimated grants, 898 weighted resolved cases, rate 0.34966592427616927. No individual-case records or labels were read from this pack.

No `fedcourts query` or `open-events` call was made, and there are no ranged-corpus transfer lines to report. No corpus blob was pulled.

## General legal context: web attempts

The following `web.run` calls returned no usable content:

1. Search: `site.supremecourt.gov opinions Barnes Felix 2025 totality circumstances 23-1239`.
2. Search: `Barnes v Felix 23-1239 Supreme Court May 15 2025 opinion`.
3. Search: `Zorn Linton 2026 per curiam qualified immunity`.
4. Open of the official Zorn opinion identified by CourtListener: `https://www.supremecourt.gov/opinions/25pdf/25-297_bqm2.pdf`.

None sought the predicted case's disposition or subsequent history.

## General legal context: CourtListener MCP

1. `search(type="o", case_name="Zorn v. Linton", court="scotus", num_results=3)`. Returned the March 23, 2026 decision, docket 25-297, opinion ID 11280281. Used only as general qualified-immunity precedent.
2. `search(type="o", case_name="Barnes v. Felix", court="scotus", filed_before="2025-05-16", filed_after="2025-05-14", num_results=2)`. Returned versions of the May 15, 2025 decision; the slip-opinion ID used below is 11051434.
3. `read_document(opinion_id=11280281, chunk_index=0, chunk_size=14500)`. Read the opening Zorn majority analysis and its procedural posture.
4. `search_document(opinion_id=11280281, query="petition", snippet_size=450)`. Verified the grant-and-reversal conclusion and the existence of the accompanying dissent.
5. `search_document(opinion_id=11051434, query="prior events", snippet_size=900)`. Verified that Barnes's totality analysis permits earlier context to support either party rather than only the officer.

No lookup concerned Moore/Romero's disposition, live docket, or subsequent history. No outcome-revealing information about this cell was encountered.

## Operational reads

Read the agent contract, predict prompt, output schemas, and path/serialization helpers. Ran the read-only `fedcourts paths` command for this cell and computed its output path through `CasePaths`. The first uv invocation could not write its default cache; using a writable temporary cache resolved that issue. Output validation is an operational check, not a prediction input.
