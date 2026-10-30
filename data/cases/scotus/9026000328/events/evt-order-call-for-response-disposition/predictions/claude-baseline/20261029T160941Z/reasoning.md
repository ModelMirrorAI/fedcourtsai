# Why P(grant) = 0.27

**Anchor.** `context.json` gives band `baseline` under sal-v4, the salience version the
statpack's band table also uses. That band's bracketed `reached` rate, pooled over OT2017
through OT2025 (Terms strictly before this case's OT2026), is about 5.1% (n ≈ 12,900).
I computed it from the per-Term rows of `metrics/statpack.md`.

**Upward adjustments:**
- **Call for a response.** The Court asked for a response after both respondents waived.
  No committed table conditions on a called-for response, so how much this moves the
  number is my judgment. Paid petitions with a called-for response grant at a
  meaningfully higher rate than the baseline band, though most are still denied. Taken
  alone, I would put this at roughly 10–12%.
- **Amicus support.** Three amicus briefs were filed at the petition stage. The
  statpack's amicus cut shows 2+ amicus petitions at about 23% grant family
  (granted + GVR; n = 1,449 resolved). That is a population shape, not an increment over
  the call for a response.
- **An acknowledged split, with petitions on both sides.** The South Carolina Supreme
  Court expressly declined to follow In re Whittaker Clark & Daniels (3d Cir. 2026), per
  the petition at Pet. App. 29a–30a. The receiver himself (No. 26-159, Paul Clement for
  the respondents) and the talc claimants' committee (No. 26-263, counsel of record
  Elizabeth Prelogar) are both seeking review of the Third Circuit decision. The corpus
  rows for those dockets show no distribution yet. The live docket for 26-159 shows the
  brief in opposition (Aug 25) and the reply (Sep 4), with no distribution yet. It looks
  as if the Court is lining up the cluster. When parties on both sides of a split ask for
  review, the chance that the Court takes the question somewhere rises a lot. A grant
  elsewhere also opens a hold-then-GVR path for this petition.
- **Elite counsel on every petition.** Gibson Dunn, Kannon Shanmugam on 26-350, Clement,
  Prelogar.

**Downward adjustments:**
- **Finality.** Review here is interlocutory: a trial on the merits remains, and
  jurisdiction rests on a Cox/Langdeau finality argument. This weakens the petition as
  the lead vehicle.
- **Competing vehicle.** The Court may prefer the federal-court Whittaker case.
- **Holds end both ways.** If Whittaker is granted and decided against the receiver, a
  GVR here is likely. If it is decided for the receiver, this petition is denied.

**Composition.** I put P(the Court takes the question in some vehicle) at about 0.45.
Given that:
- P(this petition gets a plenary grant) ≈ 0.3.
- P(held) ≈ 0.6, with about half of holds ending in a GVR.

That gives 0.45 × (0.3 + 0.3) ≈ 0.27, plus a small residual if no vehicle is taken.
I report 0.27. The same reasoning gives summary-disposition-route ≈ 0.45 conditional on
a grant. A post-hold GVR is a cert-order disposition, which is why that figure is so high.

**Uncertainties.**
- I have not read the Whittaker petitions themselves, only their docket metadata. The
  Third Circuit case arose in bankruptcy and may turn on bankruptcy-specific grounds that
  make it a poor substitute, which would favor this petition. I could not verify that.
- Hold and timing dynamics may resolve this event long after argument in a companion.
- The response, not yet filed, may raise vehicle problems I cannot see. Per the prompt,
  I do not infer what it will say.

**Increments.** relist-increment is 0.95: once the response is filed, the petition is
redistributed. The harness masks this claim on this moment. cvsg-increment is 0.12, for
the foreign-relations interest; I would expect any CVSG to come in the Third Circuit
cases instead. dissent-from-denial is 0.06: a denial here is more likely to be quiet
(or follow a hold) than to draw a written dissent.

**Inputs used.**
- Snapshot `2026-10-27.json`.
- `questions-presented.txt`, `petition.txt` (not truncated), and `appendix.txt`, which
  is truncated and which I did not read closely.
- Related snapshot `26-350.json`.
- No BIO or response is on file; both respondents waived and the requested response is
  not yet due.
