# Retrieval record

## Provisioned inputs

Read the case's `event.yaml`, `record/context.json`, `record/snapshots/2026-09-16.json`, and `record/documents/{documents.json,questions-presented.txt,petition.txt}`. No additional case-specific record, docket, outcome, appendix, or brief in opposition was fetched.

## Local context beyond the provisioned inputs

- Read the governing `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, tooling, and flags JSON schemas.
- Read `metrics/statpack.md`, specifically the modern discretionary-cert population, originating-court context, paid-scored relist/CVSG cuts, and sal-v4 segment table. Read `metrics/statpack.json` to pool exact reached-baseline data for Terms 2017–2024. The executed calculation returned numerator 593, weighted denominator 11,580, and rate 0.05120898100172712. No individual corpus cases were queried.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`; it returned commit `55121cdb8`, September 14, 2026 at 11:02 UTC. This is file provenance only, not corpus freshness.
- Ran `uv run fedcourts paths --court scotus --docket 73309407 --event evt-petition-disposition --role predictor`. The default-cache attempt failed on the read-only home directory; the retry with a temporary cache succeeded. The command masked the evaluator-only outcome path. No outcome file was opened.
- Read relevant portions of `src/fedcourtsai/paths.py`, `src/fedcourtsai/ids.py`, and `src/fedcourtsai/serialize.py` to use canonical paths and serialization. These are implementation references, not case evidence.

No `fedcourts query` or `open-events` call was made; there are no ranged-corpus transfer lines to report. The corpus blob was not pulled or interrogated.

## General web attempts

The following `web.run` calls returned no usable result content and contributed no legal facts:

1. Search: `site.supremecourt.gov Rule 10 certiorari rarely granted erroneous factual findings`.
2. Search in the same call: `site.uscode.house.gov 28 USC 1257 final judgments highest court state`.
3. Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
4. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.

I then fetched the public reproduction of Supreme Court Rule 10 at `https://www.law.cornell.edu/rules/supct/rule_10` with `curl --max-time 20 -fsSL` and selected the rule text. It supplied the discretionary-review, conflict, important-federal-question, and fact-error principles cited in the rationale. No case-name query was made through the web and no scientific source was fetched.

## CourtListener MCP

1. `search(type="o", court="scotus", case_name="Cox Broadcasting Corp. v. Cohn", num_results=1)` returned the March 3, 1975 decision, 420 U.S. 469, cluster 109207, including lead-opinion ID 9426016. Purpose: verify the general state-judgment finality doctrine and avoid treating interlocutory posture as an absolute bar.
2. `search_document(opinion_id=9426016, query="finality", snippet_size=2200)` returned the discussion of section 1257, the final-judgment rule, and exceptions. I used the jurisdictional discussion, not the unrelated press/privacy merits. No current citing-case or target-docket lookup followed.

All retrieved litigation material concerned this historical precedent, not the target petition or its later history. The sanctioned MCP worked; no direct CourtListener REST call was made.
