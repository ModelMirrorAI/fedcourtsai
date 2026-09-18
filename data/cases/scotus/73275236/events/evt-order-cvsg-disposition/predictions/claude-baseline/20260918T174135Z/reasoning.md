# Why P(any grant) = 0.50, predicted disposition `gvr`

## What I read

Provisioned inputs: `record/snapshots/2026-01-13.json` (the CVSG-moment baseline:
one distribution, CVSG on Jan 12, 2026, two amicus briefs, paid docket from CA4),
`record/context.json` (forward mode, band `high` under sal-v4, `distribution_count`
1, `cvsg_date` 2026-01-12, Term 2025), `event.yaml` (stage cert, moment cvsg), and the
three provisioned documents, all with text: `questions-presented.txt`,
`petition.txt` (54 pp., Verrilli for General Dynamics et al.) and
`brief-in-opposition.txt` (43 pp., Gupta for Scharpf). I did not read any other
predictor's output or anything under `data/qp-topics/`.

## Anchor

Context band is `high` under sal-v4, matching the statpack table's version. Pooling
the bracketed `reached` figure for `high` over Terms strictly before OT2025
(OT2017–OT2024, weighted n = 898) gives about **35%**. The paid-segment CVSG cut
agrees: among CVSG'd petitions (n = 163 resolved) the grant family is 34.9%
(granted 29.4%, gvr 5.5%), dismissed 3.1%, denied 62.0%. So the leakage-safe
anchor for this moment is roughly 0.35, of which the GVR share is small.

## What moved me off the anchor

This is a forward cell, so retrieval of this docket's later state is permitted. The
public supremecourt.gov docket (fetched 2026-09-18; CourtListener's docket record
was last modified 2026-05-18 and shows no cert grant, denial or termination) has
exactly one entry after the CVSG: a **May 18, 2026 letter** from petitioners'
counsel. It states that respondent voluntarily dismissed her claims against the
General Dynamics entities; that the other petitioners have settlements in principle
that require district-court approval as class settlements; and that petitioners ask
the Court to hold the petition in abeyance until the case becomes moot, when General
Dynamics "will file a suggestion of mootness and will request that this Court grant
certiorari and vacate the judgment below under Munsingwear." No SG brief has been
filed and no order on the letter or the petition has issued. News coverage predating
the letter confirms settlements by Huntington Ingalls, Marinette Marine and Serco
affiliates (notices filed in EDVA, March 2026) and that the district court allowed a
new plaintiff to join the putative class (April 2026).

That converts the question from "will the Court take this split" into "how does a
held, mooting petition end." My scenario weights:

| Path | Weight | Outcome split within path |
| --- | --- | --- |
| Case fully moots; GD files suggestion of mootness seeking vacatur | 0.65 | GVR 0.70, denied 0.25, dismissed 0.05 |
| Petitioners end it themselves (Rule 46 dismissal or stipulation) | 0.12 | dismissed 1.0 |
| Case stays live as to GD (new plaintiff, approval fails); SG files; ordinary cert decision | 0.23 | granted 0.30, denied 0.65, dismissed 0.05 |

Marginals: any grant ≈ 0.52 (GVR ≈ 0.46, plenary ≈ 0.07), denied ≈ 0.31,
dismissed ≈ 0.17. I round the grant number to **0.50** to reflect my uncertainty
about the abeyance being honored and about complete mootness. The modal outcome is
a Munsingwear GVR, which this pipeline's vocabulary records as `gvr` and counts as a
grant, so `granted = 1` and `predicted_disposition = gvr`.

Why 0.70 for vacatur once mootness is suggested: under U.S. Bancorp v. Bonner Mall
vacatur is the norm where mootness comes from "the unilateral action of the party
who prevailed below," which is what a respondent's voluntary dismissal of her claims
against the non-settling petitioner is, and the Court granted exactly such a request
in Chapman v. Doe (2023) over a dissent. I discount because the co-petitioners'
settlements let respondent frame the mootness as settlement-driven, because the
Court must find the whole case moot rather than just GD's part, and because a new
plaintiff in the district court may keep claims against GD alive.

## Claims

- `disposition` 0.50 — equals the top-level probability.
- `relist-increment` 0.82 — every path except a Clerk-entered Rule 46 dismissal
  (~0.15) produces at least one more distribution.
- `cvsg-increment` 0.02 — vacuous here; the CVSG is already on the docket.
- `summary-disposition-route` 0.85 — P(cert-order disposition | grant) ≈ 0.46/0.52.
- `dissent-from-denial` 0.12 — a denial most likely comes as a quiet refusal of
  vacatur or a post-SG denial of a degraded vehicle; separate writings on either are
  uncommon.

## Case read, for the live-petition branch

The petition argues a square 4-vs-1 split (CA5, CA6, CA9 vs CA4) on whether an
unwritten agreement is an affirmative act of concealment, with a Diaz dissent below
and Chamber/NAM and Shipbuilders Council amici. The BIO argues the Fourth Circuit
never adopted the categorical rule the petition attacks, applied the consensus
affirmative-acts test to detailed allegations (coded language, covert enforcement
calls, misleading teaming agreements), and that the split is illusory and the
question fact-bound. Reading the opinion as quoted by both sides, the BIO's
"no rule was adopted" point has force, which is why even on the live branch I put a
plenary grant at only 0.30 despite the CVSG. The SG's likely view is a genuine
unknown to me: the government is itself an antitrust plaintiff that benefits from
generous tolling, but the current SG's office has been business-aligned on private
antitrust exposure.

## Uncertainties and where to discount me

- I could not read the district-court docket, so I do not know whether the new
  plaintiff asserts claims against General Dynamics or whether GD's dismissal was
  with prejudice; either would change the mootness path materially.
- The Court has not ruled on the abeyance request; the Clerk may simply be holding
  the petition informally, or the request may have been overtaken by an SG filing I
  did not see (the docket page showed none).
- The statpack has no cut for mootness or Rule 46 dispositions, so the 0.70 and
  0.12 within-path figures rest on doctrine and recalled practice, not corpus counts.
- CourtListener's MCP docket-entries endpoint returned nothing for this docket; the
  docket state came from a web fetch of supremecourt.gov, which I treat as reliable
  but which was not the sanctioned CourtListener path.
