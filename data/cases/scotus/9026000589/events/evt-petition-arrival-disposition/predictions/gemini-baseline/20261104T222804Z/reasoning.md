# Reasoning (`scotus/9026000589`, `evt-petition-arrival-disposition`)

## Forecast Summary

- **Predicted disposition**: `granted` (`granted: 1`, `probability: 0.82`)
- **Conditioning state**: `stage: cert`, `moment: arrival`, `mode: forward`, `band: federal` (`salience_version: sal-v6`), `distribution_count: 0`, `cvsg_date: null`, `input_snapshot: 2026-11-05.json`

## Base-Rate Anchor

Per `record/context.json` and `metrics/statpack.md` (*Segment base rate by salience band (`sal-v6`, paid scored segment)*), this cell is an arrival-moment prediction for a paid federal-petitioner certiorari petition (`band: "federal"`). Because this is an OT2026 petition (`term: 2026`), the scored baseline pools the bracketed `[reached]` rates in the `federal` band across the strictly prior Terms in the 10-Term lookback window (OT2022–OT2025):

- **OT2022**: 71.4% (25 / 35 reached)
- **OT2023**: 72.3% (47 / 65 reached)
- **OT2024**: 75.9% (41 / 54 reached)
- **OT2025**: 73.5% (36 / 49 reached)
- **Pooled strictly prior anchor (`cert_anchor.rate`)**: **73.40%** (`0.7339901477832512`, 149 granted out of 203 reached federal petitions).

In addition, in the originating-circuit cut (`metrics/statpack.md`), paid scored petitions from the D.C. Circuit (`cadc`, `n = 114.6` weighted) carry a 21.8% grant-family rate (19.2% granted + 2.6% GVR)—well above the 12.1% overall paid scored segment rate. I do not use the relist-0 bucket (3.2%), which reflects petitions that *ended* without a relist rather than arrival-stage petitions with zero distributions to date.

## Case-Specific Adjustments from the Anchor (`0.734` -> `0.82`)

The provisioned record—specifically `record/snapshots/2026-11-05.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt` (including the reproduced en banc order at Pet. App. 1a–5a and the vacated panel opinion by Judge Rao at Pet. App. 5a–45a), `record/documents/decision-below.txt`, and `record/documents/lower-court-docket.txt`—supports an upward adjustment from the 73.40% federal arrival base rate to **0.82**:

1. **Extraordinary Fiscal Stakes and Institutional Salience (+ adjustment)**:
   The Solicitor General seeks review of an en banc D.C. Circuit judgment affirming a district-court preliminary injunction that prevents EPA from terminating grant agreements worth **$16 billion** (out of $20 billion awarded under the Greenhouse Gas Reduction Fund enacted in Section 60103 of the Inflation Reduction Act, 42 U.S.C. § 7434 (2024)) and compels continued disbursements from accounts held at Citibank as the government's financial agent. When the Solicitor General petitions from an en banc circuit ruling blocking a major executive action involving tens of billions of dollars in federal funds, the grant rate substantially exceeds the average federal-petitioner rate.

2. **Sharp En Banc Division, Circuit Split, and Direct Tension with Supreme Court Precedent on QP 1 (+ adjustment)**:
   After a D.C. Circuit panel (Rao, J., joined by Katsas, J.; Pillard, J., dissenting, 151 F.4th 519) vacated the preliminary injunction under the Tucker Act, 28 U.S.C. § 1491(a)(1), the en banc D.C. Circuit vacated the panel decision and issued a fractured per curiam order on August 7, 2026 (186 F.4th 160; `decision-below.txt`).
   - On Question Presented 1 (Tucker Act preclusion), the en banc court divided 7–3 (with Judges Katsas, Rao, and Walker dissenting), holding that the district court had jurisdiction over respondents' claim that terminating the grants violated Section 60103 of the IRA.
   - As the petition details (`petition.txt` at 14–28), that holding is in direct tension with the Supreme Court's stay orders in *Department of Education v. California*, 604 U.S. 650, 651 (2025) (per curiam), and *National Institutes of Health v. American Public Health Ass'n*, 145 S. Ct. 2658, 2658 (2025), and squarely implicates a circuit split with the Fourth Circuit (*Sustainability Institute v. Trump*, 2026 WL 2105660, at *5–6 (4th Cir. July 24, 2026)) and the Ninth Circuit (*Thakur v. Trump*, 176 F.4th 1187, 1198–1199 (9th Cir. 2026) (per curiam), cert. petition pending, No. 26-210), versus the First Circuit (*Massachusetts v. NIH*, 170 F.4th 1, 21–24 (1st Cir. 2026)) and the en banc D.C. Circuit here.

3. **Prospective Injunction Resting on a Repealed Statute and a 5–5 En Banc Split on QP 2 (+ adjustment)**:
   While the D.C. Circuit appeal was pending, Congress enacted Section 60002 of the One Big Beautiful Bill Act (OBBBA), Pub. L. No. 119-21, 139 Stat. 72, 154 (2025), repealing 42 U.S.C. § 7434. Despite that repeal, a 6–4 en banc majority affirmed Paragraph 2 of the preliminary injunction barring EPA from giving effect to its March 2025 termination notices, and an equally divided 5–5 en banc court affirmed Paragraphs 3–6 restricting future grant terminations and ordering Citibank to continue disbursing funds. Chief Judge Srinivasan agreed with the 7–3 majority on jurisdiction, but joined Judges Katsas, Rao, and Walker in voting to vacate Paragraph 2 because the OBBBA's repeal of Section 60103 removed any ongoing statutory bar to terminating the grants. Sustaining a multi-billion-dollar prospective injunction on the basis of a repealed statute—and by an equally divided en banc court as to its operational paragraphs—provides a strong second ground for review.

4. **Countervailing Vehicle and Posture Risks (- adjustment)**:
   Two procedural considerations keep my probability at `0.82` rather than `0.90+`:
   - **Interlocutory preliminary-injunction posture**: The case arrives from an appeal of a preliminary injunction while summary-judgment proceedings remain stayed in the district court (`petition.txt` at 11 n.2).
   - **Pending full en banc opinions**: The en banc D.C. Circuit issued its dispositive per curiam order on August 7, 2026, noting that full opinions would follow later (`petition.txt` at 13; `decision-below.txt` at 1). The Solicitor General filed the certiorari petition on November 2, 2026, to meet the 90-day statutory deadline from the August 7 judgment. Although the en banc opinions will almost certainly be issued and filed in a supplemental appendix before the Court acts on the petition, there is a modest chance that the forthcoming opinions, district-court developments, or action on related petitions (such as *Trump v. Thakur*, No. 26-210, distributed for the November 13, 2026 conference) complicate the vehicle or delay disposition.

## Secondary Claims and Order-Writers Calibration

- **`relist-increment` (`0.98`)**: Because `distribution_count` is currently `0` at the `arrival` moment, this claim measures the probability that the petition is distributed for conference at least once. Barring an unexpected pre-distribution Rule 46 dismissal or withdrawal (~2%), the petition will be distributed for conference once briefing concludes.
- **`cvsg-increment` (`0.01`)**: Because the Solicitor General represents the petitioners, a CVSG is practically impossible.
- **`summary-disposition-route` (`0.12`)**: Conditional on a grant, the Court will most likely set this $16 billion dispute for plenary briefing and oral argument (`0.88`). However, there is a `0.12` conditional probability of summary action in the cert order (such as a GVR once the full en banc opinions issue or in light of a companion decision, or a partial summary vacatur based on the OBBBA repeal).
- **`dissent-from-denial` (`0.35`) and `order-writers`**: Conditional on a denial (`0.18`), the probability of a separate writing is high (`0.35`) because four D.C. Circuit judges dissented on the OBBBA repeal, three dissented on Tucker Act jurisdiction, and five Justices previously voted to stay grant injunctions in *California* and *NIH*. Unconditional `order-writers` probabilities are concentrated on Justices Alito (`0.04`), Thomas (`0.04`), and Gorsuch (`0.03`), with smaller probabilities (`0.01`–`0.02`) across the remaining Justices.
