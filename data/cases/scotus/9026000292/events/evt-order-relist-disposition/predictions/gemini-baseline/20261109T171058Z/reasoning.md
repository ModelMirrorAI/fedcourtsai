# Prediction Reasoning: *Fiona Havlish, et al. v. The Taliban, et al.* (No. 26-292)

## 1. Executive Summary

- **Event**: `evt-order-relist-disposition` (`stage: cert`, `moment: relist`, `decision_target: disposition`)
- **Predicted Disposition**: `denied` (`granted: 0`)
- **Grant Probability (`probability` / `disposition`)**: **0.13** (13.0%)
- **Big Case Score (`big_case_score`)**: **0.78**
- **Secondary Claims (`cert-v3`)**:
  - `relist-increment`: **0.30**
  - `cvsg-increment`: **0.16**
  - `summary-disposition-route`: **0.08**
  - `dissent-from-denial`: **0.22**
  - `order-writers`: `Gorsuch: 0.10`, `Thomas: 0.08`, `Alito: 0.07`, `Sotomayor: 0.02`, `Kavanaugh: 0.02`, `Jackson: 0.02`, `Roberts: 0.01`, `Kagan: 0.01`, `Barrett: 0.01`

Petitioners in No. 26-292 (*Havlish*, *Doe*, *Federal Insurance*, and *Smith* judgment creditors—victims and insurers of the September 11, 2001 terrorist attacks) seek certiorari to review the Second Circuit's decision in *Havlish v. The Taliban*, 152 F.4th 339 (2d Cir. 2025), *reh'g en banc denied*, 170 F.4th 100 (2d Cir. 2026). Together with two companion petitions linked as `relation: "Vide"` in `record/related/related.json`—No. 26-293 (*Ashton v. The Taliban*, `26-293.json`) and No. 26-294 (*Owens v. The Taliban*, `26-294.json`)—petitioners seek to execute upon or attach approximately $3.5 billion in reserves of Da Afghanistan Bank (DAB), the central bank of Afghanistan, held in blocked accounts at the Federal Reserve Bank of New York (FRBNY). (`record/same-question.json` lists `petitions: []` above the 0.5 similarity threshold.)

All three *vide* petitions were first distributed on October 21, 2026 for the November 6, 2026 Conference and relisted on November 9, 2026 for the November 13, 2026 Conference (`distribution_count == 2`, `band: "elevated"` under `sal-v8` in `record/context.json`). Anchoring on the frozen `cert_anchor.rate` of **24.8%** (`0.24813153961136025`, the 10-term `sal-v8` `elevated` reached rate over OT2016–OT2025) and cross-checking against the `metrics/statpack.md` relist-count cut (20.7% grant-family rate across all `relist >= 1` petitions, `n=3510`, and 13.5% for `relist == 1`, `n=2532`), I adjust upward for the vigorous panel and four-judge en banc dissents below, the $3.5 billion stakes, and the 31-State amicus brief (+0.07), and adjust downward for the complete absence of a circuit split and the *sui generis* eight-day historical gap that triggered the issue (-0.09), the formidable constitutional and statutory alternative grounds supporting the denial of turnover and the Executive Branch's opposition below (-0.06), and the routine housekeeping explanation for the first relist following petitioners' October 30, 2026 motion for leave to file a supplemental brief in a case with no respondent appearance (-0.04). This yields a calibrated grant probability of **0.13** (13%).

---

## 2. Inputs Used and Factual/Procedural Background

### Provisioned and Retrieved Record
- **Snapshot & Context**: `record/snapshots/2026-11-09.json` and `record/context.json` (`mode: "forward"`, `band: "elevated"`, `salience_version: "sal-v8"`, `distribution_count: 2`, `cvsg_date: null`, `term: 2026`).
- **Related Dockets (`record/related/`)**: `26-293.json` (*Kathleen Ashton, et al. v. The Taliban, et al.*, `relation: "Vide"`) and `26-294.json` (*James Owens, et al. v. The Taliban, et al.*, `relation: "Vide"`). Both show parallel docketing on September 4, 2026, an amicus brief in opposition by Naseer A. Faiq on October 5, 2026, first distribution on October 21, 2026 for the November 6 Conference, supplemental filings on October 30, 2026, and a relist on November 9, 2026 for the November 13 Conference.
- **Provisioned Documents (`record/documents/`)**: `questions-presented.txt`, `petition.txt` (Petition and Appendix Vol. I, truncated by the 150,000-character pipeline cap in the middle of the appendix), and `appendix.txt` (Appendix Vol. II, listing the judgment-creditor parties). Neither side filed a brief in opposition (`brief-in-opposition.txt` is absent because no respondent appeared); the October 5 Faiq amicus brief, the October 8 31-State amicus brief, and the October 30 motion for leave to file a supplemental brief were not staged as text files.
- **CourtListener MCP Retrieval**: Because the 150,000-character middle cut in `petition.txt` omitted pages 42a–118a of the appendix, I retrieved the full text of the Second Circuit panel decision and dissent (`opinion_id=11127439`, 152 F.4th 339) and the March 19, 2026 order and opinions on denial of rehearing en banc (`opinion_id=11277807`, 170 F.4th 100) via the CourtListener MCP server.

### Litigation History Below
1. **Underlying Judgments and Blocked DAB Reserves**:
   Petitioners hold unsatisfied default judgments totaling billions of dollars against the Taliban arising out of the September 11, 2001 attacks. On August 15, 2021—the day the Taliban entered Kabul and the Government of the Islamic Republic of Afghanistan collapsed—OFAC blocked DAB's accounts at the FRBNY to keep Afghanistan's central-bank reserves out of the Taliban's hands. On August 23, 2021—eight days later—the Taliban appointed a loyalist (Hidayatullah Badri, a Specially Designated Global Terrorist) as acting governor of DAB. On February 11, 2022, President Biden issued Executive Order 14064 formally blocking all property of DAB in the United States; roughly $3.5 billion was later transferred to the Swiss-based "Afghan Fund" for the benefit of the Afghan people, while approximately $3.5 billion remained at the FRBNY pending resolution of terrorism victims' attachment and turnover motions.

2. **District Court Decisions**:
   Following a Report and Recommendation by Magistrate Judge Netburn (*In re Terrorist Attacks on September 11, 2001*, 633 F. Supp. 3d 635 (S.D.N.Y. 2022)), District Judge Daniels denied the *Havlish* and *Ashton* plaintiffs' post-judgment turnover motions under § 201(a) of the Terrorism Risk Insurance Act of 2002 (TRIA), 28 U.S.C. § 1610 note (*In re Terrorist Attacks on September 11, 2001*, 657 F. Supp. 3d 311 (S.D.N.Y. 2023)), and District Judge Caproni denied the *Aliganga* and *Owens* plaintiffs' motions to confirm pre-judgment attachments under the Foreign Sovereign Immunities Act (FSIA). Judge Daniels held that:
   - TRIA § 201(a) does not overcome DAB's central-bank execution immunity under 28 U.S.C. § 1611(b)(1) or confer subject-matter jurisdiction where the judgment debtor is a non-state terrorist group (the Taliban) rather than the recognized foreign state (Afghanistan) whose central bank holds the funds; and
   - Even if TRIA could apply, holding that DAB is an "agency or instrumentality" of the Taliban because the Taliban seized power in Kabul would require the federal judiciary to recognize the Taliban as the *de facto* government of Afghanistan, violating the President's exclusive constitutional recognition power under *Zivotofsky v. Kerry*, 576 U.S. 1 (2015).

3. **Second Circuit Panel Decision (152 F.4th 339) and En Banc Denial (170 F.4th 100)**:
   A divided Second Circuit panel (Judge Cabranes, joined by Judge Calabresi; Judge Sullivan concurring in part and dissenting in part) affirmed both district courts. On the TRIA issues, the panel majority disagreed with the District Court's jurisdictional holdings under *Weinstein v. Islamic Republic of Iran*, 609 F.3d 43 (2d Cir. 2010), but—explicitly invoking constitutional avoidance to sidestep the District Court's *Zivotofsky* recognition holding (152 F.4th at 367 n.124; App. 49a n.124)—held that whether an entity is an "agency or instrumentality" of a terrorist party under TRIA § 201(a) must be assessed **as of the date the assets at issue were blocked** (August 15, 2021). Judge Sullivan dissented on the panel, and four active Second Circuit judges (Judges Sullivan and Menashi, joined by Judges Nardini and Park) dissented from the denial of rehearing en banc on March 19, 2026 (170 F.4th 100), arguing that the panel's *sua sponte* time-of-blocking rule adds an extratextual limitation to TRIA § 201(a).

---

## 3. Base Rate Anchor and Adjustments (`probability`: 0.13)

### Base Rate Context (`metrics/statpack.md` & `record/context.json`)
- **Primary Anchor (`cert_anchor.rate`)**: In `record/context.json`, the frozen `cert_anchor.rate` for `band: "elevated"` under `sal-v8` over the 10 prior Terms (OT2016–OT2025) is **24.8%** (`0.24813153961136025`). Across the Term rows strictly before OT2026 rendered in `metrics/statpack.md` (*Segment base rate by salience band (sal-v8)*, OT2017–OT2025), the bracketed `reached` rates for `elevated` are: OT2025 21.8% (`n=174`), OT2024 27.7% (`n=213`), OT2023 24.3% (`n=235`), OT2022 27.2% (`n=202`), OT2021 27.8% (`n=230`), OT2020 22.8% (`n=254`), OT2019 20.9% (`n=206`), OT2018 24.0% (`n=221`), OT2017 26.1% (`n=272`).
- **Relist-Count Cross-Check**: In `metrics/statpack.md` (*Cert petitions by relist count (paid scored segment)*), pooling every bucket from 1 up gives:
  - `relist == 1`: `n=2532` resolved (`granted 8.3%, gvr 5.2%` -> 13.5% grant family)
  - `relist == 2`: `n=495` resolved (`granted 28.3%, gvr 12.9%` -> 41.2% grant family)
  - `relist == 3+`: `n=483` resolved (`granted 23.2%, gvr 14.1%` -> 37.3% grant family)
  - Pooled `relist >= 1` (`n=3510` resolved): **20.7%** grant-family rate.
- **Originating Circuit & Amicus Cuts**: Second Circuit petitions (*Modern cert petitions by originating circuit*, `ca2`, `n=2081` resolved) resolve at `granted 2.6%, gvr 2.4%` (5.0% grant family, slightly above the overall cert average). On the docket, two cert-stage amicus briefs have been filed (one in opposition by Naseer A. Faiq, one in support by Iowa and 30 other States), placing the docket in the `cert_amicus = 2+` bucket (`n=1446` resolved, `granted 18.2%, gvr 4.5%` = 22.7% grant family).

### Case-Specific Adjustments from the 24.8% Anchor
1. **Vigorous Panel and En Banc Dissents, Stakes, and State Amicus Support (+0.07)**:
   Four active Second Circuit judges (Sullivan, Menashi, Nardini, and Park) dissented in two thorough opinions demonstrating that the panel majority reached out to decide an unbriefed statutory timing issue and grafted an extratextual "at the time of blocking" requirement onto TRIA § 201(a). Combined with $3.5 billion in frozen reserves sought by thousands of 9/11 victims, elite Supreme Court counsel across three coordinated petitions, an amicus brief from 31 States, and the Second Circuit's practical primacy over FRBNY blocked accounts, this warrants a **+0.07** upward adjustment.

2. **Complete Absence of a Circuit Split and *Sui Generis* Factual Posture (-0.09)**:
   Both the petition and the dissenting judges below acknowledge that the Second Circuit is the first court of appeals ever to address whether TRIA § 201(a)'s "agency or instrumentality" requirement is measured at the date of blocking. Petitioners' claim of tension with *Dole Food Co. v. Patrickson*, 538 U.S. 468 (2003), is tenuous (*Dole Food* construed 28 U.S.C. § 1603(b)(2) as of the time suit is filed, which would not aid petitioners' 2002 suit, and *Bartlett*/*Aurelius* are intra-circuit Second Circuit FSIA decisions). Moreover, the eight-day gap between the August 15, 2021 preemptive blocking of DAB's accounts as Kabul fell and the Taliban's August 23, 2021 appointment of a DAB governor is a one-off historical anomaly. This warrants a **-0.09** downward adjustment.

3. **Alternative Grounds for Affirmance, Constitutional Avoidance, and Executive Branch Opposition (-0.06)**:
   Reversing the Second Circuit's blocking-date holding would immediately confront the Court (or the lower courts on remand) with multiple independent grounds supporting the denial of turnover that the United States pressed as amicus below:
   - *Constitutional recognition power*: Treating the central bank of the recognized State of Afghanistan as an instrumentality of the unrecognized Taliban regime implicates the President's exclusive recognition power under *Zivotofsky v. Kerry*, 576 U.S. 1 (2015)—the exact constitutional question the Second Circuit panel used its statutory timing rule to avoid (152 F.4th at 367 n.124).
   - *Sovereign ownership and central-bank immunity*: TRIA § 201(a) permits execution only against "the blocked assets *of* that terrorist party (including the blocked assets *of* any agency or instrumentality of that terrorist party)." As Judge Menashi noted in his en banc dissent (170 F.4th at 118 n.3) and the panel held in its FSIA ruling, DAB's capital and reserves belong to the State of Afghanistan, not the Taliban, and the District Court held that TRIA does not abrogate a non-terrorist state's central-bank immunity under 28 U.S.C. § 1611(b)(1) to satisfy a judgment against a non-state terrorist group.
   - Because the Executive Branch strongly opposed turnover below, any CVSG would almost certainly result in a recommendation to deny review. This warrants a **-0.06** downward adjustment.

4. **Routine Housekeeping Explanation for the November 9 Relist and Absence of a Respondent BIO (-0.04)**:
   On October 30, 2026—just seven days before the November 6 Conference—petitioners in Nos. 26-292 and 26-293 filed a Motion for leave to file a supplemental brief, and petitioners in No. 26-294 filed a supplemental brief. Relisting all three *vide* petitions for one week so the Court can act on the late motion for leave and review the supplemental briefs together is standard conference housekeeping. Furthermore, no respondent has entered an appearance or filed a Brief in Opposition. This procedural context reduces the grant signal of the first relist by **-0.04**.

`Probability = 0.24813 + 0.07 - 0.09 - 0.06 - 0.04 = 0.12813 ≈ 0.13`

---

## 4. Rationale for Secondary Claims and Big Case Score

- **`big_case_score` (0.78)**: If decided on the merits, a Supreme Court ruling determining whether $3.5 billion in frozen Afghan central-bank reserves can be seized by 9/11 judgment creditors under TRIA § 201(a) would be a high-stakes, nationally prominent foreign-relations and sovereign-immunity decision, even though the narrow statutory timing question is less doctrinally sweeping than a constitutional recognition holding.
- **`relist-increment` (0.30)**: In `metrics/statpack.md`, 978 of 3,510 resolved paid-segment petitions reaching `relist >= 1` (27.9%) were distributed at least once more (`relist >= 2`). Here, most of the probability mass (~70%) sits on a denial at the November 13, 2026 Conference once the October 30 motion for leave to file a supplemental brief is resolved, with a 30% chance of at least one further distribution (either for a CVSG or while a separate writing or grant order is prepared).
- **`cvsg-increment` (0.16)**: While foreign-sovereign-assets cases without an appearing respondent are prime candidates for a CVSG (`cvsg` bucket `n=164` resolved in `metrics/statpack.md`), the United States already filed extensive amicus submissions opposing turnover in both the District Court and the Second Circuit, reducing the Court's need to invite the Solicitor General's views anew to 16%.
- **`summary-disposition-route` (0.08)**: Conditional on a grant, plenary briefing and oral argument are overwhelmingly likely (~92%), as there is no intervening Supreme Court precedent for a GVR and summary reversal is virtually inconceivable on a $3.5 billion sovereign-assets claim with no respondent appearance.
- **`dissent-from-denial` (0.22) and `order-writers`**: Conditional on a denial, there is roughly a 22% chance that at least one Justice notes a dissent or statement respecting the denial of certiorari echoing Judge Sullivan's and Judge Menashi's textual critique of the Second Circuit's *sua sponte* blocking-date rule, with Justices Gorsuch (`0.10`), Thomas (`0.08`), and Alito (`0.07`) the likeliest authors.
