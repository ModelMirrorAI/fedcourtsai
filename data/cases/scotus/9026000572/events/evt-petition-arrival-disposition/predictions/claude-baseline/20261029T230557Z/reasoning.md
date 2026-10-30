# Reasoning — P(grant) = 0.52

**Inputs.** I read snapshot `2026-10-30.json`: two entries (petition filed Oct 28, 2026; the Rule 34.6 paper-only order). The SG (D. John Sauer) is counsel of record, the decision below is CA7 No. 25-3127 (July 30, 2026), and the case is a paid petition. `context.json` gives band `federal` (sal-v4), distribution_count 0, no CVSG, mode `forward`, and `paper_only_filings: true`. No documents were provisioned, which is expected for a paper-only docket, so I did not flag it. I identified the question from public sources (see retrieval.md).

**Anchor.** The arrival-population anchor is the `federal` band's bracketed `reached` rate, pooled across the prior Terms 2017–2025 in the sal-v4 table: about 151 grants out of n ≈ 206, so **≈ 73%**. (The 2026 row, 3/3, is my own Term and is excluded.) That figure covers grants plus GVRs across all SG petitions. Many of those are standalone petitions the Court takes on their own merits.

**Why I'm well below the anchor.** This petition is a follow-on to an issue the Court has already granted (*Rhoney v. Barbosa da Cunha*, granted Oct 1, 2026, on the same § 1225(b)(2)(A) question). Its outcome is therefore close to a single bet on how *Rhoney* comes out:
- Government wins *Rhoney* → GVR (counts as a grant) with ~0.97 probability.
- Government loses → denial (or Rule 46 dismissal), with maybe 5% for some other GVR or vacatur route.
- I put P(government wins *Rhoney*) at about **0.5**. Nine circuits rejected the government's reading and two accepted it, and the government's longstanding practice for nearly 30 years favors the respondents. On the other side, the textual argument about "applicant for admission" (§ 1225(a)(1)) is real, and this Court granted the government's petition. I lean slightly toward an even split.
- Combined: 0.5×0.97 + 0.5×0.05 ≈ 0.51. I add a little for a Munsingwear or mootness vacatur and for the chance this case is substituted if *Rhoney* fails as a vehicle, which gives **0.52**. The hold-for-a-lead-case structure is why the federal-band anchor does not carry over directly here.

**Claims.**
- relist-increment 0.96: a held petition is distributed at least once, and almost always again after the lead case is decided. The residual covers a quick Rule 46 dismissal or other early exit.
- cvsg-increment 0.003: the SG is the petitioner.
- summary-disposition-route | grant 0.88: almost every grant path here is a GVR. Plenary review only happens if the case is substituted for *Rhoney*.
- dissent-from-denial | denial 0.05: on a denial after *Rhoney*, Justices rarely write separately on held cases.
- order-writers: small values throughout, slightly higher for the Justices likeliest to dissent on either side (Thomas and Alito if the government loses; Jackson and Sotomayor on a GVR).

**Uncertainty and discounts.** Almost all of my uncertainty is about the *Rhoney* merits, and that call is a judgment, not a base rate. I am also assuming this case raises no distinct issue apart from *Rhoney*. I could not read the petition (paper-only), so I have not ruled out a separate question presented, such as a due-process or habeas-jurisdiction issue. If one exists, it could change the denial path. The event may also not resolve until mid-2027.
