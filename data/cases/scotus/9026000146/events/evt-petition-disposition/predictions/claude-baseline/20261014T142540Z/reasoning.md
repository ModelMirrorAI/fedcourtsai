# Reasoning — P(grant) = 0.62

**Inputs.** Snapshot `2026-10-14.json` (forward mode). No filed-document text was
provisioned: there is no `record/documents/`, so I had no petition, QP, or BIO text. I
worked from the docket skeleton plus light retrieval. CourtListener identifies the decision
below as *Daley v. Choate*, No. 24-1191 (10th Cir. Nov. 3, 2025), listed as published, from
the District of Colorado. The opinion text CourtListener served for that record was a
mismatched, unrelated district-court order, so I could not read the Tenth Circuit's
reasoning. My guess that this is an immigration-detention matter (Aurora facility warden)
is an inference, not a confirmed fact.

**Anchor.** The petitioner is the federal government, represented by the Solicitor General
(the caption names a warden, with SG counsel of record). That is the strongest grant
predictor on the cert docket. The statpack's `federal` sal-v4 column, pooled over the 2017–2025
Terms (bracketed `reached` figures), gives about 143/203 ≈ 70%. The context's frozen band is
`state`, and the same pooling for that column gives about 99/421 ≈ 23.5%. The `state` band
does not fit this caption: there is no state party, and the petitioner is the United States
through the SG. I have flagged the mismatch. I anchor on the federal figure because that is
what I actually believe. The evaluator will score against the frozen `state` band, and I
expect to beat that baseline only if the federal anchor is right.

**Adjustments.**
- Up: the Court requested a response after the petition had gone to conference, and the
  decision below is published with rehearing denied.
- Down: the Court routinely requests a response on SG petitions where the respondent waived,
  so that signal is weaker than it would be for a private petitioner. Some SG petitions are
  held and then GVR'd or denied. I could not check whether a circuit split exists or whether
  the issue is narrow or tied to the facts. Without the QP I shade down from 70% to 0.62.

**Increments.** A response is due November 23, and the petition will almost surely be
redistributed after it arrives, so relist-increment = 0.95. A CVSG is essentially impossible
with the SG as petitioner, so cvsg-increment = 0.01. Summary route given a grant = 0.20: plenary
review is the norm for SG petitions, and hold-then-GVR is the main alternative. Dissent from
denial given a denial = 0.15.

**Where to discount me.** I had no petition text, the opinion text was unreadable, and the
nature of the issue is inferred.
