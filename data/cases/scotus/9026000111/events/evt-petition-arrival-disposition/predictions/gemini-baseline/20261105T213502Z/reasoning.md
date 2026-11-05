# Prediction Reasoning: *Noah A. Herzon, et al. v. Robert Arias* (No. 26-111)

- **Case ID:** `scotus/9026000111`
- **Event ID:** `evt-petition-arrival-disposition` (`stage: cert`, `moment: arrival`)
- **Snapshot:** `2026-07-24.json`
- **Prediction:** `granted: 1`, `probability: 0.78`, `predicted_disposition: "granted"`

---

## 1. Base-Rate Anchor and Caption-Class Adjustment

Under `record/context.json`, this arrival-stage certiorari cell (`opened_at: 2026-07-23`, `cutoff: 2026-07-24`, `distribution_count: 0`, `cvsg_date: null`) carries the frozen salience band **`band: "baseline"`** (`salience_version: "sal-v7"`) and a pre-registered 10-Term reached grant-family anchor of **`cert_anchor.rate = 0.051513` (5.15%)**. Across the 10-Term lookback in `metrics/statpack.md` (OT2017–OT2025), the paid scored-segment `baseline` reached rate ranges between 4.0% (OT2025, $n=1,289$) and 6.0% (OT2023, $n=1,283$; OT2024, $n=1,243$), while all paid and IFP petitions originating from the First Circuit (`ca1`) resolve at a grant-family rate of 3.0% weighted (2.5% `granted`, 0.5% `gvr`, 95.4% `denied`, 1.5% `dismissed`; $n=910$) or 4.6% unweighted (3.8% `granted`, 0.8% `gvr`; $n=613$).

Although `band: "baseline"` is the frozen conditioning state against which Brier skill is evaluated, inspecting the docket snapshot (`2026-07-24.json`) and `petition.txt` reveals why the case's substantive prior sits far above the `baseline` floor:

1. **Solicitor General Petition on Behalf of Federal Officers:** Because *Bivens* damages actions run against federal officers in their individual capacities, the case caption (*Noah A. Herzon, et al. v. Robert Arias*) lists the six DEA task-force officers by personal name without an official government title or `"United States"` in the caption string. Consequently, the deterministic caption classifier placed the petition in `baseline` rather than `federal`. In fact, the petition was filed by **Solicitor General D. John Sauer**, Assistant Attorney General Brett A. Shumate, Deputy Solicitor General Curtis E. Gannon, and DOJ appellate counsel (`SUPREMECTBRIEFS@USDOJ.GOV`) following Justice Jackson's May 8, 2026 grant of extension application No. 25A1226.
2. **Empirical Grant Family Rate for Solicitor General Petitions:** In `metrics/statpack.md`, modern cert petitions in the `federal` petitioner band resolve in the grant family (`granted` + `gvr`) **73.5%** of the time across the live/historical slice (`granted` 52.5%, `gvr` 21.0%, `denied` 23.3%, `dismissed` 3.2%; $n=219$ resolved), with recent Term reached rates of 57.1% (OT2025, $n=28$), 62.5% (OT2024, $n=16$), 86.7% (OT2023, $n=30$), 89.5% (OT2022, $n=19$), 75.0% (OT2021, $n=12$), 67.4% (OT2020, $n=43$), 96.3% (OT2019, $n=27$), 47.6% (OT2018, $n=21$), and 75.0% (OT2017, $n=16$).

---

## 2. Case Record and Procedural Posture

In September 2016, after undercover DEA operatives made controlled purchases of fentanyl-laced heroin from respondent Robert Arias, a DEA task force executed a federal arrest warrant for Arias in the parking lot of the Rockingham Park Mall in Salem, New Hampshire (Pet. App. 59a–60a). Officers blocked in the car in which Arias was a passenger, cut his seatbelt, removed him from the vehicle, and handcuffed him. Arias sued six task-force officers in the District of New Hampshire under *Bivens v. Six Unknown Named Agents of Federal Bureau of Narcotics*, 403 U.S. 388 (1971), alleging Fourth Amendment excessive-force and failure-to-intervene claims (Pet. App. 3a, 58a–60a).

Following *Egbert v. Boule*, 596 U.S. 482 (2022), the district court (McCafferty, J.) granted summary judgment to the remaining four officers on June 27, 2023 (680 F. Supp. 3d 61; Pet. App. 58a–73a). Although the district court thought an arrest pursuant to a warrant in a mall parking lot did not by itself create a new *Bivens* context, it held that the Inspector General Act Amendments of 1988, Pub. L. No. 100-504, 102 Stat. 2515 (IGA), and 28 C.F.R. § 0.29c(c)—which established an administrative misconduct complaint process within DOJ's Office of the Inspector General—both placed the claim into a "new context" at Step One and foreclosed a *Bivens* remedy as a special factor at Step Two (Pet. App. 5a–7a).

On August 15, 2025, a divided First Circuit panel affirmed as to the failure-to-intervene claim (which Arias did not contest on appeal) but reversed as to the Fourth Amendment excessive-force claim (*Arias v. Herzon*, 150 F.4th 27; Pet. App. 1a–57a).
- **Majority Opinion (Barron, C.J., joined by Thompson, J.):** Held at *Bivens* Step One that (a) neither the existence of an arrest warrant nor the public shopping-mall parking lot location meaningfully differentiates the case from *Bivens* because excessive force is equally unconstitutional with or without a warrant and inside or outside a home (Pet. App. 17a–23a), and (b) the 1988 IGA administrative complaint mechanism does not render the context "new" at Step One because treating a general DOJ OIG complaint procedure as a Step-One difference would mean *Bivens* itself has been a "dead letter" for nearly four decades despite the Supreme Court's repeated statements declining to overrule *Bivens* (Pet. App. 23a–43a). Because the panel found no new context at Step One, it refused to reach Step Two.
- **Dissent (Lynch, J.):** Argued that under *Ziglar v. Abbasi*, 582 U.S. 120 (2017), *Egbert v. Boule*, 596 U.S. 482 (2022), and *Goldey v. Fields*, 606 U.S. 942 (2025) (per curiam), Steps One and Two resolve into a single separation-of-powers question whenever Congress has created an alternative remedial structure such as the IGA, and further concluded that executing a judicial arrest warrant in a busy public parking lot implicates different Fourth Amendment interests, legal mandates, and public-safety risks than the warrantless home intrusion in *Bivens* (Pet. App. 44a–57a). Judge Lynch explicitly noted that "[t]he Supreme Court may wish to address these circuit splits, reflecting the need for additional guidance to lower court judges" (Pet. App. 45a n.11).

On February 24, 2026, the First Circuit denied panel rehearing and rehearing en banc, with Judge Lynch dissenting from the denial of panel rehearing and Judge Aframe recused (Pet. App. 74a–75a).

---

## 3. Certiorari Factors and Interaction with *Nielsen v. Watanabe* (No. 25-417)

Several convergent factors make a grant-family disposition (`granted` or `gvr`) highly likely:

1. **Square, Acknowledged 3-2-1 Circuit Split on Core Fourth Amendment *Bivens* Scope:**
   As both the First Circuit majority (Pet. App. 20a, 22a) and Judge Lynch's dissent (Pet. App. 45a n.11, 55a–57a) recognized, the circuits are openly divided over whether *Bivens* encompasses Fourth Amendment excessive-force claims arising from warrant-authorized arrests outside the home:
   - **Permitting *Bivens* at Step One (3 circuits):** First Circuit (*Arias v. Herzon*, 150 F.4th 27 (2025)), Seventh Circuit (*Snowden v. Henning*, 72 F.4th 237, 247 (2023)), and Tenth Circuit (*Logsdon v. U.S. Marshal Service*, 91 F.4th 1352, 1357 (2024), agreeing on warrant/location though rejecting the claim on new-defendant grounds).
   - **Barred Because Arrest Occurred Outside the Home (2 circuits):** Fifth Circuit (*Byrd v. Lamb*, 990 F.3d 879, 882 (2021)) and Ninth Circuit (*Mejia v. Miller*, 61 F.4th 663, 668 (2022)).
   - **Barred Because Arrest Was Executed Pursuant to a Warrant (1 circuit):** Fourth Circuit (*Orellana v. Godec*, 145 F.4th 516, 525 (2025), relying on *Annappareddy v. Pascale*, 996 F.3d 120, 135–136 (4th Cir. 2021)).
   While the Court previously denied private officers' petitions in *Snowden*, 145 S. Ct. 137 (2024), and *Hicks v. Ferreyra*, 144 S. Ct. 555 (2024), the conflict has since deepened with the Fourth Circuit's published decision in *Orellana* (2025) and the First Circuit's divided decision here, and the **Solicitor General** has now brought the issue to the Court in a clean federal-officer vehicle.

2. **Direct Overlap with *Nielsen v. Watanabe*, No. 25-417 (Cert. Granted June 22, 2026):**
   One month before filing this petition, the Court granted certiorari in *Nielsen v. Watanabe*, No. 25-417 (reviewing *Watanabe v. Derr*, 115 F.4th 1034 (9th Cir. 2024)), in which the Solicitor General is participating as amicus curiae supporting the petitioner. In *Watanabe*, a divided Ninth Circuit panel held—using the exact two-step insulation logic adopted by Chief Judge Barron here—that factual differences from *Carlson v. Green*, 446 U.S. 14 (1980), did not create a "new context" at Step One and that the existence of alternative administrative remedies is relevant only at Step Two (115 F.4th at 1042–1043). The Solicitor General explicitly asks in Section C of the petition (Pet. 2–3, 5, 15–16) that, at a minimum, the Court hold *Herzon* pending *Nielsen*. (`record/same-question.json` indexed 13,417 petitions above threshold 0.5 and returned `petitions: []` because *Nielsen*'s Eighth Amendment QP wording differs lexically from *Herzon*'s Fourth Amendment QP wording, so the hold link is read directly from `petition.txt` and verified via corpus query on `25-417`.)

3. **Supreme Court's Unbroken 46-Year Doctrinal Trajectory Against *Bivens*:**
   As the Court emphasized in *Goldey v. Fields*, 606 U.S. 942, 944–945 (June 30, 2025) (per curiam) (summarily reversing the Fourth Circuit when prison officials petitioned with SG support), and reiterated in *Cisco Systems, Inc. v. Doe*, 146 S. Ct. 1882, 1890–1891 (2026), implied damages causes of action are strongly disfavored on separation-of-powers grounds. When a court of appeals permits a *Bivens* action to proceed over a dissent and the Solicitor General seeks review, the Court consistently intervenes—either by plenary grant, summary reversal (as in *Goldey*), or holding and issuing a GVR once a pending *Bivens* merits case (*Nielsen*) is decided.

---

## 4. Rationale for Structured Claims, Distributions, and Big-Case Score

- **`disposition` (`0.78`) and `predicted_disposition` (`"granted"`):**
  In the prediction schema, `granted: 1` encompasses `granted`, `gvr`, and `summary-reversal`. I decompose the 0.78 grant-family probability into:
  - **Plenary review (`granted`, ~0.43):** The Solicitor General's primary ask is plenary review of the 3-2-1 Fourth Amendment circuit split (Pet. 6–15). Because *Nielsen v. Watanabe* involves an Eighth Amendment (*Carlson*) prison medical claim governed by the PLRA and BOP Administrative Remedy Program—which Chief Judge Barron explicitly distinguished from the Fourth Amendment / DOJ Inspector General Act context (Pet. App. 28a–30a, 39a–41a)—resolving *Nielsen* may not settle the Fourth Amendment warrant/outside-the-home split. Within the `federal` petitioner band in `metrics/statpack.md`, `granted` (52.5%) is more than twice as common as `gvr` (21.0%).
  - **Hold for *Nielsen* followed by GVR (`gvr`, ~0.31) or per curiam summary reversal (~0.04):** The Solicitor General explicitly offers a hold-for-*Nielsen* path (Pet. 15–16). Holding No. 26-111 pending *Nielsen* and then vacating and remanding in light of *Nielsen*'s clarification of Step One and alternative remedies—or summarily reversing as in *Goldey v. Fields*, 606 U.S. 942 (2025)—accounts for ~0.35 of total probability mass.
  - **Denial (`denied`, ~0.20) or Dismissal (`dismissed`, ~0.02):** Interlocutory posture and the Court's prior denials of private officers' petitions in *Snowden* and *Hicks* leave a ~20% chance of denial and a ~2% chance of Rule 46 dismissal.
- **`relist-increment` (`0.96`):**
  At `moment: arrival`, `distribution_count` is `0`. Thus any conference distribution at all (even a single conference distribution, let alone a relist or hold for *Nielsen*) increments the distribution count past 0. Only a pre-distribution Rule 46 dismissal (~2–4%) would leave `distribution_count` at 0.
- **`cvsg-increment` (`0.01`):**
  The Solicitor General is counsel of record for petitioners; the Court does not invite the Solicitor General to file an amicus brief on a petition the Solicitor General filed.
- **`summary-disposition-route` (`0.45`):**
  Conditional on a grant (`0.78`), the probability that the Court disposes of the case in the cert order itself (a hold-then-GVR after *Nielsen* at ~0.31 unconditional, plus a *Goldey*-style summary reversal at ~0.04 unconditional: $0.35 / 0.78 \approx 0.45$) rather than setting it for plenary briefing and oral argument ($0.43 / 0.78 \approx 0.55$) is **0.45**.
- **`dissent-from-denial` (`0.18`) and `order-writers`:**
  Conditional on a denial, there is roughly an 18% chance that at least one Justice (most likely Justice Thomas, Justice Gorsuch, or Justice Alito, given their prior writings in *Egbert*, *Hernandez*, and *Abbasi* urging the cabining or overruling of *Bivens*) writes a dissent from or statement respecting the denial of certiorari. Across all order outcomes (including a small chance of a dissent by Justice Sotomayor or Justice Jackson from a per curiam summary reversal), I assign modest per-Justice `order-writers` probabilities led by `Thomas` (0.05), `Alito` (0.04), `Gorsuch` (0.04), `Sotomayor` (0.03), and `Jackson` (0.03).
- **`big_case_score` (`0.65`):**
  If decided on the merits, the case directly tests whether *Bivens* survives even in its core Fourth Amendment DEA narcotics-arrest setting once an arrest warrant is present, an arrest occurs in public, or the 1988 Inspector General Act applies—making it a significant federal-courts and constitutional-remedies case, though bounded by the fact that *Nielsen v. Watanabe* (No. 25-417) is already slated to address *Bivens* Step One in OT2026.
