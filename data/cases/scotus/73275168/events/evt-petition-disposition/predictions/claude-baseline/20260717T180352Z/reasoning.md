# Poore v. United States, No. 25-227 — petition disposition

**Prediction: GVR (grant, vacate, remand) as the modal disposition; P(any grant, GVR included) = 0.57.**

## The legal question

Whether the limits on agency deference announced in *Kisor v. Wilkie*, 588 U.S. 558
(2019), and *Loper Bright Enterprises v. Raimondo*, 603 U.S. 369 (2024), constrain the
deference courts accord the Sentencing Commission's interpretation of the Guidelines
via commentary — i.e., whether *Stinson v. United States*, 508 U.S. 36 (1993), survives
intact. Poore's felon-in-possession Guidelines range was raised from 21–27 to 57–71
months because former Application Note 1 to § 4B1.2 swept "aiding and abetting,
conspiring, and attempting" into "crime of violence," a term the Seventh Circuit
conceded the guideline text "unambiguously excluded" for inchoate offenses. The panel
nonetheless affirmed under circuit precedent (*United States v. White*) treating
*Stinson* as binding until this Court says otherwise, while acknowledging an
"entrenched circuit split" — six circuits apply *Kisor*'s genuine-ambiguity limit to
commentary, six do not, four of them en banc.

## What the docket says

The snapshot (2026-07-17) shows an unusually salient paid petition: counsel of record
Neal Katyal; an NCLA amicus at the petition stage; the Court called for a response
after the government waived (CFR, Sep 18, 2025); and after briefing completed, the
petition was distributed for the Jan 9, 2026 conference and then relisted roughly
**nine times** through the Apr 17, 2026 conference — after which the docket goes
silent for three months with no further distribution and no disposition.

## The decisive signal: the case is a hold for Beaird

The relists-then-silence pattern is explained by public companion-case events
(legitimate forward-mode signal; noted in flags.json): on **April 20, 2026** — the
Monday after Poore's last conference — the Court granted certiorari in **Beaird v.
United States, No. 25-5343**, limited to whether *Stinson* "still correctly states the
rule for the deference that courts must give the commentary to the Sentencing
Guidelines" (per SCOTUSblog's Relist Watch, Beaird was itself a five-time relist
riding tandem with nine-time-relisted Poore, and Poore "presumably awaits life as a
hold"). The Court has since appointed an amicus to defend *Stinson*, because the
Solicitor General *agrees* (and said so in the Poore BIO) that *Kisor* supplies the
standard for Guidelines commentary. Beaird will be argued in OT2026 with a decision
expected by June/July 2027; Poore's disposition should follow within weeks of that
decision.

## Why the Court passed over Poore as the vehicle

The government's BIO raised three serious vehicle problems, which likely explain the
choice of Beaird over this higher-profile petition:

1. **Mootness.** Poore finished his prison term on Nov 7, 2025 (BOP records cited in
   the BIO); only a three-year supervised-release term continues. The government
   argues redress through discretionary supervised-release reduction is too
   speculative under *Spencer v. Kemna*. Circuit law cuts the other way in the Seventh
   Circuit (*Pope v. Perdue* treats the possibility of reduced supervision as saving
   such challenges), so this is contestable rather than dispositive — but it is a real
   obstacle.
2. **Antecedent incorporation ground.** The enhancement actually ran through
   § 2K2.1's commentary, which petitioner concedes properly interprets the genuinely
   ambiguous, undefined term "crime of violence" in § 2K2.1 — and that commentary
   *expressly incorporates* Application Note 1. On this view Poore loses even if
   *Kisor* applies.
3. **Alternative elements-clause ground.** Wisconsin's party-to-a-crime liability
   requires the substantive offense (substantial battery) to be consummated, so the
   conviction arguably satisfies § 4B1.2(a)(1)'s force clause directly (cf.
   *Delligatti*), independent of the commentary.

## Probability decomposition

- **P(the petition is on hold for Beaird, disposition after Beaird): ≈ 0.95.** The
  timing (last distribution Apr 17; Beaird granted Apr 20; no action since), identical
  QP, and Relist Watch's read all point one way. The residual covers a
  dissent-from-denial in preparation, which would resolve as a denial.
- **P(Beaird undermines the Seventh Circuit's reflexive-deference rule): ≈ 0.85.**
  The QP as granted is framed as reconsidering *Stinson*; the government has abandoned
  the pure-*Stinson* position (an appointed amicus defends it, and such amici rarely
  prevail); and the Court's trajectory (*Kisor*, *Loper Bright*) runs strongly against
  reflexive deference. Even the "minimum win" — *Kisor* governs commentary — abrogates
  *White*, the precedent the panel below relied on.
- **P(GVR rather than denial | that holding): ≈ 0.7.** Held cases presenting the
  question decided in the merits case are routinely GVR'd in bulk under the lenient
  "reasonable probability of reconsideration" standard, and the panel decision rested
  squarely on *Stinson*/*White*. The discount reflects the government's mootness and
  alternative-grounds arguments, which it will press in a supplemental brief opposing
  GVR, plus the chance Poore's supervised release is terminated (or the record
  otherwise changes) before mid-2027.

Combining: 0.95 × (0.85 × 0.7 + 0.15 × ~0.03) + 0.05 × ~0.05 ≈ **0.57**. A plenary
grant of Poore itself is now vanishingly unlikely (Beaird occupies the question), so
essentially all grant probability is GVR probability — hence `predicted_disposition:
gvr` with `granted = 1`.

## Base-rate anchors (committed statpack)

- Modern discretionary-cert petitions: grant is rare overall (~2.5% in Term 2025;
  ~5.4% for paid petitions).
- Relist signal: 3+ relists → granted 21.8% / denied 76.5% historically. Nine relists
  sits in the extreme tail of that bucket; the salience-band table the prompt
  references is not present in the committed statpack, so I anchored on the relist
  bucket and adjusted upward on the case-specific hold-for-companion evidence, which
  dominates generic relist priors here.
- CA7-originating petitions grant below average (2.0%), a mild negative signal
  swamped by the docket-specific evidence.

## What would change this

If Beaird settles the methodological question but in a way that leaves
commentary-based enhancements largely intact (a mixed or amicus-side win), or if the
Court accepts the SG's mootness/alternate-grounds objections at the hold-cleanup
stage, Poore is denied — that path carries most of the remaining 43%. Outright
dismissal or withdrawal is negligible.
