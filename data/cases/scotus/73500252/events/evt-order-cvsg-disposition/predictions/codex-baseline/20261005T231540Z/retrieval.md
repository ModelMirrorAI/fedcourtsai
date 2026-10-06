# Retrieval record

## Provisioned inputs

Read this cell's event.yaml; record/context.json; record/snapshots/2026-10-05.json; and record/documents/documents.json, questions-presented.txt, petition.txt, and brief-in-opposition.txt. Petition reading was selective and included the introduction, split discussion, importance discussion, and vehicle argument; the entire truncated appendix was not reviewed. No current target docket or outcome was retrieved.

## Committed aggregate context

Read metrics/statpack.md: modern discretionary-cert dispositions, originating-circuit cut, paid scored-segment relist and CVSG cuts, and the sal-v4 per-Term segment table. Read metrics/statpack.json to obtain exact high-band reached numerators and denominators for every displayed Term preceding 2025. Local jq arithmetic produced a weighted denominator of 898 and pooled rate 0.34966592427616927. These are committed aggregate inputs, not live corpus lookups. No fedcourts query or open-events command was used, and no ranged corpus reads transfer line was produced.

## External retrieval attempts

1. web.run search_query: `site.supremecourt.gov opinions 2024 Cantero 22-529 national bank preemption`. The tool returned no usable result content.
2. web.run open: the original 2024 slip-opinion address, `https://www.supremecourt.gov/opinions/23pdf/22-529_1b7d.pdf`. The tool returned no usable content. This was an attempt to read the pre-existing 2024 authority, not the present petition's outcome.
3. CourtListener MCP search: type `o`, citation `602 U.S. 205`, court `scotus`, num_results `2`. Returned two representations of Cantero v. Bank of America, N.A., decided May 30, 2024, docket 22-529. Used the original precedent identification only, not subsequent citing cases.
4. CourtListener MCP search_document: opinion_id `11066676`, query `nuanced`, snippet_size `1800`. Returned one syllabus excerpt explaining practical assessment and comparative analysis under Barnett Bank and Dodd-Frank, and the original 2024 disposition. This concerns a pre-decision precedent, not the target event.

## Local tooling

Read AGENTS.md, the prediction prompt, and the prediction/tooling/flags schemas. Ran `uv run fedcourts paths --court scotus --docket 73500252 --event evt-order-cvsg-disposition --role predictor`; the initial attempt failed because the default uv cache directory was read-only. Repeated successfully with the cache redirected to `/tmp/uv-cache`. That workaround changes no pipeline source or provisioned input. Validation uses the same temporary cache location. No direct CourtListener REST request was made.
