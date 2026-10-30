# Reasoning: *Novartis Pharmaceuticals Corporation v. Lynn Fitch, Attorney General of Mississippi* (No. 26-457)

**Event:** `evt-order-call-for-response-disposition` (`moment: response-requested`, `stage: cert`)  
**Snapshot:** `2026-10-27.json`  
**Predicted Disposition:** `denied` (`granted: 0`, `probability: 0.14`)

---

## 1. Base-Rate Anchoring & Docket Signal Calibration

This cell forecasts the disposition of the certiorari petition in *Novartis Pharmaceuticals Corporation v. Lynn Fitch, Attorney General of Mississippi*, No. 26-457, at the `response-requested` moment.

- **Conditioning State (`record/context.json` and `record/snapshots/2026-10-27.json`):**
  - `mode`: `forward`
  - `term`: `2026`
  - `band`: `baseline` (`salience_version: "sal-v4"`)
  - `distribution_count`: `1` (distributed on October 21, 2026 for the November 6, 2026 Conference)
  - `cvsg_date`: `null`
  - **Snapshot Trajectory:** Petition filed October 2, 2026 and docketed October 7, 2026. Respondent Lynn Fitch filed a waiver of right to respond on October 14, 2026. One cert-stage amicus brief (by Community Oncology Alliance, Inc.) was filed on October 19, 2026. The petition was distributed on October 21, 2026 for the November 6, 2026 Conference, and on October 27, 2026 the Court called for a response (due November 27, 2026). That same day, Petitioner's counsel (Jessica L. Ellsworth) submitted a letter (`record/documents/party-letter.txt`) asking that any 30-day extension requested by Respondent be cabined so the petition could still be considered at the January 22, 2027 Conference.

- **Statpack Base-Rate Anchor (`metrics/statpack.md`):**
  - Under the **Segment base rate by salience band (`sal-v4`)** table in `metrics/statpack.md`, we pool the bracketed `reached` rates for the `baseline` band across the nine prior Terms strictly preceding OT 2026 (OT 2017–OT 2025):
    - OT 2025: `4.0%` (`n=1314`)
    - OT 2024: `5.9%` (`n=1274`)
    - OT 2023: `5.9%` (`n=1312`)
    - OT 2022: `5.9%` (`n=1196`)
    - OT 2021: `5.7%` (`n=1500`)
    - OT 2020: `4.5%` (`n=1740`)
    - OT 2019: `4.7%` (`n=1399`)
    - OT 2018: `4.8%` (`n=1529`)
    - OT 2017: `4.9%` (`n=1649`)
    - Pooled across OT 2017–OT 2025 (`n = 12,913` weighted resolved petitions in the `baseline` risk set), the weighted `reached` grant-family rate is **~5.1%**.
  - **Cross-checks in `metrics/statpack.md`:**
    - Originating circuit (`ca5`): in the modern discretionary-cert table, Fifth Circuit petitions have a resolved base rate of `denied 94.6%, gvr 2.1%, granted 1.7%, dismissed 1.6%` (`3.8%` grant family, `n=5399`).
    - Cert amicus count (`cert_amicus = 1` as of the snapshot, with potential to reach `2+` before disposition): in the paid scored segment, petitions ending with `1` amicus brief have a `15.1%` grant-family rate (`granted 10.3%, gvr 4.8%`, `n=1162`), and `2+` amicus briefs have a `22.9%` grant-family rate (`granted 18.4%, gvr 4.5%`, `n=1449`), though those figures are marginal and heavily confounded with relists and CVSGs.
  - **Adjustment for the Call for a Response (`moment: response-requested`):**
    - A Call for a Response (CFR) after a respondent waives is the Court's first affirmative signal that at least one chambers flagged the petition rather than letting it die on the dead list at its first conference. Moreover, the CFR guarantees that once the brief in opposition is filed, the petition will be distributed a second time (`distribution_count` will rise to at least `2`, moving the petition into the `1` relist/reschedule bucket, which has a `13.7%` grant-family rate (`granted 8.5%, gvr 5.2%`, `n=2538`)).
    - Adjusting upward from the `5.1%` `baseline` reached anchor for (a) the CFR signal, (b) top Supreme Court appellate counsel (Jessica L. Ellsworth, Hogan Lovells Cadwalader) and amicus activity, and (c) the multi-state stakes of 340B contract-pharmacy litigation pushes the baseline candidate rate into the ~15–20% range.
    - However, weighing the weak circuit-split posture, the prior cert denial on the identical issue in *PhRMA v. McClain*, and the interlocutory preliminary-injunction vehicle (detailed below), I adjust back down to **`probability: 0.14`** (`P(grant) = 14%`).

---

## 2. Substantive & Vehicle Assessment (Provisioned Documents)

I reviewed the full provisioned record in `record/documents/`: `questions-presented.txt`, `petition.txt`, `appendix.txt` (containing the Fifth Circuit's published opinion at 1a–14a, the Southern District of Mississippi's opinion at 15a–37a, the Fifth Circuit's en banc denial order at 38a–39a, the statutory text of 42 U.S.C. § 256b and Miss. H.B. 728 at 40a–97a, and Novartis's complaint at 98a–141a, noting the pipeline's 10,250-character truncation note at the end of the complaint), and `party-letter.txt`.

### A. Absence of a Genuine Published Circuit Split
1. **Unanimity Among Published Appellate Decisions Upholding State Contract-Pharmacy Laws:**
   - Every federal court of appeals to issue a published, precedential decision on whether Section 340B preempts state laws prohibiting manufacturers from restricting contract-pharmacy deliveries has **upheld** the state law:
     - **Eighth Circuit:** *Pharm. Rsch. & Mfrs. of Am. v. McClain*, 95 F.4th 1136 (8th Cir. 2024), *cert. denied*, 145 S. Ct. 768 (2024) (Arkansas Act 1103); *Pharm. Rsch. & Mfrs. of Am. v. Hanaway*, 165 F.4th 1168 (8th Cir. 2026) (Missouri law).
     - **Fifth Circuit:** *Novartis Pharms. Corp. v. Fitch*, 133 F.4th 456 (5th Cir. 2025) (this case, upholding Mississippi H.B. 728); *AbbVie, Inc. v. Fitch*, 152 F.4th 619 (5th Cir. 2025) (same); *AbbVie, Inc. v. Murrill*, 155 F.4th 413 (5th Cir. 2025) (Louisiana Act 358).
     - **Seventh Circuit:** *Eli Lilly & Co. v. Rokita*, 175 F.4th 463 (7th Cir. 2026) (Indiana law).
2. **Why the Fourth Circuit's Decision in *AstraZeneca v. Morrisey* Does Not Create a Clean Split:**
   - Novartis relies on *AstraZeneca Pharms. LP v. Morrisey*, No. 24-1939, 2026 WL 1005576 (4th Cir. Apr. 14, 2026), to claim a 3-to-1 split.
   - First, *Morrisey* is an **unpublished** per curiam/panel disposition (`2026 WL 1005576`), which does not bind future Fourth Circuit panels and rarely satisfies Rule 10.
   - Second, as the Petition itself admits (Pet. 34–35), West Virginia's statute in *Morrisey* included a reporting requirement and an **explicit auditing ban** prohibiting manufacturers from requiring covered entities to submit claims data—a provision directly colliding with manufacturers' statutory audit rights in 42 U.S.C. § 256b(a)(5)(C). Mississippi's H.B. 728 contains no such reporting mandate or audit prohibition.
   - Third, on the contract-pharmacy delivery provision, the Fourth Circuit in *Morrisey* did not enter judgment holding the law preempted; it vacated the denial of a preliminary injunction and remanded for the district court to develop a factual record on how the replenishment model works.
3. **No Conflict with the Third and D.C. Circuits (*Sanofi Aventis* and *Novartis v. Johnson*):**
   - In *Sanofi Aventis U.S. LLC v. HHS*, 58 F.4th 696 (3d Cir. 2023), and *Novartis Pharms. Corp. v. Johnson*, 102 F.4th 452 (D.C. Cir. 2024), the Third and D.C. Circuits held that Section 340B is silent on delivery and therefore does not authorize *HRSA* to force manufacturers to deliver to unlimited contract pharmacies.
   - Holding that a federal statute is silent on delivery—so a federal agency lacks statutory authority to mandate delivery—is entirely consistent with holding that Congress's silence does not preempt *states* from regulating pharmacy distribution within their borders.
4. **Prior Denial of Certiorari in *PhRMA v. McClain*:**
   - The Court already denied certiorari on this exact question in *PhRMA v. McClain*, 145 S. Ct. 768 (Dec. 2024). Since then, the Fifth and Seventh Circuits have joined the Eighth Circuit in published opinions.

### B. Interlocutory Vehicle and Undeveloped Record
- Novartis filed its motion for a preliminary injunction just one day after filing its complaint, with no discovery or factual record. Both the District Court (App. 29a) and the Fifth Circuit (App. 8a) emphasized that "at this stage of the litigation," on a bare facial/preliminary-injunction record, Novartis failed to show how H.B. 728's ban on contract-pharmacy restrictions interfered with the federal 340B scheme. That interlocutory posture makes this a poor vehicle for resolving a nationwide preemption question.

---

## 3. Claims, Vote Breakdown, and Big-Case Score Rationale

- **`claims`:**
  - `disposition`: `0.14` (matches top-level `probability`).
  - `relist-increment`: `0.99` (virtual certainty that the petition is distributed at least once more after the October 27 CFR once the BIO is filed; masked in scoring on `response-requested` cells).
  - `cvsg-increment`: `0.18` (modest chance the Court invites the Solicitor General's views given HHS's administration of Section 340B, tempered by the prior denial in *McClain* and the interlocutory posture).
  - `summary-disposition-route`: `0.08` (conditional on a grant, plenary review is far likelier than a GVR or summary reversal).
  - `dissent-from-denial`: `0.07` (small chance that one or more conservative Justices write a statement respecting denial or dissent from denial).
- **`claim_distributions` (`order-writers`):**
  - Assigned low per-Justice probabilities (`Alito: 0.030`, `Thomas: 0.025`, `Gorsuch: 0.020`, `Kavanaugh: 0.020`, `Sotomayor: 0.010`, `Jackson: 0.010`, `Roberts: 0.005`, `Kagan: 0.005`, `Barrett: 0.005`), consistent with `dissent-from-denial = 0.07`.
- **`big_case_score: 0.72`:**
  - Decoupled from grant likelihood, the underlying legal question—whether states can require drug manufacturers to ship 340B-discounted drugs to unlimited contract pharmacies—carries substantial economic and healthcare stakes (`0.72`), affecting billions of dollars in pharmaceutical discounts, roughly 20 state statutes, and safety-net providers nationwide.
- **Note on Retrieval:**
  - During this session, CourtListener MCP search calls returned HTTP 429 daily rate-limit errors. Pursuant to the prompt instructions, I degraded gracefully and relied on the local corpus (`uv run fedcourts query`), the committed `metrics/statpack.md`, and the comprehensive provisioned filings in `record/documents/`.
