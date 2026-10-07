# Evaluation of claude-baseline — scotus/73286453, evt-petition-disposition

**Cell:** cert stage (`event.yaml` stage `cert`), forward mode. **Outcome:** petition denied on 2026-10-05, the order list after the September 28, 2026 conference; one distribution, no relist, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `noted_dissent_from_denial` false).

## Scores

| Field | Value | How |
| --- | --- | --- |
| correct | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| brier_score | 0.0036 | (0.06 − 0)² |
| segment_base_rate | 0.0512 | `baseline` band, bracketed `reached` figure, pooled over Terms 2017–2024 (below) |
| base_rate_basis | risk_set | the prediction froze `context.band` `baseline` with `context.salience_version` `sal-v4`; the statpack table heading is `sal-v4` |
| brier_skill_score | −0.3732 | 1 − 0.0036 / (0.0512 − 0)² |
| reasoning_quality | 0.85 | below |
| vote_accuracy | omitted | cert stage; never scored here |

**Base rate.** The prediction's frozen context carries both `band` = `baseline` and `salience_version` = `sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the basis is `risk_set` and the figure is the bracketed `reached` rate. The case's Term is 2025 (`context.term`, docket 25-1242). The table renders Terms 2026 through 2017 ("Most recent 10 of 10 Term(s)"); 2026 is empty and 2025 is the case's own Term, so the pool is the eight prior Terms 2017–2024, weighted by each row's bracketed `n`: 592.9 grant-family outcomes over 11,580, or 5.12%. The configured in-code lookback is ten Terms, but the pack holds no rows before 2017, so the rendered window and the code's window coincide and there is no divergence to flag. The rate is computed from the table's rounded percentages, so it is approximate to a few hundredths of a point. The candidate computed the same pooled figure (about 5.1% over 11,580) and used it as its anchor.

## What the prediction got right and wrong

The headline was right and the shape of the forecast matched the event: denied, at the first conference, no separate writing. The probability of 0.06 sits a hair above the anchor, so on a denial its skill is slightly negative; that is the arithmetic of landing on the base rate and is not a reasoning fault. One silent denial cannot distinguish a 0.06 from a 0.01 on calibration, and the question here is whether the number was well derived.

It was. The candidate read every provisioned document in full, including the Eleventh Circuit opinion with Chief Judge Pryor's concurrence and Judge Jordan's partial dissent and the petitioner's own appellate brief reproduced in the opposition's appendix. From that it built a balanced ledger. Upward: a published opinion with a reasoned dissent, full adversarial briefing after an extension rather than a waiver, facts stark enough to support a plaintiff-side summary reversal, and a Gorsuch-authored circuit precedent on the petitioner's side. Downward: the question is a fact-bound clearly-established call rather than a conflict over a legal standard; the asserted split is thin, which the candidate checked rather than assumed, finding through a CourtListener search only Dean and Hughes on the Browder-based question since 2020; the preservation problem is confirmed from the record, since the petitioner's appellate brief pressed obvious clarity without citing Browder or Dean; the interlocutory posture on a motion to dismiss; the unresolved color-of-law question Chief Judge Pryor flagged, which could undo any judgment on remand; the lurking Parratt question; the Court's reluctance to expand substantive due process; and the absence of any institutional or amicus interest. Each point is tied to a page or a document rather than asserted. The candidate also read the statpack's relist-count cut correctly as a terminal bucket that understates a live petition's prospects, the exact error that would otherwise have pulled the number down for the wrong reason.

The downward factors were the operative ones, and the candidate had them all, with the preservation point stated at the right strength (it depends on the unprovisioned reply, which the candidate disclosed as a gap). Minor reservations: the relist conditional of 0.22 looks a little generous for a baseline-band private petition before the long conference, and the claim that plaintiff-side qualified-immunity grants are "overwhelmingly" summary rests on general knowledge rather than a committed cut, which the candidate itself flagged. Neither affects the headline, and the forecast document and claims are not scored here.

## Leakage

Forward mode, and the case was genuinely open: the prediction was created on 2026-09-16, the first conference was 2026-09-28, and the denial came on 2026-10-05. The log is fully captured (coverage 1.0, 22 calls). External calls: two `fedcourts query` runs over scotus 2020s rows filtered only by granted or denied disposition, with no case filter; a CourtListener docket search for 25-1242 returning nothing; a phrase search returning nothing; a caption search for "Hughes v. Locure" returning two later Eleventh Circuit opinions citing it, the latest dated 2026-05-22, which precedes the resolution and is ordinary forward signal; and a Browder-based published-opinion search whose latest document is the decision below, 2026-01-29. One shell call located another case's committed prediction as a format example, with this docket explicitly excluded from the search, so it touched no outcome material for this petition. Nothing under `data/qp-topics/`. The reasoning states it holds no knowledge of the disposition and names the first conference as after the run. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false. The candidate's own `flags.json` is not staged, so this rests on the log and the prose.

## Big case

My own read, formed from the record before weighing the candidate's: 0.22. A private section 1983 suit over a fatal off-duty drunk-driving crash, decided below on the clearly-established prong with a divided published opinion. Some public resonance on police accountability, but interlocutory, fact-bound, clouded on color of law, with no amici or government interest, and denied silently.
