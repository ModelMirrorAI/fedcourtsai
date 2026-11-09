# Predictor Rationale (`reasoning.md`)

## 1. Anchor and Base Rates

This cell forecasts `evt-order-call-for-response-disposition` (`stage: cert`, `moment: response-requested`) in `forward` mode for *Donald J. Trump, et al. v. Hillary R. Clinton, et al.*, No. 26-518 (`scotus/9026000518`).

- **Frozen Conditioning (`record/context.json`):**
  - `mode`: `forward`
  - `snapshot_date`: `2026-10-27` (`input_snapshot`: `2026-10-27.json`)
  - `band`: `baseline` under `salience_version`: `sal-v8`
  - `distribution_count`: `0`
  - `cvsg_date`: `null`
  - `amicus_briefs`: `null` (0 amicus briefs on the docket snapshot)
  - `cert_anchor`: `rate = 0.051587928582714486` (~5.16%), pooled over `lookback_terms = 10` (`statpack_digest: sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`).
- **Statpack Base Rates (`metrics/statpack.md`):**
  - The `Segment base rate by salience band (sal-v8)` table shows the bracketed `[reached]` rate for `baseline` across the 9 prior Terms rendered in the table (OT2017–OT2025): 4.0% (2025, n=1290), 6.0% (2024, n=1243), 6.0% (2023, n=1283), 5.9% (2022, n=1183), 5.7% (2021, n=1469), 4.7% (2020, n=1697), 4.7% (2019, n=1369), 4.8% (2018, n=1509), and 5.0% (2017, n=1615), pooling to the frozen `cert_anchor.rate` of **5.16%**.
  - Originating circuit (`ca11`): in the modern discretionary-cert cut, Eleventh Circuit petitions have a resolved base rate of 94.9% denied, 2.1% GVR, 1.8% dismissed, and 1.2% granted (3.3% grant family, n=3,954).
  - Fee class and amicus support: this is a paid petition with zero amicus briefs filed to date (`0` amicus bucket in the paid scored segment has a 3.8% grant-family rate: 2.0% granted, 1.8% GVR, n=11,109).

## 2. Case-Specific Adjustments from the Anchor (5.16% → 4.0%)

Starting from the frozen `baseline` band reached anchor of **5.16%** (`0.0516`), I weigh the competing signals in the provisioned snapshot (`2026-10-27.json`) and filings (`questions-presented.txt` and `petition.txt`, which includes the Eleventh Circuit's published opinion by Chief Judge William Pryor at Pet. App. 1a–39a and Judge Middlebrooks's sanctions and dismissal orders at Pet. App. 40a–222a):

### Upward Factors
1. **Call for a Response (`moment: response-requested`):** After respondents DNC Services Corp., Democratic National Committee, HFACC, Inc., Hillary Clinton, Orbis Business Intelligence, Perkins Coie, Marc Elias, Michael Sussmann, John Podesta, Robert Mook, Debbie Wasserman Schultz, Fusion GPS, and Peter Strzok filed waivers of their right to respond between October 21 and October 26, 2026, the Court called for a response on October 27, 2026 (due November 27, 2026). Calling for a response indicates that at least one Justice's chambers flagged the petition rather than letting it be denied summarily on the waivers, likely because of the petitioner's status as sitting President and the nearly $1 million inherent-authority sanction imposed on him and his attorneys.
2. **Presidential Petitioner and Constitutional Framing:** Although the petitioner is suing in his private capacity (and thus sits in the `baseline` caption class rather than `federal`), petitioners' counsel (led by Robert J. Giuffra, Jr. of Sullivan & Cromwell LLP) frame the case around Article II presidential responsibilities (`Clinton v. Jones`, 520 U.S. 681 (1997); `Trump v. Vance`, 591 U.S. 786 (2020); `Trump v. United States`, 603 U.S. 593 (2024)) and the chilling effect of inherent-authority sanctions (`Chambers v. NASCO, Inc.`, 501 U.S. 32 (1991)).

### Downward Factors (Decisive)
1. **Fatal Vehicle Defect on QP 1 (Independent Alternative Grounds Below):** The Eleventh Circuit's opinion (authored by Chief Judge William Pryor and joined by Judges Brasher and Hull) held that **even if** the four-year RICO statute of limitations were equitably tolled during President Trump's first term in office, the Amended Complaint *still* failed to state a valid RICO claim on the merits (Pet. App. 14a–18a). Specifically, the Eleventh Circuit affirmed the district court's ruling that the complaint failed to plead any valid RICO predicate acts (under the Defend Trade Secrets Act, obstruction of justice, or wire fraud) and failed to plead an enterprise or pattern of racketeering activity. The petition does not even challenge those substantive RICO holdings in its Questions Presented. Consequently, QP 1 cannot change the dismissal of the underlying lawsuit—making it a classic advisory or non-outcome-determinative question as to the dismissal.
2. **Fact-Bound Nature of QP 2 (Sanctions Rested on Broad Bad-Faith Conduct, Not Just the Tolling Argument):** Petitioners frame QP 2 as whether a court may invoke inherent authority to sanction the President and his counsel "based on their advocacy of a substantial, unresolved argument that Article II responsibilities warrant equitable tolling." However, both the district court (Pet. App. 44a–74a) and the Eleventh Circuit (Pet. App. 20a–31a) grounded the finding of bad faith under `Chambers v. NASCO` on the *totality* of the litigation conduct: filing a sprawling 186-page, 819-paragraph shotgun pleading after being warned of Eleventh Circuit precedent, knowingly or recklessly misrepresenting the Mueller Report, the DOJ Inspector General Report, and the Danchenko and Sussmann indictments, asserting a malicious prosecution claim without any prosecution, and asserting frivolous personal-jurisdiction and CFAA theories foreclosed by `Van Buren v. United States`, 593 U.S. 374 (2021). Furthermore, the Eleventh Circuit noted that President Trump filed multiple other private civil suits while in office, undercutting the factual premise that his Article II duties prevented him from filing suit.
3. **Absence of a Circuit Split and Unanimous En Banc Denial:** Neither QP 1 nor QP 2 implicates a genuine split among the federal courts of appeals. Moreover, the conservative-majority Eleventh Circuit denied rehearing en banc with no judge requesting a poll (`Pet. App. 226a–227a`).

Weighing the modest positive signal of the call for a response against the severe vehicle defects, independent alternative grounds below, and lack of a circuit conflict, I adjust slightly downward from the 5.16% `baseline` reached rate to **P(grant) = 0.04** (`predicted_disposition: "denied"`, `granted: 0`).

## 3. Secondary Claims and Distribution Claims

- **`disposition` (0.04):** Matches top-level `probability` per the contract.
- **`relist-increment` (0.99):** As noted in the prompt, on a `response-requested` cell `relist-increment` is masked by the harness because the petition sits at `distribution_count: 0` and is virtually certain to be distributed for conference once the requested response is filed or the time expires. I set `0.99` to reflect near-certainty of at least one future conference distribution.
- **`cvsg-increment` (0.01):** Almost zero chance of a CVSG. This is a private civil RICO/sanctions dispute brought by the President in his personal capacity, where federal defendants were already dismissed below and no federal agency administers the relevant rules.
- **`summary-disposition-route` (0.15):** Conditional on the Court granting review, full merits briefing and oral argument would be the primary route (85%), but there is a 15% conditional probability that the Court would summarily vacate and remand the sanctions order in part.
- **`dissent-from-denial` (0.04) and `order-writers`:** Most denials after a call for a response issue without noted dissents or statements. However, given the petitioner's identity and the nearly $1 million sanction against a former/sitting President, there is roughly a 4% conditional probability that Justice Thomas (`0.025`) or Justice Alito (`0.020`) (or, much less likely, Justice Gorsuch `0.008` or another Justice) writes a brief statement or dissent from denial regarding inherent-authority sanctions.

## 4. Big Case Score (`0.72`)

Although the legal and vehicle merits for certiorari are weak, the case carries high public salience (`0.72`): it is a lawsuit by President Donald J. Trump against his 2016 opponent Hillary R. Clinton and senior Democratic and former federal officials arising out of the 2016 election controversy, and it asks whether Article II tolls personal civil claims for a sitting President and whether federal courts may impose nearly $1 million in inherent-authority sanctions on a President and his personal counsel.

## 5. Inputs and Retrieval Notes

- I relied on the provisioned snapshot (`record/snapshots/2026-10-27.json`), `record/context.json`, `record/documents/questions-presented.txt`, and `record/documents/petition.txt` (noting that `petition.txt` was capped at 150,000 characters with pipeline truncation notes inside Appendices B, C, D, and E, while the full Petition body and Appendix A—the Eleventh Circuit's opinion—were complete).
- No `decision-below.txt` or `lower-court-docket.txt` was separately staged because Appendix A of `petition.txt` already contains the Eleventh Circuit's full opinion, and no `brief-in-opposition.txt` exists yet because the event is placed on the day the Court called for a response.
- I also ran two `uv run fedcourts query` calls against the corpus (logged in `retrieval.md`) to inspect the linked extension application (`26A276`, noting a corpus collision on that docket number) and recent OT2026 cert grants.
