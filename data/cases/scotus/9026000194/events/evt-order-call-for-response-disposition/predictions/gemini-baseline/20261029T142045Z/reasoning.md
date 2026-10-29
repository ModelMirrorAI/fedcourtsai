# Reasoning: *Mei Guo, et al. v. Luc A. Despins, Chapter 11 Trustee* (No. 26-194)

**Event:** `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`)  
**Input Snapshot:** `2026-08-21.json`  
**Predicted Disposition:** `denied` (`granted: 0`, `probability: 0.14`)

---

## 1. Procedural Posture and Base-Rate Anchoring at `moment: response-requested`

This forecast evaluates the disposition of the certiorari petition in *Mei Guo, et al. v. Luc A. Despins, Chapter 11 Trustee*, No. 26-194, conditioned on the provisioned snapshot `2026-08-21.json` and `record/context.json` (`cutoff: "2026-08-21"`, `cut_kind: "date"`, `mode: "forward"`).

### Docket State as of `2026-08-21`
- **August 11, 2026:** Petition for a writ of certiorari filed by Mei Guo and HK International Funds Investments (USA) Limited, LLC ("HK USA").
- **August 14, 2026:** Docketed as No. 26-194 (paid petition from the Second Circuit, `sJsonCaseType: "Paid"`).
- **August 17, 2026:** Respondent Luc A. Despins, Chapter 11 Trustee for the estate of Ho Wan Kwok, filed a waiver of the right to respond.
- **August 19, 2026:** Distributed for the September 28, 2026 Long Conference (`distribution_count: 1`).
- **August 20, 2026:** Response requested by the Court, due September 21, 2026.

At this cutoff, only `petition.txt` and `questions-presented.txt` are provisioned in `record/documents/` (`ocr_derived: false`, `empty_text: false`, `truncated: false`); no brief in opposition or amicus brief had been filed as of August 21, 2026.

### Statpack Base Rates (`metrics/statpack.md`)
1. **Salience Band Anchor (`band: "baseline"`, `salience_version: "sal-v4"`):**
   In `record/context.json`, the frozen salience band at the cutoff is `baseline` under `sal-v4` (`distribution_count: 1`, `cvsg_date: null`). In `metrics/statpack.md` ("Segment base rate by salience band (`sal-v4`)"), pooling the bracketed `reached` figures for `baseline` across the nine strictly prior Terms (OT2017–OT2025):
   - OT2025: 4.0% (n=1,314) → ~52.6 grants
   - OT2024: 5.9% (n=1,274) → ~75.2 grants
   - OT2023: 5.9% (n=1,312) → ~77.4 grants
   - OT2022: 5.9% (n=1,196) → ~70.6 grants
   - OT2021: 5.7% (n=1,500) → ~85.5 grants
   - OT2020: 4.5% (n=1,740) → ~78.3 grants
   - OT2019: 4.7% (n=1,399) → ~65.8 grants
   - OT2018: 4.8% (n=1,529) → ~73.4 grants
   - OT2017: 4.9% (n=1,649) → ~80.8 grants
   - **Pooled strictly-prior `baseline` [reached] rate (OT2017–OT2025):** ~659.5 / 12,913 = **5.11%**.
2. **Originating Circuit and Amicus Cuts:**
   - **Second Circuit (`ca2`):** In "Modern cert petitions by originating circuit", `ca2` has 2,070 resolved cases with `granted 2.7%` and `gvr 2.4%` (5.1% total grant family).
   - **Amicus Count:** As of the August 21, 2026 snapshot, 0 amicus briefs had been filed (in the terminal paid scored segment, `cert_amicus = 0` has `granted 2.0%`, `gvr 1.8%`, `n=11,109`). In `forward` mode, `fedcourts query --court scotus --docket-number 26-194 --include-open --full` discloses that one amicus brief (by the Official Committee of Unsecured Creditors in the Chapter 11 Case of Vanderbilt Minerals, LLC, represented by Jeffrey Alan Lamken) later appeared on the docket. In the paid scored segment, `cert_amicus = 1` (n=1,162) carries a 15.1% grant-family rate (`granted 10.3%`, `gvr 4.8%`).
3. **Adjustment for the Call for Response (`moment: response-requested`):**
   Because the Court issued a Call for Response on August 20, 2026—just one day after initial distribution following Respondent's waiver—the petition has cleared the initial screen where ~80–85% of `baseline` paid petitions are summarily denied on a waiver or first conference. Once the response arrives and the petition is redistributed, it will enter the `elevated` salience band (`relist_bucket >= 1`), where the prior-Term `reached` grant rate in `statpack.md` averages **~17.1%** (and terminal `relist_bucket = 1` is 13.7% grant family: `granted 8.5%`, `gvr 5.2%`, `n=2,538`). Thus, conditioning on the CFR plus the appearance of a single high-profile amicus brief places the structural prior before case-specific vehicle adjustments around **14–16%**.

---

## 2. Case-Specific Assessment: Legal Split vs. Vehicle Flaws

### Upward Factors (Circuit Split & Statutory Question)
The Petition (`petition.txt`) and Questions Presented (`questions-presented.txt`) raise a sharp, recurring question of Bankruptcy Code interpretation:
> "Whether 11 U.S.C. § 544(a) authorizes a bankruptcy trustee to prosecute a state-law alter ego claim merely because it belongs to creditors of the bankruptcy estate generally."

- **Real Circuit Split:** As documented in `petition.txt`, the circuits have long divided over how *Caplin v. Marine Midland Grace Trust Co.*, 406 U.S. 416 (1972), and Congress's deletion of proposed § 544(c) in the 1978 Bankruptcy Code interact with § 544(a)'s strong-arm powers. The Eighth (*In re Ozark Restaurant Equipment Co.*, 816 F.2d 1222 (8th Cir. 1987)), Ninth (*Williams v. California 1st Bank*, 859 F.2d 664 (9th Cir. 1988); *Ahcom, Ltd. v. Smeding*, 623 F.3d 1248 (9th Cir. 2010)), Tenth (*In re Hamilton Taft & Co.*, 53 F.3d 285 (10th Cir. 1995)), and Eleventh (*E.F. Hutton & Co. v. Hadley*, 901 F.2d 979 (11th Cir. 1990)) Circuits reject reading § 544(a) as authorizing a trustee to bring general creditor causes of action (including alter ego claims that belong to creditors under state law). Conversely, the Second (*St. Paul Fire & Marine Ins. Co. v. PepsiCo, Inc.*, 884 F.2d 688 (2d Cir. 1989); *In re Kwok*, 169 F.4th 99 (2d Cir. 2026)) and Seventh (*Koch Refining v. Farmers Union Central Exchange, Inc.*, 831 F.2d 1339 (7th Cir. 1987)) Circuits allow trustees to prosecute "general" creditor alter ego claims via § 544(a).
- **Textualist Appeal & Amicus Support:** Several Justices (particularly Justices Gorsuch and Thomas) closely scrutinize non-textual expansions of bankruptcy estate power, and the amicus brief filed by Jeffrey Lamken for the Official Committee of Unsecured Creditors in *Vanderbilt Minerals* underscores that the question has real significance in mass-tort and commercial Chapter 11 cases.

### Downward Factors (Severe Vehicle & Alternative-Ground Problems)
Careful reading of the three opinions reproduced in the Petition Appendix (`petition.txt`, Pet. App. 1a–123a)—the Second Circuit's published per curiam opinion (169 F.4th 99), Judge Dooley's District Court opinion, and Chief Bankruptcy Judge Manning's summary judgment memorandum—reveals major vehicle obstacles that make a grant unlikely (`P(grant) = 0.14`):

1. **Independent Alternative Ground Under 11 U.S.C. § 541(a)(1) and Collateral Estoppel:**
   The Trustee pleaded the Second Counterclaim under **11 U.S.C. §§ 541, 542, and 544** (Pet. App. 45a, 60a). Moreover, on the First Counterclaim, the Bankruptcy Court, District Court, and Second Circuit all held that under New York collateral estoppel principles (arising from the final judgment in *PAX v. Kwok* in New York Supreme Court), the Individual Debtor (Ho Wan Kwok) was the **beneficial and equitable owner** of the *Lady May* yacht (and by consent amendment, the *Lady May II*), bringing the yachts directly into the estate as "equitable interests of the debtor in property" under **11 U.S.C. § 541(a)(1)** without needing § 544(a) at all. Furthermore, the District Court held that the Second Counterclaim was independently supported under § 541(a)(1) via insider reverse veil-piercing under Delaware law. While the Second Circuit bypassed the § 541(a)(1) insider veil-piercing question as unnecessary once it affirmed under § 544(a) as to both the *Lady May* and the $37 million in Escrowed Funds, the presence of § 541(a)(1) and the collateral estoppel ruling means that reversing on § 544(a) might not change the ultimate disposition of the assets.
2. **Interlocutory Procedural Posture:**
   As the District Court explained (Pet. App. 30a–32a), the Bankruptcy Court granted **partial** summary judgment on only the First and Second Counterclaims while **three additional counterclaims** remained pending in the adversary proceeding, and the Bankruptcy Court denied Rule 54(b) certification. The appeal reached the District Court only via discretionary leave to appeal an interlocutory order under 28 U.S.C. § 158(a)(3). The Supreme Court strongly disfavors granting certiorari in interlocutory bankruptcy appeals where alternative claims remain pending in the bankruptcy court that could moot the statutory issue.
3. **Declaratory Asset-Ownership Posture vs. Third-Party Damages (*Caplin*):**
   Unlike *Caplin* or *Ozark*, where a trustee sued third parties for money damages on causes of action belonging to creditors, here Petitioner HK USA initiated the adversary proceeding against the Trustee seeking a declaration that the *Lady May* belonged to HK USA, and the Trustee counterclaimed for a declaration that HK USA was the Debtor's alter ego and that the yacht and its $37 million stipulated cash substitute were property of the bankruptcy estate to be turned over under § 542.
4. **Unfavorable Equities:**
   The record involves severe adjudicated contempt ($134 million in state-court sanctions after the Debtor fled with the *Lady May* yacht in violation of a restraining order) and a shell LLC with no revenue, no bank account, no employees, and no business purpose other than shielding luxury yachts from creditors.

Balancing the real circuit split and amicus attention against these substantial vehicle defects, I set **`probability = 0.14`** (`disposition: 0.14`, `granted: 0`, `predicted_disposition: "denied"`).

---

## 3. Secondary Claims, Big-Case Score, and Tooling Notes

- **`relist-increment: 0.95`:** At the cutoff (`2026-08-21`), `distribution_count` is `1` (the initial August 19, 2026 distribution before the August 20 CFR). Once the response is filed, the petition will be distributed again for a subsequent conference, so `distribution_count` rising above `1` is near-certain (`0.95`), with only a small 5% allowance for pre-distribution settlement/dismissal or an administrative quirk. (As noted in `predict.md`, `relist-increment` is masked by the harness on `response-requested` cells because redistribution after the response is virtually automatic, but I state the honest forward probability.)
- **`cvsg-increment: 0.04`:** Because this is a private commercial bankruptcy dispute with major vehicle flaws and no direct federal programmatic stake, a CVSG is unlikely (`0.04`).
- **`summary-disposition-route: 0.07`:** Conditional on a grant, the Court would almost certainly set the statutory § 544(a) question for plenary briefing and argument (`0.93`) rather than summary reversal or GVR (`0.07`).
- **`dissent-from-denial: 0.025` and `order-writers`:** Conditional on denial, there is a small (`2.5%`) probability that a textualist Justice (most likely Justice Gorsuch at `0.010` or Justice Thomas at `0.008`) authors a brief dissent or statement respecting denial highlighting the circuit split over § 544(a).
- **`big_case_score: 0.25`:** If decided on the merits, a Supreme Court ruling on § 544(a) trustee standing to bring general creditor alter ego claims would be significant for Chapter 11 practice and mass-tort/commercial restructurings, but has limited broader public or constitutional salience.
- **Degraded Upstream Note:** Live CourtListener MCP search calls returned HTTP 429 (`Rate limit exceeded: 1400/day`). Following the prompt's graceful degradation rule, I relied on the complete provisioned `petition.txt` (which includes the full text of the Second Circuit, District Court, and Bankruptcy Court opinions), `questions-presented.txt`, `2026-08-21.json`, `metrics/statpack.md`, and `uv run fedcourts query`.
