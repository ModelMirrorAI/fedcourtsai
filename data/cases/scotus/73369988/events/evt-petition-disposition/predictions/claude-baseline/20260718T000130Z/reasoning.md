# Honeycutt v. JPMorgan Chase Bank, N.A. (No. 25-1298) — cert disposition

**Prediction: denied. P(grant, GVR included) = 0.005.**

## The case

Patrice Honeycutt lost a second employment arbitration against JPMorgan Chase
(the first award was vacated in *Honeycutt I*, 25 Cal.App.5th 909 (2018), for
the arbitrator's disclosure failures). The Los Angeles Superior Court confirmed
the second award; the California Court of Appeal, Second Appellate District,
affirmed in an unpublished opinion (Nov. 18, 2025); the California Supreme
Court denied review (Feb. 11, 2026). The paid petition was filed May 12, 2026,
respondents waived their right to respond on June 15, 2026, and the case is
distributed for the September 28, 2026 conference (the summer long conference).

## Questions presented

1. Whether a court may affirm an arbitration award after acknowledging it is
   unclear whether federal (FAA) or state (CAA) law supplies the vacatur
   standard, without resolving which applies.
2. Whether claims of arbitrator partiality/nondisclosure may be rejected
   without applying the objective appearance-of-bias standard of
   *Commonwealth Coatings v. Continental Casualty*, 393 U.S. 145 (1968).
3. Whether due process permits affirmance where record information bearing on
   adjudicative neutrality goes unaddressed.

## Why this is a near-certain denial

**Base rates.** Modern discretionary cert petitions grant at ~2.5–3% overall
(statpack, Terms 2023–2025); paid petitions at ~5.4% (Term 2025 fee-class
detail); zero-relist petitions at 0.8%. State-court petitions fare worse than
federal ones — the statpack's originating-court cut shows the Court of Appeal
of California, Second Appellate District at 1 grant in 12 resolved (tiny n,
directionally consistent with the state-court discount).

**Case-specific signals, all negative:**

- **No circuit split is pressed.** QP1 attacks the "assume without deciding"
  practice — affirming because the petitioner loses under either candidate
  standard — which is ubiquitous and unobjectionable appellate methodology, not
  a certworthy question. There is a genuine long-standing division over the
  meaning of "evident partiality" after *Commonwealth Coatings* (QP2's
  territory), but the petition does not develop it as a split; it argues the
  lower court failed to pick a framework in this case. That is error-correction
  framing, and the Court has denied many better-vehicled evident-partiality
  petitions.
- **Fact-bound, unpublished, state-specific.** The decision below is an
  unpublished California intermediate opinion turning on whether one
  arbitrator's reappointment to the LAUSD Personnel Commission (a matter
  unrelated to the parties) required supplemental disclosure. QP3's due-process
  theory (*Caperton*/*Rippo*) is tied to a case-specific oral-argument
  disclosure about a panel member's household.
- **Respondents waived the response.** The Court virtually never grants without
  at least calling for a response; a grant path here requires a CFR first, and
  nothing in this petition suggests any chambers would request one.
- **No amici, no CVSG, no relist** (first distribution, for the long
  conference, where the deny pile is deepest). Petitioner is represented by a
  solo employment-side practitioner, not Supreme Court counsel.
- **Vehicle problems even on its own terms.** The court below rejected the
  nondisclosure claims on the ground that the affiliations were unrelated to
  the parties — an outcome that would be the same under either the federal or
  California standard, which is exactly why the choice-of-framework question
  was not outcome-dispositive below and would make this a poor vehicle for
  resolving it.

**No offsetting grant signal.** Nothing here resembles the profile of granted
paid petitions (developed split, published decision, experienced SCOTUS
counsel, amicus support, government involvement, or a relist trail). GVR is
also implausible: no pending merits case supplies an intervening decision on
these questions.

**Calibration.** Starting from the ~5% paid-petition anchor, the waived
response, splitless fact-bound QPs, unpublished state decision, and lack of any
supporting signal each push sharply down. The zero-relist rate (0.8%) is the
better reference class for a petition of this profile, and this one sits below
the middle of that class. I set P(grant) = 0.005 and predict **denied** —
likely without recorded dissent, at or shortly after the September 28, 2026
conference.

## Inputs used

- Snapshot `data/cases/scotus/73369988/record/snapshots/2026-07-17.json`
  (docket 25-1298: parties, counsel, proceedings, paid fee class, distribution).
- Provisioned `questions-presented.txt` and full `petition.txt` (29 pp.).
- No brief in opposition exists (response waived) — none was provisioned.
- Committed `metrics/statpack.md` and the per-fee-class detail in
  `metrics/statpack.json`.
- Mode: `forward` (conference date is in the future; consistent with a
  genuinely pending petition).
