# Predictor Rationale (`reasoning.md`)

## 1. Summary of Call

- **Predicted Disposition:** `denied` (`granted = 0`, `probability = 0.045`, `confidence = 0.82`)
- **Stage and Moment:** `cert` stage, `moment: response-requested` (`evt-order-call-for-response-disposition`), conditioned on snapshot `2026-08-13.json` (`cutoff = 2026-08-13`, `cut_kind = date`, `mode = forward`).

## 2. Base-Rate Anchor (`metrics/statpack.md`)

From `record/context.json`, the harness froze this cell in `band: "baseline"` under `salience_version: "sal-v4"`, with `distribution_count: 1`, `cvsg_date: null`, and `term: 2026`.

Following the prompt contract for a cert-stage cell, we anchor on the `baseline` band's bracketed `reached` grant rate in the **"Segment base rate by salience band (sal-v4)"** table of `metrics/statpack.md`, pooled across all rendered Terms strictly preceding OT2026 (OT2017–OT2025, 9 Terms):

- **OT2025:** 4.0% ($n = 1{,}314$, $\approx 52.6$ weighted grants)
- **OT2024:** 5.9% ($n = 1{,}274$, $\approx 75.2$ weighted grants)
- **OT2023:** 5.9% ($n = 1{,}312$, $\approx 77.4$ weighted grants)
- **OT2022:** 5.9% ($n = 1{,}196$, $\approx 70.6$ weighted grants)
- **OT2021:** 5.7% ($n = 1{,}500$, $\approx 85.5$ weighted grants)
- **OT2020:** 4.5% ($n = 1{,}740$, $\approx 78.3$ weighted grants)
- **OT2019:** 4.7% ($n = 1{,}399$, $\approx 65.8$ weighted grants)
- **OT2018:** 4.8% ($n = 1{,}529$, $\approx 73.4$ weighted grants)
- **OT2017:** 4.9% ($n = 1{,}649$, $\approx 80.8$ weighted grants)

Pooling across OT2017–OT2025 yields $\approx 659.4$ weighted grants over $n = 12{,}913$ weighted resolved petitions, or **5.11% (~5.1%)**.

As cross-checks from `metrics/statpack.md`:
- **Terminal `baseline` band rate (all Terms):** 1.2% grant family (`granted` 0.8% + `gvr` 0.4%, `denied` 97.5%, `dismissed` 1.3%, $n = 9{,}936$ resolved).
- **Originating circuit (`ca5`, modern discretionary-cert petitions):** 3.8% grant family (`granted` 1.7% + `gvr` 2.1%, `denied` 94.6%, `dismissed` 1.6%, $n = 5{,}399$ resolved).
- **Relist count (`paid scored segment`):** Terminal `relist_bucket = 0` is 1.8% (`granted` 1.3% + `gvr` 0.5%, $n = 10{,}203$ resolved); terminal `relist_bucket = 1`—which includes petitions redistributed once after a response is requested—is 13.7% (`granted` 8.5% + `gvr` 5.2%, $n = 2{,}538$ resolved), though that bucket pools genuine post-conference relists with pre-consideration redistributions.
- **Amicus count (`paid scored segment`):** Terminal `cert_amicus = 0` is 3.8% (`granted` 2.0% + `gvr` 1.8%, $n = 11{,}109$ resolved).
- **CVSG status (`paid scored segment`):** `none` is 6.4% (`granted` 4.1% + `gvr` 2.3%, $n = 13{,}556$ resolved).

## 3. Case-Specific Adjustments from the Provisioned Record

We read `record/snapshots/2026-08-13.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, and the full text of `record/documents/petition.txt` (including Appendices A–D: the Fifth Circuit's January 9, 2026 unpublished opinion, the Northern District of Texas's December 5, 2024 order, the Fifth Circuit's March 5, 2026 denial of rehearing en banc, and 7 P.S. § 6203(A)). Because the snapshot stops on the day after the August 12, 2026 call for a response, no brief in opposition is on the record yet, and we make no inference about what Respondent will argue beyond what appears in the lower-court opinions and petition.

### Upward Factors
1. **Call for a Response (`Response Requested`):** After Respondent waived a response on August 6, 2026, the Court requested a response on August 12, 2026 (due September 11, 2026). This confirms that at least one chamber flagged the petition for briefing rather than letting it be denied on a waiver at the September 28, 2026 Long Conference.
2. **Sophisticated Supreme Court Advocacy and Clean Framing:** The petition is filed by experienced Supreme Court counsel (Misha Tseytlin of Troutman Pepper Locke LLP) and frames a single legal question around *Younger v. Harris*, 401 U.S. 37 (1971), *NOPSI*, 491 U.S. 350, 365 (1989), and *Sprint Communications, Inc. v. Jacobs*, 571 U.S. 69 (2013), linking the abstention issue to interstate extraterritoriality concerns.

### Downward Factors (Outweighing the CFR)
1. **Unpublished Per Curiam Decision Below:** The Fifth Circuit's opinion (`App. 1a–7a`, *TMX Finance Corporate Services, Inc. v. Spicher*, No. 24-11087, 2026 WL 74504) is a short, unpublished per curiam disposition under 5th Cir. R. 47.5 that establishes no circuit precedent, and no active judge requested an en banc poll (`App. 17a–18a`).
2. **Weak and Stale Alleged Circuit Split:** Petitioner contends (`Pet. 19–25`) that the Third, Fifth, and Seventh Circuits (*PDX North, Inc. v. Commissioner New Jersey Department of Labor & Workforce Development*, 978 F.3d 871 (3d Cir. 2020); *Stroman Realty, Inc. v. Martinez*, 505 F.3d 658 (7th Cir. 2007); and the unpublished TitleMax rulings) conflict with the Fourth and Tenth Circuits (*Harper v. Public Service Commission of West Virginia*, 396 F.3d 348 (4th Cir. 2005); *Life Partners, Inc. v. Morrison*, 484 F.3d 284 (4th Cir. 2007); *Seneca-Cayuga Tribe of Oklahoma v. Oklahoma ex rel. Thompson*, 874 F.2d 709 (10th Cir. 1989)) on how to evaluate an "important state interest" under *NOPSI*. However:
   - *Seneca-Cayuga* (1989) turned on exclusive federal primacy over Indian gaming on tribal land under the Indian Gaming Regulatory Act.
   - *Harper* (2005) and *Life Partners* (2007) are two-decade-old decisions predating *Sprint* (2013), and notably, when another TitleMax affiliate filed an identical lawsuit in a district court within the Fourth Circuit (*TitleMax of South Carolina, Inc. v. Spicher*, No. 4:24-cv-04399, 2025 WL 2378121 (D.S.C. Aug. 15, 2025)), that court *also* dismissed on *Younger* grounds (`Pet. 11 n.3`).
   - Doctrinally, *NOPSI* explicitly admonished that courts "do not look narrowly to [the State's] interest in the outcome of the particular case," which would require adjudicating the merits of the federal plaintiff's constitutional challenge to decide whether to abstain, but instead look to "the importance of the generic proceedings to the State." 491 U.S. at 365. Petitioner's contention that Pennsylvania lacks an important state interest because Petitioner is an out-of-state back-office company and the loans were made in other States effectively collapses the merits of its Due Process and dormant Commerce Clause defenses into the *Middlesex*/*NOPSI* state-interest prong.
3. **Inferior Vehicle Relative to Companion Litigation (*TitleMax of Virginia*, No. 25-1359) and Absence of Amici:** Following the Pennsylvania Department of Banking and Securities' June 2024 Order to Show Cause, six TitleMax-affiliated entities filed parallel federal lawsuits across six districts (`App. 2a`, `Pet. 10–11 n.3`). Four of those cases—involving the actual operating title-lending entities—were transferred to the Middle District of Pennsylvania and affirmed by the Third Circuit in *TitleMax of Virginia, Inc. v. Spicher*, No. 25-1137, 2026 WL 49584 (3d Cir. Jan. 7, 2026), where a certiorari petition was filed earlier (`No. 25-1359`, filed June 8, 2026). Even if the Court were inclined to review the *Younger* question arising out of this Pennsylvania administrative proceeding, *TitleMax of Virginia* (from the Third Circuit, encompassing Pennsylvania and the lending entities themselves) is the primary vehicle, whereas this Texas collateral suit by a back-office affiliate—where the district court left unresolved threshold questions of personal jurisdiction over the Pennsylvania Secretary and venue transfer (`App. 8a, 16a n.1`)—is a secondary vehicle. Moreover, zero amicus briefs have been filed in support of the petition as of the cutoff date, and the Court previously denied certiorari at the subpoena enforcement stage of the same dispute (*TitleMax of Delaware, Inc. v. Vague*, No. 21-1262; `Pet. 8`).
4. **Low Likelihood of a *Suncor* Hold/GVR:** While the petition references *Suncor Energy (U.S.A.) Inc. v. County Commissioners of Boulder County*, No. 25-170 (`Pet. 1, 17–18, 26`), *Suncor* concerns federal preemption/constitutional limits on state tort claims over interstate emissions, not *Younger* abstention.

Balancing the modest positive signal of the call for a response against the unpublished per curiam opinion below, the weak circuit split, the zero-amicus record, and the secondary vehicle status alongside No. 25-1359, we adjust slightly downward from the 5.1% `baseline` band `reached` base rate to **P(grant) = 0.045 (4.5%)**.

## 4. Secondary Claims, Big-Case Score, and Order-Writers

- **`relist-increment` (0.97):** Because the August 12, 2026 call for a response sets a September 11, 2026 response deadline, the petition is virtually certain to be distributed at least once more after the response is filed (save for a ~3% chance of settlement/Rule 46 dismissal prior to redistribution).
- **`cvsg-increment` (0.01):** Pure state administrative/abstention dispute with no federal interest; well below the 1.27% paid-segment CVSG base rate.
- **`summary-disposition-route` (0.25):** Conditional on a grant, plenary review is 75% likely and GVR is 25% likely (primarily if held behind a grant in *TitleMax of Virginia*, No. 25-1359).
- **`dissent-from-denial` (0.02) and `order-writers`:** Separate writings on denial are rare (~2% here), weighted highest toward Justices Thomas (`0.008`) and Gorsuch (`0.007`) given their prior writings on personal jurisdiction, federalism, and abstention.
- **`big_case_score` (0.38):** If decided on the merits, a ruling clarifying the interplay between *NOPSI*'s "generic" state-interest test and cross-border state regulatory enforcement would have meaningful practical consequences for interstate commerce and administrative enforcement litigation, though it remains a procedural abstention issue rather than a major substantive constitutional landmark.

## 5. Retrieval and Tooling Notes

We queried corpus priors using `uv run fedcourts query` (filtered by `--court scotus --decided-before 2026 --era 2020s` and `--court scotus --disposition granted --decided-before 2026-08-13`, plus a `--citation "571 U.S. 69"` check). We also attempted one CourtListener MCP `search` call for *Harper v. Public Service Commission*, which returned HTTP 429 (rate limit exceeded); per the prompt instructions, we degraded gracefully and relied on the detailed discussion of the precedent in the provisioned petition and appendices plus the corpus tooling.
