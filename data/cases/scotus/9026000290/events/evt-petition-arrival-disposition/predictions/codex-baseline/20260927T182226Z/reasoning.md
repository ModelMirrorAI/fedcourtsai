# Rationale

## Information set

This is a forward, cert-stage arrival prediction for Mihal Emberton v. Superior Court of California, City and County of San Francisco, et al., docket 26-290. I read the event definition, `record/context.json`, the provisioned `record/snapshots/2026-09-04.json`, the document manifest, the questions presented, and relevant portions of `petition.txt`, including the factual narrative, procedural history, cert arguments, and the reproduced state appellate orders. The baseline is cut before September 4, 2026; its single proceeding is the June 23 petition filing, with a response due October 5. Context freezes `baseline`, `sal-v4`, Term 2026, and zero distributions. The lack of a conference history is the arrival moment's definition, not negative evidence from a failure to relist.

The petitioner is a private individual. The government entities on the respondent side do not make this a state-petitioner or federal-petitioner case. The snapshot identifies a paid petition. The manifest lists readable petition and QP text, neither marked truncated or empty. No BIO is provisioned, and I do not infer any respondent concession or waiver from that absence.

## Base-rate anchor

I used the committed `metrics/statpack.md` and its `metrics/statpack.json` counterpart, not a live corpus query. The sal-v4 table matches the frozen salience version. For this private arrival cell, the relevant anchor is the baseline band's bracketed **reached** rate, not the terminal baseline rate and not the terminal zero-relist bucket. Pooling every displayed strictly prior Term, 2017 through 2025, using the JSON's unrounded rates and weighted denominators gives 638 implied grants / 12,720 weighted resolved petitions = **5.0157%**. Term 2026 is excluded. This is the class-floor anchor for the paid private-petitioner arrival population, not a guarantee that this individual case is typical.

I also read the paid-segment relist and CVSG cuts. Their terminal associations show why later docket attention matters, but they cannot supply an as-at-arrival transition probability. In particular, the 97.0% denial figure in the terminal zero-relist bucket is not my arrival anchor. The broad modern-cert disposition table supplies background only.

Vintage limitation: the checked-out statpack's latest file commit is `96ebdd342`, dated September 26, 2026 at 12:03:37 UTC. That is publication provenance, not a newest-pull or newest-snapshot stamp for the underlying corpus. I did not access the corpus blob or establish its freshness, and I make no claim about current corpus counts beyond this committed pack. Case-specific evidence is the September 4 baseline; the two document manifest entries report a September 5 fetch. No case-specific `last_pulled` is supplied.

## Why 0.4%, rather than the 5.02% anchor

The petition concerns San Francisco code enforcement arising from a residential fence and related property structures. The petition alleges unconstitutional searches, acquisition of information about property, improper violation notices, and defective administrative procedures. Those are the petitioner's allegations, not facts independently established here. The central QPs contrast visibility and location with property-based exclusion and propose a broad reconstruction of what constitutes a search or seizure (`questions-presented.txt`; petition pp. 21-30).

Three case-specific considerations substantially lower my estimate:

1. **The claimed conflict is not demonstrated as an appellate split.** The petition juxtaposes Supreme Court precedents and a Ninth Circuit curtilage decision against trial-level treatment of this dispute. The supplied California Court of Appeal order is an unexplained writ denial, not a developed competing constitutional holding (petition pp. 19-20, 25-30; App. 2). I cannot identify from these materials two appellate courts resolving the same legal question differently on comparable facts. The petition's characterization of precedent as internally inconsistent is advocacy, not an independently verified split.
2. **Vehicle and reviewability are uncertain.** The appendix index identifies an order sustaining a demurrer to a seventh amended complaint with and without leave to amend, followed by denial of extraordinary writ relief and denial of discretionary state review (App. i, 1-2). That combination suggests an interlocutory or otherwise complicated route to federal review. The petition invokes 28 U.S.C. section 1257(a), but the substantive trial order is not reproduced in the supplied text: after its opening cover material, the document directs readers to additional material in the Clerk's Office. I cannot establish finality, preservation, or alternative grounds from this input. This is a vehicle-risk discount, not a finding that Supreme Court jurisdiction is absent.
3. **The presentation is broad and fact-dependent.** The request combines local code interpretation, administrative fairness, property interests, and constitutional claims. The record does not show a clean appellate resolution of a narrow search question separated from those disputes. The important general subject of residential privacy does not by itself make this the likely vehicle for resolving it.

The nonzero 0.004 allows for an overlooked constitutional issue or a stronger vehicle in the unavailable trial materials. This is a judgmental adjustment, not a fitted likelihood ratio. Lack of a BIO and incomplete lower-court reasoning limit confidence in how far below the anchor this case belongs.

## Other estimates

- `relist-increment` = 0.97 prices at least one **additional distribution from zero**, ordinarily the initial distribution. I expect one total distribution, not repeated relisting. The residual allows dismissal, withdrawal, or another route without a recorded distribution; this probability is judgmental, not extracted from a terminal relist table.
- `cvsg-increment` = 0.001 reflects the lack of an identified federal administrative or sovereign interest calling for that procedure in this individual municipal dispute. It is not zero because the proposed constitutional rule is broad.
- `summary-disposition-route` = 0.20 is conditional on the unlikely grant, not an unconditional 20% probability. The supplied record identifies no new controlling decision for a GVR, while the petition's requested doctrinal change would more naturally require briefing if accepted.
- `dissent-from-denial` = 0.005 is conditional on denial. The materials do not establish a recurring appellate conflict likely to attract a public statement.
- Stakes = 0.20 is separate from grant likelihood: the asserted rule could affect municipal inspections generally, but the demonstrated dispute is local and individualized. I have no evidence here of broader institutional attention.

## Retrieval and limitations

I attempted general web retrieval of the Court's certiorari-selection rule and the state-judgment review statute without searching this case. Those calls returned no usable response content, so they supply no verified authority and did not change the forecast. No live CourtListener or corpus query was used. I did not retrieve this petition's disposition, later docket, or subsequent history, and I do not know its Supreme Court outcome. The California denials printed in the petition are pre-existing lower-court history, not the event being predicted.

The durable data-quality flag concerns the substantive lower-court material omitted from the supplied public filing, despite the manifest's nontruncated extraction. It does not allege an extraction failure or treat ordinary absence of a BIO as a defect.
