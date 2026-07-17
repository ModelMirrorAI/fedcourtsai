# AstraZeneca Pharmaceuticals LP v. Mosaic Health, Inc. (No. 25-1070) — cert disposition

**Prediction: P(grant, GVR included) = 0.35; likeliest single disposition remains denied.**

## The case

Paid petition (Term 2025, docketed March 11, 2026) by AstraZeneca, Eli Lilly, Novo
Nordisk, and Sanofi from the Second Circuit's amended decision in *Mosaic Health v.
Sanofi-Aventis*, 156 F.4th 68 (2d Cir. 2025), which reversed a Rule 12 dismissal of a
putative antitrust class action by 340B "covered entities" challenging the
manufacturers' contract-pharmacy restrictions. Two questions presented:

1. **Illinois Brick scope** — whether indirect purchasers/sellers can evade the
   direct-purchaser rule by pleading "lost profits" from purchases never made rather
   than overcharges on purchases made.
2. **Twombly plus factors** — whether an "opportunity to conspire" via joint lobbying
   and trade-association (PhRMA) membership plausibly suggests conspiracy.

## Grant-side signals (unusually strong)

- **Call for a response.** Respondents waived; the petition was distributed for the
  May 14, 2026 conference, and on April 30 the Court **requested a response** — the
  classic signal that at least one chambers is seriously interested. Two extensions
  later, the BIO is due July 22, 2026 (still unfiled at the July 16 snapshot).
- **Acknowledged, recent circuit split on QP1.** The Second Circuit's rule squarely
  conflicts with the Third (*Howard Hess*, 424 F.3d 363) and the Sixth (*Academy of
  Allergy*, 155 F.4th 795 (2025)). In denying rehearing (164 F.4th 529 (2026)), Sixth
  Circuit judges wrote dueling separate opinions that quote the decision below and
  expressly say the issue "may be appropriate for Supreme Court review" — a
  near-invitation. No competing petition from that case is docketed yet, making this
  the lead vehicle.
- **QP2 split** is broader if softer: 2d + 1st Circuits treat trade-association
  opportunity as a plus factor; 3d, 6th, 9th, 11th, and D.C. reject it.
- **Elite cert-stage lineup.** Noel Francisco, Allon Kedem (counsel of record), John
  O'Quinn, Ashley Parrish; cert-stage amici from the U.S. Chamber of Commerce + NAM
  and the Electric Power Supply Association.
- **Court's appetite.** The Court took *Apple v. Pepper* (2019) on an analogous
  Illinois Brick boundary question; the "bright-line rule" language there is central
  to the petition. The 340B contract-pharmacy fight (~$81B/yr) is a live, recurring
  federal-program controversy the Court has seen before (*Astra USA*, *Sanofi v. HHS*,
  *Novartis v. Johnson*).

## Deny-side drags

- **Base rate.** Modern paid petitions grant at ~5.4% (Term 2025 paid class,
  corpus estimate); even most CFR'd petitions are ultimately denied.
- **Interlocutory posture.** The Second Circuit reversed a dismissal and remanded;
  the Court often lets such cases go back down (though *Twombly* itself was granted
  in exactly this posture, and both QPs are pure legal questions decided below).
- **BIO unseen.** Respondents have not yet filed; expect vehicle arguments (state-law
  claims proceed regardless of QP1; the panel relied on plus factors beyond bare
  "opportunity," making QP2 look fact-bound; the disclaimer of overcharge damages may
  be framed as narrowing the split).
- **Percolation/CVSG.** The QP1 split is young (2025–2026). A CVSG is plausible given
  the federal-program overlay — which would push disposition deep into OT2026 and is
  itself only a ~27% grant bucket in the corpus.

## Calibration

Anchors from the committed statpack (live/historical slice, denial-reweighted):
overall modern cert grant ~3%; Term 2025 paid class ~5.4%; CVSG bucket 27.1%;
2-relist bucket 33.6%; CA2-originating petitions 5.4%. This statpack build carries no
salience-band table, so I banded manually: a paid petition with a CFR, an
acknowledged split flagged by circuit judges, top-tier counsel, and business amici
sits in the top salience tier, comparable to the multiply-relisted/CVSG buckets
(~25–35%). The unfiled BIO and interlocutory posture cap how far above those buckets
I will go; the two independent cert-worthy QPs and the express Sixth Circuit
invitation push toward the top of the band.

**Probability 0.35.** Since a denial is still the single likeliest outcome,
`granted = 0` and `predicted_disposition = denied`. A GVR is implausible here (no
intervening decision); if granted, it would be a plenary grant, possibly limited to
QP1. Timing: with the BIO due July 22, 2026, distribution likely lands at the
late-September 2026 long conference, with relists or a CVSG the paths to a grant.

Confidence 0.5 — the probability estimate is well-anchored, but the BIO and the
Court's conference behavior (relists, CVSG) are the decisive unseen variables.

## Inputs used

Provisioned snapshot `record/snapshots/2026-07-16.json` (docket through June 25,
2026), `questions-presented.txt`, and the full `petition.txt` (39 pp., complete);
committed `metrics/statpack.md`/`.json` for base rates; corpus `fedcourts query` for
priors (no close antitrust matches surfaced); two CourtListener MCP searches (see
`retrieval.md`). Mode: `forward` — no outcome exists; nothing outcome-revealing was
encountered.
