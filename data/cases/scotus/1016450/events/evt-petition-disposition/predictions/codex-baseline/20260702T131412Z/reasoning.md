# Prediction: Brooks v. South Carolina

## Event

The event asks for the disposition of a SCOTUS petition in `Brooks v. South Carolina`, docket `610, Misc`. I used the snapshot at `data/cases/scotus/1016450/record/snapshots/2026-07-02.json`.

## Snapshot Facts

The snapshot is sparse. It gives the case name, SCOTUS docket number, CourtListener docket id, and one cluster reference. It has no docket entries, no filed date, no originating court, no lower-court judgment, no question presented, no party details beyond the caption, and no dates showing certiorari or another petition was granted or denied. The event definition is unresolved and targets petition disposition.

## Governing Standard

Supreme Court petition grants are discretionary and uncommon. The usual indicators that raise grant probability are a clear split of authority, an important recurring federal question, a strong vehicle, government or institutional support, and a clean record. A petition without visible issue framing, lower-court context, docket activity, or vehicle facts should be treated close to the low SCOTUS petition baseline.

## Corpus Context

I used the local corpus tools only for context. The resolved SCOTUS aggregate returned 296 cases, with 4 labeled granted, a 1.4% grant share. Grouping by SCOTUS term and originating court did not add useful case-specific calibration because this docket number has no parsed term and the snapshot gives no originating court. Broad SCOTUS priors returned mostly old or heterogeneous records, so I treated them as weak context and relied primarily on the base rate.

## Analysis

There is no snapshot evidence supporting a grant. The miscellaneous docket marker and lack of visible lower-court or question-presented information make a grant less likely than even a well-developed paid certiorari petition. The absence of docket entries also means I cannot identify a procedural reason to predict dismissal or withdrawal. For a petition-disposition event, the most conservative outcome is that the petition is denied.

I assign a 1.2% probability of a grant. That is slightly below the local SCOTUS aggregate grant rate because the snapshot contains none of the usual certworthiness signals and offers no facts that would justify moving upward. Confidence is moderate-low because the prediction is necessarily base-rate driven; more docket detail could materially change the assessment.
