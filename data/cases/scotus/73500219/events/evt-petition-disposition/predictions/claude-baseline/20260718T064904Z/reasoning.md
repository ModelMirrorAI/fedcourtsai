# Maund v. United States, No. 25-1318 — cert disposition prediction

**Prediction: deny. P(grant, GVR included) = 0.06.**

## The case

Erik Maund was convicted in the Middle District of Tennessee of conspiracy to
commit murder-for-hire (the 2020 Nashville killings of Holly Williams and
William Lanway). Two months after the verdict, court staff discovered that the
exhibit binders sent to the jury room contained nine unadmitted exhibits —
including "Carey Exhibits 3 and 4," material the district court had ruled
conditionally admissible only if Maund could introduce powerful rebuttal
evidence (which never came in, because the exhibits were never admitted). After
a Remmer hearing, the district court found the jury considered the extraneous
material and granted Maund a new trial as "structural error." On the
government's appeal, the Sixth Circuit reversed (167 F.4th 941 (6th Cir. 2026)),
holding the error harmless because the verdict "would not have been different"
given the "considerable" evidence against Maund.

## The question presented

Whether a defendant whose jury considered detrimental extra-record information
is entitled to a new trial upon showing the information influenced the jury's
deliberations to his detriment (the petitioner's reading of Mattox, Remmer I/II,
Smith v. Phillips, and Olano), or whether a court may also require
outcome-determinative prejudice — i.e., excuse the violation where the admitted
evidence is overwhelming. The petition alleges a 1st/2nd/9th (deliberations-
influence) versus 3rd/6th/10th (outcome-determinative) circuit split, with other
courts applying unstructured factor lists.

## Why deny is the likely disposition

1. **Base rates.** The committed statpack's modern discretionary-cert anchor
   puts the overall grant rate at ~2.5–3.3% per recent Term; the Term-2025
   *paid* class runs ~5.4%, and CA6-originating petitions grant at ~3.5%. The
   petition has **no relist yet** (a single distribution, for the 9/28/2026
   long conference) and no CVSG — and relists are the dominant pre-grant
   signal (relist-0 petitions grant at ~0.8%; recent grants in the corpus
   carried 3–22 distributions). The relist signal is simply not observable yet
   at this snapshot, so I anchor on the paid-class rate rather than the
   relist-0 rate, but nothing case-specific yet marks this petition as being
   on the grant track.
2. **The government waived its response** (June 8, 2026), and no call for a
   response appears on the docket as of the snapshot. The Court essentially
   never grants without a response on file, so the grant path requires a CFR
   at or after the long conference, then a BIO, redistribution, and relists —
   a conjunction of steps each short of certain. The SG's willingness to waive
   against experienced Supreme Court counsel signals the government reads the
   petition as splitless or fact-bound.
3. **Revealed preference in this doctrinal area.** The Remmer
   prejudice-standard split is decades old — the petition itself dates the
   confusion to Olano (1993) — and the Court has repeatedly declined to
   resolve it. A CourtListener search for post-2015 SCOTUS engagement with
   Remmer/extraneous-influence law surfaced only Dietz v. Bouldin (2016),
   which is adjacent (civil jury recall), not on point. Nearby modern cases
   (Warger v. Shauers, Peña-Rodriguez v. Colorado) address Rule 606(b), not
   the Remmer prejudice standard. Harmless-error/prejudice-standard splits in
   error-review posture are a category the Court characteristically lets
   percolate.
4. **Vehicle wrinkles the petition does not confront.** The new-trial grant
   preceded sentencing, so the Sixth Circuit's reversal returns the case for
   sentencing — making this petition effectively interlocutory; the claim can
   be renewed on direct review from a final judgment, which is a standard
   reason to deny now. And the QP is fact-saturated ("information presented
   with the court's apparent imprimatur, without ... any opportunity for a
   curative instruction"), inviting the response that the split is really
   about verbal formulations applied to disparate facts.

## What cuts the other way

The petition is genuinely strong on paper: paid, well-crafted, filed by capable
counsel (Barnes & Thornburg); the split it alleges is real and documented in
the case law; the vehicle claims (undisputed facts, dispositive question,
government appeal, preservation) are mostly fair; the facts are egregious
(unadmitted exhibits with the court's apparent imprimatur, discovered
post-verdict, with a district-court finding that the jury considered them);
and co-defendants' companion petitions (Nos. 25-7403, 25-7477, noted "Vide" on
the docket) present the same issue together. These features put it above the
run of paid petitions and support a probability above the ~2.5% Term-wide
anchor — they are why I land at 6% rather than 2–3% — but they do not overcome
the waiver-plus-no-CFR posture and the Court's long history of denying this
precise split.

## Probability arithmetic

Roughly: P(response requested out of the long conference) ≈ 0.2–0.3 for a
petition of this quality; conditional on CFR → BIO → relists, P(grant) ≈
0.15–0.25 given the age of the split and the vehicle wrinkles. That compounds
to ~4–7%; direct grant without a response is ~0. A GVR is implausible (no
intervening decision on point). **P(grant) = 0.06; predicted disposition:
denied.**

## Inputs used

- Snapshot `data/cases/scotus/73500219/record/snapshots/2026-07-18.json`
  (docket 25-1318, Term 2025, paid; waiver June 8, 2026; distributed June 17,
  2026 for the 9/28/2026 conference; related Nos. 25-7403, 25-7477).
- Provisioned `questions-presented.txt` and `petition.txt` (120 pp., truncated)
  — the QP, the Remmer-error narrative, the split taxonomy, and the vehicle
  argument summarized above. No brief in opposition exists (response waived).
- Committed `metrics/statpack.md` / `statpack.json` base rates and the corpus
  priors and CourtListener lookups logged in `retrieval.md`.
