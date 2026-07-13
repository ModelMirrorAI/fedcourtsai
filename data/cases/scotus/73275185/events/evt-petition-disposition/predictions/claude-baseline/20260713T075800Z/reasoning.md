# Allen v. Caster, No. 25-243 — petition disposition (evt-petition-disposition)

## Contamination disclosure (read first)

The provisioned snapshot (`record/snapshots/2026-07-13.json`) **contains this
event's outcome**: the docket's May 11, 2026 entries record the petition's
disposition and the ensuing judgment. The cell is nonetheless marked
`mode: forward` and the event `resolved: false`. I also recognize this case
independently — it is the companion to *Allen v. Milligan*, 599 U.S. 1 (2023),
and part of a widely covered redistricting saga. Per the prompt contract I have
(a) flagged both problems in `flags.json` so the evaluation can discount this
cell, and (b) reasoned below **only from the pre-decision record** — the docket
through May 11, 2026 *excluding* the disposition entries, the questions
presented as restated in the brief in opposition, the BIO itself, and general
legal context. The probability stated is what I would assign standing at the
last pre-decision moment on the record; it is not a hindsight readout, though a
contaminated cell can never fully prove that.

## The legal question

Alabama's Secretary of State and co-petitioners seek **certiorari before
judgment** (Sup. Ct. R. 11) from the Eleventh Circuit (Nos. 25-11915, 25-12802)
after a three-judge district court in the Northern District of Alabama held
that Alabama's 2023 congressional plan violates § 2 of the Voting Rights Act
and found intentional discrimination. The questions presented (as restated in
the BIO): (1) whether the 2023 plan violates § 2, and (2) whether § 2 as
applied by the district court is constitutional. This is the same litigation
the Court already took once — *Allen v. Milligan* affirmed the preliminary
Gingles ruling in 2023 — now returning after final judgment.

## The governing standard

Certiorari before judgment requires that the case be "of such imperative
public importance as to justify deviation from normal appellate practice and
to require immediate determination in this Court" (Rule 11). Standing alone,
CBJ petitions are rarely granted, and the modern-cert base rate in the corpus
statpack is ~4.9% grants (denied 92.6%) for the 2025 Term slice. A naive
base-rate prediction is therefore *denied*.

## Why this case departs sharply from the base rate

1. **The hold-for-a-lead-case pattern.** The petition was fully briefed by
   November 4, 2025 and distributed for the November 21, 2025 conference —
   then sat without action for nearly six months. A petition that is neither
   denied nor dismissed after distribution is almost always being **held** for
   a pending merits case. The record identifies the lead case explicitly: the
   eventual docket text and Alabama's May 9, 2026 letter reference *Louisiana
   v. Callais*, 608 U.S. ___ (2026), the Louisiana § 2/racial-gerrymandering
   case presenting the same constitutional question as QP 2. Held cases are
   overwhelmingly resolved by **GVR** (grant, vacate, remand for
   reconsideration in light of the new decision) once the lead case comes
   down — that is the single most predictable disposition pattern at the
   Court.

2. **Callais came down, and the record shows it changed the landscape.** By
   early May 2026 the pre-decision record shows: *Callais* decided (cited as
   608 U.S. ___ (2026)); Alabama immediately enacted a new congressional map
   (Act 2026-612, attached to its May 9 letter); the three-judge court denied
   Alabama a stay of its judgment (order attached to the same letter); and
   Alabama filed a motion to expedite (Apr. 30) plus an emergency stay
   application (25A1229, May 8), on which Justice Thomas called for a response
   within three days and the petition was redistributed for the May 14
   conference. Alabama's behavior — new map, emergency posture, urgency
   keyed to the 2026 election calendar — is only rational if *Callais*
   materially unsettled the § 2 framework the district court applied. A
   judgment resting on pre-*Callais* § 2 law is a textbook GVR candidate.

3. **The election clock forces action.** With the 2026 congressional cycle
   imminent and an emergency application pending, "deny and let the Eleventh
   Circuit sort it out" costs the Court nothing doctrinally but leaves a
   live emergency docket item; a GVR resolves both at once. The expedite
   motion plus same-conference distribution signal imminent, decisive action.

4. **Corpus context.** The statpack's modern-cert grant rate (~4.9%) is the
   right anchor for a cold petition, but this petition is not cold: it is a
   relisted/held, paid, state-party CBJ petition in a case the Court has
   already plenary-reviewed once, with the lead case decided. The corpus
   priors I pulled (2020s granted petitions) show the multi-distribution →
   grant pattern, though the corpus lacks relist/CVSG cuts to quantify it.

## Weighing the BIO

The Caster respondents' BIO (47 pp., provisioned) is a merits-heavy defense of
the district court's Gingles findings (an additional reasonably configured
majority-Black district in southern Alabama, racially polarized voting,
totality of circumstances, intentional-discrimination findings) and of § 2's
constitutionality. It argues *Allen v. Milligan* controls and stare decisis
forecloses reworking Gingles. That was a strong denial argument in October
2025; it is much weaker once *Callais* has intervened, because the BIO's
anchor precedent is precisely what *Callais* revisited. Nothing in the BIO
undercuts the GVR path — a GVR takes no position on the merits QPs.

## Probability and disposition

- **GVR / grant of the petition (records as `granted`): ~0.80.** The dominant
  outcome for a held case whose lead case has come down, amplified by the
  emergency posture and election timing.
- **Denied: ~0.15.** The live alternative: Alabama has already enacted a
  post-*Callais* map, so the Court could deny and let the Eleventh Circuit
  apply *Callais* in the first instance, handling the stay application
  separately.
- **Dismissed/other: ~0.05.** Mootness-driven dismissal after Act 2026-612,
  or a summary merits disposition.

**Prediction: granted (P(granted) = 0.80), confidence 0.6.** Confidence is
moderated because the cell is contaminated (see disclosure) and because the
grant/deny choice for a held case is genuinely closer than the GVR reflex
suggests when the state has already re-legislated.

## Predicted votes

Derived from the *Callais* alignment visible in the pre-decision record (a
§ 2 decision favorable enough to Alabama to prompt an immediate new map), not
from the disposition entries: the Justices most protective of the *Milligan*
status quo — Sotomayor, Kagan, Jackson — would dissent from vacating a § 2
judgment they believe *Milligan* controls, with the remaining six supporting
the GVR. Recorded as granted 6–3 in `prediction.json`.

## Inputs used

- Snapshot `record/snapshots/2026-07-13.json` (docket entries **before** the
  May 11, 2026 disposition only).
- `record/documents/brief-in-opposition.txt` (47 pp., full text; QPs restated
  and argument structure).
- No petition or QP document was provisioned (`documents.json` lists only the
  BIO); the QPs are taken from the BIO's restatement.
- `metrics/statpack.md` base rates; two `fedcourts query` corpus lookups
  (see `retrieval.md`).
