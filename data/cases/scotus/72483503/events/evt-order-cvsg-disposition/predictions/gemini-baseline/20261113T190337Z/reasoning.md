# Predictor Rationale (`reasoning.md`)

## Summary of Forecast Numbers

- **`probability` / `claims["disposition"]`**: `0.38` (`granted: 0`, `predicted_disposition: "denied"`)
- **`claims["relist-increment"]`**: `0.95`
- **`claims["cvsg-increment"]`**: `0.0`
- **`claims["summary-disposition-route"]`**: `0.08` (conditional on grant)
- **`claims["dissent-from-denial"]`**: `0.09` (conditional on denial)
- **`big_case_score`**: `0.45`

---

## 1. Base-Rate Anchoring

This cell (`evt-order-cvsg-disposition`, `moment: cvsg`, `mode: forward`, `cutoff: 2025-07-01`, Term `2024`) carries a frozen salience band of `high` under `sal-v8` (`distribution_count: 2`, `cvsg_date: 2025-06-30`).

1. **Frozen Salience-Band Anchor (`cert_anchor`)**: `record/context.json` supplies the pre-computed `sal-v8` `high`-band `reached` rate pooled strictly prior to OT2024 (`lookback_terms: 10`, covering OT2017–OT2023 in `metrics/statpack.md`): **`0.3323` (33.2%)**, corresponding to roughly 205 grants across 617 weighted resolved petitions in the prior-Term `high` risk sets (ranging from 26.5% in OT2021 and OT2023 to 49.5% in OT2017). This is the exact baseline against which Brier skill is scored.
2. **Statpack CVSG Cut Cross-Check**: In `metrics/statpack.md` ("Cert petitions by CVSG status (paid scored segment)"), resolved CVSG petitions (`n=164`, with `16` open) resolve as **`denied` 62.8%, `granted` 29.3%, `gvr` 5.5%, `dismissed` 2.4%**—a combined grant-family (`granted` + `gvr`) rate of **34.8%**, vs. 6.4% (`4.1%` granted + `2.3%` gvr, `n=13,550`) for paid petitions without a CVSG.
3. **Other Marginal Cuts**: Modern paid cert petitions originating from the Sixth Circuit (`ca6`, `n=3,017`) grant at only 2.7% (`1.3%` granted + `1.4%` gvr) unconditionally, and petitions with `1` cert-stage amicus brief (`n=1,159`; Encore Fiduciary filed an amicus brief on May 21, 2025, and the SG's invited brief will bring the disposition-time count into the `2+` bucket, `n=1,446`, 22.7% grant family) sit well above the 0-amicus baseline (`n=11,109`, 3.8% grant family), though both marginal cuts are already superseded by the much stronger conditional information in the CVSG order itself.

Starting from the **33.2%–34.8%** CVSG / `high`-band anchor, case-specific upward and downward forces largely offset, leaving my final estimate modestly above the baseline at **0.38**.

---

## 2. Case-Specific Adjustments to `P(grant)`

### Upward Factors (+11 to +13 percentage points)

1. **Deepening Appellate Split Reinforced After the Petition Was Filed**:
   - Below, a divided Sixth Circuit panel (122 F.4th 205; Mathis, J., joined by Clay, J.) reversed the Rule 12(b)(6) dismissal of respondents' ERISA imprudent-retention claim concerning the Northern Trust Focus target-date funds over a thorough 43-page published dissent by Judge Murphy (Pet. App. 33a–75a). Judge Murphy argued that both the majority's threshold statement ("a meaningful benchmark ... is not required," Pet. App. 18a–19a) and its acceptance of the broad S&P target-date index without allegations matching risk profile, equity-to-bond glidepath, or passive/active composition conflicted with the Eighth and Tenth Circuits (*Meiners v. Wells Fargo & Co.*, 898 F.3d 820 (8th Cir. 2018); *Davis v. Washington Univ.*, 960 F.3d 478 (8th Cir. 2020); *Matousek v. MidAmerican Energy Co.*, 51 F.4th 274 (8th Cir. 2022); *Matney v. Barrick Gold of N. Am.*, 80 F.4th 1136 (10th Cir. 2023)).
   - Between the BIO (May 21, 2025) and Cert Reply (June 9, 2025), the Ninth Circuit decided *Anderson v. Intel Corp. Investment Policy Committee*, 137 F.4th 1015 (9th Cir. May 22, 2025) (verified via CourtListener MCP), unanimously affirming dismissal of target-date fund underperformance claims that similarly relied on S&P indices and Morningstar peer-group categories, expressly adopting the Eighth Circuit's rule that conclusory "comparable" or "peer" labels fail without allegations of similar aims, risks, and rewards.
2. **Demonstrated Court Engagement on ERISA Pleading Screening**:
   - Respondents initially waived a response (April 8, 2025), a Justice called for a response prior to the May 2 conference (April 21, 2025), and the Court issued a CVSG immediately off the first post-BIO conference (June 26 / June 30, 2025).
   - Just two months earlier in *Cunningham v. Cornell University*, 604 U.S. 693 (April 17, 2025), the unanimous opinion noted "serious concerns" about ERISA claims surviving Rule 12(b)(6) too easily, and a three-Justice concurrence (Alito, J., joined by Thomas and Kavanaugh, JJ.) underscored that surviving dismissal in ERISA litigation "is often the whole ball game because of the cost of discovery." Because § 1108 affirmative defenses could not serve as a Rule 12(b)(6) gate in *Cunningham*, § 1104(a)(1)(B) plausibility standards under *Dudenhoeffer* and *Hughes* are the natural doctrinal focal point.
3. **Administration Posture of the Invited Solicitor General**:
   - The June 30, 2025 CVSG goes to Solicitor General D. John Sauer and a Republican Department of Labor. Whereas prior Democratic SGs routinely opposed employer ERISA pleading petitions, a Republican SG/DOL is substantially likelier (~42% estimated chance) to endorse petitioners' critique of the Sixth Circuit's loose benchmark language and recommend plenary review—a recommendation the Court follows at high rates (~70%+).

### Downward Factors (-7 to -8 percentage points)

1. **Justice Alito's Recusal on the CVSG Order**:
   - The June 30, 2025 order explicitly records: *"Justice Alito took no part in the consideration of this petition."* This is a major Case-Specific headwind. First, Justice Alito authored the *Cunningham* concurrence spotlighting ERISA Rule 12(b)(6) discovery asymmetry; his recusal removes a prime grant vote while leaving the Rule-of-Four requirement intact across only **eight** Justices (50% of the participating bench). Second, both the Justices and the Office of the Solicitor General are reluctant to take a contested, recurring statutory pleading issue before an eight-Justice Court that risks a non-precedential 4–4 affirmance when non-recused ERISA 401(k) benchmark cases arise frequently across the circuits.
2. **Fact-Bound Alternative Grounds and Subsequent Intra-Circuit Narrowing**:
   - Respondents have substantial ammunition to persuade the SG (and middle-bench Justices) that the circuit split is overstated on these facts. First, even the Ninth Circuit in *Anderson* (both Judge Miller's majority and Judge Berzon's concurrence) agreed with the Sixth Circuit's abstract proposition that an empirical comparator is not required for *every* imprudence theory (e.g., direct process flaws). Second, the Sixth Circuit expressly held in the alternative that respondents *did* plead a meaningful benchmark because plan disclosures described the Focus Funds as passive index-investing funds designed to track market indices and "meet industry-recognized benchmarks"—invoking the Eighth Circuit's own index-fund distinction in *Braden v. Wal-Mart Stores, Inc.*, 588 F.3d 585, 595–96 (8th Cir. 2009)—and coupled that comparison with allegations of massive portfolio turnover ($850+ million moved out of Fidelity funds). Third, in *England v. DENSO International America Inc.*, 136 F.4th 632 (6th Cir. May 6, 2025), the Sixth Circuit subsequently cited *Parker-Hannifin* for the proposition that financial-metric imprudence claims *usually do require* a "meaningful benchmark," blunting the claim that the Sixth Circuit has abandoned comparator rigor altogether.
3. **Unappealed Share-Class Claim Proceeding Below**:
   - Petitioners declined to seek certiorari on respondents' separate imprudence claim alleging failure to negotiate lower-fee share classes for the *same* Northern Trust Focus Funds (Pet. 7 n.1; BIO 24). Even though the Sixth Circuit stayed its mandate, remand and discovery concerning petitioners' monitoring of the Focus Funds will occur regardless—a classic vehicle blemish the SG's office frequently cites to counsel denial despite reservations about the opinion below.

### Probability Synthesis

Decomposing across the SG's eventual recommendation:
- **SG recommends Grant (~0.42)** × **P(Grant | SG Grant, 8-Justice Court) (~0.72)** = `0.302`
- **SG recommends Deny (~0.55)** × **P(Grant | SG Deny, 8-Justice Court) (~0.14)** = `0.077`
- **Pre-disposition Rule 46 settlement/dismissal (~0.03)** × `0.00` = `0.000`
- **Total `P(grant)`** = `0.379` → **`0.38`** (`granted: 0`, `predicted_disposition: "denied"`).

---

## 3. Rationale for Auxiliary Claims and `big_case_score`

- **`relist-increment` (`0.95`)**: `context.json` freezes `distribution_count: 2` as of `2025-07-01`. Under Supreme Court procedure (confirmed across resolved CVSG priors in the corpus such as `24-171`, `24-345`, `23-1209`, `23-1213`, and `23-1360`), once the Solicitor General files an invited brief, the Clerk distributes the petition anew for conference (`DISTRIBUTED for Conference of ...`), incrementing `distribution_count` from `2` to at least `3`. Only a pre-distribution Rule 46 dismissal/settlement (~2.4% in the statpack CVSG cut, modestly higher at ~5% here given ongoing ERISA class-action settlement incentives) prevents at least one additional distribution.
- **`cvsg-increment` (`0.0`)**: A CVSG is already on the docket (`cvsg_date: 2025-06-30`); the harness masks this claim as vacuous on `moment: cvsg` cells, and a second CVSG is effectively zero-probability.
- **`summary-disposition-route` (`0.08`)**: Conditional on a grant, GVRs represent 15.8% (`5.5 / 34.8`) of CVSG grants in the statpack. I adjust downward to `0.08` because *Cunningham* (April 17, 2025) was already decided before the CVSG and no companion § 1104(a)(1)(B) investment-prudence case is pending on the Supreme Court's merits docket (the granted ERISA case `23-1209`, *M & K Employee Solutions*, involves multiemployer pension withdrawal-liability actuarial assumptions), leaving only a small probability of an *Amgen v. Harris*-style per curiam reversal or unforeseen intervening event.
- **`dissent-from-denial` (`0.09`) & `order-writers`**: Conditional on denial, roughly 91% of orders should be summary denials without separate opinions, particularly with Justice Alito recused (`Alito: 0.001`, non-zero only if a divestiture lifted his recusal prior to disposition). However, Justices Thomas (`0.022`) and Kavanaugh (`0.016`) both joined the *Cunningham* concurrence emphasizing ERISA Rule 12(b)(6) screening, and Justice Gorsuch (`0.010`) regularly writes or joins dissents from denial on circuit splits, creating a ~9% conditional chance of a dissent from denial or Kavanaugh statement respecting denial. Unconditional `order-writers` probabilities across all nine seated Justices sum to `0.060`, matching `P(denial) × 0.09` plus negligible separate-writing hazard on a summary disposition.
- **`big_case_score` (`0.45`)**: Scored strictly on stakes/significance if decided on the merits rather than grant odds, a decision clarifying ERISA's "meaningful benchmark" pleading rule would shape motion-to-dismiss practice across a massive wave of 401(k) excessive-fee and target-date-fund class actions affecting trillions in retirement assets—on par with *Hughes v. Northwestern* and *Cunningham v. Cornell*—while remaining a technical statutory/pleading dispute rather than a headline constitutional case.

---

## 4. Uncertainties and Where to Discount This Forecast

1. **Solicitor General Recommendation Variance**: At `moment: cvsg`, the largest single unknown is whether SG Sauer's brief prioritizes doctrinal cleanup of the Sixth Circuit's outlier phrasing (pushing `P(grant)` above 0.70) or prioritizes classic OSG vehicle objections—Alito's recusal, the surviving Focus Funds share-class claim, and the panel's passive-index/turnover alternative rationale (pushing `P(grant)` below 0.15). Because those two branches sit far apart, the pre-SG-brief expectation necessarily sits in the upper-30% range even though the post-SG-brief probability will bifurcate sharply.
2. **Unprovisioned Cert-Stage Amicus Text**: The May 21, 2025 amicus brief of Encore Fiduciary appears on the `2025-07-01` docket snapshot (`1` pre-CVSG amicus) and is cited in petitioners' reply brief (pp. 10–11), though third-party amicus briefs are not separately provisioned in `record/documents/`; its policy arguments on ERISA settlement and insurance dynamics are clear from the reply brief and do not materially alter vehicle analysis.
3. **Blinding Integrity**: I did not query this case's post-2025-07-01 docket, SG brief, or disposition in any tool, and I carry no knowledge of its post-CVSG disposition from training.
