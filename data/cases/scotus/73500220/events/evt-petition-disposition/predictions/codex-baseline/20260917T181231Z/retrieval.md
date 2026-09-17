# Retrieval log

## Local sources beyond the provisioned record

- Read `metrics/statpack.md`: modern discretionary-cert disposition totals; originating-circuit background; paid-segment terminal relist/CVSG cuts; and the sal-v4 reached-band table. Read `metrics/statpack.json` for its metadata shape and the unrounded baseline risk sets. Pooled only displayed Terms 2017–2024: 593 / 11,580 = 0.05120898100172712. Later Term rows were visible in the pack but were not included in the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`: pack commit `55121cdb8`, September 14, 2026 at 11:02:00 UTC. This dates the committed artifact, not the underlying corpus's refresh.
- No `fedcourts query` or `open-events` calls; no ranged corpus reads or transfer lines.
- Read the task contract, prediction/flags/tooling schemas, and path/serialization helpers for artifact construction. Ran `fedcourts paths --court scotus --docket 73500220 --event evt-petition-disposition --role predictor`; the first invocation failed on the default read-only cache and the retry with a writable temporary cache succeeded. No outcome file was read.

## General-precedent web attempts

The following calls returned no usable results or page content:

1. Search: `site.supremecourt.gov opinions Padilla Kentucky 559 356 collateral consequences Chaidez 568 342`.
2. Batched searches: `Chaidez United States 2013 site.supremecourt.gov/opinions` and `Padilla Kentucky 2010 site.supremecourt.gov/opinions`.
3. Open: `https://www.supremecourt.gov/opinions/12pdf/11-820_j426.pdf`.
4. Open: `https://www.law.cornell.edu/supct/pdf/11-820.pdf`.

These attempts supplied no evidence and did not search the target petition.

## CourtListener MCP

1. `search(type="o", citation="568 U.S. 342", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: returned *Chaidez v. United States*, decided February 20, 2013; cluster path `/opinion/820897/chaidez-v-united-states/`, lead opinion ID 9502786. Read the returned metadata and snippets, not additional search pages.
2. `search_document(opinion_id=9502786, query="new rule", snippet_size=550)`: read returned excerpts explaining the new-rule/settled-rule distinction and the holding that Padilla does not reopen convictions final before its announcement. Used this to check the legal background to Appendix A's separate retroactivity ground, not to retrieve the target case's outcome.

No target-case live docket, later history, or disposition lookup was attempted.
