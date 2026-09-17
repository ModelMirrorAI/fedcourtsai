# Reasoning — why P(grant) = 0.007

## Cell and mode

Forward cell, `evt-petition-disposition`, `moment: distribution`, cert stage. `record/context.json`: `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`, `cutoff: null`. Snapshot read: `record/snapshots/2026-09-16.json`. Provisioned documents read: `petition.txt` (23 pages, text extracted) and `questions-presented.txt`. `documents.json` lists no brief in opposition and the docket carries no waiver, so the respondent's position is not on my desk; I am not inferring its content.

## Anchor

The statpack's *Segment base rate by salience band (sal-v4)* table matches my context's salience version and carries a `baseline` column. Pooling the bracketed `reached` figure over the eight Terms strictly before OT2025 (OT2017–OT2024, n ≈ 11,580 weighted) gives about **5.1%**. That is the rate for a paid private petition that has reached the weakest band and might still climb; the leading figure for petitions that ended in `baseline` runs about 1%. The evaluator scores me against the bracketed rate, so 5.1% is the yardstick.

## Adjustments down (large)

- **No federal question with traction.** The petition argues, in substance, that summary judgment is unconstitutional when it resolves disputed facts, citing Suja Thomas's article and Blackstone. It alleges no split of authority — not among circuits, not among state high courts. The cited Supreme Court authority (Anderson, Tolan) already states the rule the petitioner says was violated, so the petition reads as a request for error correction of a state court's application of settled law.
- **Seventh Amendment prong fails at the threshold.** QP 2 invokes the Seventh Amendment against a Washington state court; the Court has never incorporated it against the states. That leaves the due-process prong, which is a fact-bound complaint about one oral remark by the trial judge.
- **State-law vehicle.** The action was for reformation of a deed of trust's legal description, an equitable state-law claim. The Washington Court of Appeals decided it in an **unpublished** opinion and the Washington Supreme Court denied review. The statpack's originating-court cut shows state intermediate courts granting at roughly zero to one percent of resolved petitions.
- **No response on file, distributed anyway.** The Court distributed on July 8 for the long conference with neither a BIO nor a waiver docketed; the docket header on CourtListener was last modified that day and is not terminated. That means no Justice or clerk has yet asked for a response — the usual first sign of interest in an unopposed paid petition.
- **Counsel profile.** Counsel of record (Stafne Law, Arlington, WA) is, to my knowledge from training, a repeat filer of Washington foreclosure-adjacent certiorari petitions that have been denied; I could not confirm this through the corpus or CourtListener (no counsel filter, no search hits), so I weight it lightly.
- **Long-conference denominator.** Petitions decided off the September long conference are overwhelmingly denied on the first October order list.

## Adjustments up (none material)

The petition is paid, timely, and procedurally clean. That is table stakes for the band and adds nothing over the anchor.

## Result

I place the petition in the bottom tail of the baseline band, well below the 1% ended-there rate: **0.007**. The Brier cost of being at 0.007 rather than 0.02 is negligible either way; the number records my genuine view that this is a near-certain denial.

## Other claims

- **relist-increment 0.12.** From one distribution, the paid-segment shape (about a quarter of petitions show a terminal count above 0, an upper bound that includes reschedules) would suggest higher, but this petition has no response to await and nothing to attract a hold. The residual mass is a call for a response followed by redistribution, or a reschedule.
- **cvsg-increment 0.005.** No federal interest of any kind.
- **summary-disposition-route 0.55.** Conditional on a grant, the only realistic grant is a Tolan-style per curiam; the pack's overall cert-order share of grants (gvr vs granted) is near half, and I shade above it because a plenary grant on this QP is the less believable arm.
- **dissent-from-denial 0.01.** No Justice has an evident stake.

## Big-case score 0.12

Scored on stakes if decided, not grant odds. The question as framed would be enormous if the Court ever took it seriously, but the realistic content of any decision here is a one-property deed dispute, so I score low rather than high, and note the tension.

## Uncertainty and where to discount me

- I cannot see the state-court opinions (the appendix was not provisioned), so my read of the record is the petition's own characterization.
- The counsel-history point rests on training recollection, unverified this run.
- If the Court calls for a response before September 28 the relist claim resolves true and the grant probability should be read as having been formed without that signal.

## Retrieval and tooling notes

One `fedcourts query` (granted, 2020s, scotus) returned mostly emergency applications and high-profile petitions; useful only as a shape check. CourtListener MCP: the search index holds no record for 25-1310 or for the counsel name; the `dockets` endpoint confirmed the docket header (filed 2026-05-26, not terminated, last modified 2026-07-08); `docket-entries` returned nothing, as expected for a supremecourt.gov docket. No outcome material surfaced.
