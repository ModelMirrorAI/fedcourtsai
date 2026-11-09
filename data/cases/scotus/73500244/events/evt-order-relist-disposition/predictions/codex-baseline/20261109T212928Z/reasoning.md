# Rationale

## Call and information set

I assign **0.44 to any grant** and predict denial, narrowly. This includes plenary review and the smaller possibility of a grant accompanied by summary action; it is not a prediction about who would win after argument.

This is a forward, cert-stage relist cell. I use the case-level `record/snapshots/2026-11-09.json` and `record/context.json`: band **high**, salience version **sal-v8**, Term **2025**, **three distributions**, no CVSG. The distributions were entered September 30, November 2, and November 9 for conferences on October 16, November 6, and November 13, respectively. Although the event description says first relist, the actual frozen baseline already contains two repeat distributions. All increment probabilities start after the third distribution, not after an imagined one-distribution baseline. The date cutoff is November 10; it bounds the staged record, not forward retrieval.

I read the provisioned question presented, petition, opposition, reply, appendix, matched decision below, and lower-court docket summary. The documents manifest identifies these filings as untruncated, non-OCR, and text-available. No separate amicus texts, companion snapshot, or same-question list was provisioned. I do not infer their contents or any companion's current status. I neither know nor retrieved this petition's disposition, subsequent history, or coverage of its decision.

## Anchor and calibration

The authoritative frozen `cert_anchor.rate` is **0.3455056179775281**, with a ten-Term lookback and the statpack digest recorded in context. This is the proper starting point, not the whole-docket grant rate. The committed `metrics/statpack.md` sal-v8 high-band reached rates for Terms strictly before 2025 corroborate roughly **34.6%, n=712**, pooling the displayed 2017–2024 rows. I do not add the petition's own Term or 2026 to that anchor.

The paid scored-segment relist table supplies a cross-check, not an independent likelihood multiplier. Terminal relist buckets have grant-family shares of **13.5%, n=2532** for one relist; **41.2%, n=495** for two; and **37.3%, n=483** for three or more. Pooling all buckets from one upward gives approximately **20.7%, n=3510**, using rounded table percentages. That pool mixes genuine relists with pre-conference reschedules and is less specific than this petition's three dated distributions. Its terminal buckets are not a forward probability of another distribution.

The CVSG cut is **34.8% grant-family, n=164**, versus **6.4%, n=13550** without a CVSG. These are descriptive overlapping populations, not an additional adjustment for a government respondent that has already opposed review. There are **two docketed amicus briefs**, Barnett and Cato, both July 2. The amicus table's 2+ bucket is **22.7% grant-family, n=1446**; it is a terminal-count stakes proxy, not a conditional estimate after relisting. I do not multiply any of these marginal rates together.

The required filtered corpus query returned three unrelated commercial/regulatory grants with no opinion text. Because the query selected grants, it cannot establish a grant rate; I use it only as a check that the retrieval surface works, not as substantive authority or a basis to inflate this forecast.

## Why move upward from the anchor

The petition's question is whether an automobile is automatically an instrumentality of interstate commerce under 18 U.S.C. 1201(a)(1). It is a recurring federalism question, not merely a request to reweigh trial evidence. The petition, pp. 3–5 and 12–14, identifies the Toyota as the charged interstate-commerce connection and explains why the statutory and constitutional issues are outcome-determinative. The appendix, pp. 2a–4a, and matching December 31, 2025 Eleventh Circuit opinion confirm that the court decided both issues and treated Bryan as binding. This is materially better preservation than the separate McMichael petition as described in Brown's filings; I have not retrieved that petition's later proceedings.

The opposing decisions share a concrete practical dispute about wholly local kidnappings involving cars. The petition, pp. 6–11, and reply, pp. 1–3, point to Chavarria, other circuits' categorical rules, and Judge Calvert's dissent in Bryan. Brown's unpublished opinion largely applies recent precedent, so its unpublished status is a modest negative, not a fatal absence of a legal issue. The two repeat distributions and two amici strengthen the inference that the question is attracting serious attention. These considerations justify moving above the 34.6% anchor.

## Why stop below one-half

The government's strongest objection is not generic disagreement with Brown's merits position: it is that the supposed circuit split is narrower than advertised. The opposition, pp. 10–12, distinguishes an indictment identifying a Toyota Sequoia from Chavarria's indictment alleging only an unspecified motor vehicle. I checked Chavarria itself through CourtListener, opinion 11071905, corresponding to **140 F.4th 1257 (10th Cir. 2025)**. Its slip opinion, pp. 19–20, expressly distinguishes automobiles from motor vehicles, and pp. 22–23 limits the holding to the undefined generic category and the deficient indictment. Its broad federalism reasoning supports Brown, but its express reservation gives the Court a genuine reason to await a cleaner conflict. I therefore do not accept the reply's assertion that the opposite result in the Tenth Circuit is inevitable.

The opposition, pp. 5–10, also offers a substantial statutory and doctrinal defense: the 2006 amendment uses the instrumentality formulation associated with the second Lopez category, which permits regulation despite an intrastate threat. The reply answers with constitutional avoidance and the distinction between an automobile's potential and actual commercial use, but certiorari is not awarded simply because that argument is substantial. The government's narrower preservation objection to the dominant-use argument is a secondary negative; the underlying Commerce Clause claim was actually decided below.

The 44% forecast reflects meaningful selection signals without treating relisting as a grant announcement or the alleged split as undisputed. I would increase it substantially if the Tenth Circuit squarely rejected jurisdiction over an expressly identified automobile; I would decrease it if the repeated distributions proved to be calendar-only reschedules.

## Additional claims and stakes

- **Further distribution: 0.60.** With three distributions already recorded, another conference is more likely than not, but a decision after the already scheduled November 13 conference remains substantial. My central procedural path is one more distribution, with two additional distributions also plausible. This is a judgment, not a published transition rate.
- **New CVSG: 0.005.** The Solicitor General has already provided the United States' opposition. An invitation to supply the same government's views would add little. No CVSG is expected.
- **Summary route conditional on grant: 0.06.** There is no identified intervening controlling decision supplying a GVR instruction, and a disputed constitutional/statutory boundary is better suited to argument. Almost all grant probability is therefore plenary.
- **Writing conditional on denial: 0.35.** The constitutional limits argument and repeated consideration leave a real possibility of a dissent or statement, but silence is still more likely. The order-writer probabilities are unconditional and independent, concentrated on Thomas and Gorsuch; they neither sum to one nor purport to identify private cert votes. Their combined scale is compatible with a 35% writing probability on the denial branch plus occasional writings on a grant.
- **Stakes: 0.68.** A decision could affect several statutes using an instrumentality hook and the federal/state division of criminal authority. This is significance if decided, not another estimate of grant likelihood.

## Input and tooling limitations

The lower-court docket summary says no en banc petition was filed and no disposition was found. The actual appendix, p. 20a, expressly denies both panel and en banc rehearing on February 24, 2026, with no active judge requesting a poll. I prefer the filed order and flag the enrichment conflict; I infer no recorded rehearing dissent. The lower-court opinion matches the caption, case number, judgment date, and appendix, so the match itself is sound.

Two web attempts produced no usable displayed content; the Chavarria check rests on the successful CourtListener MCP retrieval instead. The initial CLI paths command failed because uv's default cache location was read-only; redirecting `UV_CACHE_DIR` to `/tmp/uv-cache` and using the existing environment with `--no-sync` resolved it without installing anything. No input or other cell's output was modified or consulted.
