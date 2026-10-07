# Evaluation of codex-baseline — scotus/73281388, evt-petition-disposition

**Outcome.** Cert stage. The petition (No. 25-1105, Thompson v. Wilson) was DENIED on
2026-10-05 after the 2026-09-28 long conference, with no noted dissent
(`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`,
`noted_dissent_from_denial: false`, `distribution_count: 2`).

**Scores.** `predicted_disposition: denied` matches, so `correct = 1`. P(grant) = 0.22,
Brier = (0.22 − 0)² = **0.0484**. Segment base rate: the prediction froze
`band: elevated` under `salience_version: sal-v4`, and the committed
`metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" carries the
same version in its heading, so the basis is `risk_set`. Pooling the bracketed
`reached` figure resolved-weighted over every rendered Term strictly before OT2025 —
OT2017 through OT2024, 484 / 2,810 — gives **0.1722** (the candidate computed the
identical pooled figure from the unrounded JSON). The caption renders 10 of 10 Terms,
so no window divergence needs flagging. Brier skill = 1 − 0.0484 / 0.1722² =
**−0.632**: the forecast named the right label but sat enough above the band rate
that the naive baseline scores better on this denial.

**What the prediction got right and wrong.** The disposition and its shape: a silent
denial after the long conference, no further distribution, no CVSG. The direction of
the adjustment from the anchor was the only thing the outcome cut against: it moved
modestly up (17% to 22%) on the response request, the amicus support and the
recurrence of the question, while its own analysis of the vehicle (contested
preservation, the closely-regulated concession, a claimed rather than established
conflict, two distributions that reflect scheduling rather than two conference looks)
pointed the other way.

**Reasoning quality: 0.80.** A rigorous, well-structured rationale. It selects the
correct yardstick, computes it from the pack's unrounded fields, and explicitly
refuses to multiply the terminal relist and CVSG cuts into transition hazards, which is
the right reading of the statpack. It engages both sides of the record on each of the
decisive points: the split (a claimed conflict is not a holding conflict, and the BIO's
distinctions are "a substantial obstacle"), preservation (reduced but not eliminated by
the reply, read at the cited pages), the closely-regulated concession, and the
posture. Unlike the other candidates it read the First Circuit opinion itself and
located footnote 18, and it correctly reads Richards v. Newsom as a decision that
upheld a comparable regime and so is not a clean opposite result. Its provenance
discipline (which vintage was used, what was and was not independently retrieved) is
exemplary. The deduction is for the join between analysis and number: having found
every vehicle problem the Court would have cared about, it still moved above the
anchor on the strength of signals it had itself discounted, without saying why the
net came out positive; and the two-distribution point is noted but not followed
through to the conclusion that the `elevated` band overstates the Court's revealed
interest here. The calibration argument is weaker than the legal analysis that
precedes it.

**Leakage.** Forward cell (`context.mode: forward`, no cutoff), created 2026-09-17
against a petition that resolved 2026-10-05, so the case was genuinely open and the
`not_applicable` default applies. The log (`result_capture_coverage` 0.97; one
web-search row, the reply URL, unobserved and graded on its query, which is this
docket's own pre-resolution filing) shows local reads, statpack.md and statpack.json,
fetches of the July 20 reply, the September 9 supplemental brief and the November 18,
2025 First Circuit opinion from the snapshot's official links, and one CourtListener
citation search for 159 F.4th 91 that returned nothing. No call names this petition's
disposition, nothing is dated on or after the resolution, and there is no
`data/qp-topics/` read. The retrieval note's own disclosure that no outcome material
was sought or encountered agrees with the log. `retrieved_outcome_material: false`,
`influenced_prediction: not_applicable`, `leakage_suspected: false`.

**Big case.** My own read, formed before consulting the candidate's score, is 0.40:
the doctrinal question could matter across closely regulated industries, but the
vehicle is a single state fisheries rule with a conceded closely-regulated status and
a contested preservation record, and the Court let it go silently at its first real
conference.

**Not scored here.** The claims block is scored in code by the harness, and the
forecast document was read for context only. This is a cert cell, so no
`vote_accuracy`, no `judgment_correct`, and no `semantic_grades` are written;
`record/opinion/` is absent, which is the ordinary state of a denied petition.
