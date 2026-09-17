# Why P(grant) = 0.01

## What I read
- `record/context.json`: `forward` mode, `band: baseline` under `sal-v4`, `distribution_count: 1`, no CVSG, Term 2025, snapshot `2026-09-16.json`.
- The snapshot `2026-09-16.json`: paid docket 25-1362, pro se petitioner (David Gasper, Chapel Hill, NC, no counsel of record), petition filed March 6, 2026 (docketed June 9, 2026 after a motion to file the supplemental appendix under seal was granted June 8, with Justice Alito not participating), respondents' waiver filed June 11, 2026, distributed once for the September 28, 2026 conference. No CVSG, no amicus, no relist.
- `record/documents/questions-presented.txt` and `petition.txt` (52 pages, full text, not truncated). No brief in opposition exists because respondents waived, so the opposition side is inferred from the docket and from the opinion below.
- Via the CourtListener MCP server: the Fourth Circuit's opinion in No. 24-1959 (published, Dec. 8, 2025, Keenan, S.J., joined by Benjamin and Berner, unanimous; petitioner was represented by counsel below). I read roughly the first two-thirds of it, through the resolution of the benefits claim.

I did not read the earlier claude-baseline run on this event from August 2026, so this forecast is formed independently of it.

## Anchor
Band `baseline` under `sal-v4`, matching the statpack's "Segment base rate by salience band (sal-v4)" table, so the anchor is that band's bracketed `reached` rate pooled over Terms strictly before OT2025: OT2017 through OT2024 (the table renders 10 Terms; OT2026 is empty). Weighting each Term's reached rate by its reached n (4.7% n=1643, 4.6% n=1524, 4.6% n=1399, 4.5% n=1739, 5.6% n=1500, 5.8% n=1192, 5.9% n=1312, 5.7% n=1271) gives a pooled rate of about 5.1% (n ≈ 11,580). That is the yardstick the evaluator will score this cell against.

Shape cuts from the same pack: paid petitions that end at 0 relists resolve granted 1.2% / gvr 0.5%; no-CVSG paid petitions resolve granted 4.0% / gvr 2.3%; the Fourth Circuit's whole-docket grant family is about 2.5%. Those bucket by terminal state and so understate the forward hazard, which is exactly why the reached-band figure is the anchor rather than the relist-0 row.

## Adjustments, all downward
1. **The QPs do not describe the decision below.** QP 1 frames a Chenery / ERISA § 503 "post-hoc rationale" problem. The panel did not affirm on a substituted administrative rationale: it reviewed the QDRO de novo as a court-approved contract under North Carolina law, held that "may be reduced" is permissive, and found the administrator's calculation consistent with that reading and with the plan's summary plan description. There is no Chenery holding to review. QP 2's "unauthorized § 205 form" theory is, in substance, the § 1056(d)(3)(C) argument the panel declined as raised for the first time on appeal (footnote 5). A petition whose questions the lower court did not decide is a poor vehicle regardless of the merits of the claimed split.
2. **The claimed circuit split is asserted, not engaged.** The petition lists First, Third, Seventh and Ninth Circuit cases applying Chenery-type limits to ERISA denials, and calls the Fourth Circuit "permissive". But the Fourth Circuit's own Gagliano, which the petition also cites, is a strict-Chenery case, so the petition's own account is of an intra-circuit inconsistency rather than a split among circuits, and the opinion below does not take a side because it never reached the issue.
3. **Stakes and posture.** The dispute is over $385.26 per month in one participant's annuity. Fact-bound contract interpretation under state law is the paradigm of what the Court declines. The one question of general ERISA law the panel flagged as open in the circuit (de novo versus abuse-of-discretion review of an administrator's reading of a QDRO) was resolved in petitioner's favor, so it cannot be a ground for his petition.
4. **Pro se, waived response.** The petitioner was represented by counsel in the Fourth Circuit but proceeds pro se here. The respondents' waiver signals that a sophisticated ERISA defense firm expects denial without a brief; the Court calls for a response in only a small fraction of such cases and that call is itself the usual precondition to a grant.
5. **Recusal.** Justice Alito's non-participation on the sealing motion suggests he will not participate in the petition either, leaving eight Justices; this slightly lowers the odds of four grant votes but is a marginal factor.

Against that, the only positive signals are that the docket is paid and professionally printed, and the opinion below is published, which removes the "unpublished opinion is a poor vehicle" discount. Neither moves the number much.

## Landing
From a 5% band anchor, the vehicle mismatch, the absence of a genuine engaged split, the trivial stakes and the waiver together put this petition well inside the weakest tail of the baseline band. I land at 0.01 for P(any grant, including GVR). I would not go lower than about 0.005 because the relist-0 terminal row itself shows a 1.7% grant family among paid petitions ending undistributed, some of which look like this one, and because holds and GVRs occasionally reach even unpromising ERISA petitions.

## Claims
- `disposition` 0.01, equal to the top-level probability.
- `relist-increment` 0.10: from one distribution, the realistic paths to a second are a reschedule off the long conference or a hold; roughly a quarter of the paid segment ever sees a second distribution, but the waiver-and-pro-se profile is far below that population's average.
- `cvsg-increment` 0.01: no federal interest was invoked, the respondent did not file, and the QPs do not present a question of plan administration the SG would be asked about.
- `summary-disposition-route` 0.35 conditional on a grant: in this profile grants are disproportionately GVRs, but I see no intervening decision that would generate one, which keeps the conditional below one-half.
- `dissent-from-denial` 0.02: no Justice has shown interest in the ERISA § 503 notice issue as framed, and separate writings on pro se denials are rare.

## Big case score
0.05. Even if decided, this is a single participant's benefits calculation. The Chenery-in-ERISA framing would be of some general interest if it were actually presented, but it is not the ground below.

## Uncertainty and where to discount me
- I could not read a brief in opposition because none exists; the respondent's side is inferred from the waiver and the opinion.
- I read the Fourth Circuit opinion only through the benefits-claim section, not the statutory-penalties discussion, which the petition does not press.
- I did not check for a pending ERISA merits case that could produce a hold; if one exists, the relist-increment number is too low and the GVR conditional too low.
- The pooled anchor arithmetic is mine from the rendered table; the pack's JSON may weight Terms slightly differently.
- Corpus freshness: the snapshot is dated 2026-09-16, one day before this run, and the `fedcourts query` priors came from the corpus service at run time (see retrieval.md); I did not run `corpus-info`.
