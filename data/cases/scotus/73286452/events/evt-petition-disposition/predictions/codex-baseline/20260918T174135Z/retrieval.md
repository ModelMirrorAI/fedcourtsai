# Retrieval record

## Provisioned baseline

Read the cell's event definition, `record/context.json`, `record/snapshots/2026-09-17.json`, and `record/documents/{documents.json,questions-presented.txt,petition.txt,brief-in-opposition.txt}`. Read the governing prompt and schemas. No outcome, other predictor's output, or topic-labeling artifact was read.

## Additional local context

- Read `metrics/statpack.md`: modern cert dispositions, paid relist/CVSG and circuit cuts, and the sal-v4 per-Term reached-band table.
- Read the corresponding fields of `metrics/statpack.json`. Pooled only displayed Terms 2017–2024 for the elevated-band anchor: weighted grants 484, weighted resolved denominator 2810, rate 0.17224199288256228.
- Used `git log -1 --format='%h %cI' -- metrics/statpack.md metrics/statpack.json` to identify committed-pack vintage: `55121cdb8`, September 14, 2026, 11:02 UTC. This does not establish remote corpus freshness.
- Ran `uv run fedcourts paths --court scotus --docket 73286452 --event evt-petition-disposition --role predictor`; the initial default cache location was read-only. Repeated successfully with the cache directed to `/tmp/uv-cache`. This resolved paths, not case evidence.
- Read path and serialization helpers to keep output location and serialization consistent with the repository contract. No corpus query or open-events command was used; consequently there are no ranged-corpus transfer lines to report.

## Web attempts

The following attempts returned no usable content in this session and supplied no substantive evidence:

1. Search queries `site.supremecourt.gov opinions Shurtleff Boston 2022 20-1800 government speech` and `site.supremecourt.gov opinions Chiles Salazar 2026 24-539` in one call.
2. Open `https://www.supremecourt.gov/opinions/21pdf/20-1800_7lho.pdf`.
3. Find `reversed` in attempted reference `https://www.supremecourt.gov/opinions/25pdf/24-539new_3fb4.pdf`.
4. Open that attempted Chiles reference.
5. Retry the Shurtleff PDF open.

## CourtListener MCP

1. `search(type="o", citation="596 U.S. 243", num_results=1)`: returned Shurtleff v. Boston, decided May 2, 2022, cluster 6468902, opinion 6341013.
2. `search_document(opinion_id=6341013, query="holistic", snippet_size=1700)`: read the syllabus and majority passage on the contextual government-speech inquiry, including majority slip pp. 5–6.
3. `search(type="o", case_name="Chiles v. Salazar", court="scotus", filed_before="2026-04-29", num_results=2)`: returned the March 31, 2026 original and revised opinions. Used revised opinion 11297434, cluster 10830655. These precede this petition and were already discussed in the provisioned briefs.
4. `read_document(opinion_id=11297434, chunk_index=0, chunk_size=11000)`: read the opening syllabus excerpt explaining the talk-therapy holding. Did not read the entire opinion.

Retrieval was limited to these general precedents, not Khatibi's Supreme Court disposition or later history. Chiles is a separate, already-decided precedent, not the target outcome. No direct CourtListener REST requests were made.
