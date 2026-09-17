# Rationale for the numbers

**P(grant) = 0.004; predicted disposition `denied`.**

## What I read

- `record/snapshots/2026-09-16.json`: paid petition (sJsonCaseType "Paid"),
  docketed May 8, 2026, from the Ninth Circuit (No. 24-7060, decided February
  6, 2026). Petitioner Christopher Veto appears pro se at a residential
  address. Two proceedings entries: the petition filed May 5, 2026 (response
  due June 8, 2026), and "DISTRIBUTED for Conference of 9/28/2026" on June 24,
  2026. No brief in opposition, no waiver entry, no amicus.
- `record/documents/petition.txt` (60 pages, text extracted, not truncated,
  per `documents.json`). No `questions-presented.txt` was provisioned, so I
  read the QP section from the petition itself. There is no BIO to weigh it
  against.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  `distribution_count` 1, no CVSG, term 2025, no cutoff.
- `metrics/statpack.md`: the sal-v4 segment table, the relist-count and CVSG
  cuts, and the originating-circuit cut.

## Anchor

The context's band is `baseline` under `sal-v4`, which matches the table's
version. Pooling the bracketed `reached` rate for `baseline` over the Terms
strictly before this case's (OT2017 through OT2024, all eight rows the table
renders before 2025) gives about 593 grants over a weighted denominator of
11,580, so roughly **5.1%**. That is the rate a live paid private petition in
the baseline band actually faces and the yardstick the evaluator scores against.

The relist-count cut's relist-0 bucket (granted 1.2%, gvr 0.5%) and the
Ninth Circuit cut (granted 2.1%, gvr 1.1%) are consistent with a low single
digit anchor but are terminal-state figures, so I do not substitute them.

## Adjustments

Almost everything about this petition sits in the far lower tail of the
baseline band, and I move well below the anchor:

- **No cognizable legal question.** The nine questions presented ask what
  penalty Boeing should suffer, whether Boeing is a monopoly, whether the
  Export-Import Bank confers unfair advantage, and whether a court of appeals
  may issue a "nation-wide injunction on illegal activity." None states a
  question of federal law decided by the court below. The petition's own
  citations (Muscarello, Kyllo, Gibbons, McCulloch, Dobbs, Bruen) bear no
  relation to a California Labor Code retaliation claim resolved on summary
  judgment.
- **Fact-bound, unpublished, state-law judgment below.** From the petition's
  own account, the district court granted summary judgment because the
  plaintiff's complaints about a marijuana odor were not objectively
  reasonable safety complaints under Cal. Lab. Code §§ 1102.5 and 6310, and
  the Ninth Circuit affirmed in an unpublished memorandum. There is no
  circuit split alleged and none plausible.
- **Pro se drafting quality.** The petition is largely a line-by-line rebuttal
  of the district court order, quoting the petitioner's own emails to counsel
  and deposition excerpts, and closes with "suggested remedies" that would
  add parties and overturn state marijuana statutes. The Court does not grant
  petitions of this kind.
- **No response.** Boeing has not filed a brief in opposition and the case was
  distributed on the response-due date passing. The Court would have to call
  for a response before granting; nothing on the docket suggests it will.

The baseline band's 5.1% is dominated by counseled petitions with at least an
arguable question. I put this petition in roughly the bottom decile of that
population, which is where the paid pro se petitions live, and land at
**0.004**. I do not go lower because the Court occasionally requests a response
or GVRs in surprising places, and because a Brier-proper score does not reward
reporting a number smaller than my honest uncertainty.

## Claims

- `disposition` 0.004, equal to the top-level probability.
- `relist-increment` 0.08. The docket shows one distribution. The relist-count
  cut says about a quarter of the paid scored segment ends with at least one
  more distribution entry, but that is a terminal figure that pools counseled
  petitions and counts reschedules; a hopeless pro se petition at the long
  conference is rarely relisted. Most of my 8% is a reschedule or a call for a
  response, not merits interest.
- `cvsg-increment` 0.002. No federal party or program is at issue.
- `summary-disposition-route` 0.5, conditional on a grant. Conditional on the
  near-impossible event of any grant, plenary review of these questions and a
  GVR are both implausible; I have no basis to favor one and split evenly.
  This claim is masked on the denial I expect.
- `dissent-from-denial` 0.01. Nothing here engages any Justice's recurring
  interests.

## big_case_score

0.03. A single-plaintiff pro se retaliation dispute. Boeing's name and the
737 MAX references give it no legal significance; if decided, nothing would
change for anyone but the petitioner.

## Retrieval and its effect

Forward mode, so retrieval was unrestricted. I confirmed via the CourtListener
docket endpoint that the docket is not terminated and was last modified on the
June 24 distribution, so the snapshot is current and the cell is not
mis-provisioned. A CourtListener opinion search for the Ninth Circuit
memorandum returned unrelated results, so my account of the decision below is
from the petition's own description and appendix references. One `fedcourts
query` for recent SCOTUS priors returned mostly emergency applications and did
not change the number. Details in `retrieval.md`.

## Where to discount me

My read of the judgment below comes entirely from the petitioner's
characterization, which is adversarial toward it; I could not read the Ninth
Circuit memorandum itself. That does not move the grant estimate, since even
the petitioner's framing discloses no certworthy question, but it means my
description of the lower-court reasoning is second-hand. I have no view on
whether the Court will call for a response, which is the one docket event that
would move the number; I would revise to roughly 0.03 if one were requested.
