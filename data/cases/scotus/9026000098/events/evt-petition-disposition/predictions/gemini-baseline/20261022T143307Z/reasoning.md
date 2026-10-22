# Certiorari Rationale: *Public Interest Legal Foundation, Inc. v. Scott T. Nago* (No. 26-98)

## I. Summary of Forecast

- **Predicted Disposition:** `denied` (`granted: 0`)
- **Grant Probability (`probability` / `disposition`):** `0.015` (1.5%)
- **Declared Claims (`cert-v2`):**
  - `disposition`: `0.015`
  - `relist-increment`: `0.08`
  - `cvsg-increment`: `0.005`
  - `summary-disposition-route`: `0.10`
  - `dissent-from-denial`: `0.03`
- **Big Case Score:** `0.45`

## II. Base-Rate Anchoring (`metrics/statpack.md`)

From `record/context.json`, this cell is in `forward` mode for Term `2026`, with `band: "baseline"` under `salience_version: "sal-v4"`, `signals_observable: true`, `distribution_count: 1`, `cvsg_date: null`, and `input_snapshot: "2026-10-22.json"`.

1. **Salience Band Anchor (`sal-v4`, strictly prior Terms 2017–2025):**
   In `metrics/statpack.md` ("Segment base rate by salience band (sal-v4)"), pooling the `baseline` column across the 9 Terms strictly preceding OT 2026 (2017–2025):
   - **Risk-set (`reached`) rate** (the evaluator's baseline for a cell carrying a frozen prediction-time band): `605.7 / 12,723 = 4.76%` (ranging from `3.9%` in OT 2025 to `5.9%` in OT 2023).
   - **Terminal (`baseline`) rate** (for petitions that *end* in the `baseline` band without relisting into `elevated` or `high`): `115.6 / 9,960 = 1.16%` (and `0.9%` in OT 2025).
2. **Signal Cuts (`metrics/statpack.md`):**
   - **Relist Count Cut (paid scored segment):** For `relist_bucket = 0` (single conference distribution), the resolved base rate is `97.0% denied`, `1.2% granted`, `0.5% gvr`, `1.2% dismissed` (`1.7%` grant family).
   - **Originating Circuit (`ca9`):** Modern discretionary-cert petitions from the Ninth Circuit have an overall resolved base rate of `94.9% denied`, `2.1% granted`, `1.1% gvr` (`3.2%` grant family).
3. **Conditioning on the Waiver / No-CFR Posture Within `baseline`:**
   The `baseline` band's `4.76%` risk-set rate pools all private paid petitions at their first distribution—both those where a Brief in Opposition (BIO) was filed (or a Call for a Response was issued prior to distribution) and those distributed solely on a respondent's waiver of the right to respond. Because the Court almost never grants plenary review or summarily reverses without first calling for a response when the respondent has waived, a petition distributed on a waiver (`distribution_count: 1`, no BIO, no CFR) can only be granted if the Court first calls for a response (which triggers a relist after the BIO arrives) and subsequently grants review. Thus, the effective grant rate for a waiver-posture `baseline` petition at first distribution sits well below the `4.76%` risk-set average and closer to the `~1.0–1.5%` range.

## III. Case-Specific Analysis of the Provisioned Record and Prior Litigation

I read the provisioned snapshot (`2026-10-22.json`), `questions-presented.txt`, and `petition.txt` (which includes the Ninth Circuit's April 28, 2026 opinion at Pet. App. 1a–45a and the District of Hawaii's orders at Pet. App. 46a–68a). No Brief in Opposition was filed because Respondent Scott T. Nago filed a waiver on September 24, 2026.

### 1. Question 1: Post-*TransUnion* Article III Informational Standing Under the NVRA
Petitioner's first question asks whether a plaintiff denied public records under the NVRA's public disclosure provision, 52 U.S.C. § 20507(i)(1), suffers an informational injury in fact under *FEC v. Akins*, 524 U.S. 11 (1998), and *Public Citizen v. U.S. Department of Justice*, 491 U.S. 440 (1989), or must instead demonstrate specific "downstream consequences" tied to increasing voter registration and participation as required after *TransUnion LLC v. Ramirez*, 594 U.S. 413 (2021).

- **The Split:** Below, the Ninth Circuit (Pet. App. 20a–30a) expressly adopted the Third Circuit's test from *Public Interest Legal Foundation v. Secretary of the Commonwealth of Pennsylvania*, 136 F.4th 456 (3d Cir. 2025), holding that the NVRA is not a pure "sunshine law" and that a requester must show downstream adverse effects matching the NVRA's statutory goal of increasing voter participation. By contrast, the Fourth Circuit (*PILF v. Knapp*, 2025 WL 2945421 (4th Cir. Oct. 17, 2025)) and Tenth Circuit (*Voter Reference Foundation, LLC v. Torrez*, 160 F.4th 1068, 1078–83 (10th Cir. 2025)) held that election-watchdog nonprofits suffer a classic *Akins*/*Public Citizen* informational injury when denied voter registration records under § 20507(i)(1) because the denial prevents them from auditing voter rolls and educating the public.
- **Why Certiorari Is Unlikely on QP 1:**
  1. **Recent Cert Denial in the Lead Third Circuit Case:** On March 2, 2026, the Supreme Court denied PILF's certiorari petition in *Public Interest Legal Foundation v. Secretary of the Commonwealth of Pennsylvania*, No. 25-379, 2026 WL 568366, which challenged the very Third Circuit opinion that the Ninth Circuit followed here.
  2. **Severe Vehicle / Ripeness Defect Below:** As the Ninth Circuit emphasized (Pet. App. 20a–22a), PILF **never actually submitted an application** for voter registration data to any Hawaii county clerk (the officials who maintained and dispensed the files under state law), and thus never had a request denied. Instead, PILF wrote to the State Chief Election Officer and refused to apply because it objected to Hawaii's statutory restrictions on how voter data may be used. That independent, self-inflicted failure to apply makes this case a significantly worse vehicle for addressing pure informational standing than *Secretary of the Commonwealth*, which the Court already declined to hear.

### 2. Question 2: Whether Statewide Voter Registration Lists Fall Within 52 U.S.C. § 20507(i)(1)
On Count III (conflict/obstacle preemption of Hawaii's use and internet-publication restrictions), the Ninth Circuit found pre-enforcement standing under *Driehaus* and reached the statutory merits (Pet. App. 30a–45a). It held that a State's current statewide voter registration list is **not** a "record[] concerning the implementation of programs and activities conducted for the purpose of ensuring the accuracy and currency of official lists of eligible voters" under 52 U.S.C. § 20507(i)(1), reasoning that the voter list itself is the *object* of list-maintenance activities rather than a record concerning their implementation, and that a contrary reading would render § 20507(i)(2) superfluous and ignore the later enactment of HAVA (52 U.S.C. § 21083(a)).

- **The Split:** This holding aligns the Ninth Circuit with the Seventh Circuit (*Wisconsin Voter Alliance v. Secord*, No. 25-1102, 2026 WL 1844225 (7th Cir. July 1, 2026) (Easterbrook, J.)) against the First Circuit (*PILF v. Bellows*, 92 F.4th 36 (1st Cir. 2024)), Fourth Circuit (*Project Vote/Voting for America, Inc. v. Long*, 682 F.3d 331 (4th Cir. 2012); *PILF v. Knapp*, 2025 WL 2945421), Sixth Circuit (*United States v. Benson*, No. 26-1225, 2026 WL 1502579 (6th Cir. May 27, 2026)), and Tenth Circuit (*Voter Reference Foundation v. Torrez*, 160 F.4th 1068 (10th Cir. 2025)).
- **Why Certiorari Is Unlikely on QP 2 in This Case:**
  1. **Vehicle Entanglement with Threshold Standing:** Because the Ninth Circuit held PILF lacked standing on Counts I and II (the direct NVRA access claims) and only reached § 20507(i)(1) via Count III (whether the NVRA preempts Hawaii's restrictions on sharing data PILF has never applied for or obtained), Respondent would strongly argue that PILF lacks standing on Count III as well, or that the case is an awkward vehicle compared to direct enforcement suits. Indeed, the Department of Justice is actively litigating § 20507(i)(1)'s scope in cases like *United States v. Benson* (6th Cir.) and *United States v. Weber* (9th Cir.), which have no private-standing defects.
  2. **Prior Cert Denials in Related NVRA Cases:** In addition to denying *PILF v. Secretary of the Commonwealth* (No. 25-379), the Court on March 2, 2026 also denied PILF's petition in *Public Interest Legal Foundation v. Benson* (No. 25-437).
  3. **Absence of Any Docket Signals:** No amicus briefs were filed supporting PILF, Hawaii waived its response, and the Court distributed the petition on October 21, 2026 without calling for a response.

## IV. Calibration of Claims and Big Case Score

- **`probability` / `disposition` (`0.015`):** Starting from the `sal-v4` `baseline` risk-set anchor of `4.76%` (and terminal `baseline` rate of `1.16%`), I adjust downward for the waiver/no-CFR posture, the absence of amicus support, the threshold standing/application defect on Counts I and II, and the Court's March 2026 denials in Nos. 25-379 and 25-437, while retaining a `1.5%` tail probability (`0.015`) because the 4–2 circuit split on Question 2 (deepened by the Ninth Circuit here and the Seventh Circuit in *Secord*) could prompt a Justice to call for a response at conference and eventually grant.
- **`relist-increment` (`0.08`):** Because the petition is in a waiver posture, any Justice interested in taking a closer look at the circuit split would ask the Clerk to call for a response from Hawaii, which would result in a subsequent distribution (`relist-increment`) once the BIO is filed. Given the genuine circuit split on § 20507(i)(1), I estimate an `8%` (`0.08`) probability that the Court calls for a response or otherwise relists the petition past its first conference.
- **`cvsg-increment` (`0.005`):** A CVSG is exceedingly unlikely (`0.5%`) on a private petition in a waiver posture where the Court already declined review in Nos. 25-379 and 25-437 without seeking the Solicitor General's views.
- **`summary-disposition-route` (`0.10`):** Conditional on a grant, the Court would almost certainly set the case for plenary briefing and oral argument (`90%`) to resolve the multi-circuit conflicts on informational standing and NVRA disclosure rather than issuing a summary reversal or GVR (`10%`).
- **`dissent-from-denial` (`0.03`):** Conditional on a denial, there is a small (`3%`) chance that a Justice (such as Justice Thomas or Justice Alito) writes a brief statement or dissent from denial noting the split over *TransUnion* informational injury or § 20507(i)(1), though none wrote in Nos. 25-379 or 25-437.
- **`big_case_score` (`0.45`):** Decoupled from grant likelihood, a merits decision resolving whether the NVRA requires public disclosure of statewide voter registration rolls and clarifying post-*TransUnion* informational standing for election-watchdog organizations would have substantial nationwide significance for state election administration, voter privacy, and public-records litigation (`0.45`).
