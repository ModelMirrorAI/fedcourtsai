# Retrieval record

## Local inputs and statistical context

Read the prediction contract and prediction schema; event definition; case-level context and November 7, 2026 snapshot; document manifest; questions presented; substantive portions of the petition, BIO, cert reply, respondent supplemental brief and matched appellate decision; and the lower-court docket report. No other prediction, evaluation, realized-outcome file, or topic-label artifact was read.

Beyond those provisioned inputs, consulted the merits, per-Justice votes, and authorship sections of `metrics/statpack.md` / `metrics/statpack.json`, and the merits methodology in `metrics/README.md`. Used `jq` to pool the prior grant-Term merits counts and prior decision-Term per-Justice counts. No corpus outcome or opinion body for this case was fetched.

## Corpus CLI attempts

1. `uv run fedcourts query --help` (with `UV_CACHE_DIR=/tmp/uv-cache`) returned the structured-filter CLI help.
2. `uv run fedcourts query --court scotus --disposition reversed --era modern --decided-before 2026 --limit 3` (same cache override) was rejected: `reversed` is not a cert-disposition label. The error also supplied the accepted disposition and decade-era vocabularies. No records or transfer line returned.
3. `uv run fedcourts query --court scotus --citation '584 U.S. 497' --era 2010s --decided-before 2026 --limit 2` (same cache override) returned no rows. Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`. The tool warned that only 200 SCOTUS rows in scope carried any reporter citation, so the empty result was not evidence against the precedent's existence.
4. The identical exact-citation command was repeated because the first command's combined display was truncated. It again returned no rows, the same sparse-citation warning, and `ranged corpus reads: 0 GET(s), 0 byte(s)`.
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3` (same cache override) returned three docket skeletons: this case's November 6 cert grant, U.S. DOGE Service v. United States District Court, and Corey Duran Berry v. United States. Stderr: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`. The coarse year mask did not make these rows pre-grant merits comparators; none supplied a merits judgment or opinion. The target row repeated only already-provisioned cert history and was not used as new evidence. No query targeted this case's eventual merits disposition.

## CourtListener MCP calls

1. `search(type="o", citation="584 U.S. 497", num_results=1)` returned Epic Systems Corp. v. Lewis, decided May 21, 2018, cluster 4499694, combined opinion 4276947, identifying Gorsuch and the official opinion PDF.
2. `search_document(opinion_id=4276947, query="clear and manifest", snippet_size=1800)` returned two matches, one in the syllabus and one in the majority's statutory-reconciliation discussion. Used the latter to confirm the demanding displacement standard.
3. `search(type="o", citation="565 U.S. 95", num_results=1)` returned an inexact top hit, Mims v. Arrow Financial Services, not CompuCredit. That hit was not relied on; no Mims opinion body was read.
4. `search(type="o", case_name="CompuCredit Corp. v. Greenwood", court="scotus", num_results=1)` returned the January 10, 2012 case, cluster 620568, lead opinion 9485182, concurrence 9485183, dissent 9485184, and combined opinion 620568. Used the metadata identifying Scalia's lead opinion and Sotomayor's concurrence joined by Kagan.
5. `search_document(opinion_id=[9485182,9485183], query="contrary", snippet_size=1000)` returned lead-opinion and concurrence passages on contrary congressional intent and the opponents' burden. Used these as general legal context and a caution against treating the vote forecast as automatic ideological sorting.

All substantive retrieved opinions precede this case. No Supreme Court or lower-court search requested this case's outcome or subsequent history.

## Web attempts

The web tool returned no usable content for each of the following attempts; none supplied facts used in the forecast:

1. Search batch: `site.supremecourt.gov opinions Epic Systems Lewis 2018 arbitration clear manifest congressional`; `site.supremecourt.gov opinions CompuCredit Greenwood arbitration 2012`.
2. Search batch: `Epic Systems Corp Lewis 584 U.S. 497 2018 opinion`; `CompuCredit Corp Greenwood 565 U.S. 95 opinion`.
3. Open the Epic Systems official opinion PDF identified by CourtListener: `https://www.supremecourt.gov/opinions/17pdf/16-285_q8l1.pdf`.

## Operational checks

The first `uv run fedcourts paths --court scotus --docket 73520108 --event evt-order-judgment --role predictor` failed because the default uv cache directory was read-only. Repeating it with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. This changed no inputs and installed nothing. The same cache override is used for validation. Shell file listings, schema reads, and `git status --short` were operational checks, not additional case retrieval.
