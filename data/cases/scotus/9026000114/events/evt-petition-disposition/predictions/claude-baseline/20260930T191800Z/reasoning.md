# Why 0.13

## Mode, inputs, and freshness

Forward cell. I read the provisioned snapshot `2026-09-30.json`, `context.json`
(band `elevated`, `salience_version` `sal-v4`, `distribution_count` 2, no CVSG,
term 2026, `signals_observable` true), `event.yaml` (stage cert, moment
distribution), and all three provisioned documents: `questions-presented.txt`,
`petition.txt` (203 pages, truncated, text intact), and
`brief-in-opposition.txt` (31 pages, complete). None had `empty_text`. Beyond
the record I read the Fourth Circuit's published opinion (No. 24-1954, Jan. 23,
2026) via the CourtListener MCP server and ran three `fedcourts query` calls;
see `retrieval.md`. Nothing I retrieved disclosed this petition's disposition;
the snapshot is dated today and the petition is pending for the October 16
conference.

## Anchor

The context band is `elevated` under `sal-v4`, which matches the statpack's
"Segment base rate by salience band (sal-v4)" table, so the table is my anchor.
Pooling the bracketed `reached` figure over every rendered Term strictly before
OT2026 (OT2017 through OT2025) gives **16.9%** (weighted grants 521.5 over
n = 3085). Petitioners are private parties (Allen and Nautilus Productions), so
no caption-class floor applies; the `baseline` class floor pooled the same way
is 5.0%, quoted only for scale. The modern-cert grant-family rate is a few
percent, and the relist-count cut would put a two-distribution petition near
28% granted plus 13% GVR, but that bucket is terminal-count and the two entries
here are not two relists (see below), so I do not use it.

## What moved me down from 16.9%

1. **The BIO lands its main punch.** Petitioners frame the Fourth Circuit as
   having adopted a "but-for" test outside Swint. The opinion itself (which I
   read) says it exercises jurisdiction "under either prong of the pendent
   jurisdiction analysis", calls the 2021 order "linked inextricably" to the
   2024 immunity ruling, and cites Fourth Circuit cases holding Swint's two
   scenarios exclusive. The BIO's point that the Fourth Circuit "follows the
   majority rule" is therefore textually accurate. That converts QP 1 from a
   clean ceiling-versus-floor split into a dispute about how loosely
   "inextricably intertwined" may be applied, which reads as error correction.
2. **The split as pleaded is contestable.** The BIO answers each minority
   circuit citation (Fifth Circuit's four "situations" as applications of
   Swint; D.C. Circuit's exceptions confined to personal jurisdiction, forum
   non conveniens, limitations; Eleventh and Federal Circuit cases as
   intra-circuit at most). I find the rebuttal at least as persuasive as the
   petition's 8-3-2 count. The Court generally wants a split it can see in
   the holdings, and here the disagreement is largely about verbal
   formulations.
3. **No amicus support.** For a petition claiming a decades-old, frequently
   recurring conflict over federal appellate jurisdiction, the absence of any
   amicus (no civil-procedure scholars, no bar groups) is a negative signal.
4. **Posture and equities.** The Court unanimously held for these respondents
   on sovereign immunity in 2020. The district court then reopened a closed
   case on a new abrogation theory while criticizing Hans v. Louisiana. A
   pending Fourth Circuit appeal (No. 26-1576) sits in abeyance. The Court is
   unlikely to want a second trip through this record to police a
   discretionary jurisdictional doctrine.
5. **Summary reversal on QP 2 is a weak ask.** A court of appeals may examine
   its own jurisdiction sua sponte; Allen himself contested jurisdiction over
   the 2021 order; and the BIO cites argument audio in which respondents said
   the intertwined prong was "one way" to reach it. That is far from the
   as-applied-to-facial transformations the Court has summarily reversed.

## What moved me back up

1. **Response requested after a waiver.** Someone at the Court wanted the
   State's answer; that is a real signal of interest and is likely part of
   why the band is `elevated`. I treat it as mostly priced into the anchor.
2. **A published, reasoned opinion, and an outcome-determinative question.**
   Vehicle mechanics are otherwise good: the Fourth Circuit rested solely on
   pendent jurisdiction (it expressly declined the merger theory), and its
   exercise of that jurisdiction ended the case with prejudice.
3. **The Court's appetite for appellate-jurisdiction cleanup and for the
   Fourth Circuit's party-presentation practice.** The petition cites three
   corrections of the Fourth Circuit last Term. That keeps the summary route
   live conditional on a grant.

Net: a little below the band anchor. **P(grant) = 0.13.** I would put a
plausible range at 0.08 to 0.20.

## The other claims

- `relist-increment` 0.28: the docket shows two distribution entries, but the
  first was superseded by the response request, so October 16 is the first
  conference at which the petition is actually considered. Roughly 0.11 of the
  0.28 is the grant path (grants almost always carry one prior relist); the
  rest is relists preceding a denial with or without a statement, and
  reschedules, which also add a distribution entry.
- `cvsg-increment` 0.04: no federal interest.
- `summary-disposition-route` 0.30, conditional on grant: no intervening
  decision exists for a GVR, so this is entirely the per curiam reversal
  petitioners request. The statpack's grant family is roughly half GVR, but
  that share is dominated by intervening-decision GVRs that cannot happen
  here, so I sit below it.
- `dissent-from-denial` 0.08, conditional on denial.
- `big_case_score` 0.3: technical procedural stakes, moderate newsworthiness
  from the Blackbeard backstory and the return trip.

## Where to discount me

I did not read the reply brief (not provisioned; I did not fetch it), so the
petitioners' response to the "illusory split" argument is unweighed. The
petition text I read was truncated at 203 pages, though the reasons-for-granting
section was intact. My relist estimate rests on general knowledge of the
Court's relist-before-grant practice rather than a corpus-conditioned hazard,
which the statpack does not publish. Corpus `query` results were used only to
confirm the prior trip (No. 18-877, granted after three distributions) and to
see the shape of recent grants; no close doctrinal prior on pendent appellate
jurisdiction exists in the corpus rows I could filter for.
