# Rationale for Prediction: *Moylan v. Guam Society of Obstetricians and Gynecologists* (No. 26-22)

## 1. Posture, Snapshot, and Base-Rate Anchor

This prediction evaluates `evt-order-call-for-response-disposition` (moment: `response-requested`, opened `2026-08-26`, cutoff `2026-08-27`) for *Douglas B. Moylan, Attorney General of Guam v. Guam Society of Obstetricians and Gynecologists, et al.*, No. 26-22.

At the snapshot cutoff (`2026-08-27.json`), the petition was docketed on July 7, 2026, respondents waived their right to respond on July 24, 2026, the petition was distributed on August 5, 2026 for the September 28, 2026 Long Conference (`distribution_count = 1`), and on August 26, 2026 the Court requested a response (due September 25, 2026).

Under `sal-v4`, the petition is in the **`state`** salience band (`context.json`: `"band": "state"`, `"salience_version": "sal-v4"`). Looking strictly at prior Terms in `metrics/statpack.md` (and `metrics/statpack.json`, OT2017–OT2025, 9 prior Terms), the **`state` band risk-set grant rate** (`prefix_est_grant_rate`, which walks the `state` → `high` reachable ladder) across the 9 strictly-prior Terms is:
- OT2025: 32.3% (10 / 31)
- OT2024: 31.6% (12 / 38)
- OT2023: 18.8% (6 / 32)
- OT2022: 13.9% (5 / 36)
- OT2021: 22.7% (22 / 97)
- OT2020: 41.3% (19 / 46)
- OT2019: 17.0% (9 / 53)
- OT2018: 23.8% (10 / 42)
- OT2017: 21.6% (11 / 51)

Pooling all 9 strictly-prior Terms gives **104 grants out of 426 risk-set resolved petitions = 24.41%** (`0.2441`). (The terminal `state` band grant rate—petitions that resolve in `state` without escalating to `high` via 2+ relists or CVSG—is 61 / 299 = **20.40%**.)

Thus, our starting base-rate anchor from the `state` risk-set is **24.4%**.

## 2. Case-Specific Analysis and Adjustments

### A. Procedural Posture and the Call for a Response
Respondents initially filed a waiver of the right to respond on July 24, 2026, and the petition was distributed for the September 28 Long Conference before a single Justice requested a response on August 26. Because the Court virtually never grants a petition (or issues a contentious dissent from denial) without first calling for a response, a CFR is a necessary step for any live consideration after a waiver, but most CFR petitions are still ultimately denied once the brief in opposition highlights vehicle flaws and local-law complexities.

### B. Absence of a True Circuit Split and Reliance on Local Territorial Law
Petitioner frames the question presented around whether a federal court may dismiss as moot a Rule 60(b)(5) motion to vacate a permanent injunction resting on overruled constitutional precedent (*Roe v. Wade* overruled by *Dobbs*). However, the Ninth Circuit majority (Judges Christen and Bade) did not hold that federal injunctions survive *Dobbs* as a matter of federal constitutional law. Rather, the panel majority held the appeal moot because:
1. Following the Guam Supreme Court's advisory decision on certified questions from the Governor of Guam (*In re Request of Lourdes A. Leon Guerrero, I Maga'hagan Guahan*, 2023 Guam 11), Guam Public Law 20-134 (enacted in 1990) was impliedly repealed by subsequent Guam legislation enacted between 1990 and 2022 (the Women's Reproductive Health Information Act of 2012, the Partial-Birth Abortion Ban Act of 2008, the Unborn Victims of Violence Act of 2013, and criminal code recodifications).
2. Because P.L. 20-134 is no longer operative law in Guam, vacating the 1990 injunction would have no real-world legal effect—the Attorney General cannot enforce a repealed statute.

Petitioner's argument that a territory cannot "impliedly repeal" a law while it is enjoined is a novel theory, and the Ninth Circuit's deferential posture toward the Guam Supreme Court on matters of local Guam statutory construction accords with *Territory of Guam v. Guerrero*, 290 F.3d 1210 (9th Cir. 2002). There is no genuine circuit conflict on this territorial statutory question.

### C. Severe Vehicle and Justiciability Defects
Even for Justices sympathetic to vacating *Roe*-era injunctions after *Dobbs* (as Judge VanDyke urged in dissent below and as Justice Thomas has previously emphasized regarding *Horne v. Flores*, 557 U.S. 433 (2009)), this petition suffers from multiple compounding vehicle problems:
1. **Defunct / Non-Participating Respondents in the District Court:** In 2023, when Attorney General Moylan moved to dissolve the 1990 injunction, **none of the original 1990 plaintiffs were served or appeared in the district court**. Individual plaintiff-physicians and clinic plaintiffs from 1990 had died, retired, or moved away; the ACLU appeared only as *amicus curiae* in the district court before later entering an appearance for certain organizational/individual respondents on appeal. This raises serious threshold questions (noted by the district court and argued below) about whether the 1990 injunction even binds or benefits any extant party in the district court, or whether the motion was properly noticed under Rule 60(b).
2. **Intragovernmental Conflict in Guam:** The Governor of Guam (a co-defendant in the original 1990 decree) actively intervened/participated as *amicus* opposing the Attorney General's motion and obtained the Guam Supreme Court ruling declaring P.L. 20-134 repealed.
3. **Lack of Practical Effect:** Because the Guam Supreme Court—the authoritative expositor of Guam law—has already held P.L. 20-134 impliedly repealed, reversing the Ninth Circuit's mootness dismissal and remanding for vacatur of the 1990 federal injunction would still leave P.L. 20-134 unenforceable under Guam law. The Supreme Court rarely grants plenary review to issue an opinion that cannot alter the enforceability of the underlying statute.

### D. Countervailing Factors: Judge VanDyke's Dissent and *Horne v. Flores*
On the other side of the ledger, Petitioner has a sharp, published 2-1 panel split with a forceful dissent by Judge VanDyke arguing that:
- Under *Horne v. Flores*, 557 U.S. 433 (2009), and *Agostini v. Felton*, 521 U.S. 203 (1997), a Rule 60(b)(5) motion to vacate a federal injunction when its sole constitutional foundation (*Roe*) has been overruled is virtually automatic; and
- It is circular to hold an appeal from the denial of vacatur moot while the federal injunction itself remains formally on the books in the District Court of Guam.

This framing will likely attract the attention of at least one or two conservative Justices (particularly Justice Thomas and Justice Alito), which explains why the Court called for a response after respondents initially waived. However, attracting four votes for plenary review—or a summary reversal/GVR that untangles Guam's local implied-repeal jurisprudence and the 1990 service/party defects—is substantially less likely. Once respondents (represented by the ACLU and Perkins Coie) file their Brief in Opposition detailing the Guam Supreme Court's holding in *In re Leon Guerrero* and the complete absence of served plaintiffs in the district court, the Court is likely to deny certiorari, potentially after one or two relists if a Justice writes a dissent from denial or statement respecting denial.

### E. Net Probability Calibration
Starting from the `state` risk-set base rate of **24.4%**:
- Downward adjustments: No federal circuit split (-6%), reliance on authoritative local territorial court ruling on statutory implied repeal that renders the underlying statute unenforceable regardless of federal vacatur (-5%), and severe threshold vehicle/notice/party defects from the 1990 proceedings (-3%).
- Upward adjustments: Published 2-1 Ninth Circuit split with a prominent Judge VanDyke dissent on a post-*Dobbs* / Rule 60(b)(5) issue (+3.6%).
- Net `probability` = **0.14** (14%), with `granted = false` and `predicted_disposition = "denied"`.

## 3. Mechanical Claims (`cert-v3`)

1. **`disposition` (`0.14`):** Matches the headline `probability` (`0.14`).
2. **`relist-increment` (`0.96`):** At the `2026-08-27` cutoff, `distribution_count = 1` (from the August 5, 2026 distribution prior to the August 26 call for response). Because the Court called for a response due September 25, 2026 (extended if requested), the petition will necessarily be distributed again for a subsequent conference once the brief in opposition is filed, causing `distribution_count` to rise above 1. (Note: `docs/outcome-decomposition.md` notes that `relist-increment` is vacuous-masked on the `response-requested` moment for precisely this reason, and setting `0.96` reflects the near-certainty of a post-response distribution.)
3. **`cvsg-increment` (`0.01`):** This dispute concerns a territorial statute of Guam and federal equity/mootness under Rule 60(b)(5); there is no federal statutory or regulatory program administered by the United States that would warrant inviting the Solicitor General's views.
4. **`summary-disposition-route` (`0.354`):** Conditional on a grant, what is the probability that the Court disposes of the case in the cert order (via GVR or summary reversal)? The strictly-prior paid grant-family cert-order share in `metrics/statpack.md` (OT2017–OT2025: 317 GVRs out of 893 paid grant-family outcomes = `0.3550`, or `0.354` over OT2017–OT2024) sits at **35.4%**. In this case, if the Court were to grant, a summary vacatur/GVR or summary reversal under *Dobbs* and *Horne v. Flores* is a plausible alternative to full merits briefing, roughly in line with the historical conditional base rate (`0.354`).
5. **`dissent-from-denial` (`0.25`):** Conditional on denial, there is a meaningful (~25%) probability that Justice Thomas and/or Justice Alito (potentially joined by Justice Gorsuch) notes a dissent from the denial of certiorari or issues a statement respecting the denial, echoing Judge VanDyke's dissent about leaving a *Roe*-based federal injunction on the books after *Dobbs*.
6. **`order-writers`:** Per-Justice probabilities of authoring a separate writing on the cert order reflect the concentration of potential dissents from denial in Justices Thomas (`0.18`), Alito (`0.15`), and Gorsuch (`0.05`), with much lower probabilities for the remaining Justices.
