# Why 0.14 — Utah v. Mullins, No. 25-1115

## What I read

Provisioned inputs: `record/snapshots/2026-09-15.json`, `record/context.json`
(mode `forward`, band `state` under sal-v4, Term 2025, one distribution, no
CVSG), and all three provisioned documents — `questions-presented.txt`,
`petition.txt` (154 pages, flagged `truncated: true`; the petition body and the
Utah Supreme Court's amended opinion at App. 1a–52a were intact, and that is
what I relied on), and `brief-in-opposition.txt` (28 pages, complete). I also
fetched the State's reply brief (docketed Aug 25, 2026, in the snapshot but not
provisioned) from the supremecourt.gov link the docket carries; see
`retrieval.md`. I do not know the outcome: the petition sits on the September
28, 2026 conference, which post-dates this run.

## The case

Utah, through its Solicitor General, seeks review of a 3–2 Utah Supreme Court
decision (2025 UT 57, amended on rehearing) vacating Morris Mullins's 2002
juvenile life-without-parole sentence under the pre-2019 version of Utah R.
Crim. P. 22(e) as "imposed in an illegal manner." The majority read Miller,
Montgomery, and Jones to mean that an affirmative finding that a juvenile can
change bars JLWOP (App. 43a), found no such affirmative finding on this record
(App. 45a), but held that the sentencing judge's "hope … [for] a chance to
change" remark, made while counsel urged leaving the corrigibility question to
the parole board, raised "significant concerns" both that Mullins may be
categorically ineligible and that the judge "misapprehended its constitutional
obligation to consider youth in the proper manner" (App. 46a). It remanded for
resentencing. The dissent read Jones as making a discretionary scheme
sufficient regardless of corrigibility.

The BIO (Federal Public Defender, D. Utah) leads with §1257 finality: the
sentence is vacated, resentencing is pending, and no Cox Broadcasting exception
applies. It then argues the split is illusory (only Maryland's *Malvo* squarely
answers the question the same way; the 16 "contrary" cases involved no
corrigibility finding), that the amended opinion rests on a second independent
ground the petition does not challenge, that the record has no clean
corrigibility finding, that the question is inconsequential (Utah abolished
JLWOP prospectively in 2016; two Utah JLWOP inmates; Mullins faces a
consecutive Arizona life sentence), and that no state filed an amicus brief in
support. The reply invokes Cox's third category (later review cannot be had,
citing *Kansas v. Marsh* and *New York v. Quarles*), characterizes the
consider-youth language as a rationale rather than a holding, and reframes the
split as one over the legal rule rather than the facts.

## Anchor

`context.json` freezes band `state` under sal-v4, which matches the statpack's
"Segment base rate by salience band (sal-v4)" table, so the anchor is the
`state` column's bracketed `reached` rate pooled over Terms strictly before
2025. Pooling the eight rendered prior Terms (2017–2024) by their `reached`
denominators:

| Term | reached rate | n |
| --- | --- | --: |
| 2024 | 29.7% | 37 |
| 2023 | 18.8% | 32 |
| 2022 | 13.9% | 36 |
| 2021 | 22.7% | 97 |
| 2020 | 41.3% | 46 |
| 2019 | 15.1% | 53 |
| 2018 | 21.4% | 42 |
| 2017 | 18.4% | 49 |

Weighted pool ≈ 89 grants / 392 ≈ **0.227**. That is the grant-family rate
(grant + GVR + summary reversal) for a paid state-petitioner petition, and the
figure the evaluator scores skill against. The relist-0 cut (1.2% granted, 0.5%
GVR) and the no-CVSG cut (4.0% / 2.3%) describe the population's shape but are
terminal-state figures and I did not anchor on them.

## Adjustments

**Down, substantially, for the final-judgment problem.** The Utah court
vacated the sentence and remanded for resentencing; a criminal judgment is the
sentence (*Berman*). The State's Cox-category-3 argument is respectable
(*Quarles*, *Marsh*), but it was raised only in the reply, the BIO's answer
(the trial court can reimpose LWOP, and the State can appeal an illegal
sentence) is not frivolous, and the Court has been burned before granting a
state criminal petition and then dismissing for want of a final judgment
(*Florida v. Thomas*). An unresolved jurisdictional question at the cert stage
is a strong reason to wait for a cleaner vehicle.

**Down for vehicle and record quality.** There is no affirmative corrigibility
finding — the Utah court said so (App. 45a, 51a) — so the QP's premise ("even
if the court finds that the juvenile is not permanently incorrigible") is not
squarely presented. The decision rests on "ambiguous comments" at a 2002
pre-Miller sentencing, framed under a state procedural rule, and carries a
second rationale (the judge appeared to leave consideration of youth to the
parole board) that reads as an ordinary Miller-process ground Jones itself
preserves. The reply's answer that both rationales "vanish" if the Court
reverses the legal rule is plausible but contestable, and contestable is
enough to make the Court prefer the next case.

**Down for stakes and support.** Utah bars JLWOP prospectively, only one other
Utah inmate is affected and his case has no corrigibility finding, Mullins
faces a consecutive Arizona life sentence, and — a point the reply does not
answer — no other state supported the petition. State petitions that the Court
grants in recent Terms have typically come with a multistate amicus brief.

**Up for the doctrinal signal.** The tension between Montgomery's "key
paragraph" and Jones's "necessary and sufficient" holding is real, the Seventh
Circuit (*Walker v. Cromwell*, 2025) has said the law "simply is not clear,"
the Utah court itself acknowledged the division, and the dissent below lays the
split out. The Court's majority is receptive to state petitions where a state
high court reads federal constitutional protections more broadly than this
Court's precedent, and the Justice who wrote Jones may be irritated by a
holding that reads like a substantive corrigibility rule. This keeps the number
well above the private-petitioner floor.

Net: from 0.227 to **0.14**. The mass under 0.14 is split between plenary
review (roughly 0.10) and a summary reversal (roughly 0.04), which is why the
conditional `summary-disposition-route` claim sits at 0.30.

## The other claims

- `relist-increment` 0.38: one distribution shown. P(relist | grant) ≈ 0.85
  under the Court's current relist-before-grant practice; P(relist | deny) ≈
  0.30 for a state petition with a colorable split, where a held-over
  conference or a possible separate writing is the usual reason. 0.14·0.85 +
  0.86·0.30 ≈ 0.38.
- `cvsg-increment` 0.03: no federal interest; CVSGs in state criminal Eighth
  Amendment cases are nearly unheard of.
- `summary-disposition-route` 0.30 (conditional on grant): reasoning above. No
  intervening decision, so a GVR is not in play.
- `dissent-from-denial` 0.12 (conditional on denial): a Thomas or Alito
  statement is conceivable given Thomas's Jones concurrence, but denials on
  interlocutory posture rarely draw writing.

## Where to discount me

The two largest uncertainties are how seriously the Court takes the finality
defect (if it treats Cox category 3 as plainly satisfied, my grant number is
too low by perhaps 0.05–0.08) and whether the Kavanaugh-authored Jones majority
sees the Utah rule as flatly contrary to Jones (which would raise both the
grant and the summary-reversal numbers). I have not read the Utah rehearing
petitions the BIO quotes, only the parties' characterizations of them. The
petition text was truncated by the pipeline, but the truncation fell inside
the appendices after the Utah opinion's conclusion, so nothing I relied on was
cut. My CourtListener searches for related SCOTUS activity returned nothing
(RECAP carries no SCOTUS docket coverage for this matter), so the check that no
companion JLWOP petition is pending or granted this Term rests on my general
knowledge through mid-2026 rather than on a retrieved result.
