# Rationale for the numbers

**P(any grant) = 0.47; granted = 0; predicted_disposition = denied.** The number is a mixture over three paths rather than a single judgment call:

| Path | P(path) | P(grant given path) | Contribution |
| --- | --- | --- | --- |
| Court grants both petitions and consolidates | 0.25 | 1.00 | 0.25 |
| Court grants McNutt, holds Ream, later GVRs (challengers win McNutt) | 0.70 × 0.32 | 1.00 | 0.22 |
| Court grants McNutt, holds Ream, later denies (government wins McNutt) | 0.70 × 0.68 | 0 | 0 |
| Court denies Ream outright at the conference | 0.05 | 0 | 0 |

The single likeliest terminal label is `denied` (about 0.48 across the hold-then-deny and deny-now paths), which is why `granted` is 0 even though the grant family sits just under one half. A GVR counts as a grant on the binary axis, so it is in the 0.47.

**Anchor.** `record/context.json` gives band `elevated` under sal-v4, matching the statpack's band table. Pooling the bracketed `reached` rate for `elevated` over Terms 2017 to 2025 (all nine rows the table renders before OT2026) gives about 16.9% (n = 3085). The relist cut (statpack, paid scored segment) puts the two-distribution bucket at roughly 41% grant family, but that bucket is terminal and this docket's second distribution is a reschedule, not a relist, so I did not read it as the answer. The modern-cert overall grant rate is a few percent and is not the right population for a petition the Solicitor General concedes warrants review.

**Why so far above the anchor.** The decisive facts are outside the provisioned inputs and were retrieved in forward mode: (1) the government's response (Aug. 14) states that the question "warrants this Court's review" and that it was filing its own petition the same day; (2) that petition, No. 26-204, was docketed Aug. 18, briefed, and distributed for the same October 9 conference; (3) the McNutt respondents (same counsel as Ream) also agree review is warranted. Both sides agreeing that a square, acknowledged split over the constitutionality of a federal criminal statute must be resolved makes a grant of at least one of the two petitions near certain. The only live question is which petition carries the case.

**Why not higher.** The government asked the Court to grant McNutt and hold Ream, citing Ream's weaker standing (two judges below found none), Ream's extra Commerce Clause question that no court of appeals reached, and the Court's practice of granting a single petition from one side of a split (its reply cites Anderson v. Intel and Murthy v. Missouri). The Court usually follows the Solicitor General's vehicle recommendation when the alternative vehicle has a jurisdictional wrinkle and the other side's advocates are already in the granted case. That is why I put only 0.25 on a consolidated grant. Within the hold path, the grant family depends entirely on the merits of McNutt. I put the government's chance of winning McNutt at about two in three: Felsenheld v. United States and United States v. Comstock give Congress wide latitude in choosing means, and Dewitt, the petitioner's lead authority, itself distinguished laws "regulating the business of distilling liquors" as plainly adapted to collecting the tax. The Fifth Circuit's no-limiting-principle argument will attract some Justices, so this is not lopsided.

**Claims.**
- `relist-increment` 0.83: a held petition is redistributed after McNutt is decided; a grant now would most likely follow one relist; only an immediate denial (about 5%) or an unusually quick grant produces no further distribution.
- `cvsg-increment` 0.01: the Solicitor General is already respondent.
- `summary-disposition-route` 0.48: of the 0.47 grant mass, 0.22 is a GVR after a hold and 0.25 is a plenary consolidated grant.
- `dissent-from-denial` 0.18: a post-McNutt denial would usually be silent; a Thomas statement on Raich is the main exception.

**Big case score 0.6.** Enumerated-powers challenge to a federal criminal statute, a request to overrule Raich, 15 states and ten organizations as amici. The question actually likely to be decided (taxing-power Necessary and Proper) is narrower than the Raich framing, which keeps this below the top tier.

**Uncertainty and where to discount me.** The 0.25 for a consolidated grant is a judgment about the Court's habits with dueling petitions, not a measured base rate; the corpus tooling has no cut for "SG petition pending from the other side of the split." The McNutt merits estimate is likewise my own read of doctrine. The provisioned documents did not include the government's response (the pipeline fetched only the petition and QP), so everything about the government's position came from retrieval, as did the companion docket. The statpack's relist and band cuts are terminal-bucket figures and I used them for shape only. Nothing I retrieved postdates the snapshot in a way that reveals the outcome; the Ream docket as of today shows nothing after the September 23 distribution, and the conference is October 9.

**Corpus query.** One `fedcourts query` for granted 2020s SCOTUS priors returned recent grants with no structural match to this posture (it surfaced mostly emergency applications and unrelated grants), so it did not move the number.
