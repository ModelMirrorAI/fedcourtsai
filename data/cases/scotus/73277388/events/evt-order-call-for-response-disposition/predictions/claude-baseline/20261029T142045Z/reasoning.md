# Why P(grant) = 0.20

**Anchor.** `record/context.json` puts the petition in band `baseline`
(sal-v4, matching the statpack table's version) with one distribution. I pooled
the bracketed `reached` rate for `baseline` over OT2017–OT2024, the Terms
strictly before this case's OT2025. Every row sits between 4.5% and 5.9%, on
roughly 1,200–1,700 weighted petitions each. The pooled rate is about **5%**.
The petitioner is private, so `baseline` is also the right caption-class floor.

**Adjustments up.**
- *Response requested.* No committed table conditions on a call for a
  response. In my judgement a call on a paid petition with elite counsel
  (Sidley) moves the odds severalfold, though most such petitions are still
  denied.
- *Amicus.* One amicus brief, from the ABA, is on file. The statpack's
  amicus-count cut puts the `1` bucket at 10.3% granted and 4.8% GVR
  (n=1,162 resolved), against 2.0% for `0`. That cut is read at disposition and
  overlaps the response-requested signal, so I do not stack it fully.
- *Subject matter.* The Court regularly reviews FAA equal-treatment
  (preemption) questions. The petition claims a 5-1 split, with the First,
  Second, Third, Sixth and Eighth Circuits against the Fourth.
- *Companion gone.* The petition names *Continental Finance v. Johnson*,
  No. 25-34, the published Fourth Circuit decision that controlled this case.
  A corpus lookup shows that docket **dismissed on 2026-05-07 with zero
  distributions**, probably by agreement. That date is after my snapshot, and
  forward mode permits reading it. It means this petition is the only vehicle
  left for the issue rather than a candidate to be held behind *Johnson*. It
  raises the grant probability a little. It also changes the route if the
  Court acts: a hold followed by a GVR is no longer likely.

**Adjustments down.**
- The opinion below is an unpublished, one-paragraph per curiam that rests on
  *Johnson* and *Noohi* (Pet. App. 1a–3a). The petition says rehearing en banc
  was denied as untimely.
- The claimed split is largely older cases, some of them dicta ("might risk
  running afoul"). Whether *Cheek* discriminates against arbitration or simply
  applies severability turns on a question of Maryland law, so the response
  has a real argument that the split is illusory.
- The response was not yet filed at my snapshot, and I do not infer its
  content.

I land at about 0.20. My largest uncertainty is how much the call for a
response is worth. I would not be surprised by anything in the 10–30% range.

**Other claims.** `relist-increment` is 0.97 because a response-requested
petition is almost always re-distributed; the harness masks this claim anyway.
`cvsg-increment` is 0.04 because no federal interest is at stake.
`summary-disposition-route` is 0.12 conditional on a grant: no GVR source
exists, and a per curiam reversal is possible but uncommon.
`dissent-from-denial` is 0.05 conditional on a denial.

**Inputs used.** The snapshot `2025-11-07.json`, the petition, the QP, the
appendix (the Fourth Circuit opinion and the district court opinion) and the
Spring Oaks Rule 12.6 letter. No brief in opposition was provisioned because
none existed at the cutoff.

**Disclosures.** I did not look up this case's own disposition or its live
docket. I did not read `summaries/`. I have no trained-in knowledge of how
No. 25-311 came out. The companion's dismissal date is post-snapshot
information, and I disclose it here. One caveat for the reader: this forward
cell runs almost a year after its snapshot, so the case's real status is
unknown to me.
