# Why P(grant) = 0.37

**Anchor.** `record/context.json` puts the petition in band `state` under `sal-v4`, which matches the statpack table's version. I pooled the bracketed `reached` figures for `state` over Terms 2017–2025, all strictly before OT2026. Weighting each Term by its n gives about 104 grants out of about 426, roughly **24%**. I set aside the 2026 row (n=3) because it contains this case's own Term.

**Upward adjustments.**
- The Court called for a response after the respondents waived. That means at least one chambers read the petition. Many response-requested petitions are still denied, but for a state petition with a credible split the call is meaningful. No committed table conditions on it, so the size of this adjustment is my judgment. I added roughly +8 points.
- The claimed split is clean and recurring. The Fifth Circuit's 90-day rule (*Smith v. Edwards*) runs against *Turner v. Rogers*' framing and, per the petition, other circuits. The en banc vote was 11–6 with written dissents, plus a statement respecting denial (Wilson, J.) that concedes the rule is about Fifth Circuit review. Combined with the PLRA's structural interest (90-day injunctions that can never be reviewed), this is the kind of issue the current Court takes from state petitioners. The petitioner's counsel is the Louisiana Solicitor General's office, a repeat Supreme Court litigant.

**Downward adjustments / uncertainty.**
- The question is technical and the stakes are confined to prison-conditions litigation. The Court can leave it for a later vehicle.
- Vehicle questions: there are two consolidated judgments (Rule 12.4), the underlying heat-conditions injunctions have expired, and the merits of the PLRA findings may complicate things. I have not read the brief in opposition (filed Oct 2, after my snapshot), so I don't know whether it disputes the split or raises vehicle defects.
- An unconditional grant could also arrive as a summary reversal, which I count as a grant.

Net: about 0.37. The predicted disposition is denial because the probability is below one half, but I hold it with low confidence.

**Inputs.** Snapshot `2026-08-04.json` (cut at the response-requested day). `questions-presented.txt`, and `petition.txt` (139 pages, truncated, appendix cut), which I skimmed for the split and en banc posture. No BIO was provisioned at this cutoff. In forward mode I also fetched the live supremecourt.gov docket. It shows the response deadline extended to Oct 2, the BIO filed Oct 2, the reply filed Oct 20, and a distribution for the 11/6/2026 conference. It shows no disposition, so the cell is properly pending. I did not read the BIO or the reply. That page confirms the relist-increment claim will resolve yes, but that claim is masked at this moment anyway.

**Other claims.** CVSG 0.04 (no federal party). Summary route given a grant 0.25. Dissent from denial given a denial 0.25: the six en banc dissenters and the PLRA angle make a statement from Alito, Thomas or Gorsuch plausible. The order-writers distribution is kept consistent with that number.
