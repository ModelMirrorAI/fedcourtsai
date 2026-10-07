# Evaluation — gemini-baseline, scotus/73500241, evt-petition-disposition

**Outcome.** Cert stage (`event.yaml` stage `cert`, moment `distribution`). The
petition was denied on 2026-10-05 after one distribution for the 2026-09-28
conference, no call for a response, no separate writing (`outcome.json`:
`actual_disposition` denied, `actual_granted` 0).

**Scores.** `predicted_disposition` denied matches, so `correct` 1. Probability
0.015 against 0 gives a Brier of 0.000225. The baseline is the `baseline` band's
bracketed `reached` figure pooled resolved-weighted over OT2017 through OT2024
from the sal-v4 table in `metrics/statpack.md`, 0.0512 on the `risk_set` basis
(the prediction froze band `baseline` under `sal-v4`, matching the table heading;
the in-code pooler returns 0.051209 on the same context). Ten of ten Terms are
rendered, so no window divergence. Brier skill is 1 - 0.000225 / 0.0512^2 = 0.9142.

**Leakage.** Forward mode, `not_applicable`, checked: prediction created
2026-09-17, denial 2026-10-05. The log carries 21 calls with
`result_capture_coverage` 0.0, every call unobserved, which is this engine's
standing shape, so each call is graded on its query. The queries are the
provisioned inputs, the statpack, and one corpus query bounded by
`--decided-before 2026-09-17`; there is no CourtListener or web call, and nothing
names this petition's disposition or `data/qp-topics/`. The reasoning reads the
waiver and the single distribution off the provisioned snapshot and nothing
later. `retrieved_outcome_material` false. The candidate's own retrieval note
says no retrieval beyond the provisioned inputs, which the log bears out, though
the one corpus query is a retrieval the note does not mention.

**Reasoning quality: 0.55.** Right answer, thin case. The one paragraph rests on
the single most predictive fact, the waiver with no call for a response, and
states the mechanism correctly: the Court almost never grants a paid petition
without first requesting a response. That alone earns a passing mark, because it
is the reason this petition was denied. But the anchor is quoted as "around a
4 to 6% reached rate" rather than pooled, so the reader cannot tell which Terms
or which basis the 0.015 was adjusted from. The question presented is
characterized in one sentence and the petition's claimed six-four circuit split
is never mentioned, so the write-up neither engages the petition's strongest
argument nor explains why it fails; the vehicle problems (intermediate state
court, damages-only posture, immunity, the Fifth-versus-Fourth Amendment framing
mismatch) that both other candidates found do not appear. The reasoning is
correct as far as it goes, and it goes about a quarter of the way. The forecast
document and the claims block were read for context only and are not scored.

**Big case.** My own read, formed before looking at the candidate's score, is
0.06.
