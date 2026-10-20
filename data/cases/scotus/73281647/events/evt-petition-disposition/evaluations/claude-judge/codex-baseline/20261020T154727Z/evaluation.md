# Evaluation — codex-baseline

## Cell and outcome

Cert-stage cell (`stage: cert`), Pena v. City of Los Angeles, No. 25-1163. Forward prediction made 2026-09-16 from the 2026-09-15 snapshot (one distribution, for the 9/28/2026 Long Conference). Outcome: **denied** on 2026-10-19 after two further distributions (10/9 and 10/16 conferences), no CVSG, no noted dissent from denial (`actual_granted` 0).

The prediction froze `band: baseline` under `sal-v4`, so the segment base rate, the Brier skill score, and `base_rate_basis` are the harness's to stamp (the stamped segment base rate); I leave them null. Votes are not scored on a cert cell. The claims block is scored in code and is not graded here.

## Scores

- `correct` = 1 (predicted `denied`, actual `denied`).
- `brier_score` = (0.28 − 0)² = 0.0784.

## Reasoning quality: 0.72

A careful, well-sourced rationale. It anchors on the baseline band's reached rate pooled over Terms before OT2025 (~5.1%), states the adjustment as judgment rather than a fitted ratio, and builds the case for review from the record: the Baker statement (Sotomayor, joined by Gorsuch) asking for percolation, the published Ninth Circuit opinion and the Seventh Circuit companion since, and five amici. Its case against review turned out to be the decisive one: it saw that the circuits disagree in reasoning but reach the same result on law-enforcement facts (BIO pp. 22–25, 31–32), that Alford is distinguishable on its facts, and that further percolation was still plausible. It also kept the parties' characterizations apart from verified facts, and it was honest about the failed retrieval.

Deductions: going from ~5% to 28% is a large jump for a petition whose own analysis puts the split in reasoning, not results. The rationale also does not weigh the Court's run of prior denials on this fact pattern (Lech, Baker, Slaybaugh) as heavily as it should. The relist estimate (48%) was reasonable, since two relists did happen. The 24% chance of a separate writing on denial was reasonable too; none appeared.

## Leakage

Forward mode, and the case was genuinely open on 2026-09-16 (first conference 9/28). The log shows provisioned-input and statpack reads, two uncaptured web calls whose queries target the earlier Baker opinion, and a CourtListener search refused with a 429. The only command naming `data/qp-topics/` excludes it with `find … -not -path`, which opens nothing there. No material resolving this petition was retrieved. `not_applicable`, not suspected.

## Big case (own read): 0.45

A recurring, organized Takings Clause question, but a small-dollar dispute on which every circuit reached the same result. The Court relisted twice and then denied with no noted writing.
