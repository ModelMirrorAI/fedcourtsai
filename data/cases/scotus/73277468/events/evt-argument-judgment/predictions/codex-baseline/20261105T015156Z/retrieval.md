# Retrieval record

## Provisioned evidence

Consulted the event definition and case-level `record/context.json`, `record/snapshots/2026-11-03.json`, `record/documents/documents.json`, `questions-presented.txt`, relevant petition and appellate-appendix excerpts, the two opening merits briefs, petitioner's merits reply, `argument-transcript.txt`, and `argument-features.json`. No other prediction or evaluation was read. No own-case outcome, subsequent-history search, or live docket lookup was attempted.

## Additional local reference material

- Read the prediction prompt and relevant prediction, flags, and tooling schemas.
- Consulted `metrics/statpack.md`'s merits and complete-lineup sections and `metrics/statpack.json`'s merits, justice-vote, and authorship term records. Pooled only eligible Terms preceding grant Term 2025; no corpus query or outcome-row retrieval was used.
- Inspected `src/fedcourtsai/pipeline/claims.py` for distribution-label conventions; one simultaneous attempt to inspect `src/fedcourtsai/justices.py` found no such file. Used the prompt's surname roster instead.
- Ran `uv run fedcourts paths --court scotus --docket 73277468 --event evt-argument-judgment --role predictor`. The first attempt failed because the default uv cache was on a read-only filesystem. Repeated with `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`; it returned the case ID, corpus path, and event path. No package installation or corpus retrieval occurred, and no ranged-corpus-read line was printed.

## Web tool attempts

The following calls concerned general procedural rules, not Younge's disposition. Each returned no usable result text or source reference in this session; none supplied factual evidence for the forecast.

1. `search_query`: `site.uscourts.gov Federal Rules Civil Procedure Rule 8 Rule 15 Rule 16 Rule 61 December 2025`.
2. `open`: `https://www.uscourts.gov/forms-rules/current-rules-practice-procedure/federal-rules-civil-procedure`.
3. `find`: the same official URL, pattern `.pdf`.
4. `open`: repeated the same official URL.

No external rule text was obtained from these attempts. The rule arguments instead come from the provisioned filings and transcript, with the Foman precedent checked separately below.

## CourtListener MCP

1. `search(type="o", citation="371 U.S. 178", num_results=1)`, query ID `5a51ab89`. Returned a nonmatching Rose v. Cox Health Systems cert-denial record, not Foman. Disregarded it; no pagination attempted.
2. `search(type="o", case_name="Foman v. Davis", court="scotus", filed_before="1963-01-01", num_results=2)`, query ID `71df5787`. Returned the December 3, 1962 merits opinion, 371 U.S. 178, opinion/cluster 106497, and the earlier cert grant. Selected only the merits opinion.
3. `read_document(opinion_id=106497)`. Read Foman's 9,740-character opinion text. It supports liberal amendment while identifying undue delay, bad faith, repeated deficiencies, prejudice, and futility as amendment considerations. It also rejects an overly technical treatment of appellate notices. Used to check both sides' characterization of that precedent, not to obtain information about the present case.

No further web, CourtListener, or corpus calls were attempted. Cell validation is a local output-contract check, not legal retrieval.
