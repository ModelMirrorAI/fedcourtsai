# Reasoning — P(grant) = 0.27

**Anchor.** `context.json` freezes band `baseline` (sal-v6), with `cert_anchor.rate` = 0.0519 (10-Term pooled reached rate). That is the scored yardstick. The band is driven by the single distribution, and it does not capture this petition's unusual features.

**Adjustments up (large):**
- **Amicus support.** The snapshot shows 14 amicus briefs at the cert stage, including West Virginia + 21 States. In the statpack amicus cut, the `2+` bucket grants 18.2% + GVR 4.5% (n=1542), against 2.0% for `0` (n=11414). Fourteen is far past the bucket floor, and a large multistate brief is a strong signal.
- **Clean question.** The QP is purely "overrule Locke v. Davey." Both the Fourth Circuit panel and the district court called the case "directly analogous" / "on all fours" with Locke, and the BIO concedes it is "factually on all fours with Locke" (BIO §II). Only this Court can answer the question, so no circuit split is possible, and that absence is no strike against the petition. Judge Richardson's concurrence below asked the Court to reconsider Locke.
- **Doctrinal trajectory.** Trinity Lutheran, Espinoza and Carson have narrowed Locke. Carson cabined it to "vocational religious instruction." Several Justices (Thomas, Gorsuch) have written that Locke should be revisited. Four votes to grant are plausible: Thomas, Alito, Gorsuch, plus one of Kavanaugh or Barrett.
- **Counsel.** Experienced Supreme Court counsel (Troutman Pepper's Tseytlin, First Liberty, National Legal Foundation).

**Adjustments down:**
- The Court has repeatedly chosen to distinguish Locke rather than overrule it. Roberts wrote both Espinoza and Carson that way, and stare decisis caution from Roberts, Kavanaugh and Barrett may favor waiting again.
- The BIO's vehicle argument rests on Virginia's own anti-establishment history (Madison's Remonstrance, the Statute for Religious Freedom). It is a merits point more than a true vehicle defect, but it may give cautious Justices a reason to wait. I found no mootness, standing or preservation problem in either filing.
- Only one distribution so far. The one "Rescheduled" entry came before any conference, so it is weak evidence.

**Net.** Starting from ~5% and the amicus `2+` bucket's ~20–23% grant-family rate, the profile here is stronger than the typical 2+ petition, offset by the Court's demonstrated reluctance to overrule Locke outright. I settle at 0.27.

**Other claims.** Relist-increment 0.55: a grant almost always follows a relist, and a reschedule also counts. CVSG 0.02. Summary route given grant 0.03. Dissent-from-denial given denial 0.33: Thomas and Gorsuch have a record on Locke. The order-writers numbers are unconditional (≈ P(deny) × per-Justice write rate) and consistent with the 0.33.

**Inputs used.** The snapshot `2026-11-02.json`; `questions-presented.txt`, `petition.txt` (QP, vehicle §II, statement), `brief-in-opposition.txt` (all three arguments), and `cert-reply.txt` (present but not read in detail, so I do not rely on its arguments); `metrics/statpack.md` (amicus, relist, CVSG and band cuts). `same-question.json` lists no matching petitions. The amicus entries are marked "VIDED", but `vide_links` and `RelatedCaseNumber` are empty, so I had no companion docket to read. I did not use web or MCP retrieval.

**Uncertainty.** The main uncertainty is the Justices' appetite for formally overruling a precedent they have already hollowed out. Reasonable forecasts span 0.15–0.45.
