# Predictor Rationale (`reasoning.md`): `scotus/9026000433` (`evt-petition-disposition`)

## 1. Record and Provisioned Inputs Consulted

- **Snapshot (`record/snapshots/2026-10-30.json`) and Context (`record/context.json`):**
  - Docket No. `26-433`, paid certiorari petition originating from the Third Circuit (`No. 25-1041`), docketed September 30, 2026 (`term = 2026`, `mode = "forward"`).
  - Respondents City of Philadelphia, Captain Luca, and Detective Walsh waived their right to respond on October 16, 2026; respondent Police Officer Christopher Culver waived his right to respond on October 20, 2026.
  - Distributed on October 28, 2026 (`distribution_count = 1`) for the Conference of November 13, 2026, with `cvsg_date = null` and `response_requested = null`.
  - One amicus curiae brief filed on October 29, 2026 by Constitutional Law Professors (Derek Charles Reinbold, counsel of record).
  - Frozen salience band under `sal-v4`: `"baseline"` (`salience_score = 0.024`).
- **Provisioned Documents (`record/documents/`):**
  - `questions-presented.txt` and `petition.txt`: Read in full. The petition (by Andrew T. Tutt and R. Stanton Jones) presents a single doctrinal question: whether a plaintiff bringing a shocks-the-conscience claim against an executive official under the Due Process Clause must prove only that the official's conduct shocks the conscience (*Rochin v. California*, 342 U.S. 165 (1952); *County of Sacramento v. Lewis*, 523 U.S. 833 (1998)), or must also prove that the conduct invaded a fundamental right deeply rooted in this Nation's history and tradition (*Washington v. Glucksberg*, 521 U.S. 702 (1997)). Crucially, Pet. 27 explicitly concedes that "Petitioner did not challenge the fundamental-rights prong of the shocks-the-conscience standard below," arguing that Third Circuit precedent (*Vargas v. City of Philadelphia*, 783 F.3d 962, 973 (3d Cir. 2015)) bound the panel.
  - `appendix.txt`: Read the Third Circuit's unpublished opinion (`App. 1a–9a`, Hardiman, J., joined by Montgomery-Reeves, J.), Judge Roth's opinion concurring in part and dissenting in part (`App. 10a–19a`), and the District Court's summary-judgment memorandum (`App. 20a–108a`, Kearney, J.).

## 2. Base Rates and Corpus Priors Consulted

- **Salience Band Anchor (`metrics/statpack.md`, `sal-v4`):**
  - The cell's frozen `context.band` is `"baseline"` under `sal-v4` in `term = 2026`.
  - Across the nine strictly-prior Terms rendered in the `Segment base rate by salience band (sal-v4)` table (OT 2017–2025), the `baseline` band's bracketed `reached` risk-set grant rates are:
    - OT 2025: `4.0% (n=1314)` (terminal `1.0%, n=994`)
    - OT 2024: `5.9% (n=1274)` (terminal `1.4%, n=936`)
    - OT 2023: `5.9% (n=1312)` (terminal `1.7%, n=958`)
    - OT 2022: `5.9% (n=1196)` (terminal `1.3%, n=894`)
    - OT 2021: `5.7% (n=1500)` (terminal `1.2%, n=1158`)
    - OT 2020: `4.5% (n=1740)` (terminal `1.0%, n=1343`)
    - OT 2019: `4.7% (n=1399)` (terminal `1.9%, n=1065`)
    - OT 2018: `4.8% (n=1529)` (terminal `1.5%, n=1181`)
    - OT 2017: `4.9% (n=1649)` (terminal `0.6%, n=1245`)
  - Pooling all 9 strictly-prior Terms (OT 2017–2025) yields a risk-set `reached` anchor of **5.1%** (`658 / 12913`), or **5.3%** (`205 / 3900`) over the 3 most recent prior Terms (OT 2023–2025).
- **Signal Cuts (`metrics/statpack.md`):**
  - **Relist count (paid scored segment):** `relist_bucket = 0` (`n=10203` resolved) resolves `denied 96.8%, granted 1.3%, dismissed 1.3%, gvr 0.5%` (1.8% grant family), compared with `13.7%` at 1 relist (`n=2538`) and `41.2%` at 2 relists (`n=495`).
  - **CVSG status (paid scored segment):** `cvsg = none` (`n=13556` resolved) resolves `denied 92.4%, granted 4.1%, gvr 2.3%, dismissed 1.2%` (6.4% grant family), vs. `34.8%` with a CVSG (`n=164`).
  - **Amicus count (paid scored segment):** `cert_amicus = 1` (`n=1162` resolved) resolves `denied 83.4%, granted 10.3%, gvr 4.8%, dismissed 1.5%` (15.1% grant family), vs. `3.8%` for `0` amici (`n=11109`). As the table caption notes, this cut is measured at disposition and pools across all relist/CVSG tiers.
  - **Originating circuit:** `ca3` (`n=1909` resolved in the modern cert cut) resolves `denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 1.0%` (2.5% grant family; in the live/historical originating-court table without IFP reweighting, `n=1000`, `granted 2.9%, gvr 1.9%`).
- **Corpus CLI (`uv run fedcourts query`):**
  - Queried `--court scotus --docket-number 26-433` and `--court scotus --limit 5` to confirm the case record and recent OT 2026 dispositions. A third query (`--court scotus --topic constitutional-rights --limit 10`) timed out against the local sidecar after 180s.

## 3. Justification for Headline Probability and Claims

- **Headline `probability` / `disposition = 0.008` (`predicted_disposition = "denied"`, `granted = 0`):**
  - Starting from the `sal-v4` `baseline` `[reached]` anchor of **5.1%**, I adjust **sharply downward** for four case-specific reasons, partially offset by a modest upward adjustment for counsel, the amicus brief, and the partial dissent below:
    1. *Waiver posture at distribution:* Both sets of respondents waived a response, and the petition was distributed on October 28, 2026 without a Call for a Response (CFR). Unlike `baseline` petitions that reach first distribution with a Brief in Opposition on file, a waived petition cannot be granted without the Court first calling for a response and redistributing the case once the opposition is filed.
    2. *Non-preservation of the Question Presented:* Petitioner candidly concedes (Pet. 27) that the *Rochin*/*Lewis* vs. *Glucksberg* question presented was never raised in the District Court or the Third Circuit. Below, Petitioner accepted the dual-prong framework and argued that *Favish* and *Marsh* satisfied *Glucksberg*. The Third Circuit dropped only a single sentence in a footnote noting that framework (`App. 3a n.2`) and assumed without deciding that *Favish* sufficed (`App. 5a`). The Court routinely denies petitions pressing a newly minted question not passed upon below.
    3. *Independent qualified-immunity barrier:* The Third Circuit affirmed solely on step two of qualified immunity ("clearly established law"). Even in circuits where conscience-shocking conduct is treated as a standalone element for physical intrusions on a plaintiff, it was not clearly established in March 2022 that photographing a third party's body at a public scene violated a family member's *own* Fourteenth Amendment rights absent a clearly established familial privacy right. And because the petition does not challenge the Third Circuit's *Taylor v. Riojas* obviousness holding, resolving the abstract *Lewis*/*Glucksberg* question would not overcome qualified immunity.
    4. *Unpublished decision and doctrinal headwinds:* The Third Circuit's decision is non-precedential (`NOT PRECEDENTIAL`), and the post-*Dobbs*/*Muñoz* Court has no appetite to dispense with *Glucksberg* in order to expand unenumerated substantive due process claims.
  - On the positive side, the petition is brought by experienced Supreme Court counsel (Andrew Tutt), is supported by an amicus brief from Constitutional Law Professors filed October 29, 2026, and involves egregious police conduct that drew a partial dissent from Judge Roth below. Those features give the petition roughly a **6% chance (`relist-increment = 0.06`)** of drawing a CFR or conference relist; conditional on a CFR/relist, the severe vehicle and preservation flaws cap the grant/GVR probability at ~13%, yielding **`0.008` (0.8%)** overall.
- **`relist-increment = 0.06`:**
  - The snapshot shows `distribution_count = 1`. Because respondents waived, any CFR requested before or at the November 13, 2026 conference—or any conference relist—will require a subsequent distribution (`distribution_count > 1`). Given the post-distribution law-professor amicus brief and Judge Roth's partial dissent on egregious facts, a 6.0% probability of a CFR or relist is well-calibrated.
- **`cvsg-increment = 0.001`:**
  - A § 1983 municipal/police tort suit with no federal statutory, regulatory, or sovereign interest has virtually zero chance (~0.1%) of drawing a CVSG.
- **`summary-disposition-route = 0.35`:**
  - Conditional on a grant, the 3-Term historical share of cert-order dispositions (GVRs and summary reversals) in the statpack (`metrics/docket.md` `cert_grants` table, OT 2023–2025: `(27 + 43 + 51) / (92 + 109 + 110) = 121 / 311`) is **38.9%**. I set `summary-disposition-route` slightly below that baseline at **35.0%**: while egregious qualified-immunity cases occasionally draw *Taylor v. Riojas*-style summary reversals, Petitioner did not brief qualified-immunity obviousness as a question presented and instead sought plenary review of a circuit split between *Lewis* and *Glucksberg*.
- **`dissent-from-denial = 0.01` and `order-writers`:**
  - Conditional on denial, the probability of a noted dissent or statement respecting denial is **1.0%**. Separate writings from denial almost always follow a CFR and multiple relists. If any Justice writes, Justice Sotomayor (`0.005`) and Justice Jackson (`0.003`) are likeliest to address qualified immunity and Officer Culver's conduct (echoing Judge Roth's dissent below), while Justice Thomas (`0.003`) and Justice Gorsuch (`0.002`) have a small chance of commenting on *Lewis* and *Glucksberg*.
- **`big_case_score = 0.25`:**
  - Decoupled from the low grant probability, if the Court actually decided whether *Rochin*/*Lewis* executive-action claims require a *Glucksberg* fundamental right, the decision would affect § 1983 substantive due process litigation across all federal circuits (`0.25`), though it involves an individual tort suit rather than invalidating a major federal or state statute.
