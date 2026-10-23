# Predictor Rationale (`reasoning.md`)

## Summary of Forecast

- **Top-level `probability` (`disposition`)**: `0.015` (`granted: 0`, `predicted_disposition: "denied"`)
- **`relist-increment`**: `0.12`
- **`cvsg-increment`**: `0.005`
- **`summary-disposition-route`**: `0.15` (conditional on grant)
- **`dissent-from-denial`**: `0.02` (conditional on denial)
- **`big_case_score`**: `0.35`

## Inputs Read and Retrieval Status

I read the provisioned snapshot `data/cases/scotus/9026000328/record/snapshots/2026-10-23.json` (`input_snapshot: "2026-10-23.json"`), `record/context.json`, `record/related/related.json` and `record/related/26-350.json`, and all provisioned documents under `record/documents/` (`documents.json`, `questions-presented.txt`, `petition.txt`, and `appendix.txt`). No brief in opposition was filed; both respondents waived their right to respond on October 15, 2026.

I also queried the corpus via `uv run fedcourts query` for the companion petition (`26-350`), the related Third Circuit petitions cited in the petition (`26-159` and `26-263`, *Whittaker, Clark & Daniels*), and the prior South Carolina receivership petition cited in the opinion below (`25-213`, *Atlas Turner, Inc. v. Welch*). An attempted lookup on the CourtListener MCP server returned HTTP 429 (rate limit exceeded), so I degraded gracefully to the provisioned record and local corpus tools as instructed by the prompt contract.

## Base-Rate Anchoring

From `record/context.json`, this cell is in `mode: "forward"`, `stage: "cert"`, `moment: "distribution"`, `term: 2026`, `salience_version: "sal-v4"`, `band: "baseline"`, `distribution_count: 1`, `cvsg_date: null`, and `signals_observable: true`.

In `metrics/statpack.md`, the **"Segment base rate by salience band (`sal-v4`, paid scored segment)"** table shows the bracketed `[reached]` grant rate for the `baseline` band across the five rendered Terms strictly preceding OT 2026 (OT 2021–OT 2025):

- **OT 2025**: `3.3%` (`n = 1,412`) -> ~46.6 grants
- **OT 2024**: `1.7%` (`n = 1,422`) -> ~24.2 grants
- **OT 2023**: `2.4%` (`n = 1,508`) -> ~36.2 grants
- **OT 2022**: `2.6%` (`n = 1,353`) -> ~35.2 grants
- **OT 2021**: `3.4%` (`n = 1,531`) -> ~52.1 grants

Pooling across all five prior Terms (`N = 7,226` weighted petitions reaching `baseline`), the pooled `baseline [reached]` anchor is **~2.69% (0.027)**.

Cross-checking the auxiliary cuts in `statpack.md` for the paid scored segment:
- **Relist count = 0** (1 conference distribution, terminal): `1.7%` grant rate (`34 / 2,013`).
- **No CVSG** (paid scored segment): `5.0%` grant rate (`376 / 7,502`).
- **State court of last resort** (whole modern cert slice): `1.8%` grant rate (`85 / 4,768`).

## Case-Specific Adjustments

Starting from the **2.7%** (`0.027`) pooled `baseline [reached]` anchor, I consider upward and downward factors:

### Upward Factors
1. **High-profile counsel, coordinated companion filing, and amicus support**: Petitioners are represented by Amir C. Tayrani (Gibson Dunn), and the companion vide petition in No. 26-350 (*Altrad Investment Authority S.A.S. v. Cape Intermediate Holdings Limited*) is represented by Kannon K. Shanmugam (Paul, Weiss). Three amici (National Union Fire Insurance Company, Atlantic Legal Foundation, and Washington Legal Foundation) filed briefs supporting petitioners at the cert stage.
2. **Institutional salience of the South Carolina asbestos receivership docket**: The petition challenges the appointment of Receiver Peter D. Protopapas, who has been appointed across dozens of asbestos cases in South Carolina, and points to an anti-suit injunction issued by the High Court of Justice of England and Wales (EWHC) as well as the Third Circuit's decision in *In re Whittaker, Clark & Daniels, Inc.*, 176 F.4th 241 (3d Cir. 2026).

### Downward Factors (Decisive)
1. **Both respondents waived a response and no response has been called for**: On October 15, 2026, both the Tibbs plaintiffs and the Receiver filed waivers of their right to respond, and the petition was distributed on October 21, 2026, for the November 6 conference without a call for response (CFR). Under Supreme Court practice, the Court virtually never grants certiorari without first requesting a response. While a CFR could still be issued after the November 6 conference, waivers at distribution indicate that the case currently sits at the earliest, lowest-probability stage.
2. **The purported conflict with the Third Circuit's *Whittaker* decision is illusory**: In *In re Whittaker, Clark & Daniels, Inc.*, 176 F.4th 241 (3d Cir. 2026), the Third Circuit held that an unrecognized South Carolina post-judgment receiver could not divest a New Jersey corporation's board of its authority to file for Chapter 11 bankruptcy in New Jersey—a core internal corporate governance act—while explicitly noting that New Jersey courts can recognize foreign receiverships. Here, by contrast, the South Carolina Supreme Court *narrowed* the pre-judgment receivership order to authorize the Receiver *only* "to collect insurance assets and pursue such legal and equitable claims the corporation may have that can result in the receipt of assets responsive to the Tibbs' pending claims" (Pet. App. 27a), expressly holding that the Receiver may *not* control Cape's internal affairs or accept service in other lawsuits. That creates no direct conflict with *Whittaker*.
3. **Prior denial of certiorari in *Atlas Turner, Inc. v. Welch* (No. 25-213)**: On January 12, 2026, after two distributions, this Court denied certiorari in *Atlas Turner, Inc. v. Welch*, which arose out of the same South Carolina Supreme Court doctrine (*Welch v. Advance Auto Parts, Inc.*, 445 S.C. 640 (2025)) and challenged the same Receiver's appointment on federal constitutional grounds. Indeed, the vehicle here is weaker than in *Welch* because the South Carolina Supreme Court applied *Welch*'s narrowing limitation directly to the Confirmation Order below.
4. **Severe vehicle, standing, preservation, and finality defects**:
   - **Third-party standing**: Petitioners (Charter Consolidated, Ltd., Central Mining & Investment Corporation, Ltd., and ESAB Corporation) are *not* the corporation in receivership (Cape Intermediate Holdings Limited, or CIHL). CIHL deliberately defaulted and has never appeared in South Carolina courts. Petitioners are third-party alter-ego defendants seeking to collaterally attack the receivership order entered in a separate lawsuit (*Park*) to defeat the Receiver's authority to bring third-party claims against them.
   - **Lack of finality under 28 U.S.C. § 1257(a)**: The South Carolina Supreme Court's decision is interlocutory. It remands the case to the circuit court to conduct jurisdictional discovery, decide personal jurisdiction over Petitioners, determine which jurisdiction's choice of law governs the alter-ego/amalgamation claims under *Pertuis*, and adjudicate the affirmative defense of the mutual release on the merits (Pet. App. 22a, 28a, 32a). Petitioners' reliance on *Cox Broadcasting* is tenuous because Petitioners can prevail on personal jurisdiction or on the merits of the alter-ego and release defenses in the state courts, mooting any federal constitutional question.
   - **Preservation and adequate and independent state grounds**: As the South Carolina Supreme Court emphasized in both its opinion (Pet. App. 14a–18a) and its August 19, 2026 order denying a stay of the remittitur (Pet. App. 48a–50a), Petitioners could only challenge the *Park* receivership order collaterally if it were "void" for lack of subject-matter or personal jurisdiction over CIHL, which the court resolved under settled state procedural law; moreover, the court noted that Petitioners failed to preserve their Foreign Commerce Clause / foreign-affairs arguments below (Pet. App. 48a–49a).

Weighing these substantial vehicle defects and the absence of a genuine split against the high-caliber advocacy and amicus support, I adjust downward from the `0.027` (`2.7%`) `baseline [reached]` anchor to **`0.015` (1.5%)**.

## Claim-Level Rationale

- **`disposition` (`0.015`)**: Matches top-level `probability`.
- **`relist-increment` (`0.12`)**: In `statpack.md` (paid scored segment), 2,013 of 2,340 petitions (`86.0%`) end with 0 relists (`distribution_count = 1`), meaning ~14.0% of paid scored petitions at their first conference are distributed at least once more. Because respondents waived a response, a relist would generally require either a Call for Response (CFR) or a hold/synchronization check with companion No. 26-350 or the pending *Whittaker* petitions (Nos. 26-159, 26-263). Given the presence of Gibson Dunn / Paul Weiss counsel and three amicus briefs, there is a small chance a chamber calls for a response or holds briefly, placing `P(relist-increment)` at `0.12`, slightly below the ~14% unconditional paid-segment forward rate.
- **`cvsg-increment` (`0.005`)**: Very few petitions without a response even reach a CFR, and a private state-court tort/receivership dispute with unpreserved foreign-affairs claims and threshold § 1257 finality defects is an exceedingly unlikely candidate for a CVSG.
- **`summary-disposition-route` (`0.15`)**: Conditional on a grant, across OT 2017–OT 2025 in `statpack.md` ("Cert-order dispositions as a share of grants"), summary cert-order dispositions (GVRs and summary reversals) represent roughly 25%–35% of all grants overall, though lower for private paid petitions without an intervening precedent. Here, the only plausible summary-disposition scenario conditional on a grant would be a hold and GVR if the Court were to grant *Whittaker* (No. 26-159 or No. 26-263) and announce a broad constitutional rule on state-court receiverships. That is unlikely even conditional on a grant, so I set `0.15`.
- **`dissent-from-denial` (`0.02`)**: Conditional on denial, separate writings are rare (~1–2% of denials) and none accompanied the denial of certiorari in *Atlas Turner, Inc. v. Welch* (No. 25-213).
- **`big_case_score` (`0.35`)**: If decided on the merits, a ruling constitutionalizing the internal affairs doctrine or limiting state courts' equitable authority to appoint receivers over foreign corporations in mass-tort litigation would be significant for corporate and cross-border litigation, though narrower than major constitutional or nationwide public-law disputes.

## Key Uncertainties

The primary uncertainty is whether the Court calls for a response (which would automatically generate at least one additional distribution once the BIO arrives, lifting `relist-increment`). Even if a response were requested, however, the interlocutory posture under 28 U.S.C. § 1257(a), third-party standing obstacles, and the South Carolina Supreme Court's narrowing of the receivership order would almost certainly lead to a denial once the BIO highlighted those vehicle flaws.
