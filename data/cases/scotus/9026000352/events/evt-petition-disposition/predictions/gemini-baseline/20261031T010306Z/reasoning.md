# Predictor Rationale (`scotus/9026000352` — `evt-petition-disposition`)

## Summary of Forecast

- **Predicted Disposition:** `denied` (`granted: 0`, `probability: 0.002`)
- **Declared Claims (`cert-v3`):**
  - `disposition`: `0.002`
  - `relist-increment`: `0.015`
  - `cvsg-increment`: `0.001`
  - `summary-disposition-route`: `0.40`
  - `dissent-from-denial`: `0.002`
- **Big Case Score:** `0.03`

## Inputs Used

I read the provisioned snapshot `record/snapshots/2026-10-31.json`, `record/context.json`, `record/same-question.json`, and all three provisioned document files listed in `record/documents/documents.json` (`questions-presented.txt`, `petition.txt`, and `appendix.txt`, none truncated and none with `empty_text: true` or `ocr_derived: true`; `petition.txt` and the snapshot had petitioner contact details scrubbed via placeholders, which I treat as routine self-represented scrubbing). I also consulted `metrics/statpack.md` for base rates and ran three `uv run fedcourts query` commands against the corpus for recent 2020s SCOTUS priors and a citation check.

## Base-Rate Anchoring

From `record/context.json`, this cell is in `forward` mode with `band: "baseline"` under `salience_version: "sal-v4"`, `distribution_count: 1`, `cvsg_date: null`, and `term: 2026`. The harness-frozen anchor in `context.cert_anchor` is:
- **`cert_anchor.rate`:** `0.050890782339271884` (~5.09%), pooled over the `baseline` band's bracketed `reached` grant rate across the prior Terms in `metrics/statpack.md` (`lookback_terms: 10`, OT2017–OT2025, where the per-Term `baseline` reached rates range from 4.0% in OT2025 [n=1,314] to 5.9% in OT2022–OT2024 [n=1,196 to 1,312]).

Cross-checking the marginal cuts in `metrics/statpack.md`:
- **Modern discretionary-cert petitions overall:** 673 granted and 601 GVR out of 44,772 resolved (~2.8% grant family).
- **Originating circuit (`ca4`, modern cert petitions):** 95.2% denied, 2.2% dismissed, 1.3% granted, 1.3% GVR (n=3,422 resolved; 2.6% grant family).
- **Relist count (`0`, paid scored segment):** 96.8% denied, 1.3% dismissed, 1.3% granted, 0.5% GVR (n=10,204 resolved; 1.8% grant family among petitions ending without a relist).
- **CVSG status (`none`, paid scored segment):** 92.4% denied, 4.1% granted, 2.3% GVR, 1.2% dismissed (n=13,549 resolved).
- **Amicus count (`0`, paid scored segment):** 95.0% denied, 2.0% granted, 1.8% GVR, 1.3% dismissed (n=11,109 resolved).

## Case-Specific Adjustments

Starting from the 5.09% `baseline` reached anchor, every case-specific feature pushes the grant probability sharply downward to `0.002` (0.2%):

1. **Pro Se Filing With Unfocused, Non-Doctrinal Questions Presented:** Although docketed on the paid docket (`sJsonCaseType: "Paid"`), the petition is filed *pro se* by Dr. Jarin M. Wray. As shown in `questions-presented.txt` and `petition.txt`, the two questions presented do not frame a concrete question of federal statutory or constitutional interpretation. Instead, they ask rhetorically whether U.S. whistleblower laws apply to businesses linked to a foreign adversary and what actions a retired servicemember who took an oath of office can take when the federal government is compromised by a foreign adversary. Pages 15–23 of `petition.txt` consist largely of sweeping assertions linking dozens of unrelated corporations (Equifax, Experian, TransUnion, the NFL, the NBA, American Express, USAA, Compass Real Estate, and petitioner's former landlord) to entities in China.
2. **Unpublished Summary Affirmance of a Routine Rule 12(b)(6) Dismissal:** `appendix.txt` reproduces both the Fourth Circuit's June 29, 2026 judgment (`Wray v. RTX Corp.`, No. 25-2360, App. B) and the Western District of North Carolina's October 20, 2025 dismissal order (`Wray v. RTX Corp.`, No. 3:25-cv-00656-MOC-SCR, App. C). The Fourth Circuit affirmed in a two-sentence unpublished *per curiam* opinion after dispensing with oral argument. The district court dismissed petitioner's complaint on straightforward, settled threshold grounds:
   - Statutes without a private right of action (FCPA, ITAR, EAR, 18 U.S.C. §§ 371, 1348, 1956);
   - Inability of a *pro se* litigant to bring a *qui tam* False Claims Act action (`Wojcicki v. SCANA/SCE&G`, 947 F.3d 240, 244 (4th Cir. 2020));
   - Failure to allege administrative exhaustion with the federal Department of Labor under the Sarbanes-Oxley Act, 18 U.S.C. § 1514A (petitioner attached a North Carolina state DOL right-to-sue letter, App. G, rather than pleading federal OSHA/ARB exhaustion as required by § 1514A(b)(1)(A)); and
   - Failure to allege under the Dodd-Frank Act, 15 U.S.C. § 78u-6, that his termination resulted from a report to the SEC (`Digital Realty Trust, Inc. v. Somers`, 583 U.S. 149 (2018)).
3. **No Circuit Split and Misplaced Reliance on *Murray*:** Petitioner argues that the dismissal conflicts with *Murray v. UBS Securities, LLC*, 601 U.S. 23 (2024). However, the district court cited *Murray* and dismissed the Sarbanes-Oxley claim for failure to plead administrative exhaustion, not for failing to plead retaliatory intent. `record/same-question.json` also confirms zero related pending or resolved petitions above the 0.5 similarity threshold (`indexed: 9756`).
4. **No Response Filed and Direct Distribution:** The response was due October 16, 2026. Respondent RTX Corporation did not file a brief in opposition, and the petition was distributed on October 28, 2026 for the November 13, 2026 conference without any call for a response. The Court virtually never grants certiorari without a brief in opposition or an intervening decision warranting a GVR.

## Rationale for Secondary Claims and Distributions

- **`relist-increment` (`0.015`):** Because no response was filed and there is no plausible hook for a call for a response (CFR) or a relist, the petition is overwhelmingly likely to be denied at its first conference on November 13, 2026. The 1.5% probability accounts for rare administrative reschedules or clerical redistributions.
- **`cvsg-increment` (`0.001`):** A CVSG on an unopposed *pro se* petition appealing an unpublished Rule 12(b)(6) dismissal is virtually impossible.
- **`summary-disposition-route` (`0.40`):** Conditional on the remote event that the Court grants review, a summary remand (GVR) accounts for a substantial share (40%) of that tiny conditional probability mass because the Court would not set a case for plenary argument without first calling for a response, though plenary review after a hypothetical subsequent CFR accounts for the remaining 60%.
- **`dissent-from-denial` (`0.002`) and `order-writers`:** There is no divisive doctrinal question or circuit split that would attract a dissent from denial or a separate statement. I assign `0.002` to `dissent-from-denial` and distribute tiny individual writing probabilities (`0.0001` to `0.0005`, summing to `0.0023`) across the nine sitting Justices (`Roberts`, `Thomas`, `Alito`, `Sotomayor`, `Kagan`, `Gorsuch`, `Kavanaugh`, `Barrett`, `Jackson`), slightly higher for Justices who more frequently author separate writings on cert orders (`Thomas`, `Alito`, `Gorsuch`, `Sotomayor`, `Jackson`).
- **`big_case_score` (`0.03`):** Decoupled from grant odds, the underlying dispute is a fact-bound individual employment termination dismissed on routine pleading and exhaustion defects, carrying negligible broader legal or policy stakes if decided.

## Uncertainties

The primary residual uncertainty is purely procedural—whether an administrative reschedule before or at the November 13, 2026 conference adds a second distribution entry (`relist-increment`), which is why `relist-increment` (`0.015`) sits an order of magnitude above `disposition` (`0.002`). On the disposition itself, the record is complete and unambiguous.
