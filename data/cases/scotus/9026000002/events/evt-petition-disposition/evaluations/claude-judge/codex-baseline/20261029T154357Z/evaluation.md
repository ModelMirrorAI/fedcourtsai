# codex-baseline — scotus/9026000002, evt-petition-disposition

## Outcome and scoring

Cert-stage cell (`stage: cert`), forward mode. Outcome: `dismissed`, `actual_granted` 0, resolved 2026-10-26 — the docket shows a joint stipulation to dismiss under Rule 46 filed 2026-10-23 and "Petition Dismissed - Rule 46" on 2026-10-26. All three candidates predicted `denied`, so `correct` = 0 for each on the exact-label axis (dismissed ≠ denied), though each was right on the binary no-grant axis that the Brier score reads.

The prediction froze `band: baseline` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I left them null and refer only to "the stamped segment base rate".

Leakage: forward; prediction made 2026-10-06 against a snapshot ending 2026-08-14, a fortnight before the Rule 46 stipulation existed. No retrieved document dates on or after resolution, no query reaching this docket's disposition, no qp-topics read. `not_applicable`, `leakage_suspected` false.

No semantic set is declared on a cert cell, so no `semantic_grades`. Votes not scored (cert stage).

## This candidate

P(grant) 0.30, predicted `denied`. Brier 0.09.

**reasoning_quality 0.7.** A careful, well-disciplined analysis. It read the full provisioned record, explicitly anchored on pooled bracketed baseline reach rates from the statpack with its arithmetic disclosed, verified the *GE Energy* reservation and the *Setty* comparator through targeted lookups, and correctly identified the petition's follow-on/hold posture and the summary-affirmance vehicle weakness. It honestly flagged the snapshot freshness gap (last proceeding Aug 14 despite an Oct 5 filename) and the missing BIO. It even decomposed its residual into denial vs. "another non-grant termination" (2%).

Weaknesses: the step from ~5% to 30% is large and admitted to be unfitted judgment; the 22.5% cert-order relief component leans heavily on a lead-case outcome it did not research (it did not look at the lead docket), so the derivative pathway is priced without evidence of the lead's prospects. The settlement/dismissal route was under-weighted relative to the visible signals (repeated extensions, a pending trial below), but that is hard to see without the lower-court docket. Overall sound reasoning; the number ran somewhat hot.
