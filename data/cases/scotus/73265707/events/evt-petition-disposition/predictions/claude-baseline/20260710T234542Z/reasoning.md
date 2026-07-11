# Uddin v. Texana Behavioral Healthcare (No. 25-7275) — petition disposition

**Prediction: cert not granted. P(granted) = 0.001; predicted disposition: denied.**

## The legal question

A pro se, in-forma-pauperis petition for certiorari to the Supreme Court of
Texas. The questions presented ask (1) whether the FAA and the Supremacy
Clause bar a state court from compelling arbitration after the opposing party
waived arbitration through litigation conduct (invoking *Morgan v. Sundance*,
596 U.S. 411 (2022)), and (2) whether compelling arbitration without a showing
of mutual assent, resolved by unreasoned summary denials, violates due process.

## Governing standard

Certiorari is discretionary under Sup. Ct. R. 10; grants require a genuine
circuit/state-court split, an important and recurring federal question, and a
clean vehicle. The modern grant rate is on the order of 1% of petitions
overall and far lower for pro se IFP petitions (historically roughly 0.1% or
less of the unpaid docket).

## Facts from the snapshot that drive the outcome

1. **The Court has already acted, and adversely.** After the June 25, 2026
   conference, the June 29, 2026 order **denied leave to proceed in forma
   pauperis** and gave petitioner until **July 20, 2026** to pay the Rule 38(a)
   docketing fee and submit a booklet-format petition compliant with Rule 33.1.
   The Court does not issue that order for petitions it is inclined to grant;
   it is a strong signal the petition will not be taken up on the merits.
2. **Fatal vehicle problems.** The case reaches the Court from the **denial of
   state mandamus** (Tex. First Court of Appeals, then the Supreme Court of
   Texas, both without opinion). An unexplained discretionary mandamus denial
   is a poor candidate for a "final judgment" under 28 U.S.C. § 1257(a) — the
   underlying suit against Texana continues in arbitration/trial court — and
   the unreasoned orders leave no reasoned federal holding to review. The
   petition also names the state trial judge as a respondent, another defect.
3. **Fact-bound questions.** Whether Texana waived arbitration by its EEOC-era
   conduct and whether the initialed document shows mutual assent are
   record-specific contract/waiver questions, not the kind of legal split
   *Morgan v. Sundance* left open. The petition alleges no split of authority,
   only error correction dressed as Rule 10(a) conflict.

## Reasoning behind the probability and disposition

Two branches remain: (a) petitioner does not pay the fee and re-submit in
compliant form by July 20, 2026 — the modal outcome for a pro se litigant whose
IFP motion was just denied (booklet printing plus the fee runs several hundred
dollars) — in which case the case terminates without a merits grant; or (b) she
pays and refiles, the petition is redistributed, and it is denied like the
overwhelming share of paid petitions with these vehicle defects. Neither branch
plausibly ends in a grant, so P(granted) ≈ 0.001 — below the ~1.4% grant share
among resolved SCOTUS cases in the corpus statpack, reflecting the pro se IFP
posture and the already-entered IFP denial.

For the categorical disposition I predict **denied**: it is the modal label for
recently resolved SCOTUS cert petitions in the corpus, and it is the near-certain
label in every branch where this docket produces a machine-readable disposition
entry ("Petition DENIED"). The main alternative is that the non-payment branch
yields a dismissal-style entry or no further entry at all; corpus priors labeled
`dismissed` in the 2020s are counseled Rule 46 dismissals (settlements), a
different pattern, which is why I put roughly 0.8 confidence on the categorical
call while being much more certain about not-granted.

No per-judge votes are predicted: cert denials are unsigned and votes are not
recorded.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-10.json` (docket through
  June 29, 2026).
- Provisioned `record/documents/petition.txt` (14 pp., complete) — questions
  presented, statement, and reasons for granting, weighed above. No
  brief in opposition or questions-presented extract was provisioned; the
  respondent's response was due May 29, 2026 and none appears on the docket,
  consistent with a waiver of response.
- Corpus priors via `fedcourts query` and the committed `metrics/statpack.md`
  base rates (see `retrieval.md`). Note: the statpack's
  "Modern discretionary-cert petitions by disposition" section referenced by
  the predict prompt is absent from the committed file; I used the overall
  SCOTUS resolved base rate and recent-era priors instead (flagged in
  `flags.json`).

This is a `forward`-mode cell: the petition is genuinely pending and no outcome
exists to leak. I did not seek any disposition information about this case.
