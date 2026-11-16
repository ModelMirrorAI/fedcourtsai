# Predictor Rationale (`scotus/9026000292` / `evt-order-cvsg-disposition`)

## Bottom-Line Forecast

- **`probability` (`P(any grant)`):** `0.39` (`granted = 0`, `predicted_disposition = "denied"`)
- **Implicit disposition breakdown:** `denied` ~0.59, `granted` (plenary) ~0.34, `gvr` ~0.05, `dismissed` ~0.02
- **`claims`:** `disposition = 0.39`, `relist-increment = 0.98`, `cvsg-increment = 0.0`, `summary-disposition-route = 0.13`, `dissent-from-denial = 0.14`
- **`big_case_score`:** `0.85`

## Inputs Read and Record State

This cell runs in **`forward` mode** (`record/context.json`: `mode: "forward"`, `cutoff: "2026-11-17"`, `cut_kind: "date"`) at `stage: cert`, `moment: cvsg`, opened on November 16, 2026—the day the Court invited the Solicitor General to file a brief expressing the views of the United States.

From `data/cases/scotus/9026000292/record/`, I read:
1. **Snapshot:** `snapshots/2026-11-16.json` (paid cert petition No. 26-292, docketed Sept. 4, 2026; two conference distributions for Nov. 6 and Nov. 13, 2026; leave to file supplemental brief granted Nov. 16, 2026; CVSG entered Nov. 16, 2026; Justice Kagan recused under 28 U.S.C. § 455(b)(3)).
2. **Conditioning & Companion Files:** `context.json`, `same-question.json` (`0` petitions above the 0.5 cosine threshold out of 15,910 indexed), and `related/related.json` along with `related/26-293.json` (*Kathleen Ashton, et al. v. The Taliban, et al.*, `relation: "Vide"`, also CVSG'd Nov. 16 with Justice Kagan recused) and `related/26-294.json` (*James Owens, et al. v. The Taliban, et al.*, `relation: "vided-amicus"` with 1 shared amicus brief, also CVSG'd Nov. 16 **without** Justice Kagan recused).
3. **Provisioned Documents (`record/documents/`):** `documents.json`, `questions-presented.txt`, `petition.txt`, `appendix.txt`, and `lower-court-docket.txt`.
   - *Pipeline caps & unstaged filings:* `petition.txt` carried two `[pipeline note: …]` cuts at the 150,000-character cap omitting 59,250 characters of Appendix A (the TRIA section and Judge Sullivan's dissent in `152 F.4th 339`) and 62,057 characters of Appendix B (the en banc concurrences and dissents in `170 F.4th 100`). In addition, `lower-court-docket.txt` recorded `dissent noted: not found` on Second Circuit entry 315 despite two published dissents joined by five judges, and `documents.json` (fetched Nov. 9, 2026) lacked `brief-in-opposition.txt` (no respondent appeared—the Taliban defaulted and garnishee FRBNY took no position) as well as Petitioners' Oct. 30, 2026 supplemental brief (leave granted Nov. 16, 2026) and the two Oct. 5, 2026 amicus briefs.
   - Because retrieval is unrestricted in `forward` mode, I retrieved the full text of both Second Circuit decisions (`152 F.4th 339` and `170 F.4th 100`) and *Exxon Mobil Corp. v. Corporación CIMEX, S.A.* (decided June 23, 2026), *Stansell II* (`771 F.3d 713`), and *Bennett* (`825 F.3d 949`) via the CourtListener MCP server, read the Oct. 30 supplemental brief and the two Oct. 5 amicus briefs (Iowa + 30 States supporting petitioners; Afghan UN Chargé d'Affaires Naseer A. Faiq opposing certiorari) from the `supremecourt.gov` URLs in the snapshot, and checked the status of Executive Order 14064 (continued by President Trump in February 2025 and February 2026).

## Base-Rate Anchoring (`metrics/statpack.md` and `record/context.json`)

1. **Frozen Salience-Band Anchor (`cert_anchor`):** Under `salience_version: "sal-v8"`, this petition sits in `band: "high"` (`distribution_count: 2`, `cvsg_date: "2026-11-16"`). Its frozen 10-Term `cert_anchor.rate`—the exact yardstick against which Brier skill is scored—is **`0.3497` (35.0%)**.
2. **Amicus-Adjusted Reference (`cert_amicus_line`):** The snapshot records `cert_amicus_briefs: 2` (Iowa and 30 States in support; Chargé d'Affaires Faiq in opposition). Under `amicus-line-v2` (`arm: "some"`, `arm_resolved: 543`), `cert_amicus_line.rate` is **`0.3517` (35.2%)**.
3. **Statpack Signal Cuts (`metrics/statpack.md`, paid scored segment):**
   - **CVSG status (`cvsg`, `n = 166` resolved, 17 open):** `denied 62.0%`, `granted 29.5%`, `gvr 6.0%`, `dismissed 2.4%`—a combined grant-family rate (`granted` + `gvr`) of **`35.5%`** (compared to `6.3%` across `13,638` resolved non-CVSG paid petitions).
   - **Relist count (`relist_bucket = 2` corresponds to 3 distributions; at `distribution_count = 2` / 1 relist, `n = 2,539` resolved):** `granted 8.3%, gvr 5.2%`, though here the second conference produced a CVSG, moving the case into the `cvsg` / `high` band population.
   - **Cert amicus count (`2+`, `n = 1,453` resolved):** `denied 76.0%, granted 18.2%, gvr 4.5%, dismissed 1.2%` (a marginal cut that sits below the CVSG cut because most 2+-amicus petitions do not draw a CVSG).
   - **Originating circuit (`ca2`, `n = 2,196` resolved):** `denied 92.9%, granted 2.5%, dismissed 2.3%, gvr 2.2%` (`4.7%` grant+GVR overall, slightly above the ~3.5% paid circuit median).

All three relevant anchors (`cert_anchor` = 35.0%, `cert_amicus_line` = 35.2%, `statpack` CVSG cut = 35.5%) converge tightly around **35%**.

## Case-Specific Adjustments From the 35.0% Anchor

To avoid narrative bias on a dramatic $3.5 billion case, I decompose the post-CVSG outcome by conditioning on the Solicitor General's forthcoming recommendation:

### 1. Upward Pressures (+11 to +12 percentage points before opposing factors)
- **Unusually strong 5-judge Second Circuit en banc dissent on the exact statutory QP:** While the Second Circuit dissenters divided over whether Executive recognition of the State of Afghanistan is conclusive under the FSIA (the issue in *Owens*, No. 26-294, where Judge Menashi, Judge Nardini, and Judge Lohier agreed with the panel majority), **all five dissenting active judges**—Chief Judge Livingston and Judges Sullivan, Bianco, Park, and Menashi—agreed that the two-senior-judge panel majority's sua sponte TRIA § 201(a) "blocking-date" rule has no foothold in statutory text, was never briefed by any party, and relied on appellate fact-finding outside the record. Tellingly, Judge Nardini's concurrence in the denial of rehearing en banc (joined by Judge Lohier) defended *only* the panel's FSIA recognition holding and said nothing in defense of the TRIA blocking-date rule.
- **High textualist vulnerability + recent SCOTUS terrorism/FSIA receptivity:** TRIA § 201(a)'s present-tense directive that "the blocked assets of that terrorist party (including the blocked assets of any agency or instrumentality of that terrorist party) shall be subject to execution" tracks standard time-of-execution attachment principles. This Court recently showed unanimous or near-unanimous willingness to reject extra-textual barriers in terrorism/sanctions statutes (*Fuld v. PLO*, 2025; *Exxon Mobil Corp. v. Corporación CIMEX, S.A.*, June 23, 2026) and has previously granted major FSIA/TRIA execution cases even over the Solicitor General's opposition (*Rubin v. Islamic Republic of Iran*, 583 U.S. 202 (2018); *Harrison v. Republic of Sudan*, 587 U.S. 295 (2019)).
- **De facto national significance of Second Circuit law & elite advocacy:** Because FRBNY and major clearing banks sit in New York, a published Second Circuit restriction on TRIA § 201(a) governs the bulk of blocked-asset turnover litigation nationwide. Petitioners are represented by top Supreme Court counsel (Ian Gershengorn, Carter Phillips, Stuart Singer, Matthew McGill, Samuel Issacharoff across the three dockets) and backed by a 31-State amicus coalition.
- **Change of presidential administration:** As Judge Sullivan noted (`170 F.4th 100` n.1), the United States filed no brief in the Second Circuit, relying only on 2022–2023 district-court Statements of Interest from the prior administration. There is a meaningful minority chance (~20% grant recommendation, ~8% GVR/remand suggestion) that the current Solicitor General breaks from or narrows that posture on TRIA's text.

### 2. Downward / Moderating Pressures (-7 to -8 percentage points, keeping P(grant) at 0.39)
- **High likelihood (~72%) that the Solicitor General recommends denying certiorari:** Despite the change in administration, President Trump formally continued Executive Order 14064's national emergency protecting DAB's reserves on both February 7, 2025 and February 9, 2026. Treasury, the State Department, and FRBNY share powerful institutional reasons to oppose any precedent under which an unrecognized terrorist group's armed capture of a foreign capital lets private creditors seize a recognized nation's central-bank reserves custodied at FRBNY.
- **Potent alternative-ground / vehicle arguments for an SG opposition:** Even without defending the panel's broad "blocking-date" rule, the Solicitor General (echoing Chargé d'Affaires Faiq's amicus opposition) can argue that petitioners lose on the merits regardless of timing because: (a) DAB's pre-August 2021 sovereign central-bank deposits belong to the recognized **State of Afghanistan**, not the unrecognized Taliban, so they are not blocked assets "of" the Taliban or a Taliban instrumentality even today; and (b) Judge Daniels held below on constitutional Article II recognition grounds (expressly left unreached by the panel in `152 F.4th at 360 n.124`) and 28 U.S.C. § 1611(b)(1) central-bank immunity grounds that turnover is barred.
- **Indirectness of the alleged circuit split:** Reviewing *Bennett* (`825 F.3d 949`) and *Stansell II* (`771 F.3d 713`) confirms that neither the Ninth nor the Eleventh Circuit addressed an entity whose assets were blocked *before* a terrorist party seized control of it; both involved entities with pre-existing terrorist/state ties at blocking. Moreover, the Court had no respondent BIO before it on Nov. 16—because the Taliban defaulted and FRBNY stood mute—meaning a CVSG was virtually mandatory just to hear the other side before acting, rather than proof that four Justices already lean toward granting.
- **Justice Kagan's recusal & non-appearing respondent:** Justice Kagan is recused on Nos. 26-292 and 26-293 (though not on FSIA-only *Owens*, No. 26-294). Requiring 4 of 8 participating Justices to grant, facing the risk of a 4–4 tie on intertwined TRIA and Article II issues, and needing an appointed amicus (or the SG) to argue in place of a defaulted respondent all weigh modestly against plenary review.

### 3. Resulting Probability Synthesis
Weighting the three SG-brief scenarios:
- **SG recommends Deny (~72%):** `P(grant or GVR | Deny) ≈ 0.25` (elevated above the ~18% typical SG-deny grant rate because of the 5-judge CA2 textualist dissent and *Rubin*/*Harrison* precedent, tempered by E.O. 14064 / alternative ownership grounds / 8-Justice bench) → contributes `0.180`.
- **SG recommends Grant (~20%):** `P(grant or GVR | Grant) ≈ 0.80` → contributes `0.160`.
- **SG suggests GVR on bypassed alternative grounds or executive restructuring (~8%):** `P(grant or GVR | GVR/other) ≈ 0.53` → contributes `0.042`–`0.050`.

Summing across scenarios yields **`probability = 0.39`** (`0.34` plenary grant + `0.05` GVR), about **+4 percentage points above** the 35.0% `cert_anchor` baseline.

## Rationale for Secondary Claims & `big_case_score`

- **`relist-increment` = `0.98`:** Once the SG's invited brief arrives, the Clerk distributes the petition for Conference again, incrementing `distribution_count` past `2` unless the petition is dismissed under Rule 46 beforehand (~2%).
- **`cvsg-increment` = `0.0`:** Vacuous because `cvsg_date` (`2026-11-16`) is already set.
- **`summary-disposition-route` = `0.13`:** Matches `0.05 / 0.39 = 0.128` (slightly below the 16.9% `6.0 / 35.5` CVSG GVR share in `statpack.md` because no pending SCOTUS merits case governs this QP).
- **`dissent-from-denial` = `0.14` and `order-writers`:** Five active CA2 judges calling the panel's rule atextual creates a real (~14% conditional on denial) prospect of a dissent or statement respecting denial—led by Justices Thomas (`0.03`), Alito (`0.03`), and Gorsuch (`0.025`), with smaller probabilities for Kavanaugh (`0.01`), Sotomayor (`0.008`), Jackson (`0.005`), Barrett (`0.003`), Roberts (`0.002`), and `0.0` for recused Justice Kagan.
- **`big_case_score` = `0.85`:** If decided on the merits, a Supreme Court ruling governing $3.5 billion in frozen Afghan central-bank reserves, $17+ billion in 9/11 judgments, TRIA execution nationwide, and FRBNY central-bank reserve immunity would be one of the Term's marquee foreign-relations and statutory decisions.

## Key Uncertainties

The single largest uncertainty is **whether the Trump Administration's Solicitor General maintains the Biden Administration's categorical opposition to turnover of DAB's reserves** (aligned with E.O. 14064's 2025 and 2026 continuations and FRBNY/Treasury institutional equities) or breaks ranks in whole or in part on TRIA's plain text. Because this cell predicts at `moment: cvsg` *before* that brief exists, a swing in the SG's recommendation moves the conditional grant probability from ~25% to ~80%.
