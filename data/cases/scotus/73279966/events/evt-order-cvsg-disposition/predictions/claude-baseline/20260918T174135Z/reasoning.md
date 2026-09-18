# Why 0.80

## What I read

Provisioned inputs: the 2026-05-19 snapshot (14 docket entries through the May 18, 2026
CVSG), `context.json` (forward mode, band `high` under sal-v4, Term 2025, one
distribution, cutoff 2026-05-19), the QP file, the petition text and the two briefs in
opposition (both truncated by the pipeline but substantively complete for the arguments
against review). I read the petition and BIOs through summarizing subagents and cite what
they reported.

## Anchors

- Salience band `high` (sal-v4, which matches the statpack table's version). Pooling the
  bracketed `reached` figures over Terms 2017 through 2024 (the rows strictly before Term
  2025) gives roughly 314 grants over 898 petitions, about **35%**. That is the yardstick
  the evaluator scores this cell against.
- The paid-segment CVSG cut agrees: granted 29.4% plus gvr 5.5%, about **35%** grant
  family, against 62% denied.
- Those rates pool CVSGs where the Solicitor General later recommended denial with those
  where it recommended grant. The post-CVSG rate is a mixture, and this cell is no longer
  in the mixture: the SG's recommendation is now known.

## The decisive signal: the Solicitor General's brief (post-snapshot, forward mode)

This is a forward cell, so this docket's own entries after my baseline are legitimate
retrieval. The Supreme Court's docket page for 25-828 shows a September 15, 2026 entry,
"Brief amicus curiae of United States filed." I downloaded and read that brief. It states
that "the petition for a writ of certiorari should be granted," argues the decision below
is wrong on both intergovernmental immunity and preemption, says it "conflicts with
decisions of other courts of appeals" (principally the Third Circuit's CoreCivic v.
Governor of New Jersey, 2025), calls the question one of "exceptional importance" for
federal immigration detention, and calls the case "an ideal vehicle" with final judgments
after jury and bench trials and no open state-law questions. It closes by asking the Court
to grant and reverse.

Historically the Court grants roughly three quarters of petitions on which the SG
recommends a grant, and this brief is unqualified. I place P(grant) at **0.80**, above
that generic rate, because the case-specific features all point the same way:

- The United States has taken GEO's side at every stage across three administrations
  (statement of interest in 2019, amicus briefs before the panel and on rehearing), so the
  Court has an unusually consistent executive-branch position, not a one-administration
  view.
- Seven Ninth Circuit judges dissented from denial of rehearing en banc, and Judge Bennett
  dissented on the panel; the Solicitor General reads the panel as inconsistent with the
  Ninth Circuit's own en banc decision in GEO Group v. Newsom (2022).
- United States v. Washington (2022), a unanimous decision striking a Washington law aimed
  at federal contractor workers at a federal facility, is a close and recent precedent,
  which makes the Court's own interest in policing this state's treatment of federal
  contractors credible.
- A $37 million judgment and a suspended federal work program give the question concrete
  consequences, and Paul Clement is counsel of record.
- A companion petition, GEO Group v. Ferguson, No. 26-71, is pending on Washington's
  facility-regulation law, so the Court is being shown a pattern rather than a one-off.

## Why not higher

- The BIOs' best point has some force: the Third Circuit in CoreCivic expressly
  distinguished this case as a law that "merely burdens" a contractor, so the conflict is
  arguable rather than square, and the Second and Fourth Circuit cases are 1985 and 1998
  licensing decisions. The Court sometimes denies SG-backed petitions where the split is
  soft.
- The case is one state's law applied to one facility, after a state supreme court answer
  on certified questions; a Court wary of state-specific wage disputes could see it as a
  vehicle for a narrow ruling.
- Only one amicus brief supported the petition at the cert stage.
- Residual paths that are not grants: settlement or withdrawal (unlikely after nine years
  of litigation, but nonzero) and a decision to hold the petition indefinitely.

## Claims

- `disposition` 0.80, identical to the top-level probability.
- `relist-increment` 0.98: the docket shows one distribution; after an SG brief the
  petition is always redistributed, so the only way this fails is a withdrawal or
  dismissal before the next conference.
- `cvsg-increment` 0.01: a CVSG is already on the docket, so the harness masks this as
  vacuous; a second invitation does not happen.
- `summary-disposition-route` 0.05: conditional on a grant, no intervening decision
  supports a GVR and the SG asks for plenary reversal on a contested constitutional
  question; a per curiam reversal is a remote possibility.
- `dissent-from-denial` 0.45: conditional on a denial, which would come over an
  SG grant recommendation and seven en banc dissenters, a noted dissent or statement is
  somewhat more likely than not to be absent but well above the ordinary rate.

## Big-case score

0.60. The stakes are the viability of the federal government's contractor model for
immigration detention and the reach of intergovernmental immunity to contractors, in a
politically charged federal-state conflict. Doctrinally the likely ruling is an
application of United States v. Washington rather than a new framework, which keeps it
short of the top tier.

## Retrieval and its limits

The CourtListener MCP docket-entries endpoint returned zero entries for this docket
(CourtListener holds no entries for SCOTUS dockets), so the post-snapshot check came from
the Supreme Court's own docket page and the SG brief PDF via web fetch, plus SCOTUSblog's
case page. One `fedcourts query` for 2020s granted SCOTUS priors returned interim
applications and unrelated cert grants and did not inform the number. Corpus base rates
came from the committed `metrics/statpack.md`. I did not read the earlier predictions in
this event's directory. I do not know this petition's outcome; as of September 18, 2026 it
is pending and has not been redistributed.
