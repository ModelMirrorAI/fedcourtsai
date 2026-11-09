# Reasoning — Novotny v. Moore, No. 25-1324 (relist moment)

**P(any grant, GVR included) = 0.36; called as a denial.**

## What the record shows
- A paid petition from a published, partly divided CA4 decision (Jan. 20, 2026; Gregory and Diaz in the majority) that upheld most of Maryland's SB 1 location bans: government buildings, mass transit, school grounds, health facilities, museums, stadiums, amusement venues and casinos. The panel reversed on alcohol-serving places and public demonstrations. Petitioners are represented by Cooper & Kirk (David Thompson). The single QP asks whether Maryland's many carry bans in places open to the public violate the Second Amendment.
- Docket (snapshot `2026-11-09.json`, checked against the live supremecourt.gov docket, which matches): the petition was distributed for 9/28, 10/9 and 10/16 and **rescheduled before each of those conferences**. It then went to conference on 11/6 and was distributed again on 11/9 for 11/13. So this is a real first relist after one real conference, and it follows three pre-conference reschedules. `distribution_count` is 5, CVSG none, one amicus brief (GOA et al.).
- The BIO (Aug. 17, 2026) makes four arguments. Wolford v. Lopez, 146 S. Ct. 2032 (2026), struck down Hawaii's private-property default rule and does not reach targeted location bans. The circuits broadly agree. Only five circuits have ruled. The Court should let the issue percolate. The BIO also says Maryland's own petition on the default rule (Moore v. Kipke, 25-1206) was dismissed after Wolford.
- The reply (Sept. 2) argues that Wolford's "daily lives" language condemns the cumulative web of bans. It also points out that the Ninth Circuit summarily held on remand that the rest of Hawaii's law was "unaffected", which shows the lower courts will not apply Wolford on their own. Koons (CA3) is pending en banc: argued Feb. 11, 2026. I found no report that it has been decided.

## Anchor and adjustments
- `cert_anchor.rate` = 0.346 (band `high`, sal-v8, 10-Term pool). The relist-count cut gives granted+GVR of 13.5% at 1 relist (n≈2532), 41% at 2 and 37% at 3+. Pooling bucket 1 and above sits near 20%. But the stored count here is inflated by three reschedules, and the band likewise counts those reschedules.
- **Up:** this is a real relist after a real conference, which is the classic signal that the Court is looking closely. The Court decided Wolford this year, and the decision below predates it, so a **GVR in light of Wolford** is a live route to the grant side. The question has very high stakes, and petitioners have elite SCOTUS counsel.
- **Down:** in Second Amendment cases this Court has repeatedly used relists to prepare dissents from denial rather than grants (e.g., Snope v. Brown and Ocean State Tactical, both denied in June 2025 after long relist runs with written dissents; Antonyuk denied in 2025). The Court chose Wolford's narrow default-rule question over broad sensitive-places review. Koons en banc is pending, which gives a percolation reason to wait. A GVR would usually have come at the first conference, and it did not. The many-locations facial posture is also a sprawling vehicle.
- Net: roughly 0.22 plenary grant, 0.14 GVR, 0.64 deny. That makes P(grant family) 0.36, essentially at the anchor. `summary-disposition-route` 0.40 is the GVR share of the grant family.

## Increments
- relist-increment 0.72: a dissent from denial being written, or a grant decision being deferred, both mean further relists. An outright grant or denial at 11/13 is the main way this resolves false.
- cvsg-increment 0.02: the respondent is a State, and the Court almost never calls for the SG's views in a state-law Second Amendment case.
- dissent-from-denial 0.65 conditional on denial: a denial after relists in a Second Amendment case very often comes with a Thomas dissent (Alito and Gorsuch often join or write).

## Uncertainty
The biggest unknown is what the three reschedules were waiting for. Possibilities include a Justice's request, Koons, or a held companion. I could not identify one. `record/related/` and `same-question.json` were not provisioned. Corpus query on Moore v. Kipke (25-1206) confirmed the related docket exists. I did not use the case summaries under `summaries/`.
