# Retrieval record

The case's own event, snapshot, context, manifest, and document texts were provisioned inputs. No outcome, other prediction, evaluation, case summary, or `data/qp-topics/` content was read. External research concerned prior decisions only; no search sought this case's disposition, later docket state, or decision coverage.

## Local context beyond the provisioned record

- Read `metrics/statpack.md`, particularly its merits and per-Justice sections; queried `metrics/statpack.json` for the merits, vote, and authorship tables and pooled strictly prior Terms. Also read relevant reporting cautions in `metrics/README.md`. The merits pool is 375/533 disturbed, with 533/549 coverage and 40 excluded dispositions, using available 2017–2024 rows within the required 2015–2024 window. Vote/authorship rows used were 2020–2024, not OT2025.
- Read the prediction, tooling, and flags schemas to implement the output contract. Used local path resolution and the required validator; these do not retrieve court facts.

## CLI setup and failed attempts

1. `uv run fedcourts paths --court scotus --docket 73280341 --event evt-brief-judgment --role predictor` failed before running the CLI because uv could not create `/home/codexcell/.cache/uv/CACHEDIR.TAG` on a read-only filesystem.
2. `uv run fedcourts query --help` failed for the same cache reason. Neither attempt returned court data or a transfer line.
3. Reissued path resolution with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1`; it succeeded. Reissued `uv run fedcourts query --help` under those environment settings; it succeeded, and its help was consulted again through `tail -68` before the broader query. No transfer line accompanies help or path resolution. Disabling synchronization avoided package installation.

## Corpus calls

All successful commands used the prefix `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1`. The shell's `DECIDED_BEFORE` was empty; these forward-cell queries nevertheless included an explicit prior-Term bound.

1. `uv run fedcourts query --court scotus --citation '568 U.S. 398' --decided-before 2025 --limit 2`

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

   Returned no matching prior. The coverage note said only 200 in-scope SCOTUS rows carried reporter citations and that these are the case's own citations, not citing-authority links. Used CourtListener instead of treating the empty result as an absence of precedent.

2. `uv run fedcourts query --court scotus --disposition granted --decided-before 2025 --limit 3`

   `ranged corpus reads: 72 GET(s), 18874368 byte(s)`

   Returned RiseandShine v. PepsiCo (24-1016), Monsanto v. Durnell (24-1068), and Hikma v. Amarin (24-889). These rows carried grants but no usable merits holdings. The year mask is not proof that each returned grant predates the named year; grant dates in 2026 remained visible. I did not treat these as resolved analogous merits precedents, hydrate opinions, or adjust the prediction from them. The target case was not among the returned rows.

## CourtListener MCP calls

1. `search(type="o", court="scotus", citation="568 U.S. 398", num_results=1)` returned *Clapper v. Amnesty International USA*, decided February 26, 2013, cluster 821306, with lead opinion 9502825 and a Court PDF link. Verified the case identity and citation.
2. `search_document(opinion_id=9502825, query="manufacture standing", snippet_size=600)` returned three excerpts confirming the rule concerning self-imposed precautions against insufficiently imminent harm. Relied on the rule, not the unrelated surveillance facts.
3. `search(type="o", court="scotus", case_name="Mirabelli v. Bonta", filed_before="2026-10-22", num_results=1)` returned the March 2, 2026 prior decision, docket 25A810, cluster 10802600, opinion 11269328, and its official PDF location. This is a different case from the prediction target. The opinion text was then read from the Court's website, not through a further MCP document request.

## Web calls

Every attempted web call is listed, including unsuccessful opens. Search-result commentary was not used to establish the target's facts or outcome.

1. Combined searches: `site.supremecourt.gov "Mirabelli" "2026" "standing"` and `site.supremecourt.gov "Clapper" "568" "398"`. Results included a reproduction of *Mirabelli* and general standing material. No target-case search was made.
2. Opened the prior opinion reproduction at `https://www.law.cornell.edu/supremecourt/text/25A810`. It supplied the March 2, 2026 *Mirabelli* opinion, Barrett concurrence, and Kagan dissent. The subsequently retrieved Court PDF was the controlling source used for the narrow discussion in reasoning.
3. Searched `"25A810" "supremecourt.gov/opinions"` to locate the official prior opinion. Results included the Cornell reproduction and material about that other case. This search did not reliably identify the official PDF; CourtListener subsequently did.
4. Attempted `https://www.supremecourt.gov/opinions/12pdf/11-1025_ihdj.pdf`, the *Clapper* download URL supplied by CourtListener with HTTPS substituted. Returned 404. No opinion text was obtained there; the successful MCP excerpts supplied the rule.
5. Opened `https://www.supremecourt.gov/opinions/25pdf/25a810_b97d.pdf`, the *Mirabelli* PDF identified by CourtListener. Successfully read the 21-page prior opinion package, especially the standing discussion, Barrett concurrence, and Kagan dissent. It concerns California school policies, not this Washington shelter case, and predates the target's briefing moment. Used it to assess the doctrinal bridge and likely lineup, with the interlocutory posture and factual differences expressly discounted.
6. Attempted `https://www.supremecourt.gov/opinions/24pdf/24-7_eo8b.pdf` while checking a possible official location for *Diamond Alternative Energy*. Returned 404. No text was obtained or relied upon; discussion of that authority rests on the provisioned parties' arguments, not this failed URL.

No package installation, direct CourtListener REST request, or corpus-wide download was attempted. No outcome-revealing material about the target surfaced.
