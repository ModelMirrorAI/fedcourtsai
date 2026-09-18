# Rationale for P(grant) = 0.09

## What I read

Provisioned inputs: `record/snapshots/2026-09-17.json`, `record/context.json`
(mode `forward`, band `elevated` under sal-v4, distribution_count 2, no CVSG,
Term 2025, paid docket), `record/documents/petition.txt` (52 pages, full text),
`record/documents/brief-in-opposition.txt` (24 pages, full text) and
`record/documents/questions-presented.txt`. None of the documents was flagged
`empty_text` or truncated. The corpus vintage is whatever the harness
provisioned as the 2026-09-17 snapshot; the docket's own last entry is the
July 29, 2026 distribution for the September 28 conference.

## Anchor

Cert-stage cell, `moment: distribution`, band `elevated`, salience version
sal-v4 matching the statpack's "Segment base rate by salience band (sal-v4)"
table. Pooling the bracketed `reached` figures over every rendered Term
strictly before this petition's Term (2017 through 2024):

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

Pooled: about 484 grants over n = 2810, a rate of roughly 17%. That is the
yardstick I am scored against, and I moved well below it.

Cross-checks from the same pack: the relist-count cut's bucket 1 (which is
where a distribution count of 2 lands) shows granted 8.2% plus gvr 5.1%; the
CVSG cut's `none` row shows 4.0% granted plus 2.3% gvr; the CA10 origin row
shows 2.5% granted plus 1.4% gvr. The modern discretionary-cert grant family is
a few percent overall.

## Why I am below the band anchor

1. **The second distribution is not a relist.** The June 2 distribution was
   pre-empted by the June 15 call for a response, and the July 29 distribution
   is the ordinary redistribution once the response and reply were in. The
   Justices have never discussed this petition at conference and chosen to
   hold it. The `elevated` band and the relist-1 bucket both read the count as
   if they had, so the population they describe is more favourable than this
   petition's real state. A call for a response is a genuine signal that at
   least one chambers found the petition worth a look, and I credit it, but it
   is weaker than a true relist.
2. **The ask is to overrule a repeatedly reaffirmed precedent with no split.**
   *Jones* has been followed by every circuit for 65 years and the BIO
   correctly notes the Court has built on it in *Aguilar*, *Harris*, *Franks*
   and *Gates*. The Court almost never grants an "overrule X" petition without
   either a split, a statutory or doctrinal intervening development, or prior
   separate writings from its own members inviting the challenge. I know of no
   Justice who has called for revisiting *Jones* or the oath requirement.
3. **The practical radius is enormous.** The proposed rule would invalidate the
   fellow-officer relay and informant affidavits that support most warrants,
   federal and state. The BIO's workability section is the strongest part of
   an otherwise thin brief, and it is the argument most likely to persuade the
   Chief Justice, Justice Kavanaugh and Justice Barrett that this is not a
   question to open.
4. **Vehicle issues.** The decision below is an unpublished Tenth Circuit order
   and judgment that says only that *Jones* binds it. The claim is a *Monell*
   damages claim against a city for following Supreme Court precedent. I think
   the BIO overstates this (an express policy that is itself unconstitutional
   needs no deliberate-indifference showing, and municipalities have no
   qualified immunity), but the Court would still be deciding a foundational
   Fourth Amendment question in a civil suit over a seized baseball bat, with
   no lower-court analysis of the merits at all.

## Why I am not lower

1. The call for a response after a waiver-shaped silence from Denver is a real
   chambers-level signal, and it came at the first conference.
2. Four cert-stage amicus briefs, including law scholars represented by Gibson
   Dunn, a law-enforcement group and victims of well-known warrant failures,
   show the issue has an organised constituency.
3. The Institute for Justice is a repeat Supreme Court advocate with recent
   grants, and the petition is a careful text-and-history brief built on a
   published law-review treatment, pitched squarely at the *Crawford*/*Ramos*
   line the originalist Justices have embraced.
4. Justices Gorsuch and Thomas have shown appetite for Fourth Amendment
   originalism, so a path to a statement or dissent, and a small path to four
   votes, exists.

Netting these, I land at 0.09: roughly half the band anchor, above the
no-signal population's few percent.

## The other claims

- **relist-increment 0.35.** The pack's terminal-count shape says a petition
  at one recorded relist reaches two about 28% of the time (970 of about 3,500
  in the relist cut). I adjust up for the response call, the amicus count and
  the material chance a Justice writes on the denial, which usually costs one
  relist, and down because the count here overstates the real relist state.
- **cvsg-increment 0.07.** No federal party; the Court has already picked its
  intervention once; the SG's answer is predictable. Kept off the floor because
  federal warrant practice is directly implicated.
- **summary-disposition-route 0.03.** Conditional on a grant. No intervening
  decision and no plausible per curiam overruling; a grant would be plenary.
- **dissent-from-denial 0.22.** Conditional on a denial. Existence only. The
  originalist framing and the sympathetic facts give two plausible authors, but
  most denials of this kind are silent.
- **big_case_score 0.7.** Stakes if decided, not odds: a merits ruling on the
  oath requirement would affect every warrant application in the country.

## Uncertainty and where to discount me

- I cannot observe what happened at the June 18 conference beyond the response
  call, and I do not know which chambers made it.
- I have no committed rate for petitions that drew a call for a response
  without a relist; my treatment of that signal as weaker than a relist is a
  judgement, not a statpack figure.
- Corpus `fedcourts query` priors returned mostly interim applications and
  unrelated petitions and did not inform the number; the CourtListener lookups
  returned nothing for this docket, so I saw no docket movement after the
  provisioned snapshot and relied on it entirely.
- I did not read either prior predictor run on this event.
