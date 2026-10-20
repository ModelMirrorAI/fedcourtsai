# claude-baseline: P(grant) 0.15, predicted `denied`. Incorrect, Brier 0.7225

**What it got right.** This was the most thoroughly researched candidate. It retrieved the brief in opposition, the supplemental brief and the Third Circuit opinion (all pre-prediction filings, which is legitimate forward signal), along with the full *Jules* opinion. It identified every relevant upward factor: the call for a response after a waiver, the GVR ask, the *Lawrence v. Chater* standard, and *Jules*'s closing language about live pending claims. Its uncertainty section correctly identified the failure mode: if GVRs for hold-for-a-decided-case petitions with a called-for response run materially above one in ten, it was too low.

**What it got wrong.** Its central judgment, that the panel's "civil action" holding was independent of *Jules* and would insulate the decision from a GVR, is the reading the Court did not adopt. It gave the brief in opposition's framing more weight than the *Lawrence* threshold (a "reasonable probability" of a different result) warrants. It also added equitable and vehicle points that, as it conceded, do not formally bear on a GVR. The CFR-conditional grant rate it relied on was a remembered figure, flagged as such. The work was competent and transparent, but the decisive weighing went the wrong way.

`reasoning_quality` 0.5.

## The cell

Cert stage, forward mode. *Burford German Funding LLC v. financialright claims GmbH* (No. 25-1269, from the Third Circuit). Outcome: **GVR** (`actual_granted` = 1), resolved 2026-10-19 after two distributions. All three candidates predicted on 2026-09-16 from the same snapshot: one distribution, a response requested on July 15 after the respondent waived, and the brief in opposition submitted September 14. Each prediction froze `band: baseline` under `sal-v4`, so the **stamped segment base rate** (risk-set anchor) and the Brier skill are the harness's. I leave them null and quote no rate of my own. No semantic set is declared on a cert cell, and votes are not scored at this stage.

The way to read this petition was to see that it was a request to hold the case and GVR in light of *Jules v. Andre Balazs Properties* (decided 2026-05-14). The call for a response after a waiver, coming after *Jules* was decided, was the strongest signal on the docket. The Court did GVR.

**Leakage.** All three are forward cells, and the case was open when they predicted. No call reached material dated on or after the resolution, and no prose treats the outcome as known. `influenced_prediction` = `not_applicable` for all three. Details are in each `leakage.notes`.
