---
case_id: scotus/9026000117
event_id: evt-petition-disposition
predictor_id: gemini-baseline
run_id: 20261109T171058Z
---

# Prediction Rationale: *Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.* (No. 26-117)

- **Stage:** `cert` (`moment: distribution`, direct appeal on Jurisdictional Statement under 28 U.S.C. § 1253)
- **Predicted `granted`:** `1` (`true`)
- **Predicted `probability`:** `0.85`
- **Predicted `predicted_disposition`:** `gvr`
- **Predicted `big_case_score`:** `0.72`

## 1. Provisioned Record and Retrieval Basis

This prediction is formed from the provisioned snapshot (`record/snapshots/2026-11-09.json`), `record/context.json`, `record/same-question.json`, and the provisioned filings in `record/documents/` (`petition.txt`, `appendix.txt`, `questions-presented.txt`, and `documents.json`), supplemented in `forward` mode by `fedcourts query` corpus lookups and CourtListener MCP retrieval of the Supreme Court's June 2, 2026 *Per Curiam* stay opinion (*Allen v. Milligan*, No. 25A1314, `opinion_id=11336479`, 146 S. Ct. 1377) and the three-judge district court's May 26, 2026 and July 20, 2026 orders (`Milligan v. Allen`, N.D. Ala. No. 2:21-cv-01530-AMM, Docs. 537 and 544).

Two notes on the provisioned document record (`documents.json`):
1. In `petition.txt` (which contains both the 40-page Jurisdictional Statement and Appendix A, the May 26, 2026 Preliminary Injunction order), a `[pipeline note]` at the end of the file indicates that the last 1,312 characters of Appendix A were omitted to fit the 150,000-character cap. Because those omitted pages (pages 77–78 of `Doc. 537`, App. 105a–106a) contained the operative remedial paragraphs of the preliminary injunction, I retrieved `Doc. 537` (`recap_document_id=480335147`) via CourtListener MCP to read the exact scope of the injunction.
2. The snapshot shows that Appellees Evan Milligan, et al. filed a Motion to Dismiss or Affirm on September 24, 2026 and Appellants filed a Reply on October 7, 2026, neither of which was staged in `record/documents/`.

## 2. Base-Rate Anchoring (`context.json` and `metrics/statpack.md`)

1. **Salience Band Anchor (`cert_anchor`):** `record/context.json` freezes `band: "high"` under `salience_version: "sal-v8"`, `distribution_count: 3`, `cvsg_date: null`, and `term: 2026`. The harness-computed `cert_anchor` rate (pooled over the 10-Term lookback window strictly preceding OT2026, i.e., OT2017–OT2025 in `metrics/statpack.md`'s **"Segment base rate by salience band (sal-v8)"** table) is **`0.3484` (34.8%)** over `n = 772` weighted resolved `high`-band cases.
2. **Relist, CVSG, and Amicus Cuts (`metrics/statpack.md`):**
   - **Relist count (`relist_bucket = 2`, corresponding to `distribution_count = 3`):** In **"Cert petitions by relist count (paid scored segment)"**, petitions at 2 relists (`n = 495` resolved) have a resolved breakdown of `granted 28.3%, gvr 12.9%, denied 57.4%, dismissed 1.4%` — a combined grant-family rate (`granted` + `gvr`) of **41.2%**. For `relist_bucket = 3+` (`n = 483` resolved), the grant-family rate is **37.3%** (`granted 23.2%, gvr 14.1%`).
   - **CVSG status (`cvsg = none`):** In **"Cert petitions by CVSG status (paid scored segment)"**, non-CVSG petitions (`n = 13550` resolved) have a base rate of `granted 4.1%, gvr 2.3%, denied 92.4%, dismissed 1.2%` (**6.4%** grant family).
   - **Amicus count (`cert_amicus = 0`):** The snapshot records 0 cert-stage amicus briefs. In **"Cert petitions by amicus-brief count (paid scored segment)"**, the `0` bucket (`n = 11109` resolved) has a base rate of `granted 2.0%, gvr 1.8%, denied 95.0%, dismissed 1.3%` (**3.8%** grant family).

## 3. Adjustments From the Anchor (`0.3484` → `0.85`)

Starting from the `0.3484` (34.8%) `high`-band anchor (and the 41.2% grant-family rate for twice-relisted paid cases), three decisive case-specific features move my `granted` probability up to **`0.85`** and point specifically to **`gvr`** as the modal `predicted_disposition`:

### A. Corpus Coding of Three-Judge District Court (§ 1253) and *Munsingwear* Vacaturs
This is a mandatory direct appeal under 28 U.S.C. § 1253 from a three-judge district court preliminary injunction, traveling alongside two companion dockets identified in `record/same-question.json`: No. 26-118 (*Allen v. Singleton*, also a § 1253 appeal) and No. 26-116 (*Allen v. Caster*, a petition for certiorari before judgment to the Eleventh Circuit).

Corpus queries confirm that whenever the Supreme Court disposes of a three-judge district court direct appeal at the jurisdictional-statement stage by vacating the order/judgment below and remanding — whether in light of an intervening precedent, for lack of jurisdiction, or as moot under *United States v. Munsingwear, Inc.*, 340 U.S. 36 (1950) — the corpus records the disposition as **`gvr`** (`granted: 1`):
- In the immediately preceding appeal in this very case, *Allen v. Milligan* (`No. 25-274`, `scotus/73275213`) and *Allen v. Singleton* (`No. 25-273`, `scotus/73275215`), the May 11, 2026 order vacating the May 2025 permanent injunction and remanding in light of *Louisiana v. Callais*, 146 S. Ct. 1131 (2026), is coded as `disposition: "gvr"`.
- Other recent three-judge district court redistricting vacaturs on jurisdictional statements — *State Board of Election Commissioners v. Mississippi State Conference of the NAACP* (`No. 25-234`, `scotus/73275174`, May 18, 2026), *Garcia v. Hobbs* (`No. 25-901`, `scotus/73279753`, Oct. 5, 2026), *Trevino v. Hobbs* (`No. 25-918`, `scotus/73279880`, Oct. 5, 2026), and *Garcia v. Hobbs* (`No. 23-467`, `scotus/72480045`, Feb. 20, 2024) — are all coded in the corpus as `disposition: "gvr"`.
- Likewise, *Munsingwear* vacaturs of moot preliminary injunctions — such as *Speech First, Inc. v. Sands* (`No. 23-156`, `scotus/68305186`), *Biden v. Feds for Medical Freedom* (`No. 23-60`, `scotus/65876852`), and *Kendall v. Doster* (`No. 23-154`, `scotus/72479704`) — are uniformly coded as `disposition: "gvr"`.

### B. The Supreme Court's June 2, 2026 *Per Curiam* Stay Opinion (`146 S. Ct. 1377`)
On June 2, 2026, a six-Justice majority stayed the exact May 26, 2026 preliminary injunction under appeal here and published a four-page *Per Curiam* opinion holding that *"The State is likely to succeed on the merits as to both claims"* (*Allen v. Milligan*, 146 S. Ct. at 1381):
- On Fourteenth Amendment intentional vote dilution, the Court held that the district court failed to apply the presumption of legislative good faith under *Alexander v. South Carolina State Conference of the NAACP*, 602 U.S. 1, 10 (2024).
- On both the constitutional and VRA § 2 claims, the Court held that the district court departed from *Callais* by excusing the plaintiffs' failure to produce an alternative map performing "just as well" on the State's traditional nonracial criteria (keeping the two Gulf Coast counties, Mobile and Baldwin, intact) and by relying on partisan voting differences to find racially polarized voting.

Because the Court has already held in a published opinion in this very case that the May 26, 2026 preliminary injunction rested on legal error, the Court will not affirm the order or leave it standing on the district court's docket.

### C. Completion of the 2026 Election Cycle and *Munsingwear* / Remand Posture
Reading the un-truncated remedial paragraphs of `Doc. 537` at page 77 (via CourtListener MCP `recap_document_id=480335147`) reveals why the Court held `26-116`, `26-117`, and `26-118` from the October 16, 2026 Conference across the November 3, 2026 general election to the November 6 and November 13, 2026 Conferences:
- The May 26, 2026 order preliminarily enjoined the Secretary of State **only** *"from conducting the 2026 congressional elections according to the 2023 Plan"* and ordered use of the Special Master Plan for *"all remaining events comprising Alabama's 2026 congressional elections."*
- Because of the June 2, 2026 stay, Alabama conducted both the August 11, 2026 special primary and the November 3, 2026 general election under the 2023 Plan.
- Meanwhile, on July 20, 2026 (`Doc. 544`, `recap_document_id=492999516`), the district court stayed all proceedings on the permanent-injunction remand (which will govern the 2028 and 2030 elections) pending the Supreme Court's resolution of this appeal.

Now that the November 3, 2026 general election has occurred, the 2026-only preliminary injunction is moot as to the 2026 election. Under *Munsingwear*, 340 U.S. at 39, when an interlocutory injunction stayed by the Supreme Court expires or becomes moot while the appeal is pending, the standard disposition is to **vacate the order below and remand** (`gvr`). And even if the Court vacates and remands on the merits in light of *Callais* and the June 2, 2026 *Per Curiam* stay opinion rather than on mootness grounds, the resulting order is still a vacatur and remand (`gvr`).

### D. Secondary Risks and Uncertainty (`0.15` Non-Grant Probability)
Why is `probability` `0.85` rather than `0.95+`?
- My main uncertainty is the ~15% chance that, because the 2026 election has now passed and Appellees filed a Motion to Dismiss or Affirm (whose text was not provisioned), the Court enters a one-line order stating *"The appeal is dismissed as moot"* without formally vacating the May 26, 2026 order. Under the pipeline's outcome schema, a dismissal of the appeal without vacatur maps to `predicted_disposition: "dismissed"` (`granted: 0`).
- Within the `0.85` grant-family probability, I assign ~72% unconditional probability to `gvr` (vacatur and remand), ~9% to `summary-reversal` (as requested by Appellants), and ~4% to `granted` (noting probable jurisdiction for full briefing and oral argument, which is unlikely given the interlocutory, moot 2026-election posture and the pending remand proceedings below). Thus, conditional on a grant, `summary-disposition-route` is `0.95` (`0.81 / 0.85`).

## 4. Rationale for Secondary Claims and `big_case_score`

- **`relist-increment` (`0.35`):** In the statpack, `relist_bucket = 2` (`n = 495`) and `relist_bucket = 3+` (`n = 483`) are nearly equal in size, indicating that roughly half of petitions reaching a second relist are distributed at least once more. Here, however, the primary reason for the relists from October 16 to November 6 and November 13 was waiting for the November 3, 2026 general election to pass and coordinating the three companion dockets (`26-116`, `26-117`, `26-118`). I therefore place `relist-increment` slightly below 50% at `0.35`.
- **`cvsg-increment` (`0.01`):** A CVSG is virtually impossible at the third distribution of a stayed state redistricting appeal where the Court has already issued a *Per Curiam* stay opinion.
- **`dissent-from-denial` (`0.15`) and `order-writers`:** If the appeal is dismissed without vacatur, there is a modest (15%) chance that Justice Thomas or Justice Alito dissents from the failure to vacate or reverse. Across all dispositions (chiefly a `gvr`), Justice Jackson (0.18) and Justice Sotomayor (0.12) have the highest individual writing probabilities given Justice Jackson's June 2, 2026 dissent (joined by Justices Sotomayor and Kagan), while Justices Thomas (0.08) and Kavanaugh (0.08) occasionally write concurring statements in VRA § 2 / *Munsingwear* orders.
- **`big_case_score` (`0.72`):** The underlying Alabama redistricting dispute is a marquee voting-rights battle following *Allen v. Milligan*, 599 U.S. 1 (2023), and *Louisiana v. Callais*, 146 S. Ct. 1131 (2026), but the stakes of *this specific appeal* are tempered by its interlocutory posture (a preliminary injunction limited to the 2026 election, which the Court already stayed on June 2, 2026 while permanent-injunction remand proceedings await below).

## Key factors

- **Prior Supreme Court Per Curiam Stay Opinion (`Allen v. Milligan`, 146 S. Ct. 1377)** — On June 2, 2026, a six-Justice majority stayed the May 26, 2026 preliminary injunction in a published *Per Curiam* opinion holding that the district court departed from *Alexander* and *Callais*, strongly shifting the probability far above the 34.8% `high`-band anchor toward vacatur (`gvr`).
- **Passage of the November 3, 2026 General Election and *Munsingwear* Practice** — Because the May 26, 2026 preliminary injunction (`Doc. 537` at 77) applied only to the 2026 congressional elections and the Court relisted the appeal past election day to the November 6 and November 13 Conferences, standard *Munsingwear* practice calls for vacating the moot preliminary injunction order and remanding (`gvr`).
- **Uniform Corpus Coding of § 1253 and *Munsingwear* Vacaturs as `gvr`** — Corpus priors confirm that summary orders vacating and remanding three-judge district court redistricting judgments (including `25-273` and `25-274` in this litigation, `25-234`, `25-901`, and `25-918`) and *Munsingwear* vacaturs of preliminary injunctions (`23-60`, `23-154`, `23-156`) are consistently recorded as `gvr` (`granted: 1`).
- **Interlocutory Posture with Paused Remand Proceedings Below (`Doc. 544`)** — Because the district court stayed the permanent-injunction remand proceedings on July 20, 2026 awaiting the outcome of this appeal, a summary vacatur and remand (`summary-disposition-route: 0.95`) is far more likely than setting a moot 2026-election preliminary injunction for full merits briefing and oral argument.
- **Residual Risk of Simple Mootness Dismissal Without Vacatur** — The primary downward adjustment (keeping `probability` at `0.85` rather than higher) is the ~15% possibility that the Court simply dismisses the appeal as moot (`dismissed`, `granted: 0`) following the November 3, 2026 election rather than entering a vacatur-and-remand order.
