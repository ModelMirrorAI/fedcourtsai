# Why P(grant) = 0.10, and not another number

## What I read

- Provisioned snapshot `record/snapshots/2026-09-17.json` (the file `context.json` names).
  Paid petition, No. 25-1322, docketed May 28, 2026, from the California Court of Appeal,
  Second District (published, 116 Cal. App. 5th 813); Cal. Supreme Court denied review
  Feb. 25, 2026. Entries: petition (May 26), four cert-stage amicus briefs (Goldwater,
  WLF, Cato et al., Manhattan Institute; June 25–29), BIO filed June 29 without being
  called for, reply July 13, **one distribution** for the Conference of 9/28/2026 (July 15).
  No relist, no CVSG.
- `record/context.json`: mode `forward`, `band: baseline`, `salience_version: sal-v4`,
  `distribution_count: 1`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (46 pp.) and
  `brief-in-opposition.txt` (29 pp.), all with `empty_text: false`, per `documents.json`.
  I read all three in full.
- `metrics/statpack.md`: the modern-cert disposition table, the relist and CVSG cuts, the
  per-Term table and the sal-v4 band segment table.

## Anchor

The band in my context is `baseline` under sal-v4, and the statpack's band table is also
sal-v4, so the table is my anchor. Pooling the bracketed `reached` figures for `baseline`
over the eight Terms strictly before OT2025 that the table renders (OT2017–OT2024,
n = 11,580 weighted) gives **5.1%**. That is the rate for a paid private petition that has
reached a first distribution with no CVSG, which is exactly this petition's state, and it is
the yardstick the evaluator scores this cell against. The whole-docket modern-cert grant
family (granted + gvr) is about 2.8%, and the relist-0 bucket of the relist cut sits at
1.7% granted-family, but both are terminal-count populations and understate a live
petition's future, so I did not anchor on them.

## Adjustments up (from 5% toward ~12%)

- **Counsel and amici.** Pacific Legal Foundation is a repeat player whose takings
  petitions have been granted at a rate far above the docket (Cedar Point, Knick, Sheetz,
  Tyler are all PLF cases). Four cert-stage amicus briefs from Cato, WLF, Goldwater and the
  Manhattan Institute is unusual support for a dispute this small; cert-stage amicus
  filings are among the strongest observable correlates of a grant in the empirical
  literature.
- **The question is one the Court's majority has views about.** The petition's takings
  argument is a direct extension of Cedar Point's per se rule, written by the Chief Justice
  for a six-Justice majority; Justices Thomas and Gorsuch in particular have pressed
  bright-line physical-takings rules.
- **Published opinion, clean legal question, sympathetic petitioner.** The state court
  said in terms that it was bound by PruneYard and could not consider whether it was
  wrongly decided, so the issue is squarely presented and preserved, and the respondent's
  message is one the Centers plausibly did not want associated with their property.

## Adjustments down (back to ~10%)

- **Cedar Point and Moody preserved PruneYard on the record.** The BIO's strongest point.
  Cedar Point (2021) distinguished PruneYard because the center was "open to the public,
  welcoming some 25,000 patrons a day"; Moody (2024) distinguished it because the center
  was not itself engaged in expression. The petition's answer is that the distinction is
  unprincipled, but the Court chose to draw it twice in the last five years, which is
  evidence about what this Court will do with a petition asking it to erase the line.
- **Interlocutory posture and § 1257 finality.** The judgment below reverses a
  preliminary-injunction denial in a state intermediate court; there is no final judgment,
  and the record on burden, time-place-manner limits and attribution is undeveloped. The
  Court rarely takes state-court PI appeals, and a jurisdictional question about finality
  is a vehicle defect that any Justice inclined toward denial can rest on.
- **No split, and an overruling ask.** The state-by-state variation the petition catalogs
  (California, New Jersey, Colorado, Massachusetts) is variation in state constitutional
  law, not disagreement about the federal question. The Court has previously let
  PruneYard-based state rulings stand without granting (the union-access cases from
  California in the 2000s and 2010s, on my recollection; not verified this session because
  the CourtListener MCP was throttled).
- **No federal interest** means no CVSG and no SG amicus to lend weight.

Net: I place P(grant) at **0.10**, roughly double the band anchor. I considered 0.15 and
came down because the interlocutory posture is a hard problem the reply cannot argue
away, and because the two recent majority opinions distinguishing PruneYard read to me as a
Court content with the line rather than one looking for a chance to move it.

## The other claims

- **relist-increment 0.35.** In the relist cut, about a quarter of paid scored petitions
  end with one or more relists (a bucket that also counts reschedules). This petition has
  more than the median amount of signal (amici, PLF, an ideologically salient ask) and sits
  on the long conference, where relists are routine. I would put a bare paid petition at
  ~0.20 and this one at 0.35. A relist here would more often reflect a Justice weighing a
  separate writing than an impending grant.
- **cvsg-increment 0.02.** No federal party, statute or program. Near the floor.
- **summary-disposition-route 0.03.** Conditional on a grant. No intervening decision to
  GVR in light of; an overruling or confining of PruneYard needs argument.
- **dissent-from-denial 0.15.** Conditional on a denial. A Thomas statement or dissent is
  the plausible form; the interlocutory posture is a ready reason for even a sympathetic
  Justice to stay quiet. No baseline is published for this claim, so this is my honest
  number, not a hedge against a baseline.
- **big_case_score 0.7.** Stakes if decided, not odds: a decision overruling or gutting
  PruneYard would be a headline property-rights and speech case affecting every
  PruneYard-following state and California's initiative signature-gathering ecosystem.

## Where to discount me

- **Retrieval was degraded.** All three CourtListener MCP calls returned HTTP 429 (the
  shared 300/hour limit, presumably exhausted by sibling cells in this fan-out), so I could
  not check the live docket for post-snapshot entries, confirm prior PruneYard-related cert
  denials, or read post-2021 opinions discussing PruneYard and Cedar Point together. The
  forecast rests on the provisioned inputs, the statpack, one corpus `query` for recent
  granted SCOTUS priors (which returned mostly interim applications and Second Amendment
  petitions, not useful as analogues), and my training knowledge of the case law.
- **My memory of prior PruneYard-challenge denials** (Fashion Valley Mall, Ralphs Grocery)
  is not verified this session; if it is wrong the "Court has let these stand" adjustment
  weakens slightly.
- **I do not know the outcome.** The conference is September 28, 2026, eleven days after
  the snapshot; nothing I read discloses a disposition, and I did not seek one.
- The band anchor is a cohort rate; nothing in the pack conditions on cert-stage amicus
  count or on counsel identity, so the size of my upward adjustment is judgment, not a
  looked-up figure.
