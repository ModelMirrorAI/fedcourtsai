# Why 0.42

## Inputs read

- `record/snapshots/2026-06-23.json` (the provisioned baseline; `context.json` names it, `cut_kind: date`, `cutoff: 2026-06-23`, mode `forward`).
- `record/context.json`: band `high` under `sal-v4`, `distribution_count` 2, `cvsg_date` 2026-06-22, term 2025, `signals_observable: true`.
- `record/documents/questions-presented.txt`, `petition.txt` (95 pp., full text), `brief-in-opposition.txt` (36 pp., full text). `documents.json` shows none empty or truncated. No reply brief was provisioned; the docket shows one filed 2026-06-02 and I did not retrieve it.
- `metrics/statpack.md`: the modern-cert base rate, the relist and CVSG cuts, and the per-Term salience-band table.
- Event: `stage: cert`, `moment: cvsg`, opened 2026-06-22.

## Anchor

The band table's heading is `sal-v4`, matching the context, and `high` is a column, so the band is my anchor. Pooling the bracketed `reached` figures for `high` over the Term rows strictly before OT2025 (2017 through 2024, n from 98 to 140 each, about 898 weighted resolved petitions in all) gives roughly 35%. Two independent cuts agree: the CVSG cut of the paid scored segment gives a grant family of about 35% (granted 29.4% plus gvr 5.5%, n=163 resolved), and the relist-count bucket 2 gives about 41% (27.8% plus 13.1%), though that bucket is not really this case's situation, because the second distribution here was a redistribution after the requested response rather than a relist after consideration. I take 35% as the anchor, and it is the yardstick the evaluator scores against.

## Adjustments up

- **Two affirmative acts by the Court.** The respondent waived; the Court called for a response anyway (2026-03-23), then called for the SG's views. Each is a signal that at least some chambers see a grant-worthy question. The band already prices the CVSG, but the response request over a waiver is not separately in the anchor.
- **The federal government's likely view.** The petition itself asked for a CVSG and predicts, correctly in my view, that the current administration will say the First Amendment does not shield status-based selection criteria. An SG brief agreeing with the petitioner on the merits raises the grant probability materially, and the Court follows SG recommendations most of the time.
- **Salience and counsel.** Consovoy McCarthy for petitioner; amici include eighteen States, Students for Fair Admissions, America First Legal, and the Manhattan Institute. The issue (whether Dale shields DEI programs) sits squarely in the current majority's area of doctrinal interest after 303 Creative and SFFA.
- **Petitioner's finality point.** The Appellate Division reversed and ordered the complaint dismissed with prejudice; the BIO does not contest finality under 28 U.S.C. 1257, so the jurisdictional-finality trap that often defeats state-intermediate-court petitions is not in play.

## Adjustments down

- **Vehicle.** The BIO's vehicle section is strong and specific: unpublished nonprecedential opinion; New Jersey Supreme Court denied certification; the challenged policy was revised in November 2025 so that every at-large seat is reachable through affinity-bar membership (petitioner belongs to one); the state-law LAD question was never decided below, so a reversal here would not end the case. The Court frequently declines such vehicles even when it dislikes the reasoning below.
- **Article III standing.** Petitioner never applied for a challenged seat, including during the 2022 to 2025 suspension, and argued below that he did not need to. New Jersey courts do not apply Article III, so no court has found standing (ASARCO). The BIO's citation of the 2025 Lab Corp DIG is apt: the Court has recently shown it will not take on a standing fight it can avoid. Petitioner's nominal-damages answer is plausible but rests on a trial-court finding the Appellate Division did not adopt.
- **Split quality.** Fearless Fund (CA11) turned on whether grant-making was expressive at all; NADOHE (CA4) is a funding-condition case. This is a conflict in reasoning more than in holdings, and many federal DEI suits are pending that could supply a cleaner vehicle. The BIO's percolation argument is one the SG may share.
- **Uncertainty about the SG's recommendation.** I put the SG's grant recommendation near even odds. A vehicle-conscious SG could well urge denial while criticizing the decision below, and that shape produces a denial most of the time.

Net: I land at 0.42, about seven points above the anchor. The upward factors are real but the vehicle defects are the kind that turn a CVSG'd petition into a denial with a statement.

## Other claims

- `relist-increment` 0.97: after a CVSG the petition is redistributed once the SG files; only a withdrawal or dismissal before then prevents another distribution.
- `cvsg-increment` 0.02: a CVSG is already on the docket, so the harness will mask this claim; a second invitation essentially never happens.
- `summary-disposition-route` 0.10 (conditional on a grant): no intervening decision to GVR against; a per curiam reversal of a state court is possible but this fact-bound expressive-association question would more likely be argued.
- `dissent-from-denial` 0.35 (conditional on a denial): a CVSG'd, ideologically salient petition denied for vehicle reasons draws a statement or dissent more often than the run of the docket, but most such denials are still silent.
- `big_case_score` 0.72: the stakes if decided are high (a constitutional defense for private DEI programs), independent of the grant odds.

## Where to discount me

- The whole forecast is a mixture over an SG recommendation that does not yet exist. If a reader knows the SG's filing, that dominates everything here.
- I did not read the reply brief or the amicus briefs; my read of the split and vehicle is from the petition and BIO only.
- `fedcourts query` is a structured filter, not a topical search, so the corpus priors I pulled (see `retrieval.md`) are recent SCOTUS grants and denials with no subject-matter link to this case; they informed nothing beyond confirming the tooling works.
- CourtListener's docket-entries feed for this docket shows no entries after 2026-06-22 and a last-modified stamp of that day, which I read as coverage lag rather than as evidence the docket has been quiet; I did not treat it as signal either way.
- Corpus vintage: I did not run `fedcourts corpus-info`; the base rates come from the committed `metrics/statpack.md`, whose OT2025 row shows the Term as complete.
