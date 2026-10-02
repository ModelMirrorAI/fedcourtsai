# Rationale for the prediction

## Information set and target

This is a forward, grant-moment **merits** forecast, not a certiorari forecast. I read the event definition, the case-level `record/snapshots/2026-10-01.json`, and `record/context.json`. The snapshot records an October 1, 2026 grant limited to Question 1. The date-cut baseline excludes October 2 and later entries. Certiorari is settled history; I do not treat the two distributions or the context's `elevated` salience band as judgment predictors.

I read `record/documents/documents.json`, `questions-presented.txt`, and the pertinent factual, substantial-burden, and vehicle sections of `petition.txt` and `brief-in-opposition.txt`. The manifest reports both filings as nonempty and untruncated, with 51 and 46 PDF pages respectively. No merits briefs were provisioned, as expected at this moment. The docket records a reply, but its text is not in the supplied documents and I did not infer its arguments. The forecast therefore rests on the petition-stage adversarial record, not merits briefing or argument.

The target is whether the Kentucky judgment will be disturbed. I assign **0.80**, with an illustrative judgment allocation of reversed 0.50, vacated 0.28, mixed affirmed/reversed 0.02, affirmed 0.15, DIG 0.045, and equally divided affirmance 0.005. The first three sum to the scored probability. DIG risk belongs in the undisturbed complement. `granted=1` expresses the predicted disturbed judgment; it does not predict a new cert grant or an unconditional entitlement to build.

## Committed anchor and its limitations

I used only the statpack's merits section as a numerical anchor, not its cert-band table. Applying the repository's `october_term_year` function to the event's October 1, 2026 opening date returns grant Term **2026**: this implementation pivots at the calendar month of October. The context's `term: 2025` is not substituted for that grant-date axis. The eligible ten-Term window is therefore **2016–2025**. The committed section contains rows for 2017–2025 and none for 2016; no missing row is invented.

Summing those eligible rows gives **377 disturbed judgments / 540 parsed judgments = 69.81%**. Coverage is **540 parsed / 589 eligible grants = 91.68%**. A further **66 excluded cert-order dispositions sit outside the 589**, not inside it. The parsed sample clears the 30-judgment floor. Although this particular window happens to include every published merits row, I selected the rows by the ten-Term rule rather than simply adopting the pack-level rate.

The freshest grant-Term row is particularly censored: 2025 has **24 parsed / 50 grants**, including 17 disturbed judgments. Its resolved subset favors quicker dispositions and is not representative of all pending cases. More generally the baseline mixes substantive fields and reflects the stored parsed slice, not a religion-specific model.

The statpack file's most recent commit is `808f812e9`, dated **2026-09-28T12:02:50Z**. Its JSON exposes no build timestamp or corpus-wide newest-pull/newest-snapshot stamps, so that is a committed-artifact vintage, **not a verified corpus freshness date**. I did not pull or query the corpus and do not claim these counts describe its current remote state. The separate case baseline is the provisioned October 1 snapshot; no per-case `last_pulled` stamp was supplied in that snapshot.

## Why above the 69.81% anchor

The petition's account of the dispute and opinion below is concrete: a religious organization seeks a grotto on its adjacent parcel; the board approved it, but the state appellate courts held that local law did not permit the approval. The Kentucky Supreme Court accepted that construction was religious exercise but rejected substantial burden based on a potential smaller grotto on the church parcel and the organization's knowledge of the restriction. See petition pp. 5–9. That presents a plausible legal error susceptible to correction without the Court itself resolving the traffic evidence.

The statutory definition specifically includes building real property for religious exercise. Petition pp. 11–17 argue that the protected activity cannot be replaced with a court-selected smaller or relocated substitute and that notice of a restriction is not a waiver. I find that reading more persuasive than an approach under which acquiring land subject to a zoning rule largely defeats the federal protection against that rule. This is my interpretive forecast, not a statement that the Court has already adopted it in this case.

I verified the pertinent passage of **Holt v. Hobbs, 574 U.S. 352, 361–62 (2015)** through CourtListener's opinion text. Holt measures the burden on the religious exercise actually at issue rather than offsetting it with other available religious practices. It is a prior institutionalized-person case, not a decision of this land-use question. Extending its reasoning here is the principal substantive inference supporting my upward adjustment. The limited grant makes that substantial-burden issue the focus while removing the petition's separate equal-terms theory from my forecast.

## Why not higher

The BIO supplies important distinctions rather than only a generic defense. At pp. 23–26 it argues that RLUIPA requires a burden imposed by government and leaves the claimant the burden of proving substantiality. It distinguishes alternative ways to perform the same exercise from Holt's irrelevant availability of other religious practices. At pp. 25–27 it emphasizes the absence of evidence that the church parcel cannot accommodate a grotto. The petition's claim that a smaller shrine is an inadequate religious substitute should not be treated as a fully established evidentiary finding.

The BIO also identifies two nontrivial procedural risks at pp. 27–28: petitioner allegedly asked the Kentucky court to adopt the Livingston framework it now criticizes, and the applicable zoning scheme allegedly lacks the individualized-assessment permission required by § 2000cc(a)(2)(C). The latter is characterized by respondents as an adequate-and-independent-state-ground problem, but whether RLUIPA applies remains a federal question; I do not simply adopt respondents' jurisdictional label. Still, either issue could prevent the broad merits ruling forecast here or preserve the result below. Review being granted despite these objections does not eliminate them.

These counterweights restrain the forecast to 0.80 rather than near certainty. Vacatur and remand is a substantial alternative to outright reversal because the record and statutory predicates may require additional work. I put reversal first because my modal outcome identifies a mistaken legal standard, while leaving implementation and remaining defenses to the lower courts.

## Votes, significance, and limitations

The six-Justice majority is a lower-confidence extrapolation than the disturbed-judgment probability. I expect Roberts, Thomas, Alito, Gorsuch, Kavanaugh, and Barrett to favor protection of the specified religious exercise; the three predicted dissenters are more likely in my view to insist on a developed showing of substantial interference and preserve room for ordinary zoning. This is not a claim of automatic ideological alignment: the Holt rationale can support a broader coalition, especially if the opinion is narrower than my semantic forecast. No provisioned evidence identifies a recusal, and writing roles are left unstated.

The **0.64 significance score** reflects a nationally reusable interpretation of RLUIPA for religious institutions and local governments, tempered by the specialized land-use setting and exclusion of Question 2. It measures stakes, not the likelihood of reversal.

General-law web searches and an official-code open attempt returned no usable visible content; they contributed no facts. CourtListener successfully supplied the Holt passage after an initial reporter search returned an irrelevant case, which I disregarded. I did not seek this case's disposition or subsequent history, did not read other predictions or outcome files, and have no known prior knowledge of its eventual merits judgment. All substantive case facts used here came from the provisioned pre-judgment record. Retrieval limitations do not block this forecast.
