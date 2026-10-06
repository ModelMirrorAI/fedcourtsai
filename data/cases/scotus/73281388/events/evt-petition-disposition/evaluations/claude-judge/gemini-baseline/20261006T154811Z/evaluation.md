# Evaluation of gemini-baseline — scotus/73281388, evt-petition-disposition

**Outcome.** Cert stage. The petition (No. 25-1105, Thompson v. Wilson) was DENIED on
2026-10-05 after the 2026-09-28 long conference, with no noted dissent
(`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`,
`noted_dissent_from_denial: false`, `distribution_count: 2`).

**Scores.** `predicted_disposition: granted` against `denied`, so `correct = 0`.
P(grant) = 0.55, Brier = (0.55 − 0)² = **0.3025**. Segment base rate: the prediction
froze `band: elevated` under `salience_version: sal-v4`, and the committed
`metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" carries the
same version in its heading, so the basis is `risk_set`. Pooling the bracketed
`reached` figure resolved-weighted over every rendered Term strictly before OT2025 —
OT2017 through OT2024, 484 / 2,810 — gives **0.1722**. The caption renders 10 of 10
Terms, so no window divergence needs flagging. Brier skill = 1 − 0.3025 / 0.1722² =
**−9.20**: far worse than simply parroting the band rate.

**What the prediction got wrong.** The headline call. It moved from a correctly
identified ~17% anchor to 55%, a more-than-threefold lift, on signals that are mostly
what put the petition in the `elevated` band in the first place (the response
request) or that are weakly diagnostic of a grant on their own (repeat-player counsel,
four ideologically aligned amicus briefs). The Court denied without a single Justice
noting dissent.

**Reasoning quality: 0.25.** The rationale is a single short paragraph pair and reads as
an impression rather than an analysis. Its strengths: it names the right anchor
(reached elevated, about 17%) and it recognises that the distribution count of 2 is
partly an artifact of the response request rather than a true relist. Its weaknesses
are the ones that mattered to the outcome. It accepts the petition's "clear circuit
split against the Sixth and Ninth Circuits" at face value even though the log shows it
read the brief in opposition, which spends its central pages arguing that the cited
cases (a pre-Burger day-care inspection case, a tire-chalking case that expressly
declined to reach the point, and step-one "was there a search" holdings) do not
conflict with the First Circuit's rule; the rationale never mentions, let alone
answers, that argument. It never engages the BIO's preservation objection (the
trespass-test framing was not argued in those terms below), the petitioner's
concession that lobstering is a closely regulated industry, or the state-respondent
posture, all of which were in the provisioned documents. The upward move rests on a
characterisation of the Court's "strong appetite" for the issue rather than on any
feature of this vehicle, and no attempt is made to say why those features should
move the number past the point where the Court grants only one in six comparable
petitions. The document also reads the briefs only through keyword greps for "split"
and "conflict with", which is consistent with the gaps above. A sound rationale can
still reach a wrong number, but this one reached its number by skipping the parts of
the record that cut against it, and that is what the score reflects. Read for context
only, the forecast document shows the same pattern; it is not scored.

**Leakage.** Forward cell (`context.mode: forward`, no cutoff), created 2026-09-17
against a petition that resolved 2026-10-05, so the case was genuinely open and the
`not_applicable` default applies. The log's `result_capture_coverage` is 0.0 (every
marker-carrying call unobserved), which is an engine's standing shape and not a
defect, so each call is graded on its query: local reads of the prompt, record,
snapshot, documents and the whole statpack; two `fedcourts query` invocations with
free-text positional arguments that could not have run as written; and one
CourtListener search for the caption "Johnson v. Wilson" (a mis-stated caption for
this case) with no date filter. None of those queries could have returned this
petition's disposition, which did not exist until 2026-10-05, and nothing is dated on
or after the resolution; there is no `data/qp-topics/` read. The reasoning treats
the petition as pending. `retrieved_outcome_material: false`, `influenced_prediction:
not_applicable`, `leakage_suspected: false`. The unobserved results are not credited
as empty; the grade rests on the queries and on the timing.

**Big case.** My own read, formed before consulting the candidate's score, is 0.40:
the doctrinal question could matter across closely regulated industries, but the
vehicle is a single state fisheries rule with a conceded closely-regulated status and
a contested preservation record, and the Court let it go silently at its first real
conference.

**Not scored here.** The claims block is scored in code by the harness, and the
forecast document was read for context only. This is a cert cell, so no
`vote_accuracy`, no `judgment_correct`, and no `semantic_grades` are written;
`record/opinion/` is absent, which is the ordinary state of a denied petition.
