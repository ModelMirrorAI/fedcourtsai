# Predictor Rationale: *Corey Duran Berry v. United States* (No. 25-7026)

- **Case ID:** `scotus/73283862`
- **Event ID:** `evt-order-judgment` (`stage: merits`, `moment: grant`, `decision_target: judgment`)
- **Mode & Provisioned Inputs:** `forward` mode (`cutoff: "2026-10-14"`, `snapshot_date: "2026-10-13"`). This forecast is formed from the provisioned docket snapshot `2026-10-13.json` and the provisioned cert-stage filings under `record/documents/` (`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, and `appendix.txt`). Because this cell sits at `moment: grant` (`opened_at: '2026-10-13'`), no merits briefs exist yet (`merits-brief-petitioner.txt` and `merits-brief-respondent.txt` have not been filed).
- **Headline Forecast:** `probability = 0.78` (`granted = 1`, i.e., judgment below disturbed); `judgment = "vacated"`; `predicted_disposition = "other"`; `big_case_score = 0.32`.

---

## 1. Base-Rate Anchor (`metrics/statpack.md`)

Per the merits-stage rules, we do not anchor on `record/context.json`'s `band: "high"` or `distribution_count: 5` (which are spent cert-stage signals). Instead, we anchor on **"The merits docket (granted cases) — Merits Outcomes by Grant Term"** in `metrics/statpack.md`.

The event's `opened_at` is `2026-10-13`, placing the grant in **October Term 2026** (`grant_term = 2026`). Pooling `disturbed` over `parsed` across the ten grant Terms strictly preceding 2026 (`2016 <= T < 2026`, i.e., **OT2016–OT2025**):

| Grant Term | Granted | Excluded (not in granted) | Parsed | Disturbed | Disturbed Rate (parsed) |
|---|---:|---:|---:|---:|---|
| 2025 | 58 | 7 | 0 | 0 | — (n=0) |
| 2024 | 60 | 20 | 58 | 43 | 74.1% (n=58) |
| 2023 | 59 | 12 | 59 | 43 | 72.9% (n=59) |
| 2022 | 56 | 24 | 54 | 38 | 70.4% (n=54) |
| 2021 | 62 | 22 | 60 | 49 | 81.7% (n=60) |
| 2020 | 58 | 51 | 52 | 39 | 75.0% (n=52) |
| 2019 | 56 | 17 | 54 | 42 | 77.8% (n=54) |
| 2018 | 77 | 22 | 75 | 50 | 66.7% (n=75) |
| 2017 | 56 | 48 | 52 | 31 | 59.6% (n=52) |
| 2016 | 62 | 67 | 39 | 25 | 64.1% (n=39) |
| **Pool (OT2016–OT2025)** | **604** | **290** | **503** | **360** | **71.6% (n=503)** |

- **Strictly-prior 10-Term pooled disturbed rate:** **360 / 503 = 71.57% (71.6%)**, which easily clears the 30-parsed-judgment floor (`MERITS_BASE_RATE_MIN_PARSED = 30`) and carries non-null `excluded` counts in every Term (meaning the label-independent grant-to-judgment gap guard has removed cert-order GVRs and summary dispositions from the pool).
- **Coverage note:** Across OT2016–OT2025, `parsed / granted` is `503 / 604` (83.3% coverage); nearly all of the unparsed gap sits in the most recent prior grant Term, OT2025 (`0 / 58` parsed), along with a partial historical parse gap in OT2016 (`39 / 62` parsed), whereas OT2017–OT2024 have 93%–100% parse coverage (`464 / 484` parsed, with 335 disturbed = 72.2%).

---

## 2. Case-Specific Adjustments From the 71.6% Baseline to `0.78`

Starting from the **0.716** base rate for `P(disturbed)`, we adjust upward by **+6.4 percentage points** to **0.78** based on the following factors from the provisioned record:

### A. Upward Drivers
1. **Limited Grant Isolating Question 2:** Berry's petition presented two questions: Question 1 challenged the Eleventh Circuit's *Beeman*/*Fernandez* rule requiring a § 2255 movant to show "historical fact" reliance on § 924(c)'s residual clause (a 7–3 circuit split where the Eleventh Circuit sits in the majority, and on which the Court denied certiorari in *Fernandez v. United States*, No. 24-7240, on October 14, 2025, `scotus/72486702`), while Question 2 challenged the Eleventh Circuit's categorical rule in *Hamilton v. Secretary, Florida Department of Corrections*, 793 F.3d 1261, 1266 (11th Cir. 2015), that binding circuit precedent forecloses a COA under 28 U.S.C. § 2253(c) even when another circuit has resolved the issue in the petitioner's favor (`questions-presented.txt`). On October 13, 2026, the Court granted the IFP motion and granted certiorari **"limited to Question 2 presented by the petition"** (`2026-10-13.json`). When the Court carves out a lopsided 2-circuit minority procedural bar from an IFP habeas petition supported by amicus briefs from Former Federal Judges and NACDL, it rarely does so to affirm.
2. **Strength of Textual and Precedential Support on Question 2:** In *Lozada v. Deeds*, 498 U.S. 430, 432 (1991) (per curiam), the Court held under the pre-AEDPA *Barefoot* standard (codified in § 2253(c)(2), *Slack v. McDaniel*, 529 U.S. 473, 483–84 (2000)) that a court of appeals erred in denying a certificate of probable cause where another circuit had resolved the constitutional issue in the petitioner's favor. And in *Miller-El v. Cockrell*, 537 U.S. 322, 338 (2003), the Court stated directly that *"a claim can be debatable even though every jurist of reason might agree, after the COA has been granted and the case has received full consideration, that petitioner will not prevail."* That statement squarely refutes the Eleventh Circuit's premise in *Hamilton* (App. 2a) that because a three-judge panel must follow circuit precedent, reasonable jurists cannot debate the claim.
3. **Track Record in Fifth/Eleventh Circuit COA Cases:** Across modern AEDPA decisions reviewing Fifth and Eleventh Circuit denials of COAs—including *Miller-El*, 537 U.S. 322 (2003), *Welch v. United States*, 578 U.S. 120 (2016), *Buck v. Davis*, 580 U.S. 100 (2017), and *Ayestas v. Davis*, 584 U.S. 28 (2018)—the Court has consistently rejected overly restrictive circuit gatekeeping rules that collapse the threshold COA inquiry into merits adjudication.

### B. Downward / Tempering Factors (Why `P(disturbed)` Is Not Higher Than `0.78`)
1. **The Solicitor General's Gatekeeping Argument:** In the Brief in Opposition (`brief-in-opposition.txt`, pp. 12–15), the Government argues that § 2253(c)'s gatekeeping purpose is to avoid pointless merits briefing before a three-judge panel that is bound by prior panel precedent to affirm, and that a prisoner can already seek en banc reconsideration or certiorari from the COA denial under *Hohn v. United States*, 524 U.S. 236 (1998). While Petitioner forcefully replies that 11th Cir. R. 22-1(c) / 35-4 bars rehearing en banc of single-judge COA denials (`cert-reply.txt`, pp. 7–8), there is a ~15% chance that five Justices accept a version of the Government's functional argument that § 2253(c)(2) does not compel a futile panel appeal when en banc or Supreme Court review is otherwise available.
2. **Alternative Grounds and DIG Risk (~7%):** The Government's BIO (pp. 15–19) argues that even if *Hamilton* is wrong, Berry cannot make a substantial showing of the denial of a constitutional right because (i) attempted federal carjacking under 18 U.S.C. § 2119 requires "intent to cause death or serious bodily harm" (*Holloway v. United States*, 526 U.S. 1 (1999)), satisfying § 924(c)(3)(A)'s elements clause even after *United States v. Taylor*, 596 U.S. 845 (2022), and (ii) Berry procedurally defaulted his claim by dismissing his direct appeal and cannot show actual innocence of his dismissed Count 4 § 924(c) charge. Although neither the District Court (App. 48a, 51a n.4) nor the Eleventh Circuit (App. 1a–3a) reached those issues, there is a small residual risk that the Court either affirms the denial of a COA on an alternative ground or dismisses the writ as improvidently granted (`dismissed-as-improvidently-granted`, which counts as undisturbed).

---

## 3. Rationale for `judgment: "vacated"`, `votes`, and `big_case_score`

- **Why `vacated` over `reversed`:** In `metrics/statpack.md`, `vacated` (173/360) and `reversed` (171/360) split disturbed judgments almost evenly overall, with `vacated` leading in OT2023 (26 vs. 17) and OT2024 (23 vs. 20). Doctrinally, when the Court corrects an erroneous COA legal standard applied by the court of appeals while leaving unaddressed alternative arguments (here, the § 2119 elements-clause issue and procedural default) open for consideration below, it vacates and remands rather than reversing outright—precisely as it did in *Welch v. United States*, 578 U.S. 120, 134–35 (2016), and *Ayestas v. Davis*, 584 U.S. 28, 50 (2018).
- **Per-Justice Votes (7–2):** Chief Justice Roberts authored *Buck v. Davis*, 580 U.S. 100 (2017) (6–2, reversing a Fifth Circuit COA denial under *Miller-El*), and is predicted to author or join a 7-Justice majority alongside Justices Sotomayor, Kagan, Gorsuch, Kavanaugh, Barrett, and Jackson. Justices Thomas and Alito dissented in *Buck*, 580 U.S. at 128, and Justice Thomas dissented in *Welch*, 578 U.S. at 136; both are predicted to dissent here.
- **Big Case Score (`0.32`):** The case resolves an entrenched 6–2 circuit split on an important recurring question of federal habeas appellate procedure under 28 U.S.C. § 2253(c) and affects en banc access in the Fifth and Eleventh Circuits, but it is a technical procedural ruling rather than a major constitutional or administrative-state controversy.
