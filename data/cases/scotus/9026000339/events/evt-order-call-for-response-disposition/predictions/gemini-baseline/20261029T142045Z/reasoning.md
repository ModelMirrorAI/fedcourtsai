# Predictor Rationale (`reasoning.md`)

## Summary of Forecast
- **Predicted Disposition**: `denied` (`granted`: `0`)
- **`probability` / `disposition`**: `0.14`
- **`relist-increment`**: `0.98` (vacuous at scoring under `moment: response-requested`)
- **`cvsg-increment`**: `0.02`
- **`summary-disposition-route`**: `0.05`
- **`dissent-from-denial`**: `0.015`
- **`big_case_score`**: `0.2`

## Provisioned Record and Posture
This cell forecasts `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`) in *FS Medical Supplies, LLC v. Tanner Pharma UK Limited, et al.*, No. 26-339, on the snapshot `2026-10-07.json` (`cutoff: 2026-10-07`, `mode: forward`).
- **Filings provisioned**: `questions-presented.txt`, `petition.txt`, `appendix.txt` (containing the Fourth Circuit's published opinion of June 25, 2026, by Judge Diaz joined by Judges Gregory and Wynn, the WDNC district court order by Judge Reidinger, the magistrate judge's M&R, and the underlying complaints/disclosures; with a pipeline truncation note omitting 7,232 characters on pages 12–16 of the PDF), and `party-letter.txt` (Petitioner's September 22, 2026 letter requesting a call for a response after respondents waived and noting that Washington Legal Foundation intended to file an amicus brief).
- **Docket state at snapshot (`2026-10-07.json`)**: Paid petition docketed September 14, 2026 (filed September 10, 2026). Both respondent groups (represented by Erik R. Zimmerman at Robinson, Bradshaw & Hinson and Jonathan Yates Ellis at Sullivan & Cromwell) filed waivers on September 21, 2026. Petitioner submitted its letter on September 24, 2026. The petition was distributed once (`distribution_count: 1`) on September 30, 2026, for the October 16, 2026 Conference. On October 6, 2026, the Court requested a response (due November 5, 2026), and Washington Legal Foundation filed an amicus curiae brief the same day. Because the snapshot stops at the call-for-response date, no Brief in Opposition is in the record yet.
- **Note on Retrieval**: Live CourtListener MCP searches returned HTTP 429 (`Rate limit exceeded: 1400/day`), so I degraded gracefully to `uv run fedcourts query`, the committed `metrics/statpack.md` / `statpack.json`, and the provisioned case record.

## Base Rate Anchoring (`metrics/statpack.md`)
1. **Salience Band Anchor**: `record/context.json` stamps `band: "baseline"` under `salience_version: "sal-v4"` for `term: 2026`. In `metrics/statpack.md` (*Segment base rate by salience band (sal-v4)*), pooling the bracketed `reached` rates across the 9 strictly prior Terms rendered in the table (OT2017–OT2025):
   - OT2025: 4.0% (n=1314)
   - OT2024: 5.9% (n=1274)
   - OT2023: 5.9% (n=1312)
   - OT2022: 5.9% (n=1196)
   - OT2021: 5.7% (n=1500)
   - OT2020: 4.5% (n=1740)
   - OT2019: 4.7% (n=1399)
   - OT2018: 4.8% (n=1529)
   - OT2017: 4.9% (n=1649)
   The weighted pooled `reached` base rate across OT2017–OT2025 is **5.11%** (660 / 12,913). This is the exact harness baseline against which `disposition` is scored.
2. **Other Marginal Cuts in `statpack.md`**:
   - **Originating Circuit (`ca4`)**: Modern cert petitions from the Fourth Circuit resolve at 1.3% `granted` and 1.2% `gvr` (2.5% grant family, n=3,480 resolved).
   - **Amicus Count (`cert_amicus`)**: Paid scored-segment petitions with 1 amicus brief resolve at 10.3% `granted` and 4.8% `gvr` (15.1% grant family, n=1,162 resolved), compared to 3.8% for 0 amici (n=11,109).
   - **Call for a Response (`moment: response-requested`)**: As `predict.md` notes, no committed table conditions on a called-for response in cert cases. Calling for a response after a waiver indicates that at least one chambers flagged the petition for closer examination, moving the probability above the 5.11% `baseline` band floor, though the vast majority of CFR petitions are still denied once the BIO arrives.

## Case-Specific Adjustments
Starting from the **5.11%** `baseline` reached rate, I adjust upward to **0.14 (14.0%)** based on the following factors, balanced against significant vehicle and doctrinal headwinds that will be highlighted once respondents file their BIO:

### Upward Factors:
1. **Call for Response + Experienced Supreme Court Counsel + Amicus Support**: Following respondents' waivers, the Court affirmatively called for a response on October 6, 2026, on the same day Washington Legal Foundation filed an amicus brief supporting petitioner. Both sides are represented by prominent Supreme Court practitioners (Kent Yalowitz and John Elwood at Arnold & Porter for petitioner; Jonathan Ellis at Sullivan & Cromwell and Erik Zimmerman at Robinson Bradshaw for respondents).
2. **Cleanly Framed Statutory Question with Acknowledged Tension in Circuit Authority**: The petition presents a pure question of statutory interpretation under 28 U.S.C. § 1332(a)(3) ("citizens of different States and in which citizens or subjects of a foreign state are additional parties"). Petitioner highlights a direct tension between the Fourth Circuit's holding below—that an LLC with three U.S.-citizen members (TX, CA) and one foreign-citizen member (China) cannot invoke § 1332(a)(3) as a sole plaintiff against NC and UK defendants—and the Seventh Circuit's decision in *Tango Music, LLC v. DeadQuick Music, Inc.*, 348 F.3d 244 (7th Cir. 2003) (Posner, J.), which upheld § 1332(a)(3) jurisdiction where the plaintiff LLC had NJ and UK members and defendants were DE/NY and UK citizens, as well as the Third Circuit's analysis in *Dresser Industries, Inc. v. Underwriters at Lloyd's of London*, 106 F.3d 494 (3d Cir. 1997). Even the magistrate judge noted that "no controlling case law directly address[es] the precise [diversity jurisdiction] situation presented here" (App. 6a).

### Downward / Limiting Factors (Why Denial Remains Strongly Favored):
1. **Doctrinal Vulnerability Under *Carden* and *Grupo Dataflux***: The Fourth Circuit's reasoning is straightforward and well-grounded in Supreme Court precedent. Under *Carden v. Arkoma Associates*, 494 U.S. 185 (1990), an unincorporated entity is not a "citizen" in its own right; its citizenship is that of each of its members, and every member's citizenship must be tested. In *Grupo Dataflux v. Atlas Global Group, L.P.*, 541 U.S. 567 (2004), a partnership with U.S. and Mexican partners suing a Mexican corporation lacked diversity because the Court refused to disaggregate or ignore the foreign partners' citizenship. Furthermore, *Tango Music* (2003) pre-dated *Grupo Dataflux* (2004) and did not specifically analyze the unincorporated-entity "single party vs. additional party" problem under § 1332(a)(3)—it focused on whether having Britons on both sides of a § 1332(a)(3) suit destroyed diversity, assuming without analysis that the LLC sat on the plaintiff side as both a U.S. citizen and an additional foreign party. Respondents' forthcoming BIO will forcefully argue that *Tango Music* passed on the specific sub-issue sub silentio or was superseded by *Grupo Dataflux*, and that the Fourth, Fifth (*Controlled Environment Systems*, unpublished), and Eighth (*Jet Midwest*) Circuits are harmonious.
2. **Severe Vehicle Problems and Self-Inflicted Postural Quirks**: The jurisdictional defect arose only because petitioner litigated for over three years mistakenly alleging that all four of its LLC members were U.S. citizens, before disclosing on the eve of a hearing that one member (Ms. Tong) was a Chinese citizen domiciled in California (App. 5a–6a, 102a). Worse still for certworthiness, after discovering the mistake, Ms. Tong transferred her LLC interest to her husband (a U.S. citizen member), and petitioner **already filed a third lawsuit** in the Western District of North Carolina (*FS Medical Supplies, LLC v. TannerGAP, Inc.*, No. 3:25-cv-00102) without the foreign member to "moot out the jurisdictional issue" (App. 6a n.2). Respondents will emphasize in their BIO that this unusual, self-inflicted pleading error—and the existence of ongoing parallel litigation—makes this case an unattractive vehicle.

Balancing the call for a response, top-tier counsel, WLF amicus brief, and the tension with *Tango Music* against the strength of the Fourth Circuit's *Grupo Dataflux* analysis and the self-inflicted vehicle flaws, **0.14** is well-calibrated.

## Secondary Claims and Distributions
- **`relist-increment` (0.98)**: The snapshot shows `distribution_count: 1` (for the October 16, 2026 Conference). Because the Court requested a response on October 6, 2026 (due November 5, 2026), the petition will be redistributed once the BIO arrives. (Under `fedcourtsai.pipeline.claims`, `relist-increment` is masked as vacuous on `moment: response-requested`, but I state the true forward probability of 0.98.)
- **`cvsg-increment` (0.02)**: Very low chance of a CVSG on a private commercial contract/fraudulent-transfer dispute turning on § 1332(a)(3).
- **`summary-disposition-route` (0.05)**: The harness baseline for `summary-disposition-route` across OT2017–OT2025 is **34.43%** (driven largely by GVRs across all grants). Here, however, conditional on a grant, the Court would be granting to resolve an alleged circuit split on diversity jurisdiction, not to GVR for an intervening decision or summarily reverse a clear error. Thus, conditional on a grant, plenary review is ~95% likely (`summary-disposition-route: 0.05`).
- **`dissent-from-denial` (0.015)** and **`order-writers`**: Separate writings on cert denials in commercial diversity-jurisdiction disputes are rare (~1.5% aggregate; 0.001–0.003 per Justice, slightly higher on Thomas and Gorsuch given their interest in statutory text and jurisdictional rules).
