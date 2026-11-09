# Reasoning — Owens v. Taliban, No. 26-294 (first-relist moment)

**P(grant, any form) = 0.27; predicted disposition: denied (narrowly the modal outcome).**

## What the record shows (snapshot 2026-11-09.json, forward mode)
- Paid petition, King & Spalding (McGill) for the Owens/Aliganga plaintiffs (1998 embassy bombing victims holding default judgments against the Taliban). It seeks review of a divided Second Circuit decision (Aug. 26, 2025) holding Da Afghanistan Bank (DAB) funds at the New York Fed immune from attachment under the FSIA. The panel treated a State Department fact sheet and a three-paragraph DOJ district-court letter as binding on whether DAB is an "agency or instrumentality" of a foreign state. Judge Sullivan dissented in part. Rehearing en banc was denied on April 3, 2026, with five judges dissenting in two opinions (Sullivan, joined by Livingston, C.J., Bianco and Park; and Menashi). Those details come from `petition.txt`. The `lower-court-docket.txt` row says "dissent noted: no", but the petition's appendix citations (App.94, 96–131) control, so I treat the en banc dissents as real.
- QP (`questions-presented.txt`): must courts interpret the FSIA independently, or defer to State Department websites and DOJ litigation filings, when deciding whether an entity is entitled to immunity?
- Docket: the respondent (the Taliban) has never appeared. No BIO, no waiver and no call for a response are on the docket. One amicus brief, from the Republic-era Afghan chargé d'affaires (Faiq), is VIDED across all three petitions. The petition was distributed Oct 21 for the 11/6 conference and distributed again Nov 9 for 11/13. That makes `distribution_count` 2, and this is the first relist.
- Companions (`record/related/`, relation `Vide`): 26-292 (Havlish, with an Iowa et al. states' amicus brief and a pending motion to file a supplemental brief) and 26-293 (Ashton). Both followed the identical distribution path. All three will move together.
- `same-question.json`: empty list (nothing above the threshold), so there is no separate split signal.

## Anchor and adjustments
- `cert_anchor.rate` = 0.248 (band `elevated`, sal-v8, 10-Term lookback). The statpack relist cut is a cross-check: bucket 2 (n≈495 resolved) has a grant family of 41.2% (28.3% granted + 12.9% gvr), and 3+ (n≈483) has 37.3%. Both pools include reschedules. The relist is genuine here: the 11/6 conference passed and the petition was set for another one.
- **Up:** a pure statutory question about FSIA methodology that the Court has repeatedly called its own province (Altmann, Samantar). A large five-judge en banc dissent including the Chief Judge. Very high stakes. Three coordinated petitions. Elite counsel. A States' amicus brief on the companion. A relist with no response on file usually means at least one Justice is engaged.
- **Down:** there is no adverse party. The Taliban defaults, and DAB never appeared. Granting would require appointing amicus counsel or relying on the United States. The foreign-relations sensitivity (non-recognition of the Taliban, the Executive's 2022 order splitting DAB assets, the Afghan Fund) makes the Court likely to want the Executive's views before granting. A relist without a response also fits a Justice preparing a dissent from denial. A relist-1 petition does not reach the 2+ bucket's rates by default.
- **Net:** close to the anchor, a little above it given the en banc signal. 0.27. A CVSG is the most plausible next step toward a grant, and it would push resolution months out.

## Claims
- relist-increment 0.62: another distribution follows a CVSG, a called-for response, or a further relist. A straight denial on 11/13 (or after one more look) is the main way it resolves "no".
- cvsg-increment 0.35: the federal interest is direct. DOJ's own letter is what the panel deferred to, and the Executive did not appear on appeal. The Court routinely CVSGs FSIA petitions. The first conference passed without one, though, which tempers the number.
- summary-disposition-route 0.06: there is no intervening decision for a GVR, and a summary reversal on a default-posture FSIA question is implausible.
- dissent-from-denial 0.35 (conditional on denial): the relist with no response is a classic precursor to a written dissent from denial. Gorsuch (skeptical of deference to the Executive) and Thomas/Alito are the likeliest writers.

## Caveats
The decision below's text came only from the petition's own description. There was no `decision-below.txt` and no BIO, because none was filed. I did not use web retrieval. One corpus query was useful (the 26-292 companion row). Calibration is uncertain because of the unusual no-respondent posture.
