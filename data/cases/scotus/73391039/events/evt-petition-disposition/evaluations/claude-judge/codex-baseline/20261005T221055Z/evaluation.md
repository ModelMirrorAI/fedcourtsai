# Evaluation: codex-baseline — Foley v. Orange County, No. 25-1308 (evt-petition-disposition)

## Outcome and scores

The petition was **denied** on the October 5, 2026 order list after a single distribution (conference of September 28, 2026), with no noted dissent. Cert stage, forward mode.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.006 − 0)² = 0.000036.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack table's heading, so the bracketed *reached* figures apply, pooled resolved-weighted over OT2017 through OT2024 (n = 11,580): 0.0512. The candidate's own pool from `statpack.json` (593 / 11,580 = 5.12%) agrees to the fourth decimal. The caption renders 10 of 10 Terms, so no window-divergence flag.
- `brier_skill_score` = 1 − 0.000036 / 0.0512² ≈ 0.9863.
- No `vote_accuracy` (cert stage). No semantic block (cert event declares none).

## Reasoning quality: 0.84

A careful, well-bounded rationale that reaches the right analysis by the right route, slightly weighed down by process narration.

What it got right:

- **Information discipline is explicit and correct.** It states what it read, that the appendices were not provisioned so the petition's account of the lower courts is advocacy, that the 2024 cert denial mentioned in the petition is prior history and not this event's outcome, and that it neither sought nor learned the disposition.
- **The anchor is computed, not estimated**, from the `statpack.json` segment rows, with the correct Terms and the correct reached denominator, and the rationale correctly declines to stack the terminal relist and CVSG buckets as independent adjustments.
- **The split is dissolved on the right ground**: the cited circuits agree that relief from a void judgment is mandatory; none holds that a Rule 60(b)(4) movant may relitigate what an earlier appellate panel necessarily decided. The rationale also notes the petition's own concession that the conflict is with this Court's precedent rather than between circuits.
- **Espinosa was actually checked** through CourtListener (opinion 1727, 559 U.S. at 270–72) and applied correctly: voidness is confined to jurisdictional or notice/opportunity defects, so a disputed reading of the pleaded property interest does not reach it. That is the step the petition's theory needed and could not make.
- **Vehicle features** (unreported decision, sanctions, repeat posture, waivers, no response request) are weighed as indications rather than as proof, which is the right epistemic stance given a one-sided record.
- It keeps a floor above zero for the right reason: the one-sided record might understate the voidness argument.

What limits it:

- **Process narration crowds the analysis.** Paragraphs on the uv cache, the `paths` command, the statpack file vintage via `git log`, and the failed web fetches are honest disclosure but belong in `retrieval.md`; in the rationale they dilute the legal argument without strengthening it.
- The `big_case` rationale at 0.22 is out of proportion to the rest of the document's own conclusion that the petition is a case-bound disagreement with settled doctrine; the rationale concedes as much ("the vehicle and concrete controversy are narrow") and still lands high. That block is not part of the graded quality but the internal tension is a small mark against coherence.
- Like the others, the depth of the discount from 5.1% to 0.6% is a judgment the pack cannot calibrate, and the rationale says so, which is to its credit.

## Leakage: forward, not applicable, `leakage_suspected` false

Mode `forward`. Prediction created September 17, 2026 against the September 16 snapshot, before the September 28 conference and the October 5 denial. Result capture coverage is 0.76: the shell reads of the prompt, record, petition and statpack are captured; two captured CourtListener calls fetched and searched the Espinosa opinion (a 2010 precedent, not this case); eight `web-search` rows are `unobserved` and so are graded on their queries, which are all attempts to reach the Espinosa opinion PDF or an unrelated OT2025 opinion URL (24-808). None names this petition, its docket number, or its disposition. No `data/qp-topics/` read. The candidate's `retrieval.md` states the same and discloses the failed web attempts. `retrieved_outcome_material` = false. The case was genuinely open at prediction time.

## Big case: 0.05 (independent read)

Formed before reading the candidate's score. A pro se Rule 60(b)(4) / law-of-the-case petition from an unreported Eleventh Circuit affirmance of a local code-enforcement dispute; respondents waived, no response requested, denied at first conference. Stakes confined to the parties.

## Not graded here

`predicted_reasoning.md` and the `claims` block were read for context only; the harness scores the claims in code and the forecast document is not graded on any stage.
