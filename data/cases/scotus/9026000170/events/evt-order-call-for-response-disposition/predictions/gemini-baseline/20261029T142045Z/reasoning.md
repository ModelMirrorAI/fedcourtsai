# Predictor Rationale (`scotus/9026000170` — `evt-order-call-for-response-disposition`)

## 1. Snapshot, Provisioned Inputs, and Conditioning State

This prediction is formed at `moment: response-requested` (`evt-order-call-for-response-disposition`) in `forward` mode, reading the provisioned snapshot `2026-08-29.json` (`cutoff: 2026-08-29`, `cut_kind: date`, `snapshot_provenance: truncated`) and the provisioned filings in `record/documents/` (`petition.txt` and `questions-presented.txt`, as listed in `documents.json`). Because the snapshot stops on the call-for-response cutoff (August 28, 2026 entry), no brief in opposition is on the record yet, and I do not infer or retrieve what any post-cutoff response says.

From `record/context.json`, the frozen conditioning state is:
- `term`: `2026`
- `band`: `baseline` (`salience_version`: `sal-v4`)
- `distribution_count`: `1`
- `cvsg_date`: `null`
- `signals_observable`: `true`

The docket snapshot (`2026-08-29.json`) shows a paid petition from the Federal Circuit (`LowerCourtCaseNumbers: (2024-1236)`, decided April 29, 2026), filed July 28, 2026 and docketed August 6, 2026 as No. 26-170. Both respondents—the United States (represented by Solicitor General D. John Sauer, following USPTO Director John A. Squires's intervention below) and Qualcomm Incorporated (represented by Jonathan S. Franklin of Norton Rose Fulbright)—filed waivers of their right to respond on August 20 and August 21, 2026. The petition was distributed on August 26, 2026 for the September 28, 2026 conference, and on August 28, 2026 the Court requested a response (due September 28, 2026). The counsel block also lists Kenneth James Weatherwax as counsel for `Other` party `VLSI Technology LLC`, indicating at least one amicus curiae appearance on the docket.

## 2. Base-Rate Anchor from `metrics/statpack.md`

Following the prompt contract for a cert-stage cell with a frozen salience band (`band: baseline`, `salience_version: sal-v4`, `term: 2026`), I anchor on the **"Segment base rate by salience band (sal-v4)"** table's bracketed `reached` rate for `baseline`, pooled across the nine rendered Terms strictly preceding OT2026 (OT2017–OT2025):

- OT2025: 4.0% ($n = 1314$)
- OT2024: 5.9% ($n = 1274$)
- OT2023: 5.9% ($n = 1312$)
- OT2022: 5.9% ($n = 1196$)
- OT2021: 5.7% ($n = 1500$)
- OT2020: 4.5% ($n = 1740$)
- OT2019: 4.7% ($n = 1399$)
- OT2018: 4.8% ($n = 1529$)
- OT2017: 4.9% ($n = 1649$)

Weighting by the risk-set denominators across OT2017–OT2025 ($\sum n = 12,913$, estimated grants $\approx 655.6$), the pooled strictly-prior `baseline [reached]` grant rate is **5.08%** (~5.1%).

Cross-checking the marginal cuts in `metrics/statpack.md` (modern discretionary-cert petitions, paid scored segment, denial-reweighted):
- **Modern discretionary-cert petitions overall**: granted 692 (1.5%), gvr 590 (1.3%), denied 42,577 (95.1%), dismissed 918 (2.1%) over $n = 44,777$ resolved.
- **Originating circuit (`cafc`)**: granted 3.0% + gvr 1.6% = **4.6%** grant family ($n = 900$ resolved).
- **Relist count (`0` relists, i.e., 1 distribution)**: granted 1.3% + gvr 0.5% = **1.8%** ($n = 10,203$ resolved); `1` relist: granted 8.5% + gvr 5.2% = **13.7%** ($n = 2,538$ resolved).
- **Amicus-brief count**: `0` amici = 3.8% grant family ($n = 11,109$); `1` amicus = 15.1% grant family (10.3% granted + 4.8% gvr, $n = 1,162$).

## 3. Case-Specific Adjustments and `probability` = 0.12

Starting from the 5.1% `baseline [reached]` anchor, I adjust upward to **P(grant) = 0.12** (`granted = 0`, `predicted_disposition = "denied"`), balancing the affirmative signals of the call for a response and the statutory posture against the absence of a circuit split and the prospective administrative mootness of the dispute:

### Upward Factors
1. **Call for a response after mutual waivers (+4% to +5%):** Both the Solicitor General and Qualcomm waived a response, and the Court affirmatively requested one two days after the initial Long Conference distribution. While a call for a response has a low threshold (requiring only a single chamber's request) and most petitions with a called-for response are still denied once the BIO arrives, it confirms that at least one chamber flagged the petition for closer scrutiny rather than letting it die on the waiver list.
2. **Striking administrative posture and *SAS* vs. *Thryv* tension (+3% to +4%):** As recounted in the petition (`petition.txt` at 3–4, 8–9) and Footnote 5 of the Federal Circuit's precedential opinion (App. 8a n.5, 174 F.4th 910), the PTAB originally refused to adjudicate whether Roambee was an unnamed real party in interest (RPI) in Qualcomm's IPRs by relying on *SharkNinja* and *Unified Patents*—which held that the Board need not decide RPI unless it would trigger a § 315(b) time bar or § 315(e)(1) PTAB estoppel (ignoring § 315(e)(2) civil-action estoppel). While the appeal was pending (October 2025), USPTO Director John A. Squires de-designated *SharkNinja* and *Unified Patents* as precedential, notified the Federal Circuit that the Office now agrees § 312(a)(2) ("A petition ... may be considered only if ... the petition identifies all real parties in interest") requires resolving RPI disputes before considering a petition, and withdrew the Office's defense of the Board's merits approach—while still maintaining that § 314(d) bars judicial review. The framing of an agency confessing statutory error while claiming total immunity from judicial review under § 314(d), combined with amicus interest (VLSI Technology LLC), is calculated to appeal to Justices skeptical of unreviewable agency action (notably Justice Gorsuch, who authored *SAS Institute* and dissented in *Thryv*).

### Downward / Limiting Factors
1. **Prospective policy correction eliminates ongoing systemic urgency:** Because the USPTO Director has already de-designated *SharkNinja* and *Unified Patents* and reinstated mandatory RPI resolution before institution, the specific agency practice FedEx challenges has already been halted prospectively by the agency itself. The Solicitor General's BIO will predictably emphasize that the question presented has diminishing prospective importance and does not warrant this Court's plenary intervention.
2. **No circuit split and cohesive Federal Circuit precedent:** The Federal Circuit has exclusive jurisdiction over IPR appeals (28 U.S.C. § 1295(a)(4)(A)), so there is no inter-circuit conflict. Moreover, the panel decision (Hughes, Cunningham, Stark, JJ.) was unanimous and aligned with settled Federal Circuit precedent (*ESIP Series 2, LLC v. Puzhen Life USA, LLC*, 958 F.3d 1378 (Fed. Cir. 2020); *Ethanol Boosting Systems, LLC v. Ford Motor Co.*, 162 F.4th 1151 (Fed. Cir. 2025)), holding that § 312(a)(2) is a prerequisite to institution closely tied to the decision whether to initiate IPR under *Cuozzo* (which itself involved § 312(a)(3)) and *Thryv* (which involved § 315(b)).
3. **Vehicle and harmless-error headwinds:** Even if the PTAB had conducted an RPI inquiry, the PTAB's October 5, 2023 order (App. 27a–41a) made extensive factual findings that (a) Qualcomm filed its IPR petitions within Roambee's one-year § 315(b) window, (b) Qualcomm acted in good faith without gamesmanship, and (c) Qualcomm repeatedly offered post-institution to amend its mandatory notices to list Roambee as an RPI while maintaining its filing date under *Proppant*, which FedEx itself opposed because FedEx wanted outright termination of the IPRs (App. 34a–36a). Furthermore, in the very decision under review (App. 14a–16a), the Federal Circuit *vacated and remanded* the Board's obviousness determination on the '797 patent claims at issue, meaning the proceeding is already returning to the PTAB on the merits. Respondents will forcefully argue in their BIOs that FedEx's alleged § 315(e)(2) district-court estoppel injury can be adjudicated directly by the Delaware district court in the Roambee litigation (or addressed on remand) and that FedEx rejected the very mandatory-notice amendment that would have formally listed Roambee.

Netting these considerations, a 12% grant probability (`0.12`) reflects an elevated chance compared to the 5.1% `baseline [reached]` prior, while recognizing that once Qualcomm and the Solicitor General file their BIOs detailing the prospective policy change and vehicle flaws, denial remains by far the most likely outcome.

## 4. Declared Claims and `order-writers` Distribution

- **`disposition` (`0.12`):** Matches top-level `probability` exactly.
- **`relist-increment` (`0.96`):** As noted in the prompt contract, on a `response-requested` cell `relist-increment` is masked by the harness because the petition is almost certain to be distributed again once the requested responses are filed (since the August 26 distribution preceded the August 28 call for a response). I set `0.96` (allowing only a tiny 4% tail for pre-distribution Rule 46 dismissal/settlement).
- **`cvsg-increment` (`0.01`):** The United States is already a named respondent represented by the Solicitor General (following the USPTO Director's intervention below), and the Court's call for a response already invites the government's brief in opposition directly. A separate CVSG order is therefore virtually impossible (`0.01`).
- **`summary-disposition-route` (`0.08`):** Conditional on a grant, plenary review is far likelier than a summary disposition in the cert order. The Solicitor General actively defended the § 314(d) jurisdictional bar below even after the Director changed policy on § 312(a)(2), so the government will not acquiesce in a GVR, and summary reversal on a complex *Cuozzo*/*SAS*/*Thryv* line-drawing question is unlikely (`0.08`).
- **`dissent-from-denial` (`0.07`):** Conditional on denial, there is a modest (~7%) chance that at least one Justice notes a dissent or statement respecting denial. Justice Gorsuch authored *SAS Institute* and dissented in *Thryv* (joined by Justice Sotomayor), and the optical narrative of an agency admitting it violated a statute ("only if") while claiming § 314(d) insulates the error from review could draw a separate writing from Justice Gorsuch (`0.04`), Justice Thomas (`0.015`), Justice Alito (`0.015`), or Justice Sotomayor (`0.015`), with lower probabilities (`0.005`–`0.01`) for the remaining Justices on `order-writers`.

## 5. Retrieval and Tooling Note

I queried the local corpus service via `uv run fedcourts query` for recent 2020s SCOTUS grants and for *Cuozzo*/*SAS*/*Thryv* reporter citations (which returned the expected sparse-citation note). I also attempted two CourtListener MCP `search` calls for the Federal Circuit's related decisions in *Dolby Laboratories* and *Ethanol Boosting Systems*, both of which returned HTTP 429 daily rate-limit errors from upstream CourtListener. Per the prompt contract, I degraded gracefully and relied on the comprehensive 87-page provisioned `petition.txt` (which includes the full Federal Circuit opinion and PTAB order in its appendix) and `metrics/statpack.md`.
