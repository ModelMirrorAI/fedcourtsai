# Retrieval record

## Provisioned and committed local inputs

Read `.github/prompts/predict.md`, the prediction/tooling/flags schemas, the event definition, `record/context.json`, `record/snapshots/2026-11-08.json`, and the document manifest, questions presented, petition, and appendix under the case-level `record/documents/`. Consulted `metrics/statpack.md`, especially modern-cert dispositions, Fifth Circuit origin, paid-segment relist/CVSG/amicus cuts, and the sal-v8 prior-Term reached-band table. No own-case outcome, other prediction, evaluation, or topic-label artifact was read.

## Tooling setup and corpus

1. `uv run fedcourts paths --court scotus --docket 9026000378 --event evt-petition-disposition --role predictor` failed before execution because `/home/codexcell/.cache/uv/CACHEDIR.TAG` was on a read-only filesystem. No case material returned.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000378 --event evt-petition-disposition --role predictor` succeeded and named the case, corpus, and event paths. Its outcome entry was explicitly evaluator-only; no outcome was opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded; the help was consulted again with `| head -64` to inspect the structured options. These were help calls, not case queries.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3` returned three denied petitions: Google LLC v. VirtaMove, Corp., No. 25-1230; Hastings College Conservation Committee v. California, No. 25-1231; and Ryan O'Donnell v. City of Chicago, No. 25-1098. The returned denial dates were October 19, 2026. This is a denial-filtered, nontopical sample, not a calibrated analogue set or a grant-rate estimate. None is the petition being predicted. No full opinion hydration was requested.

   Exact transfer report: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`.

`DECIDED_BEFORE` was empty and context mode was forward. The explicit `--decided-before 2026` was an additional prior-Term corpus filter, not a claim that these denial dates precede calendar year 2026.

## Web lookups

5. One `web.run` search call used two queries: `site.law.cornell.edu 28 USC 1915 e 2 fails to state claim` and `site.supremecourt.gov "Chiaverini" "2024" probable cause`. Results concerned Chiaverini: official argument audio, calendars and case-distribution material, the 2024 slip opinion, a 2024 journal, and the bound-volume opinion. Only the general charge-specific probable-cause holding was material; the returned materials were not about this petition's disposition.
6. Opened the official Supreme Court Chiaverini slip opinion, file `23-50_n648.pdf`. Confirmed the June 20, 2024 decision rejects a categorical any-charge bar and leaves causation questions for remand. Used only as pre-existing doctrinal context, not as a dispositive analogy.
7. Opened Cornell LII's reproduction of `28 U.S.C. § 1915`. Confirmed that subsection (e)(2)(B) separately enumerates frivolousness, failure to state a claim, and immunity. Used to test the petition's broad Neitzke-based screening argument.

## CourtListener MCP

8. `search(type="o", citation="866 F.3d 682", num_results=2)` returned McLin v. Ard, decided August 8, 2017, Fifth Circuit docket 16-30201, opinion ID 4194314, cluster 4417061.
9. `search_document(opinion_id=4194314, query="mere allegations", snippet_size=1000)` returned two passages. The relevant passage distinguishes insufficient unsupported allegations at summary judgment from fact-supported allegations sufficient at pleading. This independently supports the panel's stated taint exception and weakens the petition's categorical split characterization. No current Supreme Court docket or subsequent-history search for this case was made.

## Boundaries

No own-case live docket was fetched. No own-case disposition or subsequent history was searched for or encountered. No related or same-question petition was relied on. Corpus and MCP calls succeeded after the local cache-path correction; no REST fallback or package installation was attempted. Path resolution, local reads, JSON/schema inspection, clock/status checks, file writing, and the required validation are workflow operations, not additional substantive retrieval.
