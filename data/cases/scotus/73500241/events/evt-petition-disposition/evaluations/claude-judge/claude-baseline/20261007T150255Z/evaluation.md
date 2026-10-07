# Evaluation — claude-baseline, scotus/73500241, evt-petition-disposition

**Outcome.** Cert stage (`event.yaml` stage `cert`, moment `distribution`). The
petition was denied on 2026-10-05 after a single distribution for the 2026-09-28
conference, no call for a response, no separate writing (`outcome.json`:
`actual_disposition` denied, `actual_granted` 0, `noted_dissent_from_denial` false).

**Scores.** `predicted_disposition` denied matches, so `correct` 1. Probability
0.01 against an outcome of 0 gives a Brier of 0.0001. The band baseline is the
`baseline` band's bracketed `reached` figure pooled resolved-weighted over OT2017
through OT2024, the Terms strictly before this case's Term 2025, from the sal-v4
table in `metrics/statpack.md`: about 593 grants over 11,580, or 0.0512
(`base_rate_basis` `risk_set`, since the prediction froze a band and a
`salience_version` that matches the table heading; the in-code pooler returns
0.051209 on the same context, confirming the figure). The table renders ten of ten
Terms, so the rendered window is the full one and there is no divergence to flag.
Brier skill is 1 - 0.0001 / 0.0512^2 = 0.9619.

**Leakage.** Forward mode, graded `not_applicable`, and I checked rather than
rubber-stamped it: the prediction was created 2026-09-17 against a snapshot whose
last entry is the 2026-06-24 distribution, eighteen days before the denial. The log
(25 calls, fully captured) shows six CourtListener searches, all for the opinion
below or the split's lead cases and all empty, and one corpus query for recent
grants that returned unrelated rows. Nothing reaches this petition's docket or
disposition; nothing reads `data/qp-topics/`. `retrieved_outcome_material` false.

**Reasoning quality: 0.85.** The strongest analysis in the cell on the question
that mattered. The anchor is computed correctly from the right table and the
right basis, and the write-up says why the terminal relist-0 figure would
understate a petition that could still climb. The downward adjustments are the
ones that actually drive a denial here: the waiver with no call for a response
over three months is the dominant mechanical signal, and the candidate puts it
first; the mismatch between the petition's Fourth Amendment retention split and
its own Fifth Amendment question is argued from the petition text with the
circuits named; the vehicle defects (intermediate state court, damages-only
posture with immunity and section 1983 "person" problems never briefed, a
single-sentence dismissal below) are the ones a clerk's memo would list; and the
candidate caught the petition misattributing Federal Circuit illegal-exaction
cases to this Court. The uncertainty section is honest about not having read the
Kansas opinion and about what would change if it had. The 0.01 floor is
explained rather than asserted.

What holds it below the top: the candidate could not read the opinion below and
relied on the petition's adversarial characterization, which codex-baseline showed
was obtainable from the filed appendix; the claim that `event.yaml` carried no
`stage` or `moment` field is wrong against the committed file, a harmless slip but a
slip; and the GVR-share arithmetic for the summary-route conditional (a third
among baseline-band grants) is a terminal-band ratio pressed into a conditional
it does not quite fit. None of this touches the headline number. The forecast
document and the claims block were read for context only and are not scored
here.

**Big case.** My own read, formed before looking at the candidate's score, is
0.06: a family's damages suit over a tax levy returned in 2023, waived response,
denied silently.
