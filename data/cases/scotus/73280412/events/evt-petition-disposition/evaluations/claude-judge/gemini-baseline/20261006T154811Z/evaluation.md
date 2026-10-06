# Evaluation: gemini-baseline — scotus/73280412, evt-petition-disposition

**Outcome.** Cert stage. On October 5, 2026 the Court granted the petition, vacated the Ninth Circuit's judgment, and remanded for further consideration in light of *Louisiana v. Callais*, 608 U.S. 85 (2026): `actual_disposition = gvr`, `actual_granted = 1`, after three distributions and no CVSG.

**Prediction.** `predicted_disposition = denied`, `probability = 0.15`, `granted = 0`.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 0 | `denied` against `gvr` |
| `brier_score` | 0.7225 | (0.15 − 1)² |
| `segment_base_rate` | 0.3495 | `high` band, `sal-v4`, risk-set basis (below) |
| `brier_skill_score` | −0.7074 | 1 − 0.7225 / (0.3495 − 1)² |
| `reasoning_quality` | 0.30 | see below |

**Base rate.** The prediction's frozen context carries `band = high` and `salience_version = sal-v4`, matching the statpack table's heading, so the basis is `risk_set`: bracketed `reached` figures for `high` pooled resolved-weighted over OT2017–OT2024 (n = 898), 0.3495 from the rendered table (314/898 = 0.3497 unrounded). The table renders 10 of 10 Terms, so no window divergence. The forecast was worse than the naive baseline by a wide margin.

## What the reasoning got right

- It read the frozen band and the statpack correctly: `high` band, recent-Term reached rates between roughly 25% and 42%.
- It read the calendar correctly: a reschedule, then a call for a response, then distribution for the September 28 long conference; it recognised the response request as an affirmative signal of interest.
- It correctly identified the companion *Trevino v. Hobbs* petition and the possibility of a hold-and-GVR.

## Where it went wrong

- **It moved against the base rate without reading the briefs.** The State's June 2 brief in opposition and the June 10 reply were linked in the provisioned snapshot. The brief in opposition asked the Court to GVR this petition in light of *Callais*. That was the decisive fact in this docket and it is nowhere in the reasoning. The adjustment from a ~35% anchor down to 15% rests on a generic "vehicle is flawed" characterisation of a mootness appeal, which is the petitioner's framing of the question presented and not evidence about how the Court would dispose of it.
- **It missed *Callais* entirely.** The intervening decision of April 29, 2026 was public nearly five months before the snapshot and is the reason the State wanted a vacatur. A forecast of a Section 2–adjacent redistricting petition in September 2026 that does not mention *Callais* is missing the single most relevant piece of forward context.
- **Internal inconsistency.** The reasoning puts 0.25 on the summary-disposition route "anticipating a possible hold-and-GVR", and the forecast document calls a summary GVR "a distinct possibility". A GVR is a grant on the binary axis. If a hold-and-GVR was a live possibility, P(grant) should have been well above 0.15, and the disposition label should at least have been weighed against `gvr`. The number and the narrative pull in different directions.
- **The denial theory is thin.** "Deny or hold for *Trevino*" treats a hold as a non-grant outcome, but a petition held for a companion and then GVR'd resolves as a grant. The reasoning does not consider that the respondent might not oppose review, which is the posture it was actually in.

The analysis is short, correctly anchored, and then abandons the anchor on a vehicle intuition while leaving the two most important sources in the docket unread. `reasoning_quality` is 0.30: not incoherent, but materially under-informed on the facts it had access to, and inconsistent between its number and its own account of the summary route.

## Leakage

Forward cell (`mode = forward`). Created 2026-09-16, resolved 2026-10-05. The log carries 25 calls, every marker-carrying one `unobserved` (coverage 0.0, which is this engine's standing shape rather than a defect), so I grade the calls on their queries: statpack greps, two corpus queries with `--decided-before 2026-09-16`, one web search for the caption plus "certiorari", one `curl` to the CourtListener search API, and two CourtListener MCP searches for *Trevino v. Hobbs*. All predate the resolution by nineteen days, so none could return this petition's disposition. The reasoning cites nothing after the snapshot. No `data/qp-topics/` read. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. Because the engine captured no results and the candidate's `flags.json` is not staged, this assessment rests on query shapes and dates rather than on returned content; for a forward cell nineteen days before the order list that is sufficient.

## Big case

My own read, formed before reading the candidate's: 0.35. The candidate's 0.70 reads the case as a high-profile VRA dispute; I think that overstates a petition whose own question was mootness and whose disposition was a one-line GVR. I record no agreement number.

## Not scored here

`claim_scores` is the harness's. The forecast document was read for context only. No `semantic_grades` (cert cell; no `semantic_claims`). No `vote_accuracy` (cert stage).
