# Rationale and Calibration (`reasoning.md`)

## Summary of Forecast
- **Predicted Disposition:** `denied` (`granted = 0`, `probability = 0.005`)
- **Declared Claims (`interim-v3`):**
  - `interim-disposition`: `0.005`
  - `response-requested-increment`: `0.015`
  - `referral-increment`: `0.01`
  - `amicus-increment`: `0.01`
- **Declared Distribution (`order-writers`):** `0.001` for each of the nine sitting Justices (`Roberts`, `Thomas`, `Alito`, `Sotomayor`, `Kagan`, `Gorsuch`, `Kavanaugh`, `Barrett`, `Jackson`).
- **Big Case Score:** `0.02` (routine pro se interlocutory application arising out of an individual D.D.C. FOIA/employment suit).

---

## 1. Provisioned Record and Document Status
- **Snapshot (`record/snapshots/2026-10-21.json`) and Context (`record/context.json`):**
  This is a `forward`-mode interim-stage arrival cell (`moment: arrival`, `event_id: evt-motion-disposition`, `opened_at: 2026-10-20`, `cutoff: 2026-10-21`). Application No. `26A612` (*Martin Akerman v. Merit Systems Protection Board, et al.*), originating from the United States Court of Appeals for the D.C. Circuit (No. `26-5131`), was submitted on October 20, 2026 (`Application (26A612) for injunctive relief and stay, submitted to The Chief Justice`) and docketed October 30, 2026. Petitioner Martin Akerman appears pro se (his contact block was scrubbed by `snapshot_contact_scrub`), and Solicitor General D. John Sauer is listed for the federal respondents (`Merit Systems Protection Board, et al.`).
- **Escalation-Ladder State at Cut (`2026-10-21`):**
  `band` is `null` (normal for an interim application), `signals_observable` is `true`, `response_requested` is `false`, `referred_to_court` is `false`, and `amicus_briefs` is `0`.
- **Provisioned Document (`record/documents/application.txt`):**
  `record/documents/documents.json` lists `application.txt` (20 pages, `url`: `https://www.supremecourt.gov/DocketPDF/26/26A612/431265/20261030114918676_26A612.pdf`) with `empty_text: true`, `ocr_derived: false`, `truncated: false`, and `bytes: 19` (blank page-break newlines from a scanned image-only PDF with no embedded text layer). Accordingly, per the prompt contract, I do not treat the blank `.txt` file as a short filing; my reading of the application's subject matter and posture rests on the SCOTUS docket entry and the underlying D.C. Circuit (`No. 26-5131`) and D.D.C. (`No. 1:23-cv-02574-RDM`) dockets retrieved via CourtListener.

---

## 2. Base-Rate Anchoring (`metrics/statpack.md` and `metrics/statpack.json`)
Per the interim-stage anchoring rules in `.github/prompts/predict.md`:
- The scored baseline for an OT2026 (`26Annn`) interim cell is defined over the 10 strictly prior application-Terms (`2016 <= T < 2026`) using the per-Term `finer_granted` / `finer_resolved` counts, subject to the pre-registered floor of `>= 50` resolved substantive applications (`INTERIM_BASE_RATE_MIN_RESOLVED`) **and** `finer_unread == 0` in every pooled Term.
- In the committed statpack (`metrics/statpack.md` and `metrics/statpack.json`):
  1. `metrics/statpack.md`'s **"The interim docket (applications)"** section still carries the pre-rewrite caption calling the section *"Descriptive only — the pipeline does not predict on the application docket, so nothing here is a scored base rate,"* and its table renders only the older `resolved (subst.)` (`substantive_resolved`) and `granted` (`substantive_granted`) columns alongside `unparsed`.
  2. In `metrics/statpack.json` (`interim.terms`), every Term in `2016 <= T < 2026` currently carries `finer_granted: 0`, `finer_resolved: 0`, and a non-zero `finer_unread` (`107` in 2016, `124` in 2017, `113` in 2018, `119` in 2019, `133` in 2020, `120` in 2021, `103` in 2022, `127` in 2023, `194` in 2024, `226` in 2025; total `finer_unread = 1,366` across OT2016–OT2025, `1,465` pack-wide). Because the finer-reading pool has `0` resolved applications and non-zero `finer_unread` in every prior Term, it does not clear the 50-resolved / zero-unread floor, so **I anchored without a published finer-reading baseline** (`None` under the finer-reading rule).
  3. For descriptive population shape only (and explicitly not as a substitute scored baseline), the older registered `substantive_granted` / `substantive_resolved` columns rendered in `metrics/statpack.md` across the 10 strictly prior Terms OT2016–OT2025 sum to `160` granted out of `1,366` resolved substantive applications (`11.71%`), with `16` `unparsed` applications across the window (`15` in OT2016, `1` in OT2017, `0` in OT2018–OT2025):
     - OT2025: 17 / 226 (7.5%), unparsed 0, resp. requested 42, referred 39
     - OT2024: 16 / 194 (8.2%), unparsed 0, resp. requested 47, referred 40
     - OT2023: 18 / 127 (14.2%), unparsed 0, resp. requested 47, referred 28
     - OT2022: 9 / 103 (8.7%), unparsed 0, resp. requested 37, referred 24
     - OT2021: 30 / 120 (25.0%), unparsed 0, resp. requested 27, referred 37
     - OT2020: 25 / 133 (18.8%), unparsed 0, resp. requested 9, referred 28
     - OT2019: 12 / 119 (10.1%), unparsed 0, resp. requested 9, referred 25
     - OT2018: 12 / 113 (10.6%), unparsed 0, resp. requested 17, referred 17
     - OT2017: 12 / 124 (9.7%), unparsed 1, resp. requested 7, referred 10
     - OT2016: 9 / 107 (8.4%), unparsed 15, resp. requested 6, referred 6
  4. Across all 1,602 substantive applications in the statpack (`1,226` stay, `250` injunction, `126` vacatur), `271` had a response requested and `273` were referred to the full Court, illustrating that substantive grants are heavily concentrated in the subset of applications that draw a response request and/or referral to the full Court, and that injunction requests (`250` total across 11 Terms) face an especially demanding standard.

---

## 3. Case-Specific Adjustments and Prior Litigation History
Several strong, convergent features push the probability of a grant down to `0.005` (`0.5%`):

1. **Interlocutory Posture in Ongoing District Court Litigation:**
   CourtListener RECAP records for the originating appeal (*Martin Akerman v. MSPB*, D.C. Cir. No. `26-5131`, docket `73235695`) and the underlying district court case (*Akerman v. Merit Systems Protection Board, et al.*, D.D.C. No. `1:23-cv-02574-RDM`, docket `67786074`, before Judge Randolph D. Moss) show that the underlying suit is a pro se FOIA / Privacy Act / employment-records action against seven federal agencies (`MSPB`, `EEOC`, `Department of the Army`, `DoD OIG`, `Department of Labor`, `OSC`, `Department of the Air Force`) in which the government's motion to dismiss / motion for summary judgment (Dkt. 84/87) and Akerman's preliminary-injunction and ancillary motions remain pending in the district court without a final judgment. Akerman noticed an interlocutory appeal (`26-5131`) on April 23, 2026; a D.C. Circuit Special Panel issued a per curiam order on August 4, 2026 and a second per curiam order on October 19, 2026, prompting Akerman's emergency application to The Chief Justice the next day (October 20, 2026).

2. **Applicant's Prior 0-for-9 Record at the Supreme Court:**
   Corpus queries (`uv run fedcourts query`) confirm that Martin Akerman has prosecuted **nine prior pro se petitions** before the Supreme Court between December 2023 and October 2025, every one of which was denied without recorded dissent or a call for a response:
   - *Martin Akerman v. Merit Systems Protection Board, et al.*, No. `24-339` (`scotus/72484053`) — a prior petition from an earlier D.C. Circuit interlocutory appeal (`No. 23-5309`) in this **same** underlying D.D.C. lawsuit, denied November 18, 2024.
   - *Martin Akerman v. National Guard Bureau*, No. `24-83` (`scotus/72487099`, from D.C. Cir. No. `23-1268`), denied October 7, 2024.
   - *In Re Martin Akerman*, Nos. `24-443` (`scotus/72484153`, denied Dec. 16, 2024), `24-514` (`scotus/72484370`, denied Dec. 16, 2024), and `24-567` (`scotus/72484956`, denied Jan. 27, 2025) — three extraordinary writ petitions, all summarily denied.
   - *Martin Akerman v. Nevada National Guard*, No. `23-623` (`scotus/72481441`, denied Feb. 20, 2024); *Martin Akerman v. Sherri Doiron*, No. `23-6710` (`scotus/72481976`, from D.C. Cir. No. `23-5230`, denied Apr. 15, 2024); *Martin Akerman v. United States*, No. `23-1106` (`scotus/72479405`, from CAAF, denied May 13, 2024); and *Martin Akerman v. District of Columbia, et al.*, No. `24-1257` (`scotus/72483756`, denied Oct. 6, 2025).

3. **Comparison with Recent OT2026 Substantive Applications:**
   Corpus priors from October–November 2026 show that unreferred pro se substantive applications without a response request (`26A536` from CADC, `26A606` from CA3, `26A613`, `26A617`, `26A618`, `26A530`, `26A532`, `26A535`, `26A545`, `26A555`, `26A556`) were uniformly denied within days of docketing without calling for a response or referring the matter to the full Court.

---

## 4. Calibration of Secondary Claims and Uncertainties
- **`response-requested-increment` (`0.015`) and `referral-increment` (`0.01`):**
  Because the application is a pro se interlocutory filing in a routine administrative/FOIA dispute that the Court has already declined to review in No. `24-339`, the probability that Chief Justice Roberts calls for a response (`0.015`) or refers the application to the full Court (`0.01`) is minimal.
- **`amicus-increment` (`0.01`):**
  There is no organized amicus interest in Akerman's personal FOIA/MSPB litigation, and chambers denials typically issue within days of docketing.
- **`order-writers` (`0.001` per Justice):**
  In-chambers denials of pro se applications are entered by brief unsigned docket orders without separate opinions.
- **Main Source of Uncertainty:**
  Because `application.txt` was provisioned with `empty_text: true` (a 20-page scanned PDF without an OCR text layer), I cannot inspect the exact text of the relief requested on October 20, 2026 beyond the SCOTUS docket entry (`Application (26A612) for injunctive relief and stay`) and the lower-court docket entries in D.C. Cir. No. `26-5131` and D.D.C. No. `1:23-cv-02574-RDM`. However, even accounting for that document-text gap, the procedural posture and litigation history leave virtually no room for emergency relief.
