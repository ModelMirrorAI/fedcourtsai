# Rationale for the numbers

## What I read

Provisioned inputs: `record/snapshots/2026-10-05.json` (the docket through the
October 2 BIO filing), `record/context.json` (forward mode, band `state` under
`sal-v4`, `distribution_count` 1, no CVSG, Term 2026), the event definition
(`stage: cert`, `moment: distribution`), and the three provisioned documents:
`questions-presented.txt`, `petition.txt` (139 pages, truncated in the
appendix but complete through the petition's own conclusion), and
`brief-in-opposition.txt` (30 pages, complete). Beyond those, the committed
statpack and two `fedcourts query` pulls, plus two CourtListener MCP searches
that returned nothing (see `retrieval.md`).

## The anchor

The context freezes band `state` under `sal-v4`, which matches the statpack's
"Segment base rate by salience band (sal-v4)" table, so the evaluator's
yardstick is that band's bracketed `reached` rate pooled over Terms strictly
before OT2026. The table renders OT2017 through OT2025; pooling the bracketed
state figures weighted by their `n`:

| Term | reached rate | n |
| --- | --- | --: |
| 2025 | 37.0% | 27 |
| 2024 | 29.7% | 37 |
| 2023 | 18.8% | 32 |
| 2022 | 13.9% | 36 |
| 2021 | 22.7% | 97 |
| 2020 | 41.3% | 46 |
| 2019 | 15.1% | 53 |
| 2018 | 21.4% | 42 |
| 2017 | 18.4% | 49 |
| pooled | 23.6% | 419 |

So a paid state-petitioner petition that reached the state band faces roughly
a 24% grant-family rate (plenary grants and GVRs together). That is the
number my 0.20 is measured against.

## Adjustments up

- **The Court called for a response after a waiver.** The respondents waived
  on July 10; the Court requested a response on August 3. That is an
  affirmative act by at least one chambers (or the pool) and is not a feature
  the salience band captures. Most state petitions get a BIO as a matter of
  course, so the state-band pool is mostly petitions that were never singled
  out this way. In my experience a called-for response raises the grant
  probability of an otherwise ordinary paid petition severalfold, into the
  high teens or low twenties; it does not by itself make a grant likely.
- **Repeat-player counsel and a real en banc split below.** Louisiana's
  Solicitor General filed a clean, short petition; the Fifth Circuit denied
  rehearing 11-6 with a five-judge dissent (Jones) and a separate statement
  from Smith's own author conceding the "concerning conundrum" of serial
  90-day injunctions. The PLRA-compliance angle is one several Justices care
  about.
- **The legal point on QP 2 is genuinely strong.** Bellotti and Turner frame
  evading review around plenary review in this Court, and no one disputes
  that 90 days cannot reach that.

## Adjustments down

- **Final judgment for the petitioners.** This is the BIO's lead point and I
  find it close to dispositive on vehicle. The district court entered judgment
  for Louisiana on May 26, 2026, after a bench trial. The expired preliminary
  injunctions have merged into a final judgment resolving the same Eighth
  Amendment claim (Harper v. Poway; Shaffer v. Carter). A grant would at most
  produce a vacatur followed by a renewed dismissal below on this independent
  ground. The petition addresses this only in its last paragraph.
- **The capable-of-repetition element was never satisfied.** The petition
  argues only the evading-review prong. The BIO lays out that the three
  injunctions imposed different obligations, that petitioners changed their
  heat policies repeatedly, and that respondents disclaimed winter relief. The
  Court cannot summarily reverse on a prong the petition does not brief.
- **The Fifth Circuit did not squarely hold what QP 2 attributes to it.** The
  BIO shows that neither VOTE panel addressed the level-of-review question and
  that Smith only said the court "could have" expedited. A summary reversal
  needs an obvious error on the face of the decision below; a question the
  court below never reached is a poor target.
- **No intervening decision.** The GVR route, which carries a large share of
  the state band's grant family, is unavailable: Consumers' Research (June
  2025) predates both Fifth Circuit decisions.
- **The problem will recur in a better posture.** The BIO's closing point,
  that if this arises as often as petitioners say then a case will arrive
  before final judgment, is the kind of argument that persuades the Court to
  wait.

Net: the response request pushes toward the anchor; the vehicle problems push
below it. I land at 0.20, slightly under the 23.6% pooled band rate.

## The other claims

- **relist-increment 0.97.** The one frozen distribution was overtaken by the
  response request. Once the reply is in, the Clerk will redistribute. The
  residual is withdrawal or dismissal before redistribution, which I consider
  very unlikely for a state petitioner that just obtained a response.
- **cvsg-increment 0.04.** The paid-segment CVSG rate is about 1.2% (173 of
  roughly 14,000). A federal statute is involved and the United States is a
  frequent PLRA litigant, so I lift it modestly, but a mootness-doctrine
  question with no federal party and a response already in hand is not the
  usual CVSG shape.
- **summary-disposition-route 0.55.** The per-Term table shows the GVR share
  of the grant family at 30-59% in Terms where the label existed; my
  conditional is above the middle of that range because the petition leads
  with summary reversal, the question is short, and the posture (petitioners
  already won) makes argument unattractive. A GVR proper is unlikely; a
  per curiam vacatur is the summary form I have in mind.
- **dissent-from-denial 0.20.** Statements respecting denial are rare
  overall, but the response request, the state petitioner, and the
  district-court-compliance theme Judge Jones framed give a natural hook. I
  weigh it as a real but minority possibility.
- **big_case_score 0.3.** Institutionally meaningful for prison litigation in
  the Fifth Circuit and attached to a newsworthy underlying case, but the
  petitioners have already won and the question is procedural.

## Uncertainty and where to discount me

- I have no committed cut for "response requested after waiver" and priced
  that signal from general knowledge; if the true conditional grant rate for
  that state is materially above 20%, my number is low.
- I could not read the Fifth Circuit panel opinions or the full Jones
  dissent (the petition appendix is truncated), so my view of what the court
  below "held" rests on how the two sides characterize it. The BIO's reading
  (no categorical holding, no level-of-review holding) is the more careful
  one on the excerpts I have, but I am inferring.
- The statpack's state band is thin per Term (n 27 to 97) and the reached
  rate swings from 14% to 41% across Terms; the pooled figure is the right
  anchor but carries that variance.
- The CourtListener docket search returned no record for this docket number,
  so no post-snapshot development was observed; the snapshot is dated today
  and I treat it as current.
