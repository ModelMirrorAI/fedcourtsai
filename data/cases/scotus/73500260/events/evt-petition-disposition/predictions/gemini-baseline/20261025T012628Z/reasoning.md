# Predictor Rationale (`scotus/73500260` — `evt-petition-disposition`)

## Summary of Forecast

- **`granted`:** `0` (`predicted_disposition`: `"denied"`)
- **`probability` (`disposition`):** `0.06`
- **`claims`:**
  - `disposition`: `0.06`
  - `relist-increment`: `0.92`
  - `cvsg-increment`: `0.01`
  - `summary-disposition-route`: `0.15`
  - `dissent-from-denial`: `0.03`
- **`big_case_score`:** `0.35`

## Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)

Per `record/context.json`, this cell runs in `forward` mode at `moment: distribution` for `scotus/73500260` (*TitleMax of Virginia, Inc., et al. v. Wendy S. Spicher, Secretary, Pennsylvania Department of Banking and Securities*, No. 25-1359), with `term = 2025`, `salience_version = "sal-v4"`, `band = "baseline"`, `distribution_count = 1`, and `cvsg_date = null`.

1. **Primary Salience-Band Anchor (`sal-v4`, `baseline [reached]`):**
   In `metrics/statpack.md` ("Segment base rate by salience band (sal-v4)"), pooling the bracketed `reached` rates for the `baseline` band across all eight rendered Terms strictly preceding `term = 2025` (OT2017–OT2024) yields:
   - OT2024: `5.7%` (`n=1271`, ~72.4 grants)
   - OT2023: `5.9%` (`n=1312`, ~77.4 grants)
   - OT2022: `5.8%` (`n=1192`, ~69.1 grants)
   - OT2021: `5.6%` (`n=1500`, ~84.0 grants)
   - OT2020: `4.5%` (`n=1739`, ~78.3 grants)
   - OT2019: `4.6%` (`n=1399`, ~64.4 grants)
   - OT2018: `4.6%` (`n=1524`, ~70.1 grants)
   - OT2017: `4.7%` (`n=1643`, ~77.2 grants)
   - **Pooled strictly-prior `baseline [reached]` base rate (OT2017–OT2024):** `592.9 / 11,580 = 5.12%` (**5.1%**). (In OT2025 itself, the `baseline [reached]` rate is `3.9%`, `n=1303`.)
2. **Cross-Checks from Other Statpack Cuts:**
   - **Modern discretionary-cert petitions overall:** `1.5%` granted + `1.3%` GVR = **2.8%** grant-family rate (`denied 95.2%`, `dismissed 2.0%`, `n=44,686`).
   - **Originating circuit (`ca3`):** In the denial-reweighted modern cert table, Third Circuit petitions resolve at `denied 94.9%, dismissed 2.7%, granted 1.5%, gvr 0.9%` (**2.4%** grant-family rate, `n=1927`).
   - **CVSG status (`none`, paid scored segment):** `granted 3.9%, gvr 2.3%` (**6.2%** grant-family rate, `n=13,494`).

## Case-Specific Adjustments from the Anchor

Starting from the **5.1%** `baseline [reached]` anchor, the provisioned snapshot (`record/snapshots/2026-10-25.json`) and filings (`record/documents/petition.txt` and `questions-presented.txt`) present countervailing upward and downward signals that largely offset one another:

### Upward Factors
1. **Call for a Response (CFR) after Waiver:** Respondent filed a waiver on July 8, 2026. After the petition was distributed on July 15, 2026 for the September 28, 2026 Long Conference, the Court requested a response on July 29, 2026 (subsequently extended twice to November 2, 2026). A CFR is a necessary predicate for a grant after a waiver and indicates that at least one chambers flagged the petition for closer scrutiny.
2. **State Amicus Support and Experienced Counsel:** The State of South Carolina filed a cert-stage amicus brief on July 8, 2026 supporting petitioners' horizontal federalism arguments, and petitioners are represented by experienced Supreme Court counsel (Misha Tseytlin of Troutman Pepper Locke LLP).
3. **Parallel Multi-Circuit Litigation and Doctrinal Framing:** Petitioners allege a 3–2 circuit split between the Third, Fifth, and Seventh Circuits (*PDX North*, *TitleMax*, *TMX FCS*, *Stroman Realty*) and the Fourth and Tenth Circuits (*Harper v. Public Service Comm'n of W. Va.*, 396 F.3d 348 (4th Cir. 2005); *Life Partners, Inc. v. Morrison*, 484 F.3d 284 (4th Cir. 2007); *Seneca-Cayuga Tribe*, 874 F.2d 709 (10th Cir. 1989)) on whether *Younger*'s "important state interest" prong under *NOPSI* accounts for horizontal federalism and extraterritoriality limits. Parallel appeals from the same Pennsylvania enforcement proceeding were also litigated in the Fifth Circuit (*TMX Finance Corporate Services, Inc. v. Spicher*, 2026 WL 74504 (5th Cir. Jan. 9, 2026)) and the Fourth Circuit (*TitleMax of South Carolina, Inc. v. Spicher*, No. 25-2027 (4th Cir.)).

### Downward Factors
1. **Unpublished Decision Below:** The Third Circuit's panel opinion (`2026 WL 49584`, App. 1a–11a, by Judge Fisher joined by Judges Krause and Phipps) is explicitly non-precedential under Third Circuit I.O.P. 5.7, and rehearing en banc was denied without recorded dissent (App. 49a–50a).
2. **Prior SCOTUS Cert Denial in the Earlier Phase of This Same Dispute (`21-1262`):** In the subpoena-enforcement stage of this same dispute, the Third Circuit issued a *published* decision holding that Pennsylvania has a strong interest in prohibiting usury and that applying its usury laws to TitleMax's transactions with Pennsylvania residents does not violate the dormant Commerce Clause because the transactions do not occur "wholly outside" Pennsylvania (*TitleMax of Delaware, Inc. v. Weissmann*, 24 F.4th 230, 239–41 (3d Cir. 2022)). Corpus query (`scotus/72470586`, docket `21-1262`) confirms that the Supreme Court denied certiorari in *TitleMax of Delaware, Inc. v. Vague* on June 27, 2022 after 2 distributions. The panel below directly relied on *Weissmann* (App. 7a–8a).
3. **Acute Vehicle / Mootness / Ripeness Defects in the State Administrative Proceeding:** As the Petition candidly discloses (Pet. 14–15), in April 2026 the Pennsylvania administrative hearing examiner issued a proposed report and order **in Petitioners' favor**, recommending dismissal of the Order to Show Cause in its entirety because the Department failed to prove a sufficient connection to Pennsylvania. Although the Department's Compliance Office filed exceptions with the Banking Commission, the fact that Petitioners prevailed before the hearing examiner and may prevail before the Commission or on state judicial review (`2 Pa. C.S. § 702`) makes this a poor vehicle that could become moot before merits resolution.
4. **Weakness of the Alleged Split Post-*Sprint*:** Both *Harper* (2005) and *Seneca-Cayuga* (1989) predate *Sprint Communications, Inc. v. Jacobs*, 571 U.S. 69 (2013). Moreover, every federal court to address this specific Pennsylvania Order to Show Cause—the Middle District of Pennsylvania, the Third Circuit, the Northern District of Texas, the Fifth Circuit, and even the District of South Carolina inside the Fourth Circuit (*TitleMax of S.C., Inc. v. Spicher*, 2025 WL 2378121 (D.S.C. Aug. 15, 2025))—abstained under *Younger*. Under *NOPSI*, 491 U.S. at 365, courts look to the importance of the generic class of state enforcement proceedings rather than previewing the merits of the federal plaintiff's constitutional defense.

Weighing the CFR and state amicus brief against the unpublished decision below, the prior denial in `21-1262`, the hearing examiner's April 2026 proposed dismissal in Petitioners' favor, and the lack of a post-*Sprint* split on these facts, I set **`probability` = `0.06`** (just above the `5.1%` `baseline [reached]` anchor).

## Rationale for Auxiliary Claims and Big-Case Score

- **`relist-increment` (`0.92`):** The snapshot (`2026-10-25.json`) freezes `distribution_count = 1` from the `Jul 15 2026` distribution (which occurred after respondent's `Jul 08 2026` waiver). Because the Court requested a response on `Jul 29 2026` (now due `November 2, 2026`), the petition will be re-distributed for a conference after the BIO arrives. Because `relist-increment` resolves whether the final `distribution_count` exceeds the snapshot's `distribution_count = 1`, it will resolve positively so long as the case reaches a post-BIO conference distribution (failing only on a pre-distribution Rule 46 dismissal or withdrawal).
- **`cvsg-increment` (`0.01`):** Pure state-law enforcement and *Younger* abstention dispute with no federal agency or statutory nexus.
- **`summary-disposition-route` (`0.15`):** Conditional on a grant, the Court would most likely set the case for plenary briefing and argument (`85%`), with a `15%` conditional probability of a GVR (either following a grant in the companion Fifth Circuit case or a *Munsingwear* vacatur if the state administrative proceeding resolves in Petitioners' favor).
- **`dissent-from-denial` (`0.03`):** Slightly above the ~1–2% baseline due to the interstate federalism / extraterritoriality framing supported by South Carolina's amicus brief, but constrained by the unpublished posture and favorable hearing-examiner ruling below.
- **`big_case_score` (`0.35`):** If decided on the merits, the case would clarify the interplay between *NOPSI*'s "generic proceeding" rule and horizontal federalism limits under *Younger*, an important recurring procedural question for cross-border state regulatory enforcement, though not a direct constitutional merits ruling on extraterritorial regulation.

## Uncertainties and Limitations

The Brief in Opposition is not yet filed (`due November 2, 2026` as of the `2026-10-25` snapshot), so respondent's arguments are inferred from the Third Circuit and District Court opinions in the Petition's appendix and the procedural history described in the Petition. In addition, CourtListener MCP search was partially rate-limited (`HTTP 429`) on one secondary query (`ca4`), though two MCP queries succeeded and the provisioned record plus `fedcourts query` supplied complete context.
