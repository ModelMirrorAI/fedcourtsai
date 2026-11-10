# Predictor Rationale (`scotus/9026000201` — `evt-petition-disposition`)

## Headline Forecast

- **`granted`**: `1`
- **`probability`**: `0.94`
- **`predicted_disposition`**: `"granted"`
- **`big_case_score`**: `0.78`

## Base-Rate Anchor

From `record/context.json`, this cell is in `forward` mode at `moment: distribution` (`cutoff: null`) for October Term 2026 (`term: 2026`). The frozen conditioning state places the petition in the **`federal`** salience band under `sal-v8`, with `distribution_count: 1` and `cvsg_date: null`.

The pre-registered yardstick in `record/context.json` (`cert_anchor`) is **`0.7311`** (`73.11%`), pooled over the 10-Term lookback window strictly preceding OT2026 under `sal-v8` (`statpack_digest: sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`). In `metrics/statpack.md` ("Segment base rate by salience band (sal-v8)"), the `federal` band's bracketed `reached` grant rates across the nine rendered prior Terms (OT2017–OT2025) pool to 155 grants out of `n=212` weighted resolved petitions (`73.11%`):

- OT2025: `57.1%` (`n=28`)
- OT2024: `62.5%` (`n=16`)
- OT2023: `86.7%` (`n=30`)
- OT2022: `89.5%` (`n=19`)
- OT2021: `75.0%` (`n=12`)
- OT2020: `67.4%` (`n=43`)
- OT2019: `96.3%` (`n=27`)
- OT2018: `47.6%` (`n=21`)
- OT2017: `75.0%` (`n=16`)

Across the whole live/historical slice in `metrics/statpack.md` ("Cert petitions by salience band"), `federal` petitions resolve as `granted 52.5%, denied 23.3%, gvr 21.0%, dismissed 3.2%` (`n=219` resolved). By comparison, the unconditioned paid-segment cuts sit much lower (`1.8%` grant family at `relist_bucket = 0`, `n=10204`; `3.9%` grant family for `ca5`, `n=5418`; `22.7%` grant family for `2+` cert-stage amicus briefs, `n=1446`), because those cuts are dominated by private petitioners. I therefore anchor directly on the `73.11%` (`0.7311`) `federal` band base rate.

## Case-Specific Adjustments from the Anchor (`0.7311` → `0.94`)

Provisioned filings read from `record/documents/` (`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, `decision-below.txt`, and `lower-court-docket.txt`), together with `record/snapshots/2026-11-10.json` and the related dockets in `record/related/` (`26-199.json`, `26-332.json`, `26-335.json`, all linked via `relation: "vided-amicus"` in `related.json`), establish that this is an unusually strong Solicitor General plenary-review petition even within the already-high `federal` band:

1. **Act of Congress invalidated on its face:** In its published opinion on remand (*National Horsemen's Benevolent & Protective Ass'n v. Black*, 178 F.4th 224 (5th Cir. June 11, 2026), reproduced in `decision-below.txt` and `petition.txt`), the Fifth Circuit declared the enforcement provisions of the Horseracing Integrity and Safety Act of 2020 (HISA), 15 U.S.C. § 3051 *et seq.*, facially unconstitutional under the private nondelegation doctrine. As the Solicitor General notes (`petition.txt`, p. 15), the Court's near-uniform practice when a federal court of appeals invalidates a federal statute is to grant plenary review.
2. **Direct, post-GVR circuit split:** In June 2025, the Court granted, vacated, and remanded both the Fifth Circuit's prior judgment in this case (No. 24-429, `145 S. Ct. 2835`, and No. 24-433, `145 S. Ct. 2837`) and the Sixth Circuit's prior judgment in *Oklahoma v. United States* (`145 S. Ct. 2836`) for reconsideration in light of *FCC v. Consumers' Research*, 606 U.S. 656 (2025). On remand, the Sixth Circuit again rejected a facial private-nondelegation challenge to HISA's enforcement provisions (*Oklahoma v. United States*, 163 F.4th 294, 310–316 (6th Cir. 2025)), whereas the Fifth Circuit reissued its holding invalidating those provisions and expressly acknowledged that it "part[s] ways with our Sixth Circuit colleagues" (`decision-below.txt`, p. 34 n.22; `petition.txt`, p. 14). Because both circuits have already reconsidered the question under *Consumers' Research*, the split is intractable and cannot be resolved by another GVR.
3. **Prior Supreme Court stay of the Fifth Circuit's mandate:** In October 2024, the Court granted an application to stay the Fifth Circuit's mandate pending certiorari in this litigation (*Horseracing Integrity & Safety Authority, Inc. v. National Horsemen's Benevolent & Protective Ass'n*, No. 24A287, `145 S. Ct. 8`; confirmed via corpus lookup `scotus/69315289`). That stay maintains HISA's nationwide operation while the litigation proceeds and reflects an existing institutional commitment to resolve the constitutional question.
4. **Universal acquiescence by all respondents and heavy amicus support:** All three respondent filings in `brief-in-opposition.txt`—the National HBPA's brief in response (pp. 1, 13–20, 38–42), the Gulf Coast Racing Plaintiffs' consolidated brief in response (pp. 1–3, 6–8, 11–12), and the State of Texas's consolidated memorandum (pp. 1, 3–4)—expressly agree that certiorari should be granted in Nos. 26-199 and 26-201. In addition, the `2026-11-10.json` snapshot records 10 cert-stage amicus briefs supporting the petitioners (filed on September 17–18, 2026, all marked `VIDED` across Nos. 26-199 and 26-201).

## Uncertainties and Residual Risks (`0.06` Non-Grant Complement)

Given the factors above, the probability that the Court grants review of the HISA enforcement nondelegation question across the pending cluster of petitions is near 98–99%. Two modest vehicle-and-consolidation considerations specific to Docket No. 26-201 account for keeping `probability` at **`0.94`** (with `predicted_disposition: "granted"`):

1. **Multi-docket coordination across five pending petitions:** The related dockets in `record/related/` (`26-199.json`, `26-332.json`, `26-335.json`) are all distributed alongside No. 26-201 for the December 4, 2026 Conference, and corpus lookup confirms that *Oklahoma v. United States* (No. 25-1325, `scotus/73500226`) was distributed for the October 9, 2026 Conference and remains pending. While the Solicitor General (`cert-reply.txt`, p. 6) and all respondents (`brief-in-opposition.txt`) agree that the Court should grant both the FTC's petition (No. 26-201) and the Authority's petition (No. 26-199) and consolidate them (while holding *Oklahoma*, No. 25-1325), there is a small mechanical chance (`~0.04–0.05`) that the Court grants only one lead petition (e.g., No. 26-199 or No. 25-1325) and holds No. 26-201 pending the merits decision.
2. **Appellate-jurisdiction contention raised by the *Oklahoma* petitioners:** As the Solicitor General addresses in `cert-reply.txt` (pp. 2–3), the petitioners in *Oklahoma* (No. 25-1325) argued that the Fifth Circuit challengers had attempted to reserve unresolved claims in the district court, potentially casting doubt on finality under 28 U.S.C. § 1291. The Solicitor General's reply demonstrates that the district court's final judgment expressly found those claims "voluntarily withdr[awn]" and that the challengers confirmed abandonment on appeal (`cert-reply.txt`, p. 3). Nevertheless, even a weak finality objection introduces a slight risk (`~0.01–0.02`) that the Court could prefer or add *Oklahoma* as a vehicle.

## Secondary Claims and Big-Case Score

- **`relist-increment` (`0.55`):** The snapshot shows 1 distribution (for December 4, 2026). Because the Court routinely relists once before granting—especially when sorting through companion petitions (No. 26-199), cross-petitions (Nos. 26-332 and 26-335, plus National HBPA's cross-petition referenced in `cert-reply.txt` at p. 3 n.*), and a held petition from another circuit (No. 25-1325)—at least one further distribution is slightly more likely than an immediate grant on December 4.
- **`cvsg-increment` (`0.001`):** The Solicitor General is counsel of record for the petitioner, making a CVSG practically impossible.
- **`summary-disposition-route` (`0.03`):** Conditional on a grant, plenary review is ~97% likely because the Court already GVR'd this case in light of *Consumers' Research* and both the Fifth and Sixth Circuits have now addressed *Consumers' Research* in full published opinions. The `0.03` probability accounts mainly for the remote possibility that No. 26-201 is held behind a companion docket and later resolved by a post-merits GVR.
- **`dissent-from-denial` (`0.15`) and `order-writers` (`0.001`–`0.004`):** Plenary grant orders almost never carry separate writings. Conditional on a denial, the most likely scenario is a vehicle hold/denial alongside a grant in a companion docket (no dissent), with a minority chance of an outright denial of the whole HISA cluster that would draw a dissent from denial.
- **`big_case_score` (`0.78`):** If decided on the merits, this case will be the Court's marquee follow-up to *FCC v. Consumers' Research* on the private nondelegation doctrine, determining the survival of a nationwide federal regulatory statute (HISA) and shaping the constitutional boundaries for self-regulatory bodies such as FINRA.
