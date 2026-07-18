# Martin v. Martin, No. 25-1307 — cert prediction

**Prediction: deny. P(any grant, GVR included) ≈ 0.02.**

## The case

A paid petition (docketed May 26, 2026, Term 2025 numbering) from the Court of
Appeals of Mississippi, after the Mississippi Supreme Court denied discretionary
review 5–2 (Justices Griffis and Branning voting to grant). A Warren County
chancellor held petitioner Christy Martin in civil contempt for failing to pay a
$21,040.72 property-damage award that had been folded into her divorce judgment,
sentenced her to six months' incarceration suspended on a payment schedule
($7,135 down, $3,567.50/month), and provided that opposing counsel "shall
automatically submit to the Court an order for incarceration" on any missed
payment. The questions presented ask whether Bearden v. Georgia and Turner v.
Rogers forbid incarcerating an indigent judgment debtor for nonpayment of a
private civil money judgment without an express on-the-record ability-to-pay
finding, whether relabeling a money judgment as "contempt" evades the bar on
debtors' prisons, and whether the burden-shifting and counsel-triggered
incarceration mechanism satisfies Turner's minimum safeguards.

## Why the pull toward a grant is real but weak

- The subject matter is genuinely cert-adjacent: Turner v. Rogers itself
  addressed civil-contempt incarceration for nonpayment, and the
  "modern debtors' prison" theme has sustained DOJ/ACLU/academic attention.
  A grant here would extend Bearden/Turner from state-interest obligations
  (fines, child support) to purely private money judgments.
- Two justices of the state's highest court voted to hear the case, which the
  petition uses effectively as evidence the question is substantial.
- The order's most striking feature — counsel's "automatic" incarceration
  trigger without a contemporaneous hearing — is the kind of fact that can
  attract a summary reversal if the Court sees a square Turner violation.

## Why denial is far more likely

1. **Preservation is a serious vehicle defect.** The state-court cert petition
   (reproduced in the petition's own Appendix F) argued almost entirely under
   Article 3, § 30 of the Mississippi Constitution, Riser, and McPhail; its only
   federal reference is the bare assertion that the decision "is contrary to the
   United States Constitution." The BIO leads with Adams v. Robertson and Webb
   v. Webb, and under § 1257 practice a vague invocation of the federal
   Constitution in the highest state court is a genuine jurisdictional/
   prudential obstacle. The Court rarely takes a case where it would first have
   to litigate adequate presentation.
2. **The factual premise of the QPs is contested.** The BIO shows the chancellor
   did address ability to pay — he found Christy's inability claim not credible,
   citing her admission that she "could work as much as she wanted," her payment
   of a separate $6,000 sanction the morning of the hearing, and her election to
   stay home. The Court of Appeals affirmed that finding as supported by
   substantial credible evidence. Whether that amounts to a Turner-compliant
   "express finding" is arguable, but it makes the case look fact-bound — a
   credibility dispute dressed as a procedural-floor question — which is
   Rule 10's paradigm for denial.
3. **Ripeness/posture.** Petitioner appealed eleven days after the order, was
   never incarcerated, and the state courts expressly held (via Riser) that
   inability to pay remains a continuing defense to any future incarceration.
   The claimed Turner violation (counsel-triggered jailing without a hearing)
   has never actually operated on her. That gives the Court an easy reason to
   wait for a case with a completed deprivation — Turner itself involved a
   contemnor who had served twelve months.
4. **The asserted conflict is soft.** The petition's "entrenched conflict" mixes
   state constitutional imprisonment-for-debt clauses (Mississippi, Texas,
   Indiana, Florida), state statutes authorizing contempt for divorce-decree
   obligations (Pennsylvania, Massachusetts, Ohio), and federal fines-and-fees
   cases (Cain, ODonnell). These regimes differ on state-law grounds, not on a
   crisply presented federal question; there is no direct split on whether the
   Fourteenth Amendment permits contempt incarceration to enforce a private
   money judgment after an adverse credibility finding on ability to pay.
5. **No grant-signal machinery.** Docketed May 26, 2026; BIO filed June 22; a
   single distribution for the September 28, 2026 long conference; no relists
   yet (relist count 0 → 0.8% base grant rate); no CVSG; no amicus support; both
   sides represented by small Mississippi firms rather than Supreme Court
   specialists. The corpus sample of recent grants (e.g., the Monsanto pair,
   Petersen v. Doe) shows the opposite profile: elite counsel and multiple
   distributions.
6. **Base rates.** The statpack's modern discretionary-cert slice puts the
   overall grant rate at a few percent; for Term 2025, paid petitions run
   ~5.4% and the zero-relist bucket ~0.8%. A paid, counseled petition with a
   colorable constitutional theme sits above the zero-relist floor until the
   first conference reveals more, but the preservation defect, the fact-bound
   posture, and the absence of any grant signals push it well below the paid
   average.

## Probability

Anchor: paid Term-2025 petitions ≈ 5.4%; zero-relist petitions ≈ 0.8%. This
petition's sympathetic theme and the 5–2 state-court split argue for slightly
more than the floor; the preservation problem, ripeness posture, soft split,
and absence of specialist counsel or amici argue for much less than the paid
average. A GVR is essentially unavailable — there is no recent intervening
decision on Bearden/Turner scope to GVR against. I set **P(grant) = 0.02** and
predict **denied**, most likely without recorded dissent after the long
conference (a statement respecting denial from a criminal-justice-minded
justice is conceivable but does not change the disposition).

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-17.json` (docket through the
  July 8, 2026 distribution).
- `record/documents/questions-presented.txt`, `petition.txt` (full text incl.
  appendices: the chancery contempt order, the Court of Appeals opinion, and
  the state cert petition), and `brief-in-opposition.txt` — the BIO's
  preservation, ripeness, and fact-bound arguments drive the low probability.
- Committed `metrics/statpack.md` / `statpack.json` base rates and one
  `fedcourts query` corpus lookup (see `retrieval.md`).
