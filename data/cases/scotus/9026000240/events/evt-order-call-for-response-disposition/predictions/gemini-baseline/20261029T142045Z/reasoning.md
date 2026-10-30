# Predictor Rationale (`reasoning.md`)

## Summary of Forecast
- **Predicted disposition:** `denied` (`granted: false`)
- **Probability of grant (`P(granted)`):** `0.15` (`0.12` plenary grant + `0.03` GVR/summary route)
- **Confidence:** `0.78`
- **Big-case score:** `0.72`

## Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)
Per `record/context.json`, this cell is in `forward` mode at `moment: response-requested` (`cutoff: "2026-10-06"`, `cut_kind: "date"`), with frozen conditioning state:
- `band: "baseline"` under `salience_version: "sal-v4"`
- `distribution_count: 1`
- `cvsg_date: null`
- `term: 2026`

In `metrics/statpack.md`, the primary scored anchor is the **"Segment base rate by salience band (sal-v4)"** table across Terms strictly preceding `2026` (OT2017–OT2025), using the bracketed risk-set (`reached`) rate for the `baseline` band (private paid petitions):
- **OT2025:** `1.0% (n=994) [reached 4.0%, n=1314]`
- **OT2024:** `1.4% (n=936) [reached 5.9%, n=1274]`
- **OT2023:** `1.7% (n=958) [reached 5.9%, n=1312]`
- **OT2022:** `1.3% (n=894) [reached 5.9%, n=1196]`
- **OT2021:** `1.2% (n=1158) [reached 5.7%, n=1500]`
- **OT2020:** `1.0% (n=1343) [reached 4.5%, n=1740]`
- **OT2019:** `1.9% (n=1065) [reached 4.7%, n=1399]`
- **OT2018:** `1.5% (n=1181) [reached 4.8%, n=1529]`
- **OT2017:** `0.6% (n=1245) [reached 4.9%, n=1649]`

Pooling the risk-set (`reached`) denominators across all nine prior complete Terms (OT2017–OT2025, total `n = 12,913`) yields a segment base rate of **~5.1%** (`4.0%` in the most recent complete Term, OT2025).

Cross-checking the marginal cuts in `metrics/statpack.md` (modern discretionary-cert petitions, denial-reweighted):
- **Overall modern discretionary-cert petitions:** `denied 95.1%` (42,577 / 44,777 resolved), `dismissed 2.1%` (918), `granted 1.5%` (692), `gvr 1.3%` (590) — grant-family rate **2.9%**.
- **Originating circuit (`ca4`):** `denied 95.3%`, `dismissed 2.2%`, `granted 1.3%`, `gvr 1.2%` (`n = 3,480` resolved) — grant-family rate **2.5%**.
- **Relist count (`0`, paid scored segment):** `denied 96.8%`, `granted 1.3%`, `dismissed 1.3%`, `gvr 0.5%` (`n = 10,203` resolved), whereas petitions that reach `1` relist grant at `13.7%` (`granted 8.5%`, `gvr 5.2%`, `n = 2,538`) and `2` relists at `41.2%` (`granted 28.3%`, `gvr 12.9%`, `n = 495`).
- **Cert-stage amicus-brief count (`2+`, paid scored segment):** `denied 76.0%`, `granted 18.4%`, `gvr 4.5%`, `dismissed 1.2%` (`n = 1,449` resolved) — grant-family rate **22.9%**.

## Case-Specific Adjustments from the Provisioned Record

### 1. Upward Adjustments (Why `P(grant)` Rises from ~5.1% to ~15%)
- **Call for a Response Following Waiver (`2026-10-06.json`):** Respondents A. Scott Fleming et al. waived their right to respond on September 23, 2026, and the petition was distributed on September 30, 2026 for the October 16, 2026 Conference. Five days later, on October 5, 2026, the Court requested a response (due November 4, 2026). Calling for a response confirms active chambers interest and clears the initial hurdle where waived petitions are summarily denied.
- **Substantial Cert-Stage Amicus Support (7 Briefs, Including 22 States):** The snapshot (`2026-10-06.json`) records seven cert-stage amicus briefs supporting petitioners: six filed on September 14, 2026 and marked `VIDED` with companion petition *Hall v. Fleming*, No. 26-193 (by The Council for Christian Colleges & Universities et al., represented by Sidley Austin; American Center for Law and Justice; National Religious Broadcasters et al.; Notre Dame Education Law Project, Lindsay and Matt Moroun Religious Liberty Clinic, and Union of Orthodox Jewish Congregations of America, represented by Prof. Richard Garnett; Samaritan's Purse and Billy Graham Evangelistic Association, represented by Christopher Mills; and Association for Biblical Higher Education et al.), plus a seventh brief filed on September 24, 2026 by the State of West Virginia and 21 other States. In the statpack, `2+` cert-stage amicus briefs carry a `22.9%` marginal grant-family rate.
- **Doctrinal Salience and Institutional Advocates (`petition.txt`, `questions-presented.txt`):** Represented by Alliance Defending Freedom (James A. Campbell, John J. Bursch, David A. Cortman, Rory T. Gray), petitioners press two closely watched questions (`questions-presented.txt`): (1) whether the Religion Clauses permit governments to exclude some religious degrees (CIP Code 39 under VTAG, and theological/religious degrees under VANGSTAP) while funding similar religious degrees (CIP Code 38 under VTAG), and (2) whether *Locke v. Davey*, 540 U.S. 712 (2004), should be overruled. In the companion Fourth Circuit decision *Hall v. Fleming*, 175 F.4th 510, 516–20 (4th Cir. 2026) (`petition.txt` at 29–30, 33), Judge Richardson concurred specifically to urge the Supreme Court to formally overrule *Locke* in light of *Trinity Lutheran Church of Columbia, Inc. v. Comer*, 582 U.S. 449 (2017), *Espinoza v. Montana Department of Revenue*, 591 U.S. 464 (2020), *Carson v. Makin*, 596 U.S. 767 (2022), and *Kennedy v. Bremerton School District*, 597 U.S. 507 (2022). Petitioners also invoke *Catholic Charities Bureau, Inc. v. Wisconsin Labor & Industry Review Commission*, 605 U.S. 238 (2025) (`petition.txt` at 3–4, 27–28), arguing that Virginia's line between CIP Code 38 ("Philosophy and Religious Studies," including Christian Studies) and CIP Code 39 ("Theology and Religious Vocations," including Biblical Studies and Pastoral Leadership) discriminates along theological lines and creates excessive entanglement.

### 2. Downward Adjustments (Why Denial Remains the Modal Outcome at `0.85` Non-Grant)
- **Extraordinary Procedural Posture — Certiorari Before Judgment Under Rule 11 (`petition.txt` at i, 1–2, 37–38):** Unlike a standard petition for certiorari after a circuit judgment, No. 26-240 is a **petition for a writ of certiorari before judgment** under 28 U.S.C. § 2101(e) and Supreme Court Rule 11. On March 31, 2026, the Eastern District of Virginia (Judge Roderick C. Young) granted defendants' Rule 12(b)(6) motion to dismiss Cameron Johnson's and Luke Thomas's VTAG claims, denied dismissal of Trace Stevens's VANGSTAP claim, and denied a preliminary injunction (`petition.txt`, App. 1a–29a). Petitioners took an interlocutory appeal to the Fourth Circuit (`No. 26-1437`), which denied an injunction pending appeal on May 18, 2026 (`App. 34a–35a`) and deferred a motion to accelerate on May 22, 2026 (`petition.txt` at ii, 17). The Supreme Court grants certiorari before judgment only in rare cases of imperative public emergency where normal appellate review cannot timely proceed.
- **Presence of a Clean Post-Judgment Companion Vehicle (*Hall v. Fleming*, No. 26-193):** As petitioners repeatedly note (`petition.txt` at 2, 5, 17, 37) and as confirmed via `uv run fedcourts query --court scotus --docket-number 26-193 --decided-before 2026-10-06`, *Hall v. Fleming*, No. 26-193 (docketed August 14, 2026), is already pending before the Court from a final published judgment of the Fourth Circuit (`175 F.4th 510 (4th Cir. 2026)`) on the exact VTAG / *Locke v. Davey* question, complete with Judge Richardson's concurrence. Six of the seven amicus briefs in No. 26-240 are `VIDED` with No. 26-193. Even if the Court is inclined to revisit *Locke v. Davey*, *Hall* provides a final circuit judgment without requiring an extraordinary Rule 11 bypass of the Fourth Circuit.
- **Severe Vehicle Defects Specific to *Johnson* (`petition.txt`, App. 6a–16a, 28a):**
  1. **Unresolved Factual Record on VANGSTAP:** The district court *denied* the motion to dismiss Trace Stevens's VANGSTAP claims (`App. 11a–12a, 28a`) expressly "in light of the limited factual record before the Court—particularly with respect to the procedures utilized by the Department to administer the STAP program and execute its statutory mandate," and stayed discovery only at the parties' request pending the interlocutory preliminary-injunction appeal (`App. 30a–31a`).
  2. **Interlocutory Pendent Jurisdiction and Ripeness Issues on VTAG:** The Fourth Circuit appeal (`No. 26-1437`) arises under 28 U.S.C. § 1292(a)(1) from the denial of a preliminary injunction and relies on pendent appellate jurisdiction to reach the Rule 12(b)(6) dismissal of Johnson's and Thomas's claims (`petition.txt` at 1–2). Moreover, plaintiff Luke Thomas has not yet declared an ineligible CIP Code 39 major (`App. 6a–7a, 161a`), inviting threshold standing/ripeness objections once Virginia files its BIO.
  3. **Imminent Fourth Circuit Action:** Petitioners themselves state (`petition.txt` at 2) that Fourth Circuit briefing in `No. 26-1437` is complete and "it is likely that the Fourth Circuit will issue its opinion before the Court considers this petition."
- **Low GVR Likelihood for a Cert-Before-Judgment Petition:** Even if the Court grants *Hall v. Fleming* (No. 26-193), a petition for certiorari *before judgment* has no Fourth Circuit judgment to vacate and remand; the appeal is *already* pending in the Fourth Circuit (`No. 26-1437`), which can hold the appeal for *Hall* or apply *Hall* directly. Thus, unless the Court consolidates *Johnson* with *Hall* for plenary argument (`~0.12`) or the Fourth Circuit issues an intervening judgment before the Court disposes of No. 26-240 (`~0.03` GVR), the Court will deny certiorari before judgment in No. 26-240 (`~0.83` denied, `~0.02` dismissed/withdrawn).

## Uncertainty and Limitations
- **No Brief in Opposition Yet (`moment: response-requested`):** Because the snapshot stops on October 6, 2026—the day after the Court called for a response due November 4, 2026—Virginia's brief in opposition is not yet on the record (`documents.json` contains only `petition.txt` and `questions-presented.txt`, with `petition.txt` truncated at the 150,000-character cap inside the appendix).
- **Companion Docket Trajectory:** In `fedcourts query`, companion docket `26-193` (*Hall v. Fleming*) had `last_live_polled: null` as of the cutoff, so its exact conference/CFR dates were inferred from the `VIDED` amicus entries on the `26-240` snapshot and the petition text.
- **CourtListener MCP Throttled:** Two live CourtListener MCP search calls for *Hall v. Fleming* and *Johnson v. Fleming* returned HTTP 429 (`Rate limit exceeded: 1400/day`); however, the provisioned `petition.txt` (including the district court opinion and Fourth Circuit order in the appendix) and `fedcourts query` provided all necessary pre-cutoff context.
