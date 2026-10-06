# Evaluation: codex-baseline — scotus/73280412, evt-petition-disposition

**Outcome.** Cert stage. On October 5, 2026 the Court granted the petition, vacated the Ninth Circuit's judgment, and remanded for further consideration in light of *Louisiana v. Callais*, 608 U.S. 85 (2026): `actual_disposition = gvr`, `actual_granted = 1`, after three distributions and no CVSG.

**Prediction.** `predicted_disposition = gvr`, `probability = 0.84`, `granted = 1`.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | exact label match, `gvr` against `gvr` |
| `brier_score` | 0.0256 | (0.84 − 1)² |
| `segment_base_rate` | 0.3495 | `high` band, `sal-v4`, risk-set basis (below) |
| `brier_skill_score` | 0.9395 | 1 − 0.0256 / (0.3495 − 1)² |
| `reasoning_quality` | 0.86 | see below |

**Base rate.** The prediction's frozen context carries `band = high` and `salience_version = sal-v4`, matching the statpack table's heading, so the basis is `risk_set`: bracketed `reached` figures for `high` pooled resolved-weighted over OT2017–OT2024 (n = 898), 0.3495 from the rendered table. The candidate itself computed 314/898 = 0.3497 from the unrounded `statpack.json` fields over the same window; the two agree to three decimals. The table renders 10 of 10 Terms, so no window divergence.

## What the reasoning got right

- **The decisive signal, found and given its proper weight.** The candidate retrieved the State's June 2 brief in opposition and the June 10 reply at the exact URLs the snapshot carries, and read that Washington requested GVR treatment in light of *Callais* while the petitioner continued to press the mootness question. It called this "substantially unlike an ordinary opposed, unpublished error-correction petition", which is the right characterisation, and it was the fact that decided the case.
- **A disciplined anchor.** It pooled the correct band, the correct basis, the correct window, and said what it did not know (no refreshed corpus, no `last_pulled`). It also correctly declined to multiply the terminal relist-bucket cuts into the band rate, and correctly read the three distributions as a reschedule and a response request rather than two substantive relists.
- **A coherent allocation.** The reasoning lays out 0.805 GVR, ~0.01 other cert-order grant, ~0.025 plenary grant, 0.15 denial, 0.01 other, and derives the 0.97 conditional summary route from it. The pieces add up and the headline label follows from them.
- **Clear information boundary.** It states exactly what it fetched, that the filings predate the snapshot, that it did not search for the disposition, and that it did not treat either side's assertions as adjudicated. The retrieval note is precise about access method and the absence of saved copies.

## Where it was weaker

- **It did not test the main downside.** The State's GVR request was conditional on GVR treatment of *Soto Palmer* in *Trevino*, and the *Soto Palmer* plaintiffs pressed an intervenor-standing objection to the *Trevino* appeal. The candidate noted the conditionality and the State's alternative mootness defence, but did not retrieve the companion docket or engage with the standing argument that was the most plausible route to a denial of both petitions. It priced that risk at about 0.16 anyway, which proved right, but the number rested more on the filings' framing than on an independent look at the companion case.
- It did not independently confirm *Callais* or the Court's post-*Callais* GVR practice, relying on the State's account. The account was accurate, so no harm resulted, but a forecast that leans this hard on an intervening decision would ordinarily check it.

`reasoning_quality` is 0.86: correctly anchored, correctly sourced, internally coherent, and confident in proportion to the strength of a signal it correctly identified as decisive. The deductions are for thinner coverage of the one scenario that could have made it wrong.

## Leakage

Forward cell (`mode = forward`). Created 2026-09-16, resolved 2026-10-05. The log's 34 calls include two `unobserved` opens and four in-memory fetches of the two briefs at the snapshot's own URLs (both pre-snapshot filings); no web search, no docket-page fetch, no CourtListener or corpus call. All calls are dated September 16, nineteen days before the order list. One `find` command excludes `data/qp-topics/` by path and reads nothing under it. Nothing in the log or prose reads this petition's disposition. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case

My own read, formed before reading the candidate's: 0.35. The candidate's 0.62 weights the recurring Equal Protection / VRA remedy interaction more heavily than I do for a petition whose own disposition was a one-line GVR. I record no agreement number.

## Not scored here

`claim_scores` is the harness's. The forecast document was read for context only. No `semantic_grades` (cert cell; no `semantic_claims`). No `vote_accuracy` (cert stage).
