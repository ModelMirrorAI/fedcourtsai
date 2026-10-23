# Predictor Rationale (`scotus/73292081`, `evt-order-relist-disposition`)

## Summary of Numbers

- **`granted`**: `0` (`predicted_disposition`: `"denied"`)
- **`probability` (`disposition`)**: `0.07`
- **`relist-increment`**: `0.42`
- **`cvsg-increment`**: `0.005`
- **`summary-disposition-route`**: `0.35`
- **`dissent-from-denial`**: `0.28`
- **`big_case_score`**: `0.35`

## Inputs Consulted

I read the provisioned baseline snapshot (`2026-10-07.json`), `context.json`, `event.yaml`, and all four provisioned filings listed in `documents.json` (`questions-presented.txt`, `petition.txt` including the appended Fifth Circuit opinion at App. 1a–19a and Southern District of Texas opinion at App. 22a–48a, `brief-in-opposition.txt`, and `cert-reply.txt`), along with `metrics/statpack.md` and one corpus query (`uv run fedcourts query --court scotus --era 2020s --limit 5`). None of the provisioned documents had `empty_text: true` or `ocr_derived: true`. No `Vide` or related dockets were linked.

## Base-Rate Anchoring (`metrics/statpack.md`)

1. **Primary Salience-Band Anchor (`elevated`, `sal-v4`)**:
   - `context.json` freezes `band: "elevated"`, `salience_version: "sal-v4"`, `distribution_count: 2`, `cvsg_date: null`, `term: 2025`, and `mode: "forward"`.
   - In `metrics/statpack.md` (*Segment base rate by salience band (sal-v4)*), pooling the bracketed `reached` figures for the `elevated` band across all rendered Terms strictly preceding `term: 2025` (OT2017–OT2024) yields:
     - OT2024: 17.9% (`n=336`, ~60.1 grants)
     - OT2023: 17.5% (`n=354`, ~62.0 grants)
     - OT2022: 19.0% (`n=300`, ~57.0 grants)
     - OT2021: 20.5% (`n=342`, ~70.1 grants)
     - OT2020: 16.1% (`n=397`, ~63.9 grants)
     - OT2019: 13.8% (`n=334`, ~46.1 grants)
     - OT2018: 15.9% (`n=347`, ~55.2 grants)
     - OT2017: 17.5% (`n=400`, ~70.0 grants)
     - **Pooled strictly-prior `elevated` reached rate (OT2017–OT2024)**: `484.4 / 2810` = **17.2%** (`n=2810`). (Including OT2025's `13.5%, n=312` gives `526.5 / 3122 = 16.9%`.)

2. **Cross-Check Cuts**:
   - **Relist-count cut (paid scored segment)**:
     - Bucket `1` (`n=2521` resolved): `granted 8.3%`, `gvr 5.1%`, `denied 85.7%`, `dismissed 1.0%` (grant family = **13.4%**).
     - Bucket `2` (`n=487` resolved): `granted 27.5%`, `gvr 13.1%` (grant family = **40.6%**).
     - Bucket `3+` (`n=481` resolved): `granted 22.5%`, `gvr 14.3%` (grant family = **36.8%**).
     - Pooling every bucket from `1` up (`n = 2521 + 487 + 481 = 3489`) gives a pooled grant-family rate of **20.4%** (`12.9%` plenary grant + `7.5%` GVR).
   - **Capital-case cut (paid scored segment)**:
     - Paid `capital` petitions (`n=181` resolved) have a grant-family rate of **17.1%** (`granted 11.6%`, `gvr 5.5%`, `denied 82.9%`), compared to `6.4%` for unmarked paid petitions (`n=13477`).
   - **Originating circuit (`ca5`)**:
     - Across modern discretionary-cert dockets from the Fifth Circuit (`n=5396` resolved), the base rate is `denied 94.7%, gvr 2.1%, granted 1.6%, dismissed 1.6%` (grant family `3.7%`).

## Adjustments from the Anchor (`0.172` → `0.07`)

### Upward Signal: True Post-Conference Relist Plus Call for the Record
Unlike a pre-conference reschedule (which the `dist-v2` distribution counter and `elevated` band pool alongside true relists), the docket here shows a genuine conference relist accompanied by an affirmative request for the lower-court record: the petition was distributed for the September 28, 2026 conference, the Court requested and received the electronic record from the Fifth Circuit and Southern District of Texas on September 30, 2026, and the petition was relisted on October 7, 2026 for the October 9, 2026 conference. That confirms active chambers engagement with the record.

### Strong Downward Factors: Fatal Vehicle Flaws and *Shinn v. Ramirez*

1. **Unchallenged Independent Holding Under 28 U.S.C. § 2244(b)(2)(B)(ii) (Actual Innocence)**:
   - To proceed on a second-or-successive federal habeas petition under § 2244(b)(2)(B), a state prisoner must satisfy *both* § 2244(b)(2)(B)(i) (due diligence) *and* § 2244(b)(2)(B)(ii) (clear and convincing evidence that, but for constitutional error, no reasonable factfinder would have found him guilty of the underlying offense).
   - In Part III.B of its published opinion (`Vasquez v. Guerrero`, 161 F.4th 298; Pet. App. 17a–19a), the Fifth Circuit explicitly held that even if Vasquez could overcome § 2244(b)(2)(B)(i), he failed § 2244(b)(2)(B)(ii) because compelling independent evidence established his mens rea in beating four-year-old Miranda Lopez to death—including Vasquez's admission that he struck her head, extensive contusions and fatal blunt-force brain trauma, clumps of hair ripped from her head, and severe sexual-assault injuries providing a motive to silence her (as well as the fact that the jury itself had the Toxicology Report).
   - Crucially, **none of the Petition's three Questions Presented challenges the Fifth Circuit's § 2244(b)(2)(B)(ii) holding**, and the BIO highlights this outcome-determinative defect (BIO 25–26). Even in the Cert Reply (at 6–7), Petitioner argues only that challenging the § 2244(b)(2)(B)(ii) ruling is unnecessary because it was brief and did not weigh the state DA's position. Because reversing on QP 1, QP 2, or QP 3 cannot alter the judgment of dismissal without disturbing § 2244(b)(2)(B)(ii), the case is an exceptionally poor vehicle for plenary review.

2. **Weak Circuit-Split Claims and Controlling Precedent (*Shinn v. Ramirez*)**:
   - **QP 1**: Petitioner claims a split with the Fourth Circuit over whether § 2244(b)(2)(B)(i) bars successive ineffective-assistance-of-trial-counsel (IATC) claims when prior counsel lacked diligence. As the BIO demonstrates (BIO 17–23), Petitioner's primary Fourth Circuit authority (*Jeffus v. United States*, 2022 WL 19333404) is an unpublished, non-precedential four-sentence gatekeeping order under 28 U.S.C. § 2255(h), whereas published Fourth Circuit precedent (*Evans v. Smith*, 220 F.3d 306, 323–24 (4th Cir. 2000)) applies § 2244(b)(2)(B)(i) the same way as the Fifth Circuit. Moreover, *Shinn v. Ramirez*, 596 U.S. 366, 380–85 (2022), squarely rejected importing *Martinez v. Ryan* equitable exceptions into AEDPA's statutory requirements and reaffirmed that a habeas petitioner is bound by prior counsel's agency.
   - **QP 2**: Challenging whether reasonable persistence would have noticed that the one-page Toxicology Report introduced at the 1999 trial stated both "NEGATIVE" (under Drugs of Abuse Screen) and "POSITIVE" (under Confirmed GC/MS) is a classic factbound request for error correction. Further, as both the state habeas court and the district court noted (Pet. App. 36a–39a), no expert ever examined the underlying laboratory data to show that the quantitative GC/MS confirmation test (rather than the screen line) was erroneous.
   - **QP 3**: The dispute between the Nueces County District Attorney (who supported relief in the 2015 state habeas proceeding and sought to join Vasquez's motion in the Fifth Circuit) and the Texas Attorney General (who represents Respondent TDCJ Director Guerrero in federal court) is not presented cleanly here. First, § 2244(b)(2)(B) is jurisdictional (*Panetti v. Quarterman*, 551 U.S. 930, 942 (2007)), so no prosecutor could waive or stipulate around it in federal court. Second, Texas statutory law (Tex. Code Crim. Proc. art. 2.01; *Saldano v. Roach*, 363 F.3d 545 (5th Cir. 2004)) divides authority between local DAs in state habeas proceedings and the Attorney General in federal habeas actions against the TDCJ Director. Third, the Court recently denied certiorari in *Escobar v. Texas*, No. 25-5687 (Mar. 30, 2026), which raised local-DA confession of error on direct review from state court without AEDPA's jurisdictional successive-petition bar.

3. **Why the Record Request Points Toward a Separate Writing Rather Than a Grant**:
   - In capital habeas litigation, a post-Long Conference call for the record followed by a relist is a recurring pattern when one or two Justices are scrutinizing the trial and state habeas record to draft a dissent from denial (or statement respecting denial) highlighting troubling forensic evidence and trial-counsel failures, or when chambers verify whether the Fifth Circuit's alternative holdings hold up against the record. Given the unchallenged § 2244(b)(2)(B)(ii) barrier and *Shinn v. Ramirez*, the probability of assembling four votes to grant (`0.07`) is well below the `elevated` reached anchor (`0.172`), while the conditional probability of a dissent or statement respecting denial (`0.28`) and of at least one further relist while that review/writing proceeds (`0.42`) are both high.

## Rationale for Remaining Claims and `big_case_score`

- **`relist-increment` (`0.42`)**: In the statpack, `968 / 3489 = 27.7%` of resolved paid petitions in `relist_bucket >= 1` reach `2+` relists. Because this case is a true post-conference relist where the record arrived on September 30, 2026 (just nine days before the October 9 conference) and involves a capital record likely to draw a separate writing, the forward hazard of at least one more distribution (`distribution_count >= 3`) is substantially higher at `0.42`.
- **`cvsg-increment` (`0.005`)**: State prisoner § 2254 habeas petition with no federal interest and a record call already issued.
- **`summary-disposition-route` (`0.35`)**: In the statpack, GVRs account for `32.2%` of grants in paid capital cases (`5.5% / 17.1%`) and `36.8%` of grants in `relist_bucket >= 1` (`7.5% / 20.4%`). Because the Court already called for the record and QP 2 is fact-intensive, a summary per curiam disposition or GVR accounts for `0.35` of the conditional grant probability.
- **`dissent-from-denial` (`0.28`)**: Elevated by the capital posture, the September 30 record request, the facially contradictory toxicology report, and the local District Attorney's support for relief.
- **`big_case_score` (`0.35`)**: Decoupled from grant odds, a decision on the merits addressing AEDPA § 2244(b)(2)(B)(i) diligence imputation or state-versus-county prosecutorial authority in federal habeas would be significant for capital habeas practitioners (`0.35`), though technical and procedural compared to major constitutional rulings.
