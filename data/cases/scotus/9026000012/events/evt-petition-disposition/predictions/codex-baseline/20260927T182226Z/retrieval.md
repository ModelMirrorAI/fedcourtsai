# Retrieval record

## Provisioned inputs and local context

- Read the case's September 27, 2026 snapshot, context, event definition,
  questions presented, petition, BIO, and document manifest. The docketed reply
  and amicus texts were not retrieved.
- Read the committed `metrics/statpack.md` cert, relist, CVSG, circuit, and
  sal-v4 segment tables and the corresponding `metrics/statpack.json` prior-Term
  elevated risk-set fields. Calculated the weighted pool locally: 521 / 3,085.
- Read schema contracts and the path/serialization helpers. Ran
  `uv run fedcourts paths --court scotus --docket 9026000012 --event evt-petition-disposition --role predictor`.
  Its first invocation failed because the default cache was read-only; retry
  with a cache under `/tmp` succeeded. No outcome file was opened.
- Checked the statpack's repository commit timestamp, September 26, 2026 at
  12:03:37 UTC. This is not a corpus refresh timestamp.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines.

## External calls

1. Web search: `site.supreme.justia.com cases federal us 429 252 Arlington Heights discriminatory impact starting point`.
   The tool returned no visible results or text; no evidence used.
2. Web open: the Justia opinion page for 429 U.S. 252. No visible result or
   opinion text was returned; no evidence used.
3. CourtListener MCP `search`: type `o`, query
   `caseName:(Sargent) AND "School District"`, filed before `2026-09-27`,
   three results. The relevant result was Sherice Sargent v. School District
   of Philadelphia, Third Circuit No. 24-3112, filed February 2, 2026,
   cluster 10782820, opinion 11249456. Two unrelated results were not pursued.
4. CourtListener MCP `search_document`: opinion 11249456, literal `aggregate`,
   context 1,000 characters. Used its discussion of individualized proof,
   disagreement with the First/Fourth Circuits, and continued injury requirement.
5. CourtListener MCP `read_document`: opinion 11249456, chunks 10 and 11 of
   8,000 characters. Read the surrounding discussion at slip opinion pp. 36-41,
   including earlier related cert-denial writings and the limits of the holding.

No search targeted this petition's disposition, current docket, or subsequent
history. No outcome of this petition surfaced. All substantive external
evidence used concerned the earlier, separate Sargent litigation. The failed
general-doctrine web attempts supplied no answer; the provisioned briefs and
CourtListener primary opinion supplied the relevant legal context instead.
