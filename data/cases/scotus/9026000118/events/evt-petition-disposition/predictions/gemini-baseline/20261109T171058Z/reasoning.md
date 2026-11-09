# Prediction Rationale: *Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.* (No. 26-118)

## 1. Summary of Numbers

- **Headline call:** `granted = 1`, `probability = 0.80`, `predicted_disposition = "gvr"`
- **Declared claims (`cert-v3`):**
  - `disposition`: `0.80` (comprising `P(gvr) = 0.44`, `P(granted [probable jurisdiction noted]) = 0.30`, and `P(summary-reversal) = 0.06`, against `P(dismissed) = 0.17` and `P(denied) = 0.03`)
  - `relist-increment`: `0.35`
  - `cvsg-increment`: `0.01`
  - `summary-disposition-route`: `0.625` (`0.50 / 0.80` conditional on grant)
  - `dissent-from-denial`: `0.15`
- **Big-case score:** `0.85`

---

## 2. Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)

1. **Frozen `cert_anchor` (`high` band, `sal-v8`):**
   - `record/context.json` freezes `band = "high"`, `salience_version = "sal-v8"`, `distribution_count = 3`, `mode = "forward"`, and `cert_anchor.rate = 0.3484455958549223` (34.8% pooled risk-set grant rate across the 10 prior Terms, OT2016–OT2025).
   - In `metrics/statpack.md` (*Segment base rate by salience band (sal-v8)*), the `high` band's reached rate across OT2017–OT2025 ranges from 26.5% (OT2021, OT2023) to 49.5% (OT2017), and stands at 38.3% (`n=60`) in OT2025 and 43.2% (`n=95`) in OT2024.
2. **Signal cuts in `metrics/statpack.md`:**
   - **Relist count (`Cert petitions by relist count (paid scored segment)`):** With `distribution_count = 3` (two relists after the initial Oct. 16, 2026 conference), this case sits in the `relist_bucket = 2` tier (`n=495` resolved), where the grant-family rate is **41.2%** (`granted 28.3% + gvr 12.9%`, with `denied 57.4%` and `dismissed 1.4%`).
   - **CVSG and Amicus counts:** No CVSG has been issued (`cvsg = none`), and no cert-stage amicus briefs appear on the docket (`cert_amicus = 0`), which is typical for a fast-moving direct appeal following an emergency stay where amici already filed at the stay stage (`Nos. 25A1314 & 25A1315`).
   - **Note on `granted` / `gvr` binary scoring:** As documented in `schemas/prediction.schema.json` and `metrics/statpack.md`, both `granted` (noting probable jurisdiction) and `gvr` (vacating and remanding, including a *Munsingwear* vacatur for mootness) resolve to `granted = 1` on the binary Brier axis.

---

## 3. Case-Specific Adjustments From the 34.8% Anchor to `P(grant) = 0.80`

Starting from the frozen `cert_anchor` of **0.3484** (and the 2-relist bucket rate of **0.412**), four case-specific factors warrant a substantial upward adjustment to **0.80**:

1. **Mandatory Appellate Jurisdiction Under 28 U.S.C. § 1253 (+0.20):**
   - Unlike discretionary certiorari petitions that dominate the `high` band, No. 26-118 (along with No. 26-117, *Allen v. Milligan*) is a direct appeal as of right from a three-judge district court order granting an interlocutory injunction against a state congressional redistricting statute (`28 U.S.C. §§ 1253, 2284`). On a § 1253 direct appeal from an order granting an injunction that this Court has already stayed, a simple "denial" is procedurally unavailable.
2. **This Court's June 2, 2026 Stay Order (`Allen v. Milligan`, 146 S. Ct. 1377) (+0.18):**
   - On May 11, 2026, this Court vacated the three-judge court's May 8, 2025 permanent injunction in both *Allen v. Singleton* (`No. 25-273`, `disposition = "gvr"`) and *Allen v. Milligan* (`No. 25-274`, `disposition = "gvr"`) and remanded for further consideration in light of *Louisiana v. Callais*, 608 U.S. ___ (Apr. 29, 2026).
   - Just 12 days later, on May 26, 2026, the three-judge court entered a 113-page preliminary injunction (`App.1a–113a`) on the existing trial record, again enjoining Alabama's 2023 Plan for the 2026 general election.
   - On June 2, 2026 (`Nos. 25A1314 & 25A1315`), this Court (6–3) stayed the May 26, 2026 order across all three dockets (`Nos. 2:21-cv-1291, 2:21-cv-1530, and 2:21-cv-1536`) pending the filing and disposition of the jurisdictional statements in *Milligan* and *Singleton* and the cert petition in *Caster*. Justice Kavanaugh (joined by the Chief Justice and Justice Alito) concurred on *Purcell* grounds, while Justice Thomas (joined by Justice Gorsuch) concurred on both *Purcell* and the merits under *Callais*. Having stayed the May 26, 2026 preliminary injunction 6–3, the Court will not leave that order intact below.
3. **Interlocutory Mootness After the November 3, 2026 General Election Points Strongly to *Munsingwear* Vacatur (`gvr`) or Plenary/Summary Intervention (+0.07):**
   - By its express terms (`App.111a–112a`), the May 26, 2026 preliminary injunction granted relief **solely for the 2026 general election** and denied preliminary relief for later elections, while permanent-injunction proceedings for the 2028 and 2030 elections remain pending in the district court (stayed by the three-judge panel on July 20, 2026 pending these appeals, see `Milligan Doc. 544`, RECAP ID `492999516`).
   - Because of this Court's June 2, 2026 stay, Alabama held its November 3, 2026 general election under the enacted 2023 Plan. Notably, the Court did not act at the October 16, 2026 pre-election conference; instead, it held all three cases (`26-116`, `26-117`, `26-118`) past Election Day to the November 6 and November 13, 2026 conferences.
   - Under *United States v. Munsingwear, Inc.*, 340 U.S. 36 (1950), when a preliminary injunction governing a specific election becomes moot on appeal after being stayed by this Court, the standard disposition is to **vacate the order below and remand** (`disposition = "gvr"`, which scores as `granted = 1`). Alternatively, if the Court treats the dispute as capable of repetition yet evading review because the 2028/2030 permanent-injunction proceedings turn on the same trial record, it will either note probable jurisdiction (`granted`) or summarily reverse (`summary-reversal`)—all of which resolve to `granted = 1`.

---

## 4. Key Uncertainties and Downward Discount (-0.15 from near-certainty to 0.80)

Why is `P(grant)` **0.80** rather than **0.95** in No. 26-118 specifically?

1. **Appellees' September 18, 2026 Motion to Dismiss in *Singleton*:**
   - The docket snapshot (`2026-11-09.json`) shows that on September 18, 2026, Appellees Bobby Singleton, et al. filed a standalone **Motion to Dismiss** (not a Motion to Dismiss or Affirm), and Appellants filed a Response on September 29, 2026. Neither filing was provisioned in `record/documents/` (noted in `flags.json` and `tooling.json`), so their exact text could not be read directly.
   - However, from the provisioned Appendix (`App.111a`, `App.580a`) and the N.D. Ala. RECAP docket (`Singleton Doc. 357`, `recap_document_id=480176543`), the basis for the *Singleton* Appellees' motion is clear: in both the May 8, 2025 Final Judgment and the May 26, 2026 Preliminary Injunction, the three-judge court **expressly reserved ruling on the *Singleton* Plaintiffs' Fourteenth Amendment constitutional claims** (`App.111a`) and rested its injunction solely on the *Milligan* and *Caster* Plaintiffs' VRA § 2 claims. Moreover, once the 2026 election cycle progressed under the June 2, 2026 stay, the 2026-only preliminary injunction could no longer operate.
2. **Why Dismissal Without Vacatur Remains the Minority Outcome (~0.20):**
   - Despite that procedural wrinkle, the May 26, 2026 Preliminary Injunction was entered on the consolidated caption of all three cases (`Singleton Doc. 363`, `Milligan Doc. 537`, `Caster Doc. 443`) and granted the *Singleton* Plaintiffs' own May 15, 2026 Motion for a Preliminary Injunction (`Singleton Doc. 357`).
   - Crucially, in Round 2 (`No. 25-273` *Allen v. Singleton* and `No. 25-274` *Allen v. Milligan*, decided May 11, 2026) and in the stay applications (`Nos. 25A1314 & 25A1315`, decided June 2, 2026), *Singleton* stood in the exact same posture, and this Court entered identical dispositions in both *Singleton* and *Milligan* (`gvr` on May 11, 2026; `granted` on June 2, 2026). All three current cases (`26-116`, `26-117`, `26-118`) have been relisted in lockstep across all three conferences. I therefore assign a **0.80** probability that No. 26-118 receives a grant-family disposition (`0.44 gvr + 0.30 granted + 0.06 summary-reversal`) and a **0.20** probability that the Court grants Appellees' motion to dismiss (`0.17 dismissed + 0.03 denied`) while acting on *Milligan* (`No. 26-117`).
