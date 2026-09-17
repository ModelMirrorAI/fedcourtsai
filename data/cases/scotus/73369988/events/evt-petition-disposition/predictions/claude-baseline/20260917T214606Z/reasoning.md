# Reasoning — claude-baseline, run 20260917T214606Z

**P(grant) = 0.006.** Predicted disposition: denied.

## What I read

Provisioned inputs, in the order the prompt sets: `AGENTS.md`, the predict
prompt and `schemas/prediction.schema.json`; then `event.yaml` (kind
`petition`, no `stage` or `moment` field, so it reads as a cert cell at the
distribution moment), the snapshot `record/snapshots/2026-09-16.json`,
`record/context.json` (mode `forward`, band `baseline` under `sal-v4`,
`distribution_count` 1, no CVSG, Term 2025, `cutoff` null), and the two
provisioned documents: `petition.txt` (29 pages, text extracted, not
truncated) and `questions-presented.txt`. There is **no brief in
opposition** on disk because none was filed: the docket records
respondent's waiver on June 15, 2026. The Court of Appeal's November 18,
2025 opinion (B331199) is unpublished and is not indexed on CourtListener,
so my account of what it held comes from the petition's own description
and the passages it quotes.

Retrieval beyond the provisioned inputs is listed in `retrieval.md`. The
docket read on CourtListener shows no activity after July 1, 2026 and no
cert grant or denial recorded, so the cell is correctly provisioned as a
pending petition. Nothing I retrieved bears on the outcome.

## The anchor

`context.json` freezes the band at `baseline` under `sal-v4`, and the
statpack's "Segment base rate by salience band (sal-v4)" table matches that
version, so the anchor is that band's **bracketed `reached` rate pooled over
Terms strictly before 2025** (OT2017 through OT2024, all eight rows the
table renders):

| Term | reached rate | n |
| --- | --- | --: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Pooled, that is roughly **5.1%** over about 11,580 weighted petitions. It
is the grant-family rate (plenary grants plus GVRs) among paid petitions
that ever reached the baseline band, and it is the yardstick the evaluator
scores this cell against. The cuts beside it agree on the neighbourhood:
the relist-0 bucket of the paid scored segment resolves granted 1.2% plus
gvr 0.5%, the no-CVSG bucket granted 4.0% plus gvr 2.3%, and OT2025's own
estimated grant rate is 2.6%.

## Why I sit well below the anchor

Every case-specific signal points down from a 5% anchor, and none points up.

- **No split, no federal-law hook stated as one.** The petition alleges no
  conflict among circuits or state courts. Its lead question is whether a
  court may affirm an award while leaving open whether federal or state
  vacatur law governs. The one genuinely open issue underneath (whether FAA
  section 10 binds state courts at all, left open by Hall Street) is not
  presented as such, and petitioner cites only Hall Street, Commonwealth
  Coatings, Caperton and Rippo, none of which the decision below purports to
  contradict.
- **Not outcome-determinative.** By the petition's own account the Court of
  Appeal assumed the more petitioner-friendly federal manifest-disregard
  standard arguendo and held petitioner had not met it, and rejected the
  nondisclosure claims on the ground that the arbitrator's outside
  affiliations were unrelated to the parties. Resolving the choice-of-law
  question would not change the result, which is a vehicle defect the Court
  treats as disqualifying.
- **Weak constitutional theory.** Question 3 applies Caperton and Rippo
  (judicial recusal under the Due Process Clause) to a private arbitrator
  and to an appellate panel member's household affiliation, while the
  petition expressly disclaims any allegation of misconduct or actual bias.
  A due-process neutrality claim against a private arbitrator has a
  state-action problem the petition does not address.
- **Unpublished state intermediate-court opinion.** The originating-court
  cut for the California Court of Appeal, Second Appellate District, shows
  granted 0.7% and gvr 4.6%; the GVR share there is dominated by criminal
  petitions swept in behind lead cases, a pattern that does not reach a
  civil arbitration dispute.
- **Waived response, solo-practitioner counsel, no amici.** The Court
  essentially never grants a paid petition without first calling for a
  response, and no call had issued as of the September 16 snapshot with the
  conference twelve days away. Counsel of record is a sole practitioner
  with no visible Supreme Court practice, and no amicus has appeared. The
  corpus query I ran over 2020s granted SCOTUS priors returned, as
  expected, government parties, repeat Supreme Court advocates and amici on
  nearly every row; this petition has none of those features.
- **Error-correction framing.** The reasons-for-granting section argues that
  the courts below got it wrong, not that the question recurs in a way
  the Court needs to settle. This is the profile of the 97% of baseline-band
  petitions that are denied on first distribution.

Taking the 5.1% risk-set anchor and conditioning on all of the above
(waived response with no call for response, state-court origin,
unpublished opinion, no split, non-outcome-determinative lead question)
leaves me at about half a percent. I write **0.006**, keeping a sliver for
a GVR behind an intervening arbitration decision I have not identified and
for the residual chance that four Justices see the FAA-in-state-court
question in it.

## The other claims

- **relist-increment 0.06.** The docket shows one distribution. A second
  entry would come from a call for a response at or before the September 28
  conference (the only route by which a petition this thin gets a grant, and
  therefore the most likely form of any further distribution), a reschedule
  of the long-conference list, or a relist for a Justice's look. The
  population's relist-1 bucket is roughly a fifth the size of relist-0, but
  that population is weighted toward petitions with a response on file and
  a plausible split; I discount heavily for this one.
- **cvsg-increment 0.003.** No federal interest.
- **summary-disposition-route 0.55.** Conditional on a grant. The
  statpack's modern-cert disposition table puts GVRs at roughly 47% of the
  grant family; I shade above that because a plenary grant on these
  questions presented is the less plausible of two unlikely routes.
- **dissent-from-denial 0.01.** No Justice-level interest in this issue and
  nothing in the record to draw a statement.

## Big-case score

0.05. A private employment-arbitration dispute of consequence to the parties
alone; arbitrator-disclosure standards are of some general professional
interest, but the vehicle is narrow and unpublished.

## Where to discount me

I have not read the opinion below; if the petition's account of it is
uncharitable and the Court of Appeal in fact held the FAA standard
inapplicable in a way that conflicts with other state high courts, the
petition is stronger than I have scored it, though still far below the
anchor given the waiver and vehicle posture. I also cannot see whether a
reply brief or a call for a response landed between September 16 and today;
the CourtListener docket read shows no entry after July 1, and the
snapshot's twelve-day lead on the conference leaves little room for one.
