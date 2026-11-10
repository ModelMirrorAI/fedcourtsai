# Prediction Reasoning: *Horseracing Integrity and Safety Authority, Inc., et al. v. National Horsemen's Benevolent and Protective Association, et al.* (No. 26-199)

- **Case ID:** `scotus/9026000199`
- **Event ID:** `evt-petition-disposition` (`stage: cert`, `moment: distribution`)
- **Snapshot:** `2026-11-10.json`
- **Prediction:** `granted: 1`, `probability: 0.88`, `predicted_disposition: "granted"`

---

## 1. Base-Rate Anchoring (`context.json` and `metrics/statpack.md`)

1. **Salience Band Anchor (`cert_anchor`):** In `record/context.json`, the frozen conditioning state is `mode: "forward"`, `band: "baseline"` (`salience_version: "sal-v8"`), `distribution_count: 1`, `cvsg_date: null`, and `term: 2026`. The pooled 10-term strictly-prior `reached` base rate for `baseline` in `cert_anchor` is **`0.0516` (`5.2%`)** (`statpack.md` shows `baseline` bracketed `reached` rates between `4.0%` and `6.0%` across OT2017–OT2025).
2. **Other Statpack Cuts:**
   - **Originating Circuit (`ca5`):** In `statpack.md` ("Modern cert petitions by originating circuit"), the Fifth Circuit has a denial-reweighted resolved base rate of `denied 94.6%, gvr 2.3%, dismissed 1.6%, granted 1.6%` (`n=5418`, grant family `3.9%`).
   - **Relist Count (`0` relists / `1` distribution so far):** Petitions ending at `0` relists have a grant-family rate of `1.8%` (`granted 1.3%, gvr 0.5%`, `n=10204`), though this petition is only at its first scheduled distribution (`2026-12-04`) and has not yet reached a conference.
   - **Cert Amicus Count (`2+`):** The snapshot `2026-11-10.json` already records **five** cert-stage amicus briefs (`Senator Mitch McConnell, et al.`; `Thoroughbred Industry Participants`; `Repole Stable, Inc.`; `Cocktail Waitresses, Trainers, and Horsemen`; and `American Veterinary Medical Association`). In `statpack.md` ("Cert petitions by amicus-brief count (paid scored segment)"), petitions in the `2+` amicus bucket grant at **`22.7%`** (`granted 18.2%, gvr 4.5%`, `n=1446`), more than ten times the `0`-amicus bucket (`3.8%`, `n=11109`).
   - **Companion Federal Petition (`No. 26-201`):** Although `No. 26-199` is banded as `baseline` because its lead petitioner is the private Horseracing Integrity and Safety Authority, it is paired with the Federal Trade Commission's parallel petition from the same judgment (`No. 26-201`, staged in `record/related/26-201.json` with `relation: "vided-amicus"`). In `statpack.md`, `federal` band petitions have a pooled grant-family rate of **`73.5%`** (`granted 52.5%, gvr 21.0%`, `n=219`).

---

## 2. Case-Specific Evidence Driving the Upward Adjustment to `0.88`

From the `5.2%` `baseline` anchor (and the `22.7%` `2+` amicus rate / `73.5%` federal-petitioner rate), the provisioned filings (`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, `appendix.txt`, and `related/26-201.json`, `26-332.json`, `26-335.json`) establish an overwhelming case for certiorari:

1. **Act of Congress Held Facially Unconstitutional:** In *National Horsemen's Benevolent & Protective Ass'n v. Black*, 178 F.4th 224 (5th Cir. June 11, 2026) (`appendix.txt`, Pet. App. 1a–53a), the Fifth Circuit held the enforcement provisions of the Horseracing Integrity and Safety Act (HISA), 15 U.S.C. §§ 3051–3060, facially unconstitutional under the private-nondelegation doctrine. A court of appeals decision invalidating a federal statute on its face—challenged by both the Solicitor General (`No. 26-201`) and the statutory Authority (`No. 26-199`)—is the single strongest doctrinal predictor of a Supreme Court grant.
2. **Direct, Acknowledged Post-GVR Circuit Split with the Sixth Circuit:**
   - On June 30, 2025, the Supreme Court granted, vacated, and remanded the prior petitions in this case (`No. 24-433` and `No. 24-429`), as well as the Sixth and Eighth Circuit HISA petitions (`No. 24-472`, `No. 24-420`), for further consideration in light of *FCC v. Consumers' Research*, 606 U.S. 656 (2025) (Pet. App. 120a–121a).
   - On remand, the Sixth Circuit (Sutton, C.J.) again upheld HISA's enforcement provisions as facially constitutional under *Consumers' Research*, *Rahimi*, and *Moody* (*Oklahoma v. United States*, 163 F.4th 294 (6th Cir. 2025)).
   - The Fifth Circuit (Duncan, J.) reached the opposite conclusion on remand, reissuing its prior opinion and adding a section explaining why *Consumers' Research* did not change its view, while expressly stating: "[i]n doing so, we part ways with our esteemed colleagues on the Sixth Circuit." (Pet. App. 5a.)
3. **Prior Supreme Court Stay of Mandate (`No. 24A287`):** On October 28, 2024, the Supreme Court granted the Authority's emergency application (`No. 24A287`) to stay the Fifth Circuit's mandate pending disposition of certiorari (Pet. App. 118a–119a), signaling that a majority of the Court already viewed the Fifth Circuit's invalidation of HISA's enforcement regime as certworthy and warranting interim preservation of the statute. Following its June 2026 decision on remand, the Fifth Circuit stayed its own mandate pending disposition of this petition (Pet. App. 122a–124a).
4. **Unanimous Respondent Acquiescence and Vehicle Consensus:**
   - All three respondent groups in `brief-in-opposition.txt`—the National Horsemen's Benevolent and Protective Association (`NHBPA`), the Gulf Coast Racing plaintiffs, and the State of Texas and Texas Racing Commission—explicitly acquiesce in certiorari in `No. 26-199` and `No. 26-201`.
   - Furthermore, petitioners and all respondents agree that the Fifth Circuit petitions (`No. 26-199` and `No. 26-201`) are a superior vehicle to the pending Sixth Circuit petition (*Oklahoma v. United States*, `No. 25-1325`, which corpus lookup shows was distributed for the October 9, 2026 Conference and has been held without disposition awaiting these petitions), because `No. 26-199` and `No. 26-201` review the only appellate judgment invalidating the statute, arise from a full bench-trial record (`Black II`, Pet. App. 54a–117a), and contain the Fifth Circuit's direct response to *Oklahoma II*.

---

## 3. Main Uncertainty: Consolidation vs. Hold Behind `No. 26-201`

The primary source of residual uncertainty (`12%` complement) is not whether the Supreme Court will review the Fifth Circuit's judgment—which is near-certain (`~96%`)—but the small procedural possibility (`~8%`) that the Court grants *only* the Solicitor General's companion petition (`No. 26-201`, or `No. 25-1325`) and holds `No. 26-199` pending the merits rather than granting and consolidating both `No. 26-199` and `No. 26-201`. However, when both a federal agency (represented by the Solicitor General) and the regulated/statutory entity at the heart of the constitutional challenge petition from the same judgment below presenting the same question, the Court's standard practice is to grant both petitions and consolidate them—just as it did in *FCC v. Consumers' Research*, 606 U.S. 656 (2025), and when granting and GVR'ing both `No. 24-433` and `No. 24-429` in June 2025. Both petitioners (`cert-reply.txt` at 8) and respondents (`brief-in-opposition.txt`) request consolidation of `No. 26-199` and `No. 26-201`.

---

## 4. Justification for Secondary Claims and Big-Case Score

- **`relist-increment: 0.55`:** The snapshot shows 1 distribution (`12/4/2026`). With five related dockets (`26-199`, `26-201`, `26-332`, `26-335`, and `25-1325`) before the Conference, there is a `55%` probability of at least one additional distribution (relist) as the Court coordinates vehicle selection and consolidation across the cluster.
- **`cvsg-increment: 0.01`:** The Solicitor General is already a party and companion petitioner (`No. 26-201`), making a CVSG virtually impossible.
- **`summary-disposition-route: 0.04`:** Because the Court already GVR'd the case once in light of *Consumers' Research* and the circuits remain squarely split on remand, plenary review (`96%` conditional on grant) is overwhelmingly more likely than a second GVR or summary reversal (`4%`).
- **`dissent-from-denial: 0.35` and `order-writers`:** Conditional on an unexpected denial, there would be a `35%` chance of a dissent or statement respecting denial given the invalidation of a federal statute and square circuit split, led by Justices Thomas, Alito, or Gorsuch (`0.03` unconditional writing probability each).
- **`big_case_score: 0.78`:** Major separation-of-powers dispute testing the post-*Consumers' Research* boundaries of the private-nondelegation doctrine and the constitutionality of self-regulatory enforcement models across federal administrative law.
