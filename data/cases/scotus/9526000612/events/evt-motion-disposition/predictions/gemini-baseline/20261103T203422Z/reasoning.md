# Prediction Reasoning: `scotus/9526000612` (`evt-motion-disposition`)

## 1. Case & Event Overview

- **Case:** *Martin Akerman v. Merit Systems Protection Board, et al.*, No. 26A612 (`scotus/9526000612`)
- **Event:** `evt-motion-disposition` (`stage: interim`, `kind: motion`, `moment: arrival`, `mode: forward`)
- **Cutoff & Snapshot:** `2026-10-21` (`2026-10-21.json`, `cut_kind: arrival-position`, `cut_anchor_index: 0`)
- **Frozen Conditioning (`record/context.json`):** `band: null`, `salience_version: null`, `signals_observable: true`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `term: 2026`
- **Originating Court & Docket:** United States Court of Appeals for the District of Columbia Circuit, No. 26-5131 (arising out of *Akerman v. Merit Systems Protection Board, et al.*, No. 1:23-cv-02574-RDM, U.S. District Court for the District of Columbia)
- **Circuit Justice:** Chief Justice Roberts (D.C. Circuit); application submitted to Justice Gorsuch
- **Parties & Counsel:** Applicant Martin Akerman is proceeding *pro se* (`snapshot_contact_scrub` withheld 4 fields in 1 Petitioner block). The respondents are the Merit Systems Protection Board (MSPB) and federal agencies/officials represented by Solicitor General D. John Sauer.

At the arrival snapshot (`2026-10-21.json`), the single docket entry (dated October 20, 2026) reads: *"Application (26A612) for immediate administrative stay and stay pending appeal, submitted to Justice Gorsuch."*

*Note on Provisioned Document:* The provisioned `record/documents/application.txt` has `empty_text: true` in `documents.json` (`pages: 20`, `empty_pages: 20`, `ocr_derived: false`, consisting of 19 form-feed bytes from a scanned filing with no text layer). Per the prompt instructions, I treat `application.txt` as content-unavailable rather than inferring from a blank file, and I have recorded an informational `provisioning` note in `flags.json`. In `forward` mode, the underlying procedural posture and dispute are thoroughly documented in the corpus and CourtListener RECAP records.

---

## 2. Procedural & Factual Context from Lower Courts and Prior SCOTUS Filings

Using `uv run fedcourts query` and CourtListener MCP lookups (`cadc` docket `26-5131`, `docket_id: 73235695`; `dcd` docket `1:23-cv-02574`, `docket_id: 67786074`; and related `cadc` mandamus docket `26-1285`, `docket_id: 74946868`), the background of this application is clear:

1. **District Court Litigation (`1:23-cv-02574-RDM`):** In September 2023, Akerman filed a *pro se* Freedom of Information Act (FOIA) and whistleblower-related action in the U.S. District Court for the District of Columbia against the MSPB, the Department of the Air Force, the Department of the Army, the Department of Defense Office of Inspector General, the Department of Labor, the Equal Employment Opportunity Commission, and the Office of Special Counsel. Following numerous procedural motions (including unsuccessful efforts to transfer the case to Nevada that were rejected by both Judge Randolph D. Moss and the D.C. Circuit in No. 23-5309), Judge Moss issued an omnibus order on April 18, 2026 (ECF No. 98) denying Akerman's motions for preliminary injunction, reconsideration, appointment of counsel, joinder, and other miscellaneous relief, followed by an order on April 20, 2026 (ECF No. 102).
2. **D.C. Circuit Interlocutory Appeal (`26-5131`) & Related Mandamus (`26-1285`):** On April 20, 2026, Akerman noticed an interlocutory appeal to the D.C. Circuit (docketed April 23, 2026 as No. 26-5131) from the district court's April 18, 2026 order (ECF No. 98). On August 4, 2026, a Special Panel of the D.C. Circuit issued a *per curiam* order denying an emergency injunction, and on August 7, 2026, the Clerk suspended briefing. Following further post-order submissions (and a parallel emergency mandamus petition docketed October 9, 2026 in CADC No. 26-1285), the D.C. Circuit Special Panel in No. 26-5131 issued another *per curiam* order on October 19, 2026. The next day (October 20, 2026), Akerman submitted this emergency stay application (`26A612`) to the Supreme Court, addressing it to Justice Gorsuch.
3. **Applicant's Prior SCOTUS Applications:** Akerman is a frequent *pro se* litigant across multiple circuits (D.C., Fourth, Ninth, and Federal Circuits) and the Supreme Court in interconnected disputes stemming from his federal employment/National Guard tenure and MSPB individual right of action (IRA) proceedings. In the Supreme Court corpus:
   - `23-6709` (*Akerman v. United States*, from CADC `23-5229`): Certiorari denied March 18, 2024.
   - `23-6710` (*Akerman v. Doiron*, from CADC `23-5230`): Certiorari denied April 15, 2024.
   - `24A730` (*Akerman v. Merit Systems Protection Board*, from CAFC `24-130`): Substantive application referred to the Court and **denied** March 24, 2025 (`referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`).
   - `24A731` (*Akerman v. Merit Systems Protection Board*, from CAFC `24-1926`): Substantive application referred to the Court and **denied** March 24, 2025 (`referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`).

---

## 3. Statistical Base Rates (`metrics/statpack.md` & `metrics/statpack.json`)

Under the interim-stage anchoring rules (`Stage: interim` in `.github/prompts/predict.md`), the baseline is the substantive resolved slice's grant rate under the finer reading (`finer_granted / finer_resolved`, where partial grants count as granted and moot dismissals are excluded), pooled over the 10 application-Terms strictly preceding `term: 2026` (`2016 <= T < 2026`), provided `finer_unread == 0` in every pooled Term and the pooled sample clears `INTERIM_BASE_RATE_MIN_RESOLVED = 50`:

- **Per-Term Counts (`metrics/statpack.json`, `interim_docket.terms`, OT 2016–OT 2025):**
  - **OT 2025:** `finer_granted = 20`, `finer_resolved = 223` (`finer_moot = 3`, `finer_unread = 0`, `unparsed = 0`)
  - **OT 2024:** `finer_granted = 20`, `finer_resolved = 194` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 0`)
  - **OT 2023:** `finer_granted = 21`, `finer_resolved = 127` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 0`)
  - **OT 2022:** `finer_granted = 9`, `finer_resolved = 103` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 0`)
  - **OT 2021:** `finer_granted = 30`, `finer_resolved = 120` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 0`)
  - **OT 2020:** `finer_granted = 31`, `finer_resolved = 133` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 0`)
  - **OT 2019:** `finer_granted = 12`, `finer_resolved = 119` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 0`)
  - **OT 2018:** `finer_granted = 13`, `finer_resolved = 113` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 0`)
  - **OT 2017:** `finer_granted = 13`, `finer_resolved = 124` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 1`)
  - **OT 2016:** `finer_granted = 9`, `finer_resolved = 107` (`finer_moot = 0`, `finer_unread = 0`, `unparsed = 15`)
- **Pooled 10-Term Finer Baseline (OT 2016–OT 2025):**
  - Total `finer_granted = 178`, total `finer_resolved = 1,363` (**13.06%**, clearing the 50-case floor with `finer_unread = 0` across all 10 Terms).
  - Under the older table columns rendered in `metrics/statpack.md` (`substantive_granted / substantive_resolved` across OT 2016–OT 2025), the pool is `160 / 1,366 = 11.71%`.
- **Adjusting from the Unconditioned Pool to This Case:**
  - As the statpack cautions, the ~13.1% pooled substantive grant rate blends high-salience institutional/governmental stay applications (where the Circuit Justice requests a response and amici file briefs) with uninvited *pro se* applications. Across the entire `1,490`-case substantive slice in `statpack.md`, `302` had a response requested, `800` were referred to the Court, and `141` had amicus support.
  - When no response is requested (`response_requested: false`) and there are no amici (`amicus_briefs: 0`), and when the applicant is a *pro se* individual seeking an interlocutory stay in a personal civil suit, the empirical grant rate is **< 1%**.

---

## 4. Legal & Procedural Assessment (`interim-v3` Claims & `order-writers`)

1. **`interim-disposition` (`0.01`, `granted: 0`, `predicted_disposition: "denied"`):**
   - To obtain a stay pending appeal or an administrative stay from the Supreme Court, an applicant must satisfy *Nken v. Holder*, 556 U.S. 418, 434 (2009), and *Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010): a reasonable probability that four Justices will vote to grant certiorari, a fair prospect that a majority will vote to reverse, and a likelihood of irreparable harm.
   - Here, the underlying D.C. Circuit proceeding (No. 26-5131) is an interlocutory appeal from a district court order denying preliminary and procedural motions in an ongoing *pro se* FOIA/whistleblower suit (`1:23-cv-02574-RDM`). There is no circuit split, no final judgment, and no extraordinary legal question warranting Supreme Court intervention. Moreover, Akerman's two prior substantive applications against the MSPB (`24A730` and `24A731`) were summarily denied.
2. **`response-requested-increment` (`0.02`):**
   - At arrival (`2026-10-21.json`), `response_requested` is `false`. Given the *pro se* interlocutory posture and the absence of any plausible basis for emergency relief, there is only a ~2% chance that the Circuit Justice or the Court calls for a response from the Solicitor General.
3. **`referral-increment` (`0.35`):**
   - At arrival (`2026-10-21.json`, `cut_kind: arrival-position` at index 0), `referred_to_court` is `false`. While many *pro se* applications are denied by a single Justice in chambers, Akerman addressed this D.C. Circuit application to Justice Gorsuch rather than Chief Justice Roberts (the Circuit Justice for the D.C. Circuit), and both of Akerman's prior MSPB applications (`24A730` and `24A731`) were referred to the full Court before being denied without a response request. Accordingly, I estimate a `0.35` probability that the application is referred to the full Court after the arrival entry.
4. **`amicus-increment` (`0.01`):**
   - At arrival, `amicus_briefs` is `0`. Because this is a personal *pro se* dispute with no third-party or institutional participation in any of the underlying or companion dockets, the probability of any amicus filing is minimal (`0.01`).
5. **`order-writers` (`0.001`–`0.002` per Justice):**
   - Routine denials of *pro se* interlocutory stay applications issue as standard unsigned order lines without separate writings from any Justice.
6. **`big_case_score` (`0.02`):**
   - This is an individual *pro se* interlocutory dispute with no broader doctrinal, institutional, or public policy stakes.
