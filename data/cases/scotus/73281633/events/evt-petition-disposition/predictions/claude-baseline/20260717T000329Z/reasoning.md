# Council for Responsible Nutrition v. James, No. 25-1145 — cert prediction

**Prediction: deny. P(grant, GVR included) ≈ 0.06.**

## The case

CRN, the dietary-supplement industry's trade association, challenges N.Y. Gen.
Bus. Law § 391-oo, which bans selling to minors any dietary supplement that is
"labeled, marketed, or otherwise represented" for weight loss or muscle
building. The district court (S.D.N.Y., Carter, J.) denied a preliminary
injunction; a unanimous Second Circuit panel (Chin, Pérez, Nathan) affirmed on
November 13, 2025 (159 F.4th 155), holding the law likely survives *Central
Hudson* intermediate scrutiny even assuming it is a content-based regulation of
commercial speech. Rehearing en banc was denied December 30, 2025. The
questions presented attack the panel's third-prong holding (that "simple common
sense" plus two general studies can show direct advancement, assertedly against
the Fourth, Fifth, Sixth, Ninth, and Tenth Circuits) and its fourth-prong
deference to the legislature's choice of a marketing-based trigger over the
vetoed ingredient-based alternative.

## Signals for a grant

- **Cert-stage amicus support.** Four amicus briefs at the petition stage
  (Pacific Legal Foundation, National Retail Federation, Manhattan Institute,
  Taxpayers Protection Alliance) — a well-above-median salience signal that
  historically correlates with a several-fold higher grant rate.
- **A recurrent doctrinal itch.** Members of the Court have repeatedly
  questioned *Central Hudson*'s rigor (Thomas in *Matal*, *Lorillard*, *44
  Liquormart*; the *Borgner* dissent from denial flagged exactly the
  evidentiary-sufficiency question QP1 raises), and *Greater New Orleans*
  expressly reserved the lack-of-evidence question the petition tees up.
- **Paid petition, capable counsel, state respondent.** The NY Solicitor
  General took two extensions and filed a substantive 42-page BIO rather than
  waiving — the state took the petition seriously.
- **Novel regulatory technique.** A sales ban triggered by a product's
  marketing is a new form of speech-adjacent regulation; if it spreads to other
  states the issue will recur.

## Signals against a grant

- **Interlocutory posture — the dominant factor.** This is review of a
  preliminary-injunction denial in a live case; discovery is ongoing and both
  sides expect to build a fuller record on the very fact-bound prongs at issue.
  The Court overwhelmingly denies in this posture absent urgency.
- **Not outcome-determinative.** The district court alternatively denied
  relief on equitable grounds (five-month delay eroding irreparable harm; the
  public interest), which the Second Circuit called an independent basis for
  affirmance. The BIO leads with this vehicle defect, and it is real: a
  petitioner win on both QPs could leave the judgment intact.
- **The split is contestable.** The BIO plausibly recharacterizes the cited
  circuit conflict as differing fact-bound applications of an agreed standard —
  every circuit recites *Florida Bar*'s "studies and anecdotes … history,
  consensus, and simple common sense" formulation, and here the state did cite
  studies and anecdotes, unlike the no-evidence records in *Bailey*, *Pagan*,
  and *Pacific Frontier*. This is not a crisp rule-vs-rule conflict.
- **Waiver.** The heightened-scrutiny/Sorrell argument was not pressed below,
  narrowing the doctrinal payoff of a grant.
- **The Court has declined this invitation before.** *Borgner* (2002) presented
  the same "quality of evidence under prong three" question and was denied with
  only two noted dissents; no intervening development compels a different
  answer, and no other circuit is currently wrestling with a comparable
  supplement-marketing statute (my CourtListener sweep found no parallel
  litigation).
- **No pre-grant signals yet.** Docketed April 2, 2026; distributed July 1 for
  the September 28, 2026 long conference — first distribution, no relist, no
  CVSG. The long conference is also historically the least generous
  distribution of the year.

## Base rate and adjustment

From the committed statpack: modern discretionary-cert petitions deny ~95%;
paid petitions specifically granted ~5.4% (Term 2025) and ~6.9% (Term 2024) —
call the paid-petition anchor ~6%. Second Circuit origin is near the average
(5.4% granted among modern cert petitions). The relist-count cut is
uninformative pre-conference (relist 0 so far is just "not yet conferenced").
No salience-band table is present in the committed statpack, so I anchor on the
paid fee-class rate.

The amicus support and doctrinal salience would push a merits-posture version
of this petition well above the paid-petition anchor (to perhaps 15–20%). But
the interlocutory posture plus the independent equitable ground for affirmance
are the kind of vehicle defects that reliably sink otherwise attractive
petitions — the likeliest outcomes for this legal issue are a denial here
(possibly with a statement respecting denial) and a return trip after final
judgment. Netting these, I land essentially at the paid-petition base rate:
**P(grant) = 0.06, predict denied.** A GVR path is implausible (no intervening
decision), so the grant probability is effectively all plenary grant.

## Inputs used

Provisioned snapshot (2026-07-16), questions-presented.txt, petition.txt
(including the Second Circuit opinion reproduced in the appendix), and
brief-in-opposition.txt; the committed `metrics/statpack.md` and
`metrics/statpack.json` for base rates; one corpus `fedcourts query` (no
matching priors returned) and one CourtListener opinion search (details in
`retrieval.md`). Mode is `forward`; the petition is genuinely pending
(conference not until 2026-09-28), and nothing I retrieved revealed or could
reveal a disposition.
