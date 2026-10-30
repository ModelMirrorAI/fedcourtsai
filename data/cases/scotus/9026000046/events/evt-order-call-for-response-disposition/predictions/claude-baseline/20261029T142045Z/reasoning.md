# Why P(grant family) = 0.46

**Inputs read.** Snapshot `2026-09-09.json` (one distribution, a response
requested on 2026-09-08 after the City waived, two amicus briefs, a paid
petition from Cooper & Kirk). `record/documents/petition.txt` and
`questions-presented.txt` (both have full text; not OCR). `context.json`: band
`baseline` under sal-v4, `distribution_count` 1, forward mode.

**Anchor.** The statpack sal-v4 table, baseline band, bracketed `reached` rate
pooled over OT2017–OT2025, comes to about 5% (each Term falls between 4.0% and
5.9%, with n ≈ 1,200–1,750). On top of that: the call for a response (no committed table
conditions on it; my judgement is that it roughly doubles to triples the
rate), and two amicus briefs (the amicus 2+ bucket is ~23% grant family, n=1,449,
but that bucket is selected and counted at disposition). Both of those
together would put a generic petition near 10–15%.

**Why I move far above that.** This is not a generic petition. The structure of
the case matters more than the base rates do:
1. *Viramontes v. Cook County* (No. 25-238) was granted on 2026-06-30. I read its
   corpus row with `fedcourts query --docket-number 25-238`: granted, 22
   distributions, merits not yet decided. It is an arms-ban case
   with the same counsel of record (David H. Thompson). The petition expressly
   asks for a hold for *Viramontes* as an alternative. Held petitions resolve
   in the grant family (as GVRs) at high rates whenever the lead case changes the
   governing framework at all. The Court's practice with the post-*Rahimi*
   Second Amendment GVRs is the template.
2. The decision below is an unpublished summary order that turns on placing the
   common-use burden on plaintiffs at the textual step. That is exactly the
   framework question *Viramontes* is likely to address, and the petition argues
   *Wolford* (decided after the decision below) already undercuts it.
3. Stun guns were the subject of *Caetano* (a 2016 per curiam summary vacatur),
   so a summary disposition is plausible even without a hold.

**Rough decomposition.**
- P(hold for *Viramontes*) ≈ 0.6.
  - × P(GVR | held) ≈ 0.6. This rests on P(*Viramontes* favors challengers or
    reworks the framework) ≈ 0.65–0.7, discounted for a denial even after a
    favorable ruling.
  - ≈ 0.36.
- P(GVR in light of *Wolford*, or summary reversal, before *Viramontes*) ≈ 0.07.
- P(plenary grant) ≈ 0.03.
- **Total ≈ 0.46.** The rest is a denial, either outright soon after the response
  (≈ 0.2) or after an adverse *Viramontes* ruling.

I set `granted` = 0 and `predicted_disposition` = denied only because 0.46 falls
just under one-half. My modal *grant-family* outcome is a GVR, which is why
`summary-disposition-route` is 0.85.

**Uncertainties, and where to discount me.**
- I cannot see what QP *Viramontes* was granted on. If it is narrowly about
  "dangerous and unusual" weapons and leaves the textual step alone, a GVR here
  is less likely.
- The vehicle has a weakness: the panel also faulted petitioners for failing to
  put commonality evidence in the record. The City's response (due 2026-11-23)
  will press that point, and the Court may see the case as fact-bound.
- The State of New York did not intervene, and the City may raise
  standing or which-law arguments I cannot anticipate.
- P(hold) is my own judgement; no committed table measures it.
- `dissent-from-denial` 0.4: Justice Thomas has repeatedly written on denials in
  arms cases. The figure is lower than it would be for an outright denial,
  because part of the denial mass comes after an adverse *Viramontes* ruling.

**Retrieval.** One live docket read (supremecourt.gov) showed only the
extension of the response deadline to 2026-11-23, with no disposition. There
was no leakage. Two corpus queries are listed in `retrieval.md`. I did not
read the case's `summaries/` files.
