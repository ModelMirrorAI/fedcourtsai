# Retrieval log

## Provisioned inputs

Read the event definition, September 18, 2026 snapshot, context, document
manifest, questions presented, and substantive excerpts from the petition
and brief in opposition. All case-specific facts came from these inputs.
No outcome file, other prediction, or labeling-measurement artifact was read.

## Additional context

- Read `metrics/statpack.md`: modern discretionary-cert, originating-circuit,
  paid scored-segment relist and CVSG cuts, and sal-v4 segment rates. Computed
  the elevated reached-rate anchor from displayed Terms 2017-2024 using a
  local arithmetic script, not a remote corpus query.
- Web search: `site.supremecourt.gov opinions 2021 Egbert Boule 21-147 pdf`.
  The tool returned no usable results or text.
- Web open attempted for the Supreme Court Egbert opinion PDF, identified
  by document path `/opinions/21pdf/21-147_g31h.pdf`. No usable text returned.
- CourtListener MCP `search(type="o", case_name="Egbert v. Boule",
  court="scotus", num_results=1, filed_before="2023-01-01")`: returned the
  June 8, 2022 decision, 596 U.S. 482, cluster 6475794, opinion 6347905.
- CourtListener MCP `search_document(opinion_id=6347905,
  query="alternative", snippet_size=380)`: reviewed excerpts concerning
  alternative remedial structures, the majority's refusal to extend Bivens,
  and the dissent's contrary treatment of the grievance process. Used the
  majority as general context, not as a determination of this case's threshold.

No `fedcourts query` or `open-events` call was made, so no ranged-corpus
transfer line applies. No live docket or case-outcome search was performed.

## Local contract and validation tooling

Read repository instructions, prediction/feedback schemas, and the relevant
path and serialization helpers. `uv run fedcourts paths --court scotus
--docket 73298285 --event evt-petition-disposition --role predictor` initially
failed because its default cache directory was read-only; using a writable
temporary cache allowed it to resolve the paths. These were contract and
filesystem checks, not legal or outcome retrieval.
