# Why P(grant) = 0.01

## What I read

Provisioned inputs, in the prompt's order: `AGENTS.md`, the predict prompt and
`schemas/prediction.schema.json`; then `event.yaml` (kind `petition`, no
`stage` field, so the cert standard governs; `opened_at` 2026-05-14), the
snapshot `record/snapshots/2026-09-16.json` (the file `context.json` names),
`record/context.json` (mode `forward`, band `baseline` under `sal-v4`,
`distribution_count` 1, `cvsg_date` null, `term` 2025, `signals_observable`
true, `cutoff` null), and `record/documents/`: `documents.json` lists the
petition (40 pages, text extracted, not truncated) and the questions-presented
cut; there is **no brief in opposition** on disk, and none on the docket.

## The record

- Paid petition, No. 25-1285, docketed May 14, 2026, from the Washington Court
  of Appeals, Division II (unpublished opinion of April 22, 2025; reconsideration
  order August 5, 2025). The Washington Supreme Court denied review on January 7,
  2026. Justice Kagan granted a routine extension of time (25A1064).
- Petitioner is a private individual (Moneesha Kamani); respondents are a
  veterinarian and the veterinary company that employs him. Caption class:
  private. That matches the frozen `band: baseline`, and I use the frozen band
  as instructed rather than deriving one.
- Docket entries: extension application and grant (March 2026); petition filed
  May 8, 2026 with response due June 15, 2026; **distributed July 1, 2026 for the
  conference of September 28, 2026**. One distribution, no relist, no CVSG, no
  amicus, no BIO, and no waiver entry.
- The petition: a suit for intentional infliction of emotional distress and
  fraud after the petitioner's dog died following discharge from an emergency
  clinic. The trial court dismissed the intentional torts at summary judgment
  (certified final under Washington CR 54(b)); the Court of Appeals affirmed.
  QP 1 asks whether a private party's cease-and-desist letter threatening
  criminal libel and civil action may be "discounted as a matter of law"
  notwithstanding the First Amendment and state anti-SLAPP law; QP 2 asks
  whether a court may grant summary judgment by disregarding record evidence.
  The "Reasons for Granting" section argues the court below misapplied summary
  judgment standards (citing Tolan v. Cotton and Anderson v. Liberty Lobby) and
  imposed novel elements on the outrage tort; it asserts an "intractable split
  between state and federal courts" but identifies no conflicting holdings on a
  defined legal question.

## Anchor

The committed `metrics/statpack.md` at this checkout (HEAD `aadcafcb2`,
corpus refreshed 2026-09-16 per the live/pull commits at the tip) carries the
"Segment base rate by salience band (sal-v4)" table, which matches
`context.salience_version`. Per the prompt, a cell with a band frozen at
prediction is scored against the bracketed `reached` figure, pooled over Terms
strictly before this case's own (OT2025). Pooling the `baseline` column's
`reached` rates over OT2017–OT2024 (n = 11,580 weighted resolved) gives
**5.1%**. Cross-checks from the same pack: the paid-segment relist-count cut
puts `relist 0` petitions at granted 1.2% / gvr 0.5%; the paid-segment CVSG
cut puts `none` at granted 4.0% / gvr 2.3%; the terminal `baseline` band row
shows granted 0.8% / gvr 0.4%. The per-Term table's OT2025 grant-family rate is
2.6% across all fee classes.

## Adjustments from the anchor (all downward)

The 5.1% figure is the grant rate for the *whole* private-petitioner class,
which includes well-lawyered petitions presenting genuine splits that later
climbed to `elevated` or `high`. This petition is in the weakest stratum of
that class on every dimension the Court's cert practice weighs:

1. **No federal question the court below decided.** The First Amendment claim
   runs against private defendants (no state action) and the petition itself
   says the court of appeals did not address the cease-and-desist letter's
   speech-suppressing character, so the federal question was not passed upon.
   QP 2 concerns a state court's application of its own summary-judgment rule
   to state-law torts; Tolan v. Cotton governs federal courts under Rule 56 and
   does not bind a state court applying state procedure.
2. **No split.** The asserted "state versus federal" split is not documented
   with conflicting holdings; the petition is a catalogue of alleged factual
   errors in an unpublished opinion.
3. **Vehicle.** Unpublished state intermediate-court opinion; partial final
   judgment under CR 54(b) with negligence claims apparently still live below,
   which raises a 28 U.S.C. § 1257 finality question the petition addresses
   only in a sentence.
4. **No opposition, no waiver, no amici, no repeat Supreme Court counsel.** The
   petition was distributed unopposed; a grant without first calling for a
   response is essentially unheard of, so any grant path requires a call for a
   response and a redistribution that the record gives no reason to expect.

A GVR is excluded on its own terms (no intervening decision). Dismissal or
withdrawal is possible but rare (~1% in the paid segment) and would resolve as
a non-grant anyway.

Weighing these, I put P(any grant) at **0.01**, roughly a fifth of the class
floor and slightly below the `relist 0` cut's grant-family rate of 1.7%, which
is the population this petition most resembles.

## Claims

- `disposition` 0.01 — equals the top-level probability.
- `relist-increment` 0.10 — the docket shows one distribution. About 25% of
  paid petitions receive at least one further distribution (statpack relist
  cut: 3,503 of 13,911 weighted), but that share is driven by petitions with
  interest. For a weak unopposed petition, further distribution comes mainly
  from a reschedule off the long conference or a call for a response; I put
  the combined chance at 10%.
- `cvsg-increment` 0.003 — CVSGs occur on 1.2% of paid petitions and require a
  federal interest; none exists here.
- `summary-disposition-route` 0.55 — conditional on a grant. The petition's
  only colourable theory is a Tolan-style summary reversal, and it asks for
  one; plenary review of this case is less plausible than a summary order. The
  pack's prior-Term GVR share of the grant family runs 30–59%, and I sit
  slightly above it because a GVR is impossible here while a per curiam is the
  one grant shape that fits.
- `dissent-from-denial` 0.01 — conditional on denial. No Justice has a clean
  occasion to write on this vehicle.

## Uncertainties and where to discount me

- I could not read a BIO because none exists, and I cannot confirm whether a
  waiver was filed: the snapshot has no waiver entry and the CourtListener
  docket carries no entries at all (see `retrieval.md`). I have read the
  distribution as unopposed under Rule 15.5 either way.
- Finality under § 1257 I infer from the petition's own description of the
  CR 54(b) certification; I did not read the lower-court opinions.
- My number sits below the class floor on case-specific judgment; if the
  evaluator believes the frozen band should carry the forecast, the class
  floor (5.1%) is the figure I moved away from.
- Corpus retrieval (`fedcourts query`) returned application and high-profile
  rows unrelated to this petition's profile and did not inform the number; I
  relied on the committed statpack for base rates.
