# Reasoning and Calibration: *William Maxwell v. Albert Thomas, III, Warden* (`scotus/73281102`, `evt-order-judgment`)

## 1. Headline Numbers

- **`probability` / `claims[judgment-disturbed]`:** `0.88`
- **`granted`:** `1`
- **`predicted_disposition`:** `"other"` (merits-stage event)
- **`judgment`:** `"reversed"`
- **`confidence`:** `0.82`
- **`big_case_score`:** `0.35`

## 2. Evidence Base and Moment Constraints

This is a **forward-mode** merits prediction at **`moment: grant`** (`evt-order-judgment`, opened `2026-06-01`, with `context.cutoff: "2026-06-02"` and `snapshot_provenance: "truncated"`).

- **Provisioned inputs read:**
  - `record/snapshots/2026-06-02.json` (truncated at `2026-06-02`, ending with the June 1, 2026 order granting IFP status and granting certiorari limited to the reformulated First Step Act / § 2241 question; the undated top-level `Other` counsel block reflects the appointment of Brian W. Barnes as amicus curiae in support of the judgment below and several amici supporting petitioner).
  - `record/context.json` (`term: 2025`, `cutoff: "2026-06-02"`, `mode: "forward"`).
  - `record/documents/documents.json` and all five provisioned cert-stage documents:
    1. `petition.txt` (Petitioner William Maxwell's pro se petition for a writ of certiorari, filed August 20, 2025).
    2. `questions-presented.txt` (the petition's Questions Presented section).
    3. `appendix.txt` (containing the Fifth Circuit's unpublished per curiam opinion of March 31, 2025 in No. 23-40653, the Eastern District of Texas's September 18, 2023 Memorandum Order adopting the Magistrate Judge's Report and Recommendation and dismissing on exhaustion grounds, the Magistrate Judge's August 14, 2023 Report and Recommendation, and the Fifth Circuit's June 23, 2025 order denying rehearing).
    4. `brief-in-opposition.txt` (Solicitor General's Brief in Opposition, filed April 20, 2026).
    5. `cert-reply.txt` (Petitioner's Reply Brief filed May 12, 2026 by Supreme Court counsel at Davis Polk & Wardwell LLP and Paul, Weiss, Rifkind, Wharton & Garrison LLP).
- **No merits briefs or argument transcript were provisioned**, which is expected for a `moment: grant` cell cut at `2026-06-02`.

## 3. Base-Rate Anchor (`metrics/statpack.md`)

Per the merits-stage instructions, cert-stage signals (relist count and salience band) are spent and ignored. The anchor is the **strictly-prior pooled disturbed rate** from **"The merits docket (granted cases)"** section in `metrics/statpack.md`:

- **Grant Term (`grant_term`):** Certiorari was granted on June 1, 2026, which falls in **October Term 2025** (`grant_term = 2025`).
- **Lookback Window (`2015 <= T < 2025`):** The committed statpack table contains eight grant Terms strictly prior to OT2025 (`2017` through `2024`), every one of which publishes an explicit `excluded (not in granted)` count (discharging the cert-order vacatur guard).
- **Pooled Counts and Coverage (OT2017–OT2024):**
  - `granted`: `75 + 55 + 74 + 67 + 79 + 56 + 77 + 56 = 545` (plus `34 + 13 + 1 + 1 + 2 + 2 + 0 + 3 = 56` excluded cert-order dispositions not in `granted`).
  - `parsed`: `73 + 55 + 73 + 65 + 69 + 54 + 75 + 52 = 516` (`516 / 545 = 94.7%` coverage across OT2017–OT2024; in the most recent prior Term, OT2024, coverage is `73 / 75 = 97.3%`). This easily clears the 30-parsed-judgment floor.
  - `disturbed`: `50 + 34 + 50 + 46 + 57 + 42 + 50 + 31 = 360` (comprising `235` `reversed`, `115` `vacated`, and `10` `affirmed-in-part-reversed-in-part`; the `156` undisturbed rows comprise `140` `affirmed`, `12` `DIG`, and `4` `equally divided`).
  - **Strictly-Prior Pooled Disturbed Base Rate:** `360 / 516 = 0.6977` (**69.8%**).

## 4. Case-Specific Adjustments from the 69.8% Base Rate

Starting from the **69.8%** strictly-prior merits disturbed rate, I adjust upward to **0.88** (`+18.2` percentage points) for three principal reasons, partially tempered by vehicle and historical-scope risks:

1. **Solicitor General Concession on the Legal Question Presented (`+14%`):**
   In the Brief in Opposition (pp. 7–8), the Solicitor General expressly conceded that the Fifth Circuit's categorical rule—barring a § 2241 habeas petition solely because application of First Step Act time credits toward halfway-house or home-confinement transfer would not accelerate total release from custody—is inconsistent with *Jones v. Hendrix*, 599 U.S. 465, 475 (2023) (which stated that § 2241 encompasses a prisoner's claim *"that he is being detained in a place or manner not authorized by the sentence, that he has unlawfully been denied parole or good-time credits, or that an administrative sanction affecting the conditions of his detention is illegal"*), as well as *Skinner v. Switzer*, 562 U.S. 521, 534 (2011), and *Woodall v. Federal Bureau of Prisons*, 432 F.3d 235, 243 (3d Cir. 2005). Because both the Petitioner and the United States urge the Court to reject the Fifth Circuit's bright-line rule, and the judgment below is defended only by a Court-appointed amicus curiae, the historical probability of reversal or vacatur rises substantially above the ~70% baseline.
2. **The Grant Order Narrowed the Case to the Pure Legal Question and Rejected Cert-Stage Vehicle Objections (`+7%`):**
   The SG opposed certiorari not on the merits of QP1, but on two vehicle grounds: (a) that the District Court had dismissed on administrative exhaustion, and (b) that Maxwell's pro se filings focused on the Elderly Offender Pilot Program and § 3621(b) rather than FSA earned time credits under 18 U.S.C. §§ 3631–3635. The Supreme Court considered those exact objections, declined QP2 (exhaustion), and granted certiorari limited to a cleanly reformulated question on FSA time credits under §§ 3631–3635. That deliberate narrowing signals a strong institutional commitment to resolving the 4–2 circuit split on the § 2241 question and leaving case-specific exhaustion/preservation defenses for remand.
3. **Textual and Remedial Alignment Across Judicial Philosophies (`+3%`):**
   Under 18 U.S.C. § 3632(d)(4)(C), earned time credits *"shall be applied toward time in prerelease custody or supervised release,"* and the BOP Director *"shall transfer eligible prisoners, as determined under section 3624(g), into prerelease custody or supervised release."* Holding that § 2241 covers credits applied toward supervised release while forcing prisoners to bring a non-existent *Bivens* action (as the Fifth Circuit suggested below) for credits applied toward halfway-house or home-confinement transfer would split a single mandatory statutory command in half and leave federal prisoners with no judicial remedy at all.
4. **Downward Adjustments / Undisturbed Risks (`-5.8%`, leaving `0.12` undisturbed):**
   - **Risk of Affirmance (`~0.08`):** The Court-appointed amicus will likely argue (1) that as an originalist and statutory matter under 28 U.S.C. § 2241 and 18 U.S.C. § 3624(g)(2), a prisoner in a halfway house or home confinement remains in BOP "custody," so a transfer from prison to prerelease custody does not "release" the prisoner from custody and falls outside the core of habeas under *Preiser v. Rodriguez*, 411 U.S. 475 (1973); and (2) in the alternative, that the judgment of affirmance can be sustained on administrative-exhaustion or pleading-preservation grounds. While the Supreme Court rarely affirms on an unreached fact-bound alternative ground ("a court of review, not of first view"), there is a modest chance that an originalist majority or alternative-ground disposition affirms.
   - **Risk of DIG (`~0.04`):** Because the underlying district court record was litigated pro se and focused heavily on CARES Act / Elderly Offender Pilot Program / § 3621(b) requests alongside First Step Act references, there remains a non-trivial ~4% chance that merits briefing persuades the Court that the factual record is too muddled to cleanly tee up §§ 3631–3635, resulting in a DIG (which counts as undisturbed).

## 5. Choice of Modal Judgment Label (`reversed` vs. `vacated`) and Vote Lineup

- **`reversed` vs. `vacated`:** Both `reversed` and `vacated` count as disturbed (`granted = 1`). Within the `0.88` disturbed mass, I place roughly `0.48` on `reversed` and `0.40` on `vacated`. Although the Fifth Circuit left the District Court's exhaustion ground unreached (a posture in which the Court sometimes vacates and remands), in the 2017–2024 statpack pool `reversed` outnumbers `vacated` by more than 2 to 1 (`235` vs. `115`, and `38` vs. `12` in OT2024), and in prior habeas/civil-rights boundary cases from the Fifth and Eleventh Circuits (*Skinner v. Switzer*, 562 U.S. 521, 537 (2011); *Nance v. Ward*, 597 U.S. 159, 174 (2022); *Hill v. McDonough*, 547 U.S. 573, 585 (2006); *Nelson v. Campbell*, 541 U.S. 637, 651 (2004)), the Court's decretal line was *"reversed, and the case is remanded for further proceedings consistent with this opinion."* Accordingly, `reversed` is the modal single-label forecast.
- **Per-Justice Votes (`votes`):** For every sitting Justice, the individual marginal probability of joining the judgment disturbing the Fifth Circuit's ruling exceeds 50%. Even for Justices Thomas and Alito—the two Justices most receptive to historical common-law limits on habeas—Justice Thomas authored the 6-Justice majority opinion in *Jones v. Hendrix*, 599 U.S. at 475, containing the exact formulation the Solicitor General and Petitioner invoke. Thus, predicting all nine Justices in the `majority` maximizes expected per-Justice accuracy, with a 7–2 or 8–1 split (Thomas and/or Alito dissenting) as the main source of lineup uncertainty.
