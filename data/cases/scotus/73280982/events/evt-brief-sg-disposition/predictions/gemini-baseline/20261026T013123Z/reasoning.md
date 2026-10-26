# Rationale for Prediction (`scotus/73280982`, `evt-brief-sg-disposition`)

## Summary of Forecast

- **`probability` / `disposition`**: **0.82** (`granted: 1`, `predicted_disposition: "granted"`)
- **`relist-increment`**: **0.99**
- **`cvsg-increment`**: **0.00** (vacuous; CVSG already ordered on June 1, 2026 and SG brief filed October 7, 2026)
- **`summary-disposition-route`**: **0.02** (conditional on grant)
- **`dissent-from-denial`**: **0.15** (conditional on denial)
- **`big_case_score`**: **0.62**

## Provisioned Inputs Used

I read and relied upon the following provisioned files under `data/cases/scotus/73280982/`:
1. `events/evt-brief-sg-disposition/event.yaml` (`stage: cert`, `moment: sg-brief`, `opened_at: '2026-10-07'`).
2. `record/context.json` (`mode: "forward"`, `term: 2025`, `band: "high"`, `salience_version: "sal-v4"`, `distribution_count: 1`, `cvsg_date: "2026-06-01"`, `snapshot_date: "2026-10-07"`, `cutoff: "2026-10-08"`).
3. `record/snapshots/2026-10-07.json` (the docket snapshot through October 7, 2026).
4. `record/documents/documents.json` and the five provisioned document files:
   - `sg-invited-brief.txt` (Brief for the United States as Amicus Curiae, filed Oct. 7, 2026, 29 pages).
   - `petition.txt` (Petition for a Writ of Certiorari, filed Feb. 5, 2026, 60 pages, including the actual Questions Presented on page (I)).
   - `brief-in-opposition.txt` (Brief in Opposition, filed Apr. 23, 2026, 45 pages).
   - `cert-reply.txt` (Reply Brief for Petitioners, filed May 11, 2026, 21 pages).
   - `questions-presented.txt` (Note: due to a PDF kerning space in `QUESTION S PRESENTED` on page (I) of the petition, the automated QP extractor matched a later section heading on page 32 of the petition, `"E. The Questions Presented In This Case Are Exceptionally Important"`. Because both `petition.txt` at page (I) and `sg-invited-brief.txt` at page (I) contain the complete verbatim Questions Presented, no information was lost; I recorded a low-severity `info` note in `flags.json` for maintainer awareness.)
5. `metrics/statpack.md` for the committed base rates.

## Base-Rate Anchoring

This is a `cert`-stage prediction at `moment: sg-brief` for a paid OT2025 petition from the Ninth Circuit (`25-944`) carrying `band: "high"` under `sal-v4`, `distribution_count: 1`, and `cvsg_date: "2026-06-01"`.

1. **Salience-band base rate (`high`, `sal-v4`, strictly prior Terms OT2017–OT2024)**:
   Pooling the bracketed `reached` counts for the `high` band across the eight rendered Terms strictly preceding OT2025 in `metrics/statpack.md` (`Segment base rate by salience band (sal-v4)`):
   - OT2024: 40.5% ($n = 116$, $\approx 47.0$ grants)
   - OT2023: 31.4% ($n = 102$, $\approx 32.0$ grants)
   - OT2022: 37.1% ($n = 105$, $\approx 39.0$ grants)
   - OT2021: 32.1% ($n = 140$, $\approx 44.9$ grants)
   - OT2020: 34.2% ($n = 111$, $\approx 38.0$ grants)
   - OT2019: 25.5% ($n = 98$, $\approx 25.0$ grants)
   - OT2018: 35.4% ($n = 99$, $\approx 35.0$ grants)
   - OT2017: 41.7% ($n = 127$, $\approx 53.0$ grants)
   - **Pooled strictly-prior `high` band reached rate**: $313.9 / 898 = \mathbf{35.0\%}$ ($n = 898$).

2. **Statpack CVSG cut (`Cert petitions by CVSG status (paid scored segment)`)**:
   Across all resolved CVSG petitions in the paid scored segment ($n = 164$ resolved, 15 open), the disposition breakdown is `denied 62.2%, granted 29.3%, gvr 5.5%, dismissed 3.0%`. The grant family (`granted` + `gvr`) is $\mathbf{34.8\%}$ ($n = 164$).

Both anchors (~35.0% and ~34.8%) represent the **unconditioned** grant rate across *all* petitions that draw a CVSG—a population in which the Solicitor General recommends denial roughly three-quarters of the time.

## Case-Specific Adjustments and the Solicitor General's Recommendation

The critical new evidence at `moment: sg-brief` is `sg-invited-brief.txt`, signed by the Solicitor General and joined by the General Counsel and Solicitor of the Securities and Exchange Commission.

1. **What the Solicitor General recommended**:
   The United States explicitly recommends that **"the petition for a writ of certiorari should be granted with respect to the first question presented"** (SG Br. 1, 24), and proposes a modest reformulation of Question 1 ("Whether an issuer can be found liable under the misleading-omissions prong of Section 11(a) of the Securities Act of 1933, 15 U.S.C. 77a *et seq.*, based on a determination that the issuer failed to disclose interim financial information that is material within the meaning of Section 11(a), without an additional inquiry to determine whether the omission rendered any affirmative statement misleading," SG Br. I, 19). The United States recommends denying review on Question 2 (Item 303 of Regulation S-K).

2. **Why I adjust substantially upward from ~35% to 0.82**:
   - **Conditional impact of an SG recommendation to grant**: Because the ~35% CVSG base rate pools the ~75% of CVSG briefs recommending denial (which grant at <15%) with the ~25% of CVSG briefs recommending a grant or partial grant, an affirmative SG recommendation to grant certiorari historically results in a grant roughly 75%–88% of the time.
   - **Direct doctrinal continuity with *Omnicare* and *Macquarie***: Two Terms ago in *Macquarie Infrastructure Corp. v. Moab Partners, L.P.*, 601 U.S. 257 (2024), the Court unanimously held that Rule 10b-5(b)'s misleading-omissions clause covers only "half-truths, not pure omissions." And in *Omnicare, Inc. v. Laborers District Council Construction Industry Pension Fund*, 575 U.S. 175, 189–194 (2015), the Court emphasized that Section 11(a)'s misleading-omissions prong is not a general disclosure duty for all material information. Here, a divided Ninth Circuit panel (over Judge Rawlinson's comprehensive dissent) expressly "collaps[ed] the duty to disclose into materiality" whenever an alleged omission involves the relationship between a prior historical financial statement and a subsequent intra-quarter event (Pet. App. 23a, 28a). The SG and SEC persuasively demonstrate (SG Br. 10–13) that the Ninth Circuit nullified one of Section 11(a)'s two statutory elements.
   - **Multi-circuit split**: As the SG details (SG Br. 13–16), the Ninth Circuit's rule conflicts with decisions of the Third Circuit (*In re Adams Golf, Inc. Sec. Litig.*, 381 F.3d 267 (2004)), Tenth Circuit (*UFCW Local 880 Pension Fund v. Chesapeake Energy Corp.*, 774 F.3d 1229 (2014)), and Eleventh Circuit (*Oxford Asset Mgmt., Ltd. v. Jaharis*, 297 F.3d 1182 (2002)), which separate materiality from whether an omission renders an affirmative statement misleading, as well as the First Circuit's "extreme departure" test (*Shaw v. Digital Equip. Corp.*, 82 F.3d 1194 (1st Cir. 1996)), which the Ninth Circuit expressly rejected.
   - **High stakes and elite representation**: The petition is brought by Jeffrey B. Wall (Sullivan & Cromwell) with Cravath and Orrick, supported at the cert stage by three heavy-hitting amici (former SEC Commissioner Prof. Joseph A. Grundfest, SIFMA/U.S. Chamber of Commerce, and Washington Legal Foundation), and now backed by the United States and the SEC.
   - **Clean resolution of respondents' vehicle objections**: In the BIO (at 3, 22–23), respondents attempted to evade review by claiming they agree that an inquiry into misleadingness is required because materiality and misleadingness "converge" in this context. The SG's proposed reformulation—inserting the word "additional" before "inquiry"—cleanly frames the exact legal disagreement between the parties (SG Br. 18–19). Moreover, the interlocutory Rule 12(b)(6) posture matches *Macquarie*, 601 U.S. at 261–262.

3. **Why I stop at 0.82 rather than >0.90 (uncertainties and discount factors)**:
   - **Split recommendation across the two QPs**: The SG recommends denying review on Question 2 (Item 303). In their supplemental brief responding to the SG, respondents will argue that because the Ninth Circuit also vacated the dismissal of their Section 11(a) required-statements claim predicated on Item 303, reversing on Question 1 alone will not terminate the litigation on remand. While the SG directly rebuts this (SG Br. 23) and the Court frequently grants limited to a single question in multi-claim securities cases, a small residual risk remains that the Justices view the surviving Item 303 remand or the case-specific prospectus disclosures as diminishing vehicle appeal.

## Secondary Claims and Distributions

- **`relist-increment` (0.99)**: The snapshot is cut on October 7, 2026—the day the SG's brief was filed—when `context.distribution_count` is still `1` (from the May 12, 2026 distribution for the May 28, 2026 conference). Because the Clerk must re-distribute the petition for a post-CVSG conference after the 14-day supplemental-briefing window so the Court can act on the petition, `distribution_count` is virtually certain to increase from 1 to at least 2 (barring an extraordinarily unlikely Rule 46 settlement/dismissal within two weeks of a favorable SG brief).
- **`cvsg-increment` (0.00)**: A CVSG was already ordered on June 1, 2026; this claim is masked as vacuous by the harness at `moment: sg-brief`.
- **`summary-disposition-route` (0.02)**: Conditional on a grant, plenary review is overwhelmingly likely; the SG asks the Court to reformulate Question 1 for merits briefing and argument rather than to GVR or summarily reverse.
- **`dissent-from-denial` (0.15) & `order-writers`**: Conditional on a denial (an 18% event), there is roughly a 15% chance that at least one Justice notes a dissent or statement respecting the denial, given the SG's grant recommendation, Judge Rawlinson's dissent below, and the tension with *Omnicare* and *Macquarie*. In `order-writers`, I allocate small unconditional writing probabilities across the nine sitting Justices (`Thomas: 0.010`, `Alito: 0.009`, `Gorsuch: 0.006`, `Kavanaugh: 0.004`, `Sotomayor: 0.002`, and `0.001` each for `Roberts`, `Kagan`, `Barrett`, and `Jackson`), consistent with `P(deny) * P(dissent | deny) ≈ 0.027`.
