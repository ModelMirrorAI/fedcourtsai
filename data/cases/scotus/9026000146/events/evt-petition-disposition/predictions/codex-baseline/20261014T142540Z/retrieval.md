# Retrieval record

## Local references beyond provisioned inputs

- Read AGENTS.md, .github/prompts/predict.md, schemas/prediction.schema.json, schemas/agent_flags.schema.json, and schemas/agent_tooling.schema.json for the output contract.
- Read metrics/statpack.md: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist/CVSG cuts, and sal-v4 reached-band table. Used metrics/statpack.json to compute weighted state and federal reached rates across displayed Terms 2017–2025. No current-Term anchor was used.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json`: cf9ae960e, 2026-10-13T19:17:46Z. This is artifact vintage, not corpus freshness.
- Ran `uv run fedcourts paths --court scotus --docket 9026000146 --event evt-petition-disposition --role predictor`. The initial attempt failed on the default cache's read-only location; retrying with a writable temporary cache succeeded. No corpus query or open-events lookup was made, and there were no ranged-corpus-read transfer lines.

## CourtListener MCP

1. Search opinions, court ca10, docket_number 24-1191, filed_before 2026-07-31, five-result limit. Returned Daley v. Choate, November 3, 2025, cluster 10729625, opinion 11196210, matching the provisioned lower-court docket and decision date.
2. Search opinion 11196210 for literal `circuit`, 500-character context. Located the express disagreement with the Fourth and Fifth Circuits.
3. Read opinion 11196210, 8,000-character chunks 0, 7, and 8; the displayed response was partially truncated. Then read 4,500-character chunk 1 separately to verify the question, excluded appellate issues, and fee-award posture. Relied on the portions actually displayed, not an assumed full read.
4. Search opinions for `"Obando-Segura" OR "Barco v. Witte"`, courts ca4/ca5, filed_before 2025-11-04, five-result limit. Returned Gomez Barco v. Witte, 65 F.4th 782 (2023), opinion 9388593, and United States v. Conyers, 108 F.4th 351 (2024). Conyers was not opened or used.
5. Search opinion 9388593 for literal `Obando`, 650-character context: no matches.
6. Read opinion 9388593, 6,000-character chunk 1, then chunk 2. Confirmed the Fifth Circuit's contrary EAJA holding and its express disagreement with other circuits.

## Web attempts

- Attempted to open the official Tenth Circuit PDF identified by the MCP result: `https://www.ca10.uscourts.gov/sites/ca10/files/opinions/010111328396.pdf`. The web tool returned no usable content.
- Searched `site.ca10.uscourts.gov "24-1191" "EAJA"`. The web tool returned no usable results. No factual claim relies on either web attempt.

No Supreme Court disposition, subsequent history of this petition, other predictor output, evaluation, outcome file, or topic-label measurement artifact was sought or read. All substantive external documents consulted predate the petition's filing.
