# Rationale and Calibration: *James P. Abrams v. United States* (No. 25-1236)

**Event:** `evt-order-call-for-response-disposition` (`moment: response-requested`, `stage: cert`)  
**Input Snapshot:** `2026-06-10.json`  
**Predicted Disposition:** `denied` (`granted: 0`, `probability: 0.25`)  
**Big Case Score:** `0.30`

---

## 1. Provisioned Record and Conditioning State

We forecast from the provisioned snapshot `2026-06-10.json` (`context.json`: `mode: "forward"`, `cutoff: "2026-06-10"`, `cut_kind: "date"`, `band: "baseline"`, `salience_version: "sal-v4"`, `distribution_count: 1`, `cvsg_date: null`, `amicus_briefs: null`, `term: 2025`) and the two provisioned documents in `record/documents/` (`questions-presented.txt` and `petition.txt`, neither OCR-derived nor empty; `petition.txt` carries a pipeline truncation note at the end of Appendix B, the district court judgment, after the full petition and the complete Third Circuit opinion in Appendix A).

On April 30, 2026, Petitioner James P. Abrams docketed a paid petition for a writ of certiorari (No. 25-1236) seeking review of a published Third Circuit decision (*United States v. Abrams*, 165 F.4th 784 (3d Cir. Jan. 30, 2026), Smith, J., joined by Scirica and Bibas, JJ.). On May 19, 2026, the Solicitor General waived the United States' right to respond. The petition was distributed on May 27, 2026 for the June 11, 2026 conference (`distribution_count: 1`). On June 9, 2026, the Court requested a response (CFR) from the Solicitor General, due July 9, 2026. Because the snapshot stops on June 10, 2026, no Brief in Opposition is on the record yet, and we do not infer its contents beyond what is apparent from the Third Circuit's opinion and standard Supreme Court practice. No cert-stage amicus briefs are docketed (`0` amicus entries on the snapshot).

---

## 2. Base-Rate Anchor (`metrics/statpack.md`)

In `record/context.json`, the frozen conditioning state assigns `band: "baseline"` under `salience_version: "sal-v4"` and `term: 2025`. Following the prompt's band-anchoring rule for `sal-v4` in `metrics/statpack.md` ("Segment base rate by salience band (sal-v4)"), we pool the **bracketed `reached`** grant rate for `baseline` across all rendered Terms strictly preceding OT2025 (OT2017–OT2024, 8 Terms):
- OT2024: 5.9% (`n = 1,274`, ~75.2 grants)
- OT2023: 5.9% (`n = 1,312`, ~77.4 grants)
- OT2022: 5.9% (`n = 1,196`, ~70.6 grants)
- OT2021: 5.7% (`n = 1,500`, ~85.5 grants)
- OT2020: 4.5% (`n = 1,740`, ~78.3 grants)
- OT2019: 4.7% (`n = 1,399`, ~65.8 grants)
- OT2018: 4.8% (`n = 1,529`, ~73.4 grants)
- OT2017: 4.9% (`n = 1,649`, ~80.8 grants)
- **Pooled strictly-prior `baseline [reached]` anchor (OT2017–OT2024):** ~607.0 / 11,599 = **5.23%** (whereas the leading terminal `baseline` rate is ~1.2%–1.3%).

Cross-checking the other `statpack.md` cuts:
- **Originating circuit (`ca3`):** In "Modern cert petitions by originating circuit," `ca3` (`n = 1,909` resolved) has a base rate of `denied 94.8%, dismissed 2.7%, granted 1.5%, gvr 1.0%` (2.5% grant family).
- **Amicus count (`0`):** In "Cert petitions by amicus-brief count (paid scored segment)," bucket `0` (`n = 11,109` resolved) has `denied 95.0%, granted 2.0%, gvr 1.8%` (3.8% grant family), though our petition is still pre-BIO.
- **Relist count (`1`+ once redistributed post-CFR):** Petitions that end with 1 relist (`n = 2,538` resolved) grant at 13.7% (`granted 8.5%, gvr 5.2%`), and those that reach `elevated` after a subsequent distribution have a strictly-prior `reached` rate of ~17.5% across OT2017–OT2024.

---

## 3. Case-Specific Adjustments from the Anchor

Starting from the **5.2%** `baseline [reached]` anchor—and recognizing that the June 9, 2026 Call for a Response guarantees that the petition cleared the initial waiver screen and will be redistributed once the Solicitor General responds—we weigh the strong split against the vehicle problems revealed in the Third Circuit's opinion:

### Upward Adjustments (+26%)
1. **Acknowledged, Deep 7–4 Circuit Split on Federal Rule of Criminal Procedure 29(a):**
   The petition presents a textbook procedural split on a recurring question in federal criminal trials: whether a general Rule 29 motion ("I move for judgment of acquittal on Rule 29(a). I waive argument.") preserves *de novo* sufficiency review on appeal.
   - Seven circuits (1st, 2d, 6th, 7th, 9th, 10th, and D.C., plus the 4th Circuit in practice) hold that a general Rule 29 motion preserves *de novo* review of all sufficiency challenges, because Rule 29(a)—unlike Civil Rule 50(a)(2)—contains no requirement to specify the law and facts entitling the movant to judgment, and the 1944 Advisory Committee Note to Criminal Rule 47(b) explains that a motion for judgment of acquittal "need not specify the grounds therefor."
   - Four circuits (3d, 5th, 8th, and 11th) hold that a general Rule 29 motion fails to preserve specific sufficiency challenges, triggering plain-error review.
   - Crucially, in *Abrams*, the Third Circuit panel (Judges Smith, Scirica, and Bibas) treated this as a square threshold holding in a published precedential opinion (Pet. App. 10a–18a), explicitly acknowledging the Seventh Circuit's contrary holdings in *Hosseini* and *Maez* and stating "We decline to follow it" (Pet. App. 17a).
2. **Quality of Advocacy and Clean Preservation of the Threshold Issue:**
   The petition is filed by experienced Supreme Court counsel (David A. O'Neil of Debevoise & Plimpton LLP alongside the Federal Public Defender). Moreover, the Government itself asked the Third Circuit in its appellate brief to resolve the open preservation question rather than bypass it, and the Third Circuit did so squarely.

### Downward / Limiting Adjustments (-6%)
1. **Non-Outcome-Determinative Vehicle Posture on the Underlying Convictions:**
   A close reading of Part III.A.3 of the Third Circuit's opinion (Pet. App. 24a–39a) reveals a major vehicle obstacle that the Solicitor General will inevitably press in opposing certiorari: Abrams's underlying sufficiency challenges fail under *de novo* review just as surely as under plain-error review.
   - **Wire and Mail Fraud (Counts 1–19):** Abrams's primary legal theory—that the investors got the "benefit of the bargain" and that he lacked intent to cause net economic loss—was squarely rejected by *Kousisis v. United States*, 605 U.S. 114, 124 (2025), decided while his appeal was pending, as Abrams conceded in his reply brief below (Pet. App. 26a). His backup argument—that sophisticated investors did not reasonably rely on his forged documents—is foreclosed by *Neder v. United States*, 527 U.S. 1, 24–25 (1999) (justifiable reliance has "no place in the federal fraud statutes") (Pet. App. 27a). And on factual intent, the Third Circuit explicitly held under the *Jackson v. Virginia* standard that "the record contains more than sufficient evidence, viewed in the light most favorable to the prosecution, from which a rational trier of fact could have found that both elements were met beyond a reasonable doubt" (Pet. App. 25a), detailing doctored contracts with Rockwell Collins, PNNL, and Battelle, forged signatures, falsified tax returns, and rapid diversion of $800,000 in investor proceeds to buy a personal home in South Carolina.
   - **Aggravated Identity Theft (Counts 20–24):** Abrams argued that § 1028A requires pecuniary or reputational harm to the identity victim and that his conduct fell outside *Dubin v. United States*, 599 U.S. 110 (2023). The Third Circuit did not merely rely on the second prong of plain error; it evaluated the evidence under the *Jackson* standard ("viewing the evidence 'in the light most favorable to the prosecution'—a reasonable jury could find that Abrams's use of another's identifying information was at the 'crux' of his fraud," Pet. App. 34a–39a) and found that forging the names and signatures of real officials at Battelle, PNNL, Rockwell Collins, and his accounting firm misrepresented *who* was vouching for the startup's technology and finances.
   - **Unchallenged Counts (Counts 25–48):** Abrams did not even challenge the sufficiency of the evidence on his 24 convictions for money laundering, unlawful monetary transactions, obstruction of justice, and false statements to federal agents, which carry concurrent 48-month sentences (Pet. App. 10a).
2. **Prior Denial in *Tovar v. United States* (No. 25-6344):**
   Corpus lookup (`uv run fedcourts query --court scotus --docket-number 25-6344`) shows that the Court denied certiorari on May 18, 2026 in *Ralph Kevin Tovar v. United States* (`scotus/73282036`), which raised the same Rule 29 preservation split from the Eleventh Circuit (Pet. 10 n.2, 21 n.4), without holding *Tovar* for *Abrams* (which had been docketed on April 30, 2026). While *Abrams* lacks *Tovar*'s waiver-by-specific-objection complication, the denial in *Tovar* confirms that the Court does not view every petition raising this split as a mandatory grant where the conviction would stand regardless of the standard of review.

Netting these factors, we set **`probability: 0.25`** (`predicted_disposition: "denied"`, `granted: 0`).

---

## 4. Secondary Claims and Stakes Calibration

- **`disposition` (`0.25`):** Matches top-level `probability`.
- **`relist-increment` (`0.99`):** Because the snapshot is taken at the CFR moment (`distribution_count: 1`) before the response is filed, the petition is almost certain to be distributed again once the Solicitor General files the Brief in Opposition.
- **`cvsg-increment` (`0.0`):** The United States is already the respondent.
- **`summary-disposition-route` (`0.05`):** Conditional on a grant, the Court would set this clean 7–4 Rule 29 split for plenary briefing and oral argument rather than summarily reversing a published opinion by Judges Smith, Scirica, and Bibas.
- **`dissent-from-denial` (`0.04`) and `order-writers`:** Small probability (`0.04` overall, led by `Gorsuch: 0.015`, `Sotomayor: 0.012`, `Jackson: 0.012`) that a Justice writes separately to highlight the Rule 29 preservation split, tempered by the poor harmless-error posture of Abrams's underlying sufficiency claims.
- **`big_case_score` (`0.30`):** If decided, the case would settle a recurring procedural question across federal criminal trials nationwide, giving it moderate doctrinal significance (`0.30`), though low public or political salience.
